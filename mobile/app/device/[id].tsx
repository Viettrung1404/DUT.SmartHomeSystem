import React, { useState } from 'react';
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
import { mockDevices, Device } from '@/services/mockData';

export default function DeviceDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();

    // Find device across all rooms
    const allDevices = Object.values(mockDevices).flat();
    const foundDevice = allDevices.find((d) => d.id === id);
    const [device, setDevice] = useState<Device | undefined>(foundDevice);

    if (!device) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={[Typography.body, { color: colors.textSecondary }]}>Không tìm thấy thiết bị</Text>
            </SafeAreaView>
        );
    }

    const updateDevice = (updates: Partial<Device>) => {
        setDevice((prev) => prev ? { ...prev, ...updates } : prev);
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
                        <Toggle
                            value={device.isOn}
                            onToggle={(val) => updateDevice({ isOn: val })}
                            disabled={!device.isOnline}
                        />
                    </View>
                </Card>

                {/* Light Controls */}
                {device.type === 'light' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Độ sáng</Text>
                        <Slider
                            value={device.brightness ?? 0}
                            onValueChange={(val) => updateDevice({ brightness: val })}
                            label="Độ sáng"
                            unit="%"
                            disabled={!device.isOn || !device.isOnline}
                        />
                    </Card>
                )}

                {/* AC Controls */}
                {device.type === 'ac' && (
                    <>
                        <Card style={{ marginBottom: Spacing.md }}>
                            <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Nhiệt độ</Text>
                            <View style={{ alignItems: 'center', marginBottom: Spacing.md }}>
                                <Text style={[Typography.displayLarge, { color: colors.primary }]}>
                                    {device.targetTemp ?? 24}°C
                                </Text>
                                <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                    Nhiệt độ phòng: {device.temperature ?? '--'}°C
                                </Text>
                            </View>
                            <Slider
                                value={device.targetTemp ?? 24}
                                onValueChange={(val) => updateDevice({ targetTemp: val })}
                                label="Mục tiêu"
                                unit="°C"
                                min={16}
                                max={30}
                                step={1}
                                disabled={!device.isOn || !device.isOnline}
                            />
                        </Card>

                        <Card style={{ marginBottom: Spacing.md }}>
                            <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Chế độ</Text>
                            <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                                {['Cool', 'Dry', 'Fan'].map((mode) => (
                                    <Pressable
                                        key={mode}
                                        onPress={() => updateDevice({ mode })}
                                        style={{
                                            flex: 1,
                                            paddingVertical: Spacing.md,
                                            borderRadius: BorderRadius.md,
                                            backgroundColor: device.mode === mode ? colors.primary : colors.surface,
                                            alignItems: 'center',
                                            borderWidth: 1,
                                            borderColor: device.mode === mode ? colors.primary : colors.border,
                                        }}
                                    >
                                        <Feather
                                            name={mode === 'Cool' ? 'thermometer' : mode === 'Dry' ? 'droplet' : 'wind'}
                                            size={20}
                                            color={device.mode === mode ? '#FFFFFF' : colors.icon}
                                        />
                                        <Text
                                            style={[
                                                Typography.captionMedium,
                                                {
                                                    color: device.mode === mode ? '#FFFFFF' : colors.textSecondary,
                                                    marginTop: Spacing.xs,
                                                },
                                            ]}
                                        >
                                            {mode === 'Cool' ? 'Làm lạnh' : mode === 'Dry' ? 'Hút ẩm' : 'Quạt'}
                                        </Text>
                                    </Pressable>
                                ))}
                            </View>
                        </Card>
                    </>
                )}

                {/* Camera Controls */}
                {device.type === 'camera' && (
                    <Card style={{ marginBottom: Spacing.md }}>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Xem trước</Text>
                        <View
                            style={{
                                height: 200, backgroundColor: colors.surface, borderRadius: BorderRadius.md,
                                alignItems: 'center', justifyContent: 'center',
                                borderWidth: 1, borderColor: colors.border,
                            }}
                        >
                            {device.isOnline ? (
                                <>
                                    <Feather name="play-circle" size={48} color={colors.primary} />
                                    <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.sm }]}>
                                        Nhấn để xem toàn màn hình
                                    </Text>
                                </>
                            ) : (
                                <>
                                    <Feather name="video-off" size={48} color={colors.textTertiary} />
                                    <Text style={[Typography.body, { color: colors.textTertiary, marginTop: Spacing.sm }]}>
                                        Camera ngoại tuyến
                                    </Text>
                                </>
                            )}
                        </View>
                    </Card>
                )}

                {/* Device Info */}
                <Card>
                    <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Thông tin thiết bị</Text>
                    {[
                        { label: 'Loại', value: device.type === 'light' ? 'Đèn' : device.type === 'ac' ? 'Máy lạnh' : device.type === 'camera' ? 'Camera' : device.type === 'fan' ? 'Quạt' : device.type === 'lock' ? 'Khóa' : device.type === 'sensor' ? 'Cảm biến' : 'Rèm' },
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
        </SafeAreaView>
    );
}
