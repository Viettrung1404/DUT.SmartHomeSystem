import { Feather } from '@expo/vector-icons';

const LEGACY_ROOM_ICON_MAP: Record<string, keyof typeof Feather.glyphMap> = {
    living_room: 'tv',
    living: 'tv',
    bedroom: 'moon',
    bed: 'moon',
    kitchen: 'coffee',
    dining: 'coffee',
    bathroom: 'droplet',
    office: 'briefcase',
    kids: 'smile',
    child: 'smile',
    garden: 'sun',
    balcony: 'wind',
    garage: 'truck',
    storage: 'archive',
    other: 'grid',
};

const ROOM_ICON_RULES: Array<{ match: RegExp; icon: keyof typeof Feather.glyphMap }> = [
    { match: /khach|living/, icon: 'tv' },
    { match: /ngu|bed/, icon: 'moon' },
    { match: /bep|kitchen|dining/, icon: 'coffee' },
    { match: /tam|bath/, icon: 'droplet' },
    { match: /ban cong|balcony/, icon: 'wind' },
    { match: /gara|garage/, icon: 'truck' },
    { match: /lam viec|office/, icon: 'briefcase' },
    { match: /tre|kids|child/, icon: 'smile' },
    { match: /kho|storage/, icon: 'archive' },
    { match: /vuon|garden/, icon: 'sun' },
];

function normalizeRoomName(name: string) {
    return name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

export function resolveRoomIcon(name: string, icon?: string | null): keyof typeof Feather.glyphMap {
    const normalizedIcon = icon?.toLowerCase?.().trim();
    if (normalizedIcon) {
        if (normalizedIcon in Feather.glyphMap) {
            return normalizedIcon as keyof typeof Feather.glyphMap;
        }
        if (normalizedIcon in LEGACY_ROOM_ICON_MAP) {
            return LEGACY_ROOM_ICON_MAP[normalizedIcon];
        }
    }

    const normalizedName = normalizeRoomName(name);
    const rule = ROOM_ICON_RULES.find((item) => item.match.test(normalizedName));
    return rule?.icon ?? 'home';
}

export function findRoomPresetKey(iconOrValue?: string | null): string | null {
    const normalized = iconOrValue?.toLowerCase?.().trim();
    if (!normalized) return null;
    if (normalized in LEGACY_ROOM_ICON_MAP) {
        return normalized;
    }
    return null;
}
