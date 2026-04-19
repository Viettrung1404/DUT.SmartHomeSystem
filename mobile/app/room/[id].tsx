import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { DeviceCard, DeviceCardModel } from '@/components/DeviceCard';
import { Card } from '@/components/ui/Card';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { devicesAPI, roomsAPI } from '@/services/api';

export default function RoomDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const router = useRouter();
    const [room, setRoom] = useState<{
        id: string;
        name: string;
        energyToday: number;
    } | null>(null);
    const [devices, setDevices] = useState<DeviceCardModel[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        loadRoomData(id);
    }, [id]);

    const loadRoomData = async (roomId: string) => {
        try {
            setLoading(true);
            const roomResponse = await roomsAPI.get(roomId);
            setRoom({
                id: roomResponse.id,
                name: roomResponse.name,
                energyToday: roomResponse.energy_today,
            });

            const deviceResponses = await devicesAPI.list(roomId);
            setDevices(
                deviceResponses.map((device) => ({
                    id: device.id,
                    name: device.name,
                    type: device.type,
                    icon: device.type,
                    isOnline: device.online_status,
                    isOn: device.status,
                    brightness: typeof device.metadata?.brightness === 'number' ? device.metadata.brightness : undefined,
                    temperature: typeof device.metadata?.temperature === 'number' ? device.metadata.temperature : undefined,
                    humidity: typeof device.metadata?.humidity === 'number' ? device.metadata.humidity : undefined,
                    battery: typeof device.metadata?.battery === 'number' ? device.metadata.battery : undefined,
                })),
            );
        } catch (error) {
            console.error('Failed to load room detail:', error);
            setRoom(null);
            setDevices([]);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
                <ActivityIndicator size="large" color={colors.primary} />
            </SafeAreaView>
        );
    }

    if (!room) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={[Typography.body, { color: colors.textSecondary }]}>Không tìm thấy phòng</Text>
            </SafeAreaView>
        );
    }

    const handleToggle = async (deviceId: string, value: boolean) => {
        setDevices((prev) =>
            prev.map((d) => (d.id === deviceId ? { ...d, isOn: value } : d)),
        );

        try {
            await devicesAPI.toggle(deviceId, value);
        } catch (error) {
            console.error('Failed to toggle device:', error);
            setDevices((prev) =>
                prev.map((d) => (d.id === deviceId ? { ...d, isOn: !value } : d)),
            );
        }
    };

    const handleDevicePress = (device: DeviceCardModel) => {
        router.push({ pathname: '/device/[id]', params: { id: device.id } });
    };

    const onlineCount = devices.filter((d) => d.isOnline).length;
    const activeCount = devices.filter((d) => d.isOn).length;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title={room.name} showBack subtitle={`${devices.length} thiết bị`} />

            {/* Room Stats */}
            <View style={{ flexDirection: 'row', gap: Spacing.sm, paddingHorizontal: Spacing.md, marginBottom: Spacing.md }}>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.primary }]}>{activeCount}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Đang bật</Text>
                    </View>
                </Card>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.success }]}>{onlineCount}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Online</Text>
                    </View>
                </Card>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.warning }]}>{room.energyToday}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
                    </View>
                </Card>
            </View>

            {/* Devices Grid */}
            <FlatList
                data={devices}
                keyExtractor={(item) => item.id}
                numColumns={2}
                contentContainerStyle={{ paddingHorizontal: Spacing.md, gap: Spacing.sm }}
                columnWrapperStyle={{ gap: Spacing.sm }}
                renderItem={({ item }) => (
                    <View style={{ flex: 1 }}>
                        <DeviceCard device={item} onToggle={handleToggle} onPress={handleDevicePress} />
                    </View>
                )}
                showsVerticalScrollIndicator={false}
            />
        </SafeAreaView>
    );
}
