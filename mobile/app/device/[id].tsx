import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Toggle } from '@/components/ui/Toggle';
import { Slider } from '@/components/ui/Slider';
import { Badge } from '@/components/ui/Badge';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { devicesAPI, roomsAPI, DeviceResponse } from '@/services/api';
import { useWebSocket } from '@/hooks/use-websocket';

interface DeviceViewModel {
    id: string;
    name: string;
    type: string;
    icon?: string;
    isOnline: boolean;
    isOn: boolean;
    temperature?: number;
    humidity?: number;
    speed?: string;
    door?: string;
    distanceCm?: number;
    distanceAlert?: boolean;
    gasDetected?: boolean;
    rainDetected?: boolean;
    distanceLight?: string;
    buzzer?: string;
    rainAngle?: number;
}

function getDeviceIcon(type: string): keyof typeof Feather.glyphMap {
    const iconMap: Record<string, keyof typeof Feather.glyphMap> = {
        light: 'sun',
        fan: 'wind',
        door: 'door-open',
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

function mapMetadataToDeviceFields(metadata: Record<string, any> | undefined): Partial<DeviceViewModel> {
    return {
        temperature: typeof metadata?.temperature === 'number' ? metadata.temperature : undefined,
        humidity: typeof metadata?.humidity === 'number' ? metadata.humidity : undefined,
        speed: typeof metadata?.speed === 'string' ? metadata.speed : undefined,
        door: typeof metadata?.door === 'string' ? metadata.door : undefined,
        distanceCm: typeof metadata?.distance_cm === 'number' ? metadata.distance_cm : undefined,
        distanceAlert: typeof metadata?.distance_alert === 'boolean'
            ? metadata.distance_alert
            : undefined,
        gasDetected: typeof metadata?.gas_detected === 'boolean' ? metadata.gas_detected : undefined,
        rainDetected: typeof metadata?.rain_detected === 'boolean' ? metadata.rain_detected : undefined,
        distanceLight: typeof metadata?.distance_light === 'string'
            ? metadata.distance_light
            : undefined,
        buzzer: typeof metadata?.buzzer === 'string' ? metadata.buzzer : undefined,
        rainAngle: typeof metadata?.angle === 'number' ? metadata.angle : undefined,
    };
}

const readOnlyTypes = new Set([
    'temperature_humidity',
    'distance_sensor',
    'gas_sensor',
    'rain_sensor',
    'sensor',
]);

const noToggleTypes = new Set(['door', 'rain_servo']);

function mapDevice(response: DeviceResponse): DeviceViewModel {
    const normalizedType = response.type?.toLowerCase?.() ?? response.type;
    return {
        id: response.id,
        name: response.name,
        type: normalizedType,
        icon: getDeviceIcon(normalizedType),
        isOnline: response.online_status,
        isOn: response.status,
        ...mapMetadataToDeviceFields(response.metadata),
    };
}

export default function DeviceDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const [device, setDevice] = useState<DeviceViewModel | undefined>(undefined);
    const [homeId, setHomeId] = useState<string | null>(null);
    const { subscribe } = useWebSocket(homeId);

    useEffect(() => {
        if (!id) return;
        loadDevice(id);
    }, [id]);

    useEffect(() => {
        if (!homeId || !device?.id) return;
        const deviceId = device.id;
        const unsubscribe = subscribe('device_update', (message) => {
            if (message.device_id !== deviceId) return;
            setDevice((prev) => {
                if (!prev) return prev;
                const data = message.data ?? {};
                const metadata = data.metadata as Record<string, any> | undefined;
                return {
                    ...prev,
                    isOn: typeof data.status === 'boolean' ? data.status : prev.isOn,
                    isOnline: typeof data.online === 'boolean' ? data.online : prev.isOnline,
                    ...mapMetadataToDeviceFields(metadata),
                };
            });
        });
        return unsubscribe;
    }, [homeId, device?.id, subscribe]);

    const loadDevice = async (deviceId: string) => {
        try {
            const response = await devicesAPI.get(deviceId);
            setDevice(mapDevice(response));
            try {
                const roomResponse = await roomsAPI.get(response.room_id);
                setHomeId(roomResponse.home_id);
            } catch (roomError) {
                console.warn('Failed to load room for WS:', roomError);
            }
        } catch (error) {
            console.error('Failed to load device:', error);
            setDevice(undefined);
        }
    };

    if (!device) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={[Typography.body, { color: colors.textSecondary }]}>Không tìm thấy thiết bị</Text>
            </SafeAreaView>
        );
    }

    const updateDevice = (updates: Partial<DeviceViewModel>) => {
        setDevice((prev) => prev ? { ...prev, ...updates } : prev);
    };

    const isReadOnly = readOnlyTypes.has(device.type);
    const isToggleAllowed = !isReadOnly && !noToggleTypes.has(device.type);

    const toggleDevice = async (value: boolean) => {
        if (!device) return;
        updateDevice({ isOn: value });
        try {
            await devicesAPI.toggle(device.id, value);
        } catch (error) {
            console.error('Failed to toggle device:', error);
            updateDevice({ isOn: !value });
        }
    };


    const sendCommand = async (command: string, value?: unknown) => {
        if (!device) return;
        try {
            const updated = await devicesAPI.command(device.id, command, value);
            setDevice(mapDevice(updated));
        } catch (error) {
            console.error(`Failed to send command ${command}:`, error);
        }
    };

    const iconName = (device.icon || 'circle') as keyof typeof Feather.glyphMap;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title={device.name} showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {/* Status Card */}
                <Card style={{ alignItems: 'center', paddingVertical: Spacing.xl, marginBottom: Spacing.md }}>
                    <View
                        style={{
                            width: 80, height: 80, borderRadius: 24,
                            backgroundColor: device.isOn ? colors.primaryLight : colors.surface,
                            alignItems: 'center', justifyContent: 'center', marginBottom: Spacing.md,
                            borderWidth: 2, borderColor: device.isOn ? colors.primary + '40' : colors.border,
                        }}
                    >
                        <Feather name={iconName} size={36} color={device.isOn ? colors.primary : colors.iconMuted} />
                    </View>
                    <Badge variant={device.isOnline ? 'online' : 'offline'} label={device.isOnline ? 'Trực tuyến' : 'Ngoại tuyến'} size="md" />
                    <View style={{ marginTop: Spacing.lg, flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                        <Text style={[Typography.bodyMedium, { color: colors.textSecondary }]}>
                            {device.isOn ? 'Đang bật' : 'Đã tắt'}
                        </Text>
                        {isToggleAllowed && (
                            <Toggle
                                value={device.isOn}
                                onToggle={toggleDevice}
                                disabled={!device.isOnline}
                            />
                        )}
                    </View>
                    {isReadOnly && (
                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.sm }]}>
                            Thiết bị chỉ đọc
                        </Text>
                    )}
                </Card>


                {/* Fan Controls */}
                {device.type === 'fan' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Toc do quat</Text>
                        <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                            {[
                                { label: 'Tat', value: 'off' },
                                { label: 'Yeu', value: 'weak' },
                                { label: 'Manh', value: 'strong' },
                            ].map((option) => (
                                <Pressable
                                    key={option.value}
                                    onPress={() => {
                                        updateDevice({ speed: option.value, isOn: option.value !== 'off' });
                                        sendCommand('set_speed', option.value);
                                    }}
                                    disabled={!device.isOnline}
                                    style={{
                                        flex: 1,
                                        paddingVertical: Spacing.md,
                                        borderRadius: BorderRadius.md,
                                        backgroundColor: device.speed === option.value ? colors.primary : colors.surface,
                                        alignItems: 'center',
                                        borderWidth: 1,
                                        borderColor: device.speed === option.value ? colors.primary : colors.border,
                                        opacity: device.isOnline ? 1 : 0.6,
                                    }}
                                >
                                    <Feather name="wind" size={20} color={device.speed === option.value ? '#FFFFFF' : colors.icon} />
                                    <Text
                                        style={[
                                            Typography.captionMedium,
                                            {
                                                color: device.speed === option.value ? '#FFFFFF' : colors.textSecondary,
                                                marginTop: Spacing.xs,
                                            },
                                        ]}
                                    >
                                        {option.label}
                                    </Text>
                                </Pressable>
                            ))}
                        </View>
                    </Card>
                )}

                {/* Door Controls */}
                {device.type === 'door' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Cua</Text>
                        <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                            {[
                                { label: 'Mo', value: 'open' },
                                { label: 'Dong', value: 'close' },
                            ].map((option) => (
                                <Pressable
                                    key={option.value}
                                    onPress={() => sendCommand(option.value)}
                                    disabled={!device.isOnline}
                                    style={{
                                        flex: 1,
                                        paddingVertical: Spacing.md,
                                        borderRadius: BorderRadius.md,
                                        backgroundColor: colors.surface,
                                        alignItems: 'center',
                                        borderWidth: 1,
                                        borderColor: colors.border,
                                        opacity: device.isOnline ? 1 : 0.6,
                                    }}
                                >
                                    <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}> {option.label} </Text>
                                </Pressable>
                            ))}
                        </View>
                    </Card>
                )}

                {/* Buzzer Controls */}
                {device.type === 'buzzer' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Coi</Text>
                        <Toggle
                            value={device.isOn}
                            onToggle={(value) => {
                                updateDevice({ isOn: value });
                                sendCommand(value ? 'on' : 'off');
                            }}
                            disabled={!device.isOnline}
                        />
                    </Card>
                )}

                {/* Distance Light Controls */}
                {device.type === 'distance_light' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Den khoang cach</Text>
                        <Toggle
                            value={device.isOn}
                            onToggle={(value) => {
                                updateDevice({ isOn: value });
                                sendCommand(value ? 'on' : 'off');
                            }}
                            disabled={!device.isOnline}
                        />
                    </Card>
                )}

                {/* Rain Servo Controls */}
                {device.type === 'rain_servo' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Che mua</Text>
                        <View style={{ flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md }}>
                            {[
                                { label: 'Mua', value: 'wet' },
                                { label: 'Kho', value: 'dry' },
                            ].map((option) => (
                                <Pressable
                                    key={option.value}
                                    onPress={() => sendCommand('set_position', option.value)}
                                    disabled={!device.isOnline}
                                    style={{
                                        flex: 1,
                                        paddingVertical: Spacing.md,
                                        borderRadius: BorderRadius.md,
                                        backgroundColor: colors.surface,
                                        alignItems: 'center',
                                        borderWidth: 1,
                                        borderColor: colors.border,
                                        opacity: device.isOnline ? 1 : 0.6,
                                    }}
                                >
                                    <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}> {option.label} </Text>
                                </Pressable>
                            ))}
                        </View>
                        <Slider
                            value={device.rainAngle ?? 0}
                            onValueChange={(val) => {
                                updateDevice({ rainAngle: val });
                                sendCommand('set_angle', val);
                            }}
                            label="Goc"
                            unit="do"
                            min={0}
                            max={180}
                            step={1}
                            disabled={!device.isOnline}
                        />
                    </Card>
                )}

                {/* Sensor Cards */}
                {device.type === 'temperature_humidity' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Nhiet do / Do am</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Nhiet do: {device.temperature ?? '--'}°C</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>Do am: {device.humidity ?? '--'}%</Text>
                    </Card>
                )}

                {device.type === 'distance_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Sieu am</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Khoang cach: {device.distanceCm ?? '--'}cm</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Canh bao: {device.distanceAlert ? 'Co' : 'Khong'}
                        </Text>
                    </Card>
                )}

                {device.type === 'gas_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Gas</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Phat hien: {device.gasDetected ? 'Co' : 'Khong'}</Text>
                    </Card>
                )}

                {device.type === 'rain_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Mua</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Phat hien: {device.rainDetected ? 'Co' : 'Khong'}</Text>
                    </Card>
                )}
                {/* Device Info */}
                <Card>
                    <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Thong tin thiet bi</Text>
                    {[
                        {
                            label: 'Loai',
                            value:
                                device.type === 'light' ? 'Den'
                                    : device.type === 'fan' ? 'Quat'
                                        : device.type === 'door' ? 'Cua'
                                            : device.type === 'buzzer' ? 'Coi'
                                                : device.type === 'distance_light' ? 'Den khoang cach'
                                                    : device.type === 'temperature_humidity' ? 'Nhiet do / Do am'
                                                        : device.type === 'distance_sensor' ? 'Sieu am'
                                                            : device.type === 'gas_sensor' ? 'Gas'
                                                                : device.type === 'rain_sensor' ? 'Mua'
                                                                    : device.type === 'rain_servo' ? 'Che mua'
                                                                        : 'Khac',
                        },
                        { label: 'Trang thai', value: device.isOnline ? 'Truc tuyen' : 'Ngoai tuyen' },
                        { label: 'ID', value: device.id },
                    ].map((info, i) => (
                        <View
                            key={i}
                            style={{
                                flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
                                paddingVertical: Spacing.sm,
                                borderTopWidth: i > 0 ? 1 : 0,
                                borderTopColor: colors.border,
                            }}
                        >
                            <Text style={[Typography.bodySmall, { color: colors.textSecondary }]}>{info.label}</Text>
                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{info.value}</Text>
                        </View>
                    ))}
                </Card>

                <View style={{ height: Spacing.xl }} />
            </ScrollView>
        </SafeAreaView >
    );
}
