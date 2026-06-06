/**
 * API service — connects React Native to FastAPI backend.
 * Handles auth tokens, request/response, and error handling.
 */

import Constants from 'expo-constants';
import { Platform } from 'react-native';

const PROD_API_BASE_URL = 'https://api.smarthome.vn';

function normalizeBaseUrl(url: string): string {
    return url.replace(/\/+$/, '');
}

function getHostFromUri(uri?: string | null): string | null {
    if (!uri) return null;

    const normalized = uri.includes('://') ? uri : `http://${uri}`;

    try {
        const host = new URL(normalized).hostname;
        return host || null;
    } catch {
        const match = normalized.match(/^(?:[a-z]+:\/\/)?([^/:?#]+)/i);
        return match?.[1] ?? null;
    }
}

function resolveApiBaseUrl(): string {
    const explicitBaseUrl = process.env.EXPO_PUBLIC_API_URL?.trim();
    if (explicitBaseUrl) {
        const explicitHost = getHostFromUri(explicitBaseUrl);
        const isExplicitLocalhost = explicitHost === 'localhost' || explicitHost === '127.0.0.1';

        // On native dev, localhost env vars are usually unreachable from physical devices.
        if (!(Platform.OS !== 'web' && __DEV__ && isExplicitLocalhost)) {
            return normalizeBaseUrl(explicitBaseUrl);
        }
    }

    if (!__DEV__) {
        return PROD_API_BASE_URL;
    }

    // In Expo dev, derive host from Metro URI so physical devices can reach backend on the same LAN.
    const hostCandidates = [
        Constants.expoConfig?.hostUri,
        Constants.platform?.hostUri,
        Constants.linkingUri,
    ];

    for (const candidate of hostCandidates) {
        const host = getHostFromUri(candidate);
        if (!host) continue;
        if (host === 'localhost' || host === '127.0.0.1') continue;
        return `http://${host}:8000`;
    }

    if (Platform.OS === 'android') {
        return 'http://10.0.2.2:8000';
    }

    return 'http://localhost:8000';
}

const API_BASE_URL = resolveApiBaseUrl();

function createNetworkError(): Error {
    return new Error(
        `Khong the ket noi backend (${API_BASE_URL}). Neu dang dung dien thoai that, dat EXPO_PUBLIC_API_URL=http://<IP-may-ban>:8000`
    );
}

const TOKEN_STORAGE_KEY = 'smarthome.auth.tokens';

interface StoredTokens {
    accessToken: string;
    refreshToken: string;
}

interface WebStorageLike {
    getItem: (key: string) => string | null;
    setItem: (key: string, value: string) => void;
    removeItem: (key: string) => void;
}

// Token storage (in production, use SecureStore)
let accessToken: string | null = null;
let refreshToken: string | null = null;

function getWebStorage(): WebStorageLike | null {
    const storage = (globalThis as { localStorage?: WebStorageLike }).localStorage;
    if (!storage) return null;
    return storage;
}

function persistTokens(access: string, refresh: string) {
    const storage = getWebStorage();
    if (!storage) return;

    try {
        storage.setItem(
            TOKEN_STORAGE_KEY,
            JSON.stringify({ accessToken: access, refreshToken: refresh } satisfies StoredTokens)
        );
    } catch {
        // Ignore storage failures and keep in-memory tokens as fallback.
    }
}

function removePersistedTokens() {
    const storage = getWebStorage();
    if (!storage) return;
    try {
        storage.removeItem(TOKEN_STORAGE_KEY);
    } catch {
        // Ignore storage failures during cleanup.
    }
}

export async function hydrateTokensFromStorage(): Promise<boolean> {
    const storage = getWebStorage();
    if (!storage) return false;

    let raw: string | null = null;
    try {
        raw = storage.getItem(TOKEN_STORAGE_KEY);
    } catch {
        return false;
    }

    if (!raw) return false;

    try {
        const parsed = JSON.parse(raw) as Partial<StoredTokens>;
        if (typeof parsed.accessToken !== 'string' || typeof parsed.refreshToken !== 'string') {
            removePersistedTokens();
            return false;
        }

        accessToken = parsed.accessToken;
        refreshToken = parsed.refreshToken;
        return true;
    } catch {
        removePersistedTokens();
        return false;
    }
}

export function setTokens(access: string, refresh: string) {
    accessToken = access;
    refreshToken = refresh;
    persistTokens(access, refresh);
}

export function clearTokens() {
    accessToken = null;
    refreshToken = null;
    removePersistedTokens();
}

export function getAccessToken() {
    return accessToken;
}

async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken) return false;
    try {
        const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (res.ok) {
            const data = await res.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }
    } catch (e) {
        console.error('Token refresh failed:', e);
    }
    return false;
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
    };
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    let res: Response;
    try {
        res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    } catch {
        throw createNetworkError();
    }

    // Auto-refresh on 401
    if (res.status === 401 && refreshToken) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${accessToken}`;
            try {
                res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
            } catch {
                throw createNetworkError();
            }
        }
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
        // FastAPI có thể trả detail là string hoặc array (validation errors)
        let message: string;
        if (typeof error.detail === 'string') {
            message = error.detail;
        } else if (Array.isArray(error.detail)) {
            // Pydantic validation error: [{loc, msg, type}, ...]
            message = error.detail.map((e: any) => e.msg ?? JSON.stringify(e)).join(', ');
        } else {
            message = `Lỗi ${res.status}`;
        }
        throw new Error(message);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
}

// ============ AUTH ============

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface UserResponse {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
}

export const authAPI = {
    register: (email: string, full_name: string, password: string) =>
        apiFetch<UserResponse>('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, full_name, password }),
        }),

    login: (email: string, password: string) =>
        apiFetch<LoginResponse>('/auth/login-json', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        }),

    me: () => apiFetch<UserResponse>('/auth/me'),
};

// ============ HOMES ============

export interface HomeResponse {
    id: string;
    owner_id: string;
    name: string;
    address?: string;
    created_at: string;
    room_count: number;
    device_count: number;
    active_devices: number;
}

export const homesAPI = {
    list: () => apiFetch<HomeResponse[]>('/homes/'),
    get: (id: string) => apiFetch<HomeResponse>(`/homes/${id}`),
    create: (name: string, address?: string) =>
        apiFetch<HomeResponse>('/homes/', {
            method: 'POST',
            body: JSON.stringify({ name, address }),
        }),
    update: (id: string, data: { name?: string; address?: string }) =>
        apiFetch<HomeResponse>(`/homes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    delete: (id: string) => apiFetch<void>(`/homes/${id}`, { method: 'DELETE' }),
};

// ============ ROOMS ============

export interface RoomResponse {
    id: string;
    home_id: string;
    name: string;
    icon?: string;
    created_at: string;
    device_count: number;
    active_devices: number;
    is_online: boolean;
}

export const roomsAPI = {
    list: (homeId: string) => apiFetch<RoomResponse[]>(`/rooms/?home_id=${homeId}`),
    get: (id: string) => apiFetch<RoomResponse>(`/rooms/${id}`),
    create: (homeId: string, name: string, icon?: string) =>
        apiFetch<RoomResponse>('/rooms/', {
            method: 'POST',
            body: JSON.stringify({ home_id: homeId, name, icon }),
        }),
    update: (id: string, data: { name?: string; icon?: string }) =>
        apiFetch<RoomResponse>(`/rooms/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    delete: (id: string) => apiFetch<void>(`/rooms/${id}`, { method: 'DELETE' }),
};

// ============ DEVICES ============

export interface DeviceResponse {
    id: string;
    room_id: string;
    name: string;
    type: string;
    status: boolean;
    online_status: boolean;
    last_seen?: string;
    metadata?: Record<string, any>;
    created_at: string;
}

export const devicesAPI = {
    list: (roomId: string) => apiFetch<DeviceResponse[]>(`/devices/?room_id=${roomId}`),
    get: (id: string) => apiFetch<DeviceResponse>(`/devices/${id}`),
    create: (roomId: string, name: string, type: string, metadata?: Record<string, any>) =>
        apiFetch<DeviceResponse>('/devices/', {
            method: 'POST',
            body: JSON.stringify({ room_id: roomId, name, type, metadata }),
        }),
    update: (id: string, data: { room_id?: string; name?: string; type?: string; metadata?: Record<string, any> }) =>
        apiFetch<DeviceResponse>(`/devices/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    delete: (id: string) => apiFetch<void>(`/devices/${id}`, { method: 'DELETE' }),
    toggle: (id: string, status: boolean) =>
        apiFetch<DeviceResponse>(`/devices/${id}/toggle`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        }),
    command: (id: string, command: string, value?: any) =>
        apiFetch<DeviceResponse>(`/devices/${id}/command`, {
            method: 'POST',
            body: JSON.stringify({ command, value }),
        }),
};

// ============ AUTOMATIONS ============

export interface AutomationResponse {
    id: string;
    home_id: string;
    name: string;
    enabled: boolean;
    created_at: string;
    conditions: { id: string; condition_type: string; value: string }[];
    actions: { id: string; device_id?: string; action: string; value?: string }[];
}

export const automationsAPI = {
    list: (homeId: string) => apiFetch<AutomationResponse[]>(`/automations/?home_id=${homeId}`),
    get: (id: string) => apiFetch<AutomationResponse>(`/automations/${id}`),
    create: (data: {
        home_id: string;
        name: string;
        conditions: { condition_type: string; value: string }[];
        actions: { device_id?: string; action: string; value?: string }[];
    }) =>
        apiFetch<AutomationResponse>('/automations/', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    update: (id: string, data: { name?: string; enabled?: boolean }) =>
        apiFetch<AutomationResponse>(`/automations/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    delete: (id: string) => apiFetch<void>(`/automations/${id}`, { method: 'DELETE' }),
};

// ============ SECURITY ============

export interface SecurityEventResponse {
    id: string;
    home_id: string;
    event_type: string;
    severity: string;
    description: string;
    timestamp: string;
}

export interface SecuritySummaryResponse {
    risk_level: string;
    total_events: number;
    high_count: number;
    medium_count: number;
    low_count: number;
    recent_events: SecurityEventResponse[];
}

export const securityAPI = {
    summary: (homeId: string) => apiFetch<SecuritySummaryResponse>(`/security/summary?home_id=${homeId}`),
    events: (homeId: string, limit = 50) =>
        apiFetch<SecurityEventResponse[]>(`/security/events?home_id=${homeId}&limit=${limit}`),
};

// ============ SUGGESTIONS ============

export interface SuggestionResponse {
    id: number;
    user_id: string;
    action_type: 'SCHEDULE' | 'ALERT' | 'AUTOMATION';
    suggestion_text: string;
    suggestion_json?: {
        title?: string;
        description?: string;
        device_id?: string;
        schedule_payload?: Record<string, unknown>;
    };
    was_accepted?: boolean | null;
    created_at: string;
}

export interface SuggestionsListResponse {
    total: number;
    suggestions: SuggestionResponse[];
}

export const suggestionsAPI = {
    listMine: (limit = 20, offset = 0) =>
        apiFetch<SuggestionsListResponse>(`/suggestions/me?limit=${limit}&offset=${offset}`),
    accept: (suggestionId: number, wasAccepted: boolean) =>
        apiFetch<SuggestionResponse>(`/suggestions/${suggestionId}/accept`, {
            method: 'POST',
            body: JSON.stringify({
                was_accepted: wasAccepted,
                action_taken: wasAccepted ? 'ACCEPTED' : 'DISMISSED',
            }),
        }),
};

export { API_BASE_URL };
