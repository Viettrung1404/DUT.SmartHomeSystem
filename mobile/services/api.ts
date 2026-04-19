/**
 * API service — connects React Native to FastAPI backend.
 * Handles auth tokens, request/response, and error handling.
 */

const API_BASE_URL = __DEV__
    ? 'http://192.168.1.100:8000'  // Local dev — change to your machine's IP
    : 'https://api.smarthome.vn';

// Token storage (in production, use SecureStore)
let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(access: string, refresh: string) {
    accessToken = access;
    refreshToken = refresh;
}

export function clearTokens() {
    accessToken = null;
    refreshToken = null;
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
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
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

    let res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

    // Auto-refresh on 401
    if (res.status === 401 && refreshToken) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${accessToken}`;
            res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
        }
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `API Error ${res.status}`);
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
        apiFetch<LoginResponse>('/auth/login', {
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
    energy_today: number;
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

// ============ ENERGY ============

export interface EnergyDataPoint {
    label: string;
    value: number;
}

export interface EnergySummaryResponse {
    total: number;
    data: EnergyDataPoint[];
    breakdown: { device_name: string; device_type: string; usage: number; percentage: number }[];
    comparison?: number;
}

export const energyAPI = {
    daily: (homeId: string) => apiFetch<EnergySummaryResponse>(`/energy/daily?home_id=${homeId}`),
    weekly: (homeId: string) => apiFetch<EnergySummaryResponse>(`/energy/weekly?home_id=${homeId}`),
    monthly: (homeId: string) => apiFetch<EnergySummaryResponse>(`/energy/monthly?home_id=${homeId}`),
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

export { API_BASE_URL };
