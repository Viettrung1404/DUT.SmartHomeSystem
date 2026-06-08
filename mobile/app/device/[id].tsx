import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
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

function mapMetadataToDeviceFields(metadata: Record<string, any> | undefined): Partial<DeviceViewModel> {
    const angle =
        typeof metadata?.angle === 'number'
            ? metadata.angle
            : typeof metadata?.angle === 'string'
                ? Number(metadata.angle)
                : undefined;

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
        rainAngle: Number.isFinite(angle) ? angle : undefined,
    };
}

const readOnlyTypes = new Set([
    'temperature_humidity',
    'distance_sensor',
    'gas_sensor',
    'rain_sensor',
    'sensor',
]);

const noToggleTypes = new Set(['door', 'lock', 'curtain', 'rain_servo']);

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

function clampOpenPercent(percent: number): number {
    return Math.max(0, Math.min(100, Math.round(percent)));
}

function angleToOpenPercent(angle?: number): number {
    const normalizedAngle = Math.max(0, Math.min(180, Math.round(angle ?? 0)));
    return clampOpenPercent((normalizedAngle / 180) * 100);
}

function openPercentToAngle(percent: number): number {
    const normalizedPercent = clampOpenPercent(percent);
    return Math.round((normalizedPercent / 100) * 180);
}

export default function DeviceDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const [device, setDevice] = useState<DeviceViewModel | undefined>(undefined);
    const [homeId, setHomeId] = useState<string | null>(null);
    const [rainServoOpenPercentDraft, setRainServoOpenPercentDraft] = useState(0);
    const [isSendingRainAngle, setIsSendingRainAngle] = useState(false);
    const { subscribe } = useWebSocket(homeId);

    useEffect(() => {
        if (!id) return;
        loadDevice(id);
    }, [id]);

    useEffect(() => {
        if (device?.type !== 'rain_servo') return;
        setRainServoOpenPercentDraft(angleToOpenPercent(device.rainAngle));
    }, [device?.type, device?.rainAngle]);

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

    const applyRainServoOpenPercent = async (nextPercent: number) => {
        if (!device) return;
        const clampedPercent = clampOpenPercent(nextPercent);
        const nextAngle = openPercentToAngle(clampedPercent);
        setRainServoOpenPercentDraft(clampedPercent);
        setIsSendingRainAngle(true);
        updateDevice({ rainAngle: nextAngle });
        try {
            const updated = await devicesAPI.command(device.id, 'set_angle', nextAngle);
            setDevice(mapDevice(updated));
        } catch (error) {
            console.error('Failed to set rain servo angle:', error);
            updateDevice({ rainAngle: device.rainAngle });
            setRainServoOpenPercentDraft(angleToOpenPercent(device.rainAngle));
        } finally {
            setIsSendingRainAngle(false);
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
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Tốc độ quạt</Text>
                        <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                            {[
                                { label: 'Tắt', value: 'off' },
                                { label: 'Yếu', value: 'weak' },
                                { label: 'Mạnh', value: 'strong' },
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
                {(device.type === 'door' || device.type === 'lock' || device.type === 'curtain') && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>
                            {device.type === 'curtain' ? 'Rèm' : 'Cửa / Khóa'}
                        </Text>
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
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Còi</Text>
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
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Đèn khoảng cách</Text>
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
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Mái che mưa</Text>
                        <View style={{ flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md }}>
                            {[
                                { label: 'Đóng hết', percent: 0 },
                                { label: 'Mở 50%', percent: 50 },
                                { label: 'Mở hết', percent: 100 },
                            ].map((option) => (
                                <Pressable
                                    key={option.label}
                                    onPress={() => void applyRainServoOpenPercent(option.percent)}
                                    disabled={!device.isOnline}
                                    style={{
                                        flex: option.percent === 50 ? 1.2 : 1,
                                        paddingVertical: Spacing.md,
                                        borderRadius: BorderRadius.md,
                                        backgroundColor: colors.surface,
                                        alignItems: 'center',
                                        borderWidth: 1,
                                        borderColor: colors.border,
                                        opacity: device.isOnline ? 1 : 0.6,
                                    }}
                                >
                                    <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}>{option.label}</Text>
                                </Pressable>
                            ))}
                        </View>
                        <View
                            style={{
                                backgroundColor: colors.surface,
                                borderRadius: BorderRadius.md,
                                borderWidth: 1,
                                borderColor: colors.border,
                                padding: Spacing.md,
                                marginBottom: Spacing.md,
                            }}
                        >
                            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.sm }}>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>Độ mở hiện tại</Text>
                                <Text style={[Typography.h3, { color: colors.primary }]}>{rainServoOpenPercentDraft}%</Text>
                            </View>
                            <Slider
                                value={rainServoOpenPercentDraft}
                                onValueChange={setRainServoOpenPercentDraft}
                                label="Điều chỉnh độ mở"
                                unit="%"
                                min={0}
                                max={100}
                                step={1}
                                disabled={!device.isOnline || isSendingRainAngle}
                            />
                            <View style={{ flexDirection: 'row', gap: Spacing.sm, marginTop: Spacing.md }}>
                                {[
                                    { label: '-10%', value: Math.max(0, rainServoOpenPercentDraft - 10) },
                                    { label: '50%', value: 50 },
                                    { label: '+10%', value: Math.min(100, rainServoOpenPercentDraft + 10) },
                                ].map((option) => (
                                    <Pressable
                                        key={option.label}
                                        onPress={() => setRainServoOpenPercentDraft(option.value)}
                                        disabled={!device.isOnline || isSendingRainAngle}
                                        style={{
                                            flex: 1,
                                            paddingVertical: Spacing.sm,
                                            borderRadius: BorderRadius.md,
                                            backgroundColor: colors.background,
                                            alignItems: 'center',
                                            borderWidth: 1,
                                            borderColor: colors.border,
                                            opacity: device.isOnline ? 1 : 0.6,
                                        }}
                                    >
                                        <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}>{option.label}</Text>
                                    </Pressable>
                                ))}
                            </View>
                            <Button
                                title="Áp dụng độ mở"
                                onPress={() => void applyRainServoOpenPercent(rainServoOpenPercentDraft)}
                                loading={isSendingRainAngle}
                                disabled={!device.isOnline}
                                style={{ marginTop: Spacing.md }}
                            />
                        </View>
                        <Slider
                            value={angleToOpenPercent(device.rainAngle)}
                            onValueChange={() => undefined}
                            label="Độ mở đã đồng bộ"
                            unit="%"
                            min={0}
                            max={100}
                            step={1}
                            disabled
                        />
                    </Card>
                )}

                {/* Sensor Cards */}
                {device.type === 'temperature_humidity' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Nhiệt độ / Độ ẩm</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Nhiệt độ: {device.temperature ?? '--'}°C</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>Độ ẩm: {device.humidity ?? '--'}%</Text>
                    </Card>
                )}

                {device.type === 'distance_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Siêu âm</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Khoảng cách: {device.distanceCm ?? '--'}cm</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Cảnh báo: {device.distanceAlert ? 'Có' : 'Không'}
                        </Text>
                    </Card>
                )}

                {device.type === 'gas_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Gas</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Phát hiện: {device.gasDetected ? 'Có' : 'Không'}</Text>
                    </Card>
                )}

                {device.type === 'rain_sensor' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Mưa</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Phát hiện: {device.rainDetected ? 'Có' : 'Không'}</Text>
                    </Card>
                )}
                {/* Device Info */}
                <Card>
                    <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Thông tin thiết bị</Text>
                    {[
                        {
                            label: 'Loại',
                            value:
                                device.type === 'light' ? 'Đèn'
                                    : device.type === 'fan' ? 'Quạt'
                                        : device.type === 'door' ? 'Cửa'
                                            : device.type === 'lock' ? 'Khóa'
                                                : device.type === 'curtain' ? 'Rèm'
                                            : device.type === 'buzzer' ? 'Còi'
                                                : device.type === 'distance_light' ? 'Đèn khoảng cách'
                                                    : device.type === 'temperature_humidity' ? 'Nhiệt độ / Độ ẩm'
                                                        : device.type === 'distance_sensor' ? 'Siêu âm'
                                                            : device.type === 'gas_sensor' ? 'Gas'
                                                                : device.type === 'rain_sensor' ? 'Mưa'
                                                                    : device.type === 'rain_servo' ? 'Mái che mưa'
                                                                        : 'Khác',
                        },
                        { label: 'Trạng thái', value: device.isOnline ? 'Trực tuyến' : 'Ngoại tuyến' },
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
