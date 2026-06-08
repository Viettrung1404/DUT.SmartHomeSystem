import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';
import { useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { DeviceCard, DeviceCardModel } from '@/components/DeviceCard';
import { Card } from '@/components/ui/Card';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { devicesAPI, roomsAPI } from '@/services/api';
import { useWebSocket } from '@/hooks/use-websocket';
import { Feather } from '@expo/vector-icons';

function getDeviceIcon(type: string): keyof typeof Feather.glyphMap {
    const iconMap: Record<string, keyof typeof Feather.glyphMap> = {
        light: 'sun',
        fan: 'wind',
        door: 'unlock',
        lock: 'lock',
        curtain: 'columns',
        buzzer: 'bell',
        distance_light: 'activity',
        temperature_humidity: 'thermometer',
        distance_sensor: 'radio',
        gas_sensor: 'alert-triangle',
        rain_sensor: 'cloud-rain',
        rain_servo: 'droplet',
    };
    return iconMap[type] ?? 'circle';
}

function mapMetadataToDeviceFields(metadata: Record<string, any> | undefined): Partial<DeviceCardModel> {
    const angle =
        typeof metadata?.angle === 'number'
            ? metadata.angle
            : typeof metadata?.angle === 'string'
                ? Number(metadata.angle)
                : undefined;

    return {
        brightness: typeof metadata?.brightness === 'number' ? metadata.brightness : undefined,
        temperature: typeof metadata?.temperature === 'number' ? metadata.temperature : undefined,
        humidity: typeof metadata?.humidity === 'number' ? metadata.humidity : undefined,
        battery: typeof metadata?.battery === 'number' ? metadata.battery : undefined,
        speed: typeof metadata?.speed === 'string' ? metadata.speed : undefined,
        door: typeof metadata?.door === 'string' ? metadata.door : undefined,
        distanceCm: typeof metadata?.distance_cm === 'number' ? metadata.distance_cm : undefined,
        distanceAlert:
            typeof metadata?.distance_alert === 'boolean' ? metadata.distance_alert : undefined,
        gasDetected:
            typeof metadata?.gas_detected === 'boolean' ? metadata.gas_detected : undefined,
        rainDetected:
            typeof metadata?.rain_detected === 'boolean' ? metadata.rain_detected : undefined,
        rainAngle: Number.isFinite(angle) ? angle : undefined,
        distanceLight:
            typeof metadata?.distance_light === 'string' ? metadata.distance_light : undefined,
        buzzer: typeof metadata?.buzzer === 'string' ? metadata.buzzer : undefined,
    };
}

export default function RoomDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const router = useRouter();
    const [room, setRoom] = useState<{
        id: string;
        name: string;
    } | null>(null);
    const [homeId, setHomeId] = useState<string | null>(null);
    const [devices, setDevices] = useState<DeviceCardModel[]>([]);
    const [loading, setLoading] = useState(true);
    const { subscribe } = useWebSocket(homeId);

    useEffect(() => {
        if (!homeId) return;
        const unsubscribe = subscribe('device_update', (message) => {
            if (!message.device_id) return;
            setDevices((prev) =>
                prev.map((device) => {
                    if (device.id !== message.device_id) return device;
                    const data = message.data ?? {};
                    const metadata = data.metadata as Record<string, any> | undefined;
                    return {
                        ...device,
                        isOn: typeof data.status === 'boolean' ? data.status : device.isOn,
                        isOnline: typeof data.online === 'boolean' ? data.online : device.isOnline,
                        ...mapMetadataToDeviceFields(metadata),
                    };
                }),
            );
        });
        return unsubscribe;
    }, [homeId, subscribe]);

    const loadRoomData = useCallback(async (roomId: string) => {
        try {
            setLoading(true);
            const roomResponse = await roomsAPI.get(roomId);
            setRoom({
                id: roomResponse.id,
                name: roomResponse.name,
            });
            setHomeId(roomResponse.home_id);

            const deviceResponses = await devicesAPI.list(roomId);
            setDevices(
                deviceResponses.map((device) => {
                    const normalizedType = device.type?.toLowerCase?.() ?? device.type;
                    return {
                        id: device.id,
                        name: device.name,
                        type: normalizedType,
                        icon: getDeviceIcon(normalizedType),
                        isOnline: device.online_status,
                        isOn: device.status,
                        ...mapMetadataToDeviceFields(device.metadata),
                    };
                }),
            );
        } catch (error) {
            console.error('Failed to load room detail:', error);
            setRoom(null);
            setDevices([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            if (!id) return;
            void loadRoomData(id);
        }, [id, loadRoomData]),
    );

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
            <Header
                title={room.name}
                showBack
                subtitle={`${devices.length} thiết bị`}
                rightIcon="settings"
                onRightPress={() => router.push({ pathname: '/room/[id]/manage', params: { id: room.id } } as never)}
            />

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
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Trực tuyến</Text>
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
