import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import { Header } from '@/components/ui/Header';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { useTheme } from '@/contexts/ThemeContext';
import { devicesAPI, homesAPI, roomsAPI, DeviceResponse } from '@/services/api';
import {
    QuickActionId,
    loadQuickActionConfig,
    saveQuickActionConfig,
    normalizeDeviceType,
    isLightDevice,
    isToggleableDevice,
} from '@/services/quickActions';

const ACTION_META: Record<QuickActionId, { title: string; description: string; filter: 'lights' | 'toggleable' }> = {
    lights_off: {
        title: 'Tắt đèn',
        description: 'Chọn đèn sẽ tắt (không gồm cảm biến).',
        filter: 'lights',
    },
    leave_home: {
        title: 'Rời nhà',
        description: 'Chọn thiết bị sẽ tắt (không gồm cảm biến).',
        filter: 'toggleable',
    },
    arrive_home: {
        title: 'Về nhà',
        description: 'Chọn thiết bị sẽ bật (không gồm cảm biến).',
        filter: 'toggleable',
    },
    doors_open: {
        title: 'Mở cửa',
        description: 'Thao tác cửa không cần cấu hình.',
        filter: 'toggleable',
    },
    doors_close: {
        title: 'Đóng cửa',
        description: 'Thao tác cửa không cần cấu hình.',
        filter: 'toggleable',
    },
};

interface DeviceItem {
    id: string;
    name: string;
    type: string;
    roomName?: string;
    isOnline: boolean;
}

export default function QuickActionConfigScreen() {
    const { action } = useLocalSearchParams<{ action?: string }>();
    const router = useRouter();
    const { colors } = useTheme();
    const actionId = action as QuickActionId | undefined;
    const meta = actionId ? ACTION_META[actionId] : undefined;

    const [homeId, setHomeId] = useState<string | null>(null);
    const [devices, setDevices] = useState<DeviceItem[]>([]);
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const configurable = actionId === 'lights_off' || actionId === 'leave_home' || actionId === 'arrive_home';

    useEffect(() => {
        if (!actionId || !meta || !configurable) return;
        loadData(actionId, meta.filter);
    }, [actionId, meta?.filter, configurable]);

    const loadData = async (id: QuickActionId, filter: 'lights' | 'toggleable') => {
        try {
            setLoading(true);
            const homes = await homesAPI.list();
            if (!homes.length) {
                setHomeId(null);
                setDevices([]);
                setSelectedIds(new Set());
                return;
            }

            const primaryHome = homes[0];
            setHomeId(primaryHome.id);

            const rooms = await roomsAPI.list(primaryHome.id);
            const roomNames = new Map(rooms.map((room) => [room.id, room.name]));
            const deviceGroups = await Promise.all(rooms.map((room) => devicesAPI.list(room.id)));
            const allDevices = deviceGroups.flat();

            const filtered = filterDevices(allDevices, filter).map((device) => ({
                id: device.id,
                name: device.name,
                type: normalizeDeviceType(device.type),
                roomName: roomNames.get(device.room_id),
                isOnline: device.online_status,
            }));

            const config = await loadQuickActionConfig(primaryHome.id);
            const configuredIds = config[id];
            const defaultIds = filtered.map((device) => device.id);
            const initialIds = new Set(
                (configuredIds?.length ? configuredIds : defaultIds).filter((deviceId) =>
                    filtered.some((device) => device.id === deviceId),
                ),
            );

            setDevices(filtered);
            setSelectedIds(initialIds);
        } finally {
            setLoading(false);
        }
    };

    const filterDevices = (list: DeviceResponse[], filter: 'lights' | 'toggleable') => {
        return list.filter((device) => {
            const type = normalizeDeviceType(device.type);
            if (filter === 'lights') return isLightDevice(type);
            return isToggleableDevice(type);
        });
    };

    const toggleDevice = (id: string) => {
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    };

    const selectAll = () => {
        setSelectedIds(new Set(devices.map((device) => device.id)));
    };

    const clearAll = () => {
        setSelectedIds(new Set());
    };

    const handleSave = async () => {
        if (!homeId || !actionId) return;
        setSaving(true);
        try {
            await saveQuickActionConfig(homeId, actionId, Array.from(selectedIds));
            router.back();
        } finally {
            setSaving(false);
        }
    };

    const deviceList = useMemo(() => devices, [devices]);

    if (!actionId || !meta) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
                <Header title="Cấu hình nhanh" showBack />
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <Text style={[Typography.body, { color: colors.textSecondary }]}>Không tìm thấy thao tác.</Text>
                </View>
            </SafeAreaView>
        );
    }

    if (!configurable) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
                <Header title={meta.title} showBack />
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: Spacing.lg }}>
                    <Text style={[Typography.body, { color: colors.textSecondary, textAlign: 'center' }]}>Thao tác này không cần cấu hình.</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title={meta.title} showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md, paddingBottom: Spacing.xl }}>
                <Text style={[Typography.bodySmall, { color: colors.textSecondary, marginBottom: Spacing.md }]}>
                    {meta.description}
                </Text>

                <View style={{ flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md }}>
                    <Button title="Chọn tất cả" onPress={selectAll} size="sm" variant="ghost" />
                    <Button title="Bỏ chọn" onPress={clearAll} size="sm" variant="ghost" />
                </View>

                {loading ? (
                    <View style={{ paddingVertical: Spacing.lg, alignItems: 'center' }}>
                        <ActivityIndicator size="large" color={colors.primary} />
                    </View>
                ) : deviceList.length === 0 ? (
                    <Card>
                        <Text style={[Typography.bodySmall, { color: colors.textSecondary }]}>Không có thiết bị phù hợp.</Text>
                    </Card>
                ) : (
                    <View style={{ gap: Spacing.sm }}>
                        {deviceList.map((device) => {
                            const selected = selectedIds.has(device.id);
                            return (
                                <Pressable
                                    key={device.id}
                                    onPress={() => toggleDevice(device.id)}
                                    style={{
                                        padding: Spacing.md,
                                        borderRadius: 14,
                                        borderWidth: 1,
                                        borderColor: selected ? colors.primary : colors.border,
                                        backgroundColor: selected ? colors.primaryLight : colors.card,
                                    }}
                                >
                                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <View style={{ flex: 1 }}>
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{device.name}</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>Phòng: {device.roomName || 'Khác'}</Text>
                                        </View>
                                        <Feather
                                            name={selected ? 'check-circle' : 'circle'}
                                            size={20}
                                            color={selected ? colors.primary : colors.iconMuted}
                                        />
                                    </View>
                                </Pressable>
                            );
                        })}
                    </View>
                )}
            </ScrollView>

            <View style={{ padding: Spacing.md, borderTopWidth: 1, borderTopColor: colors.border }}>
                <Button title="Lưu cấu hình" onPress={handleSave} loading={saving} disabled={loading} />
            </View>
        </SafeAreaView>
    );
}
