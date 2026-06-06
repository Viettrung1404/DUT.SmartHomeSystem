/**
 * Quick action helpers for device control and configuration persistence.
 */

import { Feather } from '@expo/vector-icons';

export type QuickActionId =
    | 'lights_off'
    | 'leave_home'
    | 'arrive_home'
    | 'doors_open'
    | 'doors_close';

export interface QuickActionDefinition {
    id: QuickActionId;
    label: string;
    icon: keyof typeof Feather.glyphMap;
    configurable: boolean;
}

export const QUICK_ACTIONS: QuickActionDefinition[] = [
    { id: 'lights_off', label: 'Tắt đèn', icon: 'sunset', configurable: true },
    { id: 'leave_home', label: 'Rời nhà', icon: 'log-out', configurable: true },
    { id: 'arrive_home', label: 'Về nhà', icon: 'home', configurable: true },
    { id: 'doors_open', label: 'Mở cửa', icon: 'unlock', configurable: false },
    { id: 'doors_close', label: 'Đóng cửa', icon: 'lock', configurable: false },
];

const STORAGE_PREFIX = 'smarthome.quickActions.v1';

interface StorageLike {
    getItem: (key: string) => string | null;
    setItem: (key: string, value: string) => void;
    removeItem: (key: string) => void;
}

const memoryStore: Record<string, string> = {};

function getStorage(): StorageLike {
    const storage = (globalThis as { localStorage?: StorageLike }).localStorage;
    if (storage) return storage;
    return {
        getItem: (key) => (key in memoryStore ? memoryStore[key] : null),
        setItem: (key, value) => {
            memoryStore[key] = value;
        },
        removeItem: (key) => {
            delete memoryStore[key];
        },
    };
}

export type QuickActionConfigState = Partial<Record<QuickActionId, string[]>>;

function getStorageKey(homeId: string) {
    return `${STORAGE_PREFIX}.${homeId}`;
}

export async function loadQuickActionConfig(homeId: string): Promise<QuickActionConfigState> {
    const storage = getStorage();
    const raw = storage.getItem(getStorageKey(homeId));
    if (!raw) return {};

    try {
        const parsed = JSON.parse(raw) as QuickActionConfigState;
        return parsed ?? {};
    } catch {
        return {};
    }
}

export async function saveQuickActionConfig(
    homeId: string,
    actionId: QuickActionId,
    deviceIds: string[],
): Promise<void> {
    const storage = getStorage();
    const key = getStorageKey(homeId);
    const current = await loadQuickActionConfig(homeId);
    const next: QuickActionConfigState = {
        ...current,
        [actionId]: deviceIds,
    };
    storage.setItem(key, JSON.stringify(next));
}

export function normalizeDeviceType(type?: string | null): string {
    return type?.toLowerCase?.() ?? '';
}

export const SENSOR_TYPES = new Set([
    'temperature_humidity',
    'distance_sensor',
    'gas_sensor',
    'rain_sensor',
    'sensor',
]);

export const NO_TOGGLE_TYPES = new Set(['door', 'rain_servo']);

export function isSensorDevice(type: string): boolean {
    return SENSOR_TYPES.has(type);
}

export function isDoorDevice(type: string): boolean {
    return type === 'door' || type === 'lock';
}

export function isLightDevice(type: string): boolean {
    return type === 'light' || type === 'distance_light';
}

export function isToggleableDevice(type: string): boolean {
    return !isSensorDevice(type) && !NO_TOGGLE_TYPES.has(type);
}
