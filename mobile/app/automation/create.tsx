import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';

import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { useTheme } from '@/contexts/ThemeContext';
import { automationsAPI, devicesAPI, homesAPI, roomsAPI } from '@/services/api';

interface SelectableDevice {
    id: string;
    name: string;
    type: string;
    roomName: string;
}

const weekdayOptions = [
    { value: 1, label: 'T2' },
    { value: 2, label: 'T3' },
    { value: 3, label: 'T4' },
    { value: 4, label: 'T5' },
    { value: 5, label: 'T6' },
    { value: 6, label: 'T7' },
    { value: 0, label: 'CN' },
];

function getDeviceIcon(type: string): keyof typeof Feather.glyphMap {
    const iconMap: Record<string, keyof typeof Feather.glyphMap> = {
        light: 'sun',
        fan: 'wind',
        door: 'unlock',
        lock: 'lock',
        curtain: 'columns',
        camera: 'camera',
        sensor: 'activity',
        buzzer: 'bell',
        distance_light: 'activity',
        temperature_humidity: 'thermometer',
        distance_sensor: 'radio',
        gas_sensor: 'alert-triangle',
        rain_sensor: 'cloud-rain',
        rain_servo: 'droplet',
    };
    return iconMap[type] ?? 'cpu';
}

function isValidTime(value: string): boolean {
    return /^([01]\d|2[0-3]):([0-5]\d)$/.test(value.trim());
}

export default function CreateAutomationScreen() {
    const { colors } = useTheme();
    const router = useRouter();

    const [step, setStep] = useState(0);
    const [timeValue, setTimeValue] = useState('22:00');
    const [selectedWeekdays, setSelectedWeekdays] = useState<number[]>([]);
    const [automationName, setAutomationName] = useState('');
    const [deviceActionValues, setDeviceActionValues] = useState<Record<string, 'true' | 'false'>>({});
    const [homeId, setHomeId] = useState<string | null>(null);
    const [devices, setDevices] = useState<SelectableDevice[]>([]);
    const [selectedDeviceIds, setSelectedDeviceIds] = useState<string[]>([]);
    const [loadingOptions, setLoadingOptions] = useState(true);
    const [saving, setSaving] = useState(false);

    const stepTitles = ['Điều kiện', 'Thiết bị', 'Xem lại'];
    const selectedDevices = useMemo(
        () => devices.filter((device) => selectedDeviceIds.includes(device.id)),
        [devices, selectedDeviceIds],
    );
    const selectedWeekdayLabels = weekdayOptions
        .filter((option) => selectedWeekdays.includes(option.value))
        .map((option) => option.label)
        .join(', ');
    const actionCounts = selectedDeviceIds.reduce(
        (counts, deviceId) => {
            if ((deviceActionValues[deviceId] ?? 'true') === 'true') {
                counts.on += 1;
            } else {
                counts.off += 1;
            }
            return counts;
        },
        { on: 0, off: 0 },
    );
    const actionSummary =
        actionCounts.on > 0 && actionCounts.off > 0
            ? `Bật/Mở ${actionCounts.on}, Tắt/Đóng ${actionCounts.off}`
            : actionCounts.off > 0
                ? 'Tắt / Đóng'
                : 'Bật / Mở';
    const deviceSummary =
        selectedDevices.length <= 3
            ? selectedDevices.map((device) => device.name).join(', ')
            : `${selectedDevices.slice(0, 3).map((device) => device.name).join(', ')} +${selectedDevices.length - 3}`;

    const canAdvanceFromStep0 = isValidTime(timeValue);
    const canAdvanceFromStep1 = selectedDeviceIds.length > 0;
    const canSubmit = !!homeId && canAdvanceFromStep0 && canAdvanceFromStep1 && automationName.trim().length > 0;

    const toggleWeekday = (day: number) => {
        setSelectedWeekdays((current) =>
            current.includes(day)
                ? current.filter((value) => value !== day)
                : [...current, day].sort((a, b) => a - b),
        );
    };

    const toggleDeviceSelection = (deviceId: string) => {
        setSelectedDeviceIds((current) => {
            if (current.includes(deviceId)) {
                setDeviceActionValues((values) => {
                    const next = { ...values };
                    delete next[deviceId];
                    return next;
                });
                return current.filter((id) => id !== deviceId);
            }

            setDeviceActionValues((values) => ({ ...values, [deviceId]: values[deviceId] ?? 'true' }));
            return [...current, deviceId];
        });
    };

    const setDeviceActionValue = (deviceId: string, value: 'true' | 'false') => {
        setSelectedDeviceIds((current) => (current.includes(deviceId) ? current : [...current, deviceId]));
        setDeviceActionValues((current) => ({ ...current, [deviceId]: value }));
    };

    useEffect(() => {
        let isMounted = true;

        async function loadOptions() {
            try {
                setLoadingOptions(true);
                const homes = await homesAPI.list();
                if (!homes.length) {
                    if (isMounted) {
                        setHomeId(null);
                        setDevices([]);
                        setSelectedDeviceIds([]);
                    }
                    return;
                }

                const firstHomeId = homes[0].id;
                const roomResponses = await roomsAPI.list(firstHomeId);
                const deviceGroups = await Promise.all(
                    roomResponses.map(async (room) => {
                        const roomDevices = await devicesAPI.list(room.id);
                        return roomDevices.map((device) => ({
                            id: device.id,
                            name: device.name,
                            type: device.type?.toLowerCase?.() ?? device.type,
                            roomName: room.name,
                        }));
                    }),
                );

                if (!isMounted) return;

                const flattenedDevices = deviceGroups.flat();
                setHomeId(firstHomeId);
                setDevices(flattenedDevices);
                setSelectedDeviceIds((current) => (current.length ? current : flattenedDevices[0] ? [flattenedDevices[0].id] : []));
                setDeviceActionValues((current) =>
                    Object.keys(current).length || !flattenedDevices[0]
                        ? current
                        : { [flattenedDevices[0].id]: 'true' },
                );
            } catch (error) {
                console.error('Failed to load automation options:', error);
                if (isMounted) {
                    setHomeId(null);
                    setDevices([]);
                    setSelectedDeviceIds([]);
                }
            } finally {
                if (isMounted) {
                    setLoadingOptions(false);
                }
            }
        }

        void loadOptions();

        return () => {
            isMounted = false;
        };
    }, []);

    useEffect(() => {
        if (automationName.trim() || selectedDevices.length === 0) return;
        const target = selectedDevices.length === 1 ? selectedDevices[0].name : `${selectedDevices.length} thiết bị`;
        setAutomationName(`Tự động ${target}`);
    }, [automationName, selectedDevices]);

    const handleCreateAutomation = async () => {
        if (!canSubmit || !homeId) return;

        try {
            setSaving(true);
            const condition =
                selectedWeekdays.length > 0
                    ? {
                        condition_type: 'weekday_time',
                        value: JSON.stringify({
                            time: timeValue.trim(),
                            days_of_week: selectedWeekdays,
                        }),
                    }
                    : { condition_type: 'time', value: timeValue.trim() };

            await automationsAPI.create({
                home_id: homeId,
                name: automationName.trim(),
                conditions: [condition],
                actions: selectedDeviceIds.map((deviceId) => ({
                    device_id: deviceId,
                    action: 'toggle',
                    value: deviceActionValues[deviceId] ?? 'true',
                })),
            });

            Alert.alert('Đã tạo tự động hóa', 'Kịch bản mới đã được lưu và sẽ xuất hiện ở danh sách.');
            router.back();
        } catch (error) {
            console.error('Failed to create automation:', error);
            Alert.alert('Không tạo được tự động hóa', error instanceof Error ? error.message : 'Vui lòng thử lại.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Tạo tự động hóa" showBack />

            <View style={{ flexDirection: 'row', paddingHorizontal: Spacing.md, marginBottom: Spacing.md, gap: Spacing.xs }}>
                {stepTitles.map((title, i) => (
                    <View key={title} style={{ flex: 1, alignItems: 'center' }}>
                        <View
                            style={{
                                width: 32,
                                height: 32,
                                borderRadius: 16,
                                backgroundColor: i <= step ? colors.primary : colors.surface,
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderWidth: 2,
                                borderColor: i <= step ? colors.primary : colors.border,
                                marginBottom: Spacing.xs,
                            }}
                        >
                            {i < step ? (
                                <Feather name="check" size={16} color="#FFFFFF" />
                            ) : (
                                <Text style={[Typography.captionMedium, { color: i <= step ? '#FFFFFF' : colors.textSecondary }]}>
                                    {i + 1}
                                </Text>
                            )}
                        </View>
                        <Text style={[Typography.caption, { color: i <= step ? colors.primary : colors.textTertiary, textAlign: 'center' }]}>
                            {title}
                        </Text>
                    </View>
                ))}
            </View>

            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {loadingOptions ? (
                    <View style={{ paddingVertical: Spacing.xxl, alignItems: 'center', gap: Spacing.md }}>
                        <ActivityIndicator size="large" color={colors.primary} />
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Đang tải thiết bị và cấu hình nhà...</Text>
                    </View>
                ) : !homeId ? (
                    <Card>
                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>Chưa có nhà để tạo tự động hóa</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Hãy tạo nhà và phòng trước khi cấu hình tự động hóa.
                        </Text>
                    </Card>
                ) : (
                    <>
                        {step === 0 && (
                            <>
                                <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>NẾU...</Text>
                                <Text style={[Typography.body, { color: colors.textSecondary, marginBottom: Spacing.lg }]}>
                                    Chạy tự động hóa theo thời gian đã đặt
                                </Text>

                                <Card
                                    style={{
                                        borderWidth: 2,
                                        borderColor: colors.primary,
                                    }}
                                >
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                        <View
                                            style={{
                                                width: 44,
                                                height: 44,
                                                borderRadius: 12,
                                                backgroundColor: colors.primaryLight,
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                            }}
                                        >
                                            <Feather name="clock" size={20} color={colors.primary} />
                                        </View>
                                        <View style={{ flex: 1 }}>
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>Theo thời gian</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                Engine sẽ kiểm tra lịch mỗi phút.
                                            </Text>
                                        </View>
                                        <Feather name="check-circle" size={20} color={colors.primary} />
                                    </View>
                                </Card>

                                <Input
                                    label="Giờ kích hoạt (HH:MM)"
                                    placeholder="22:00"
                                    value={timeValue}
                                    onChangeText={setTimeValue}
                                    icon="clock"
                                    error={
                                        timeValue.length > 0 && !isValidTime(timeValue)
                                            ? 'Nhập theo định dạng 24h, ví dụ 06:30 hoặc 22:15.'
                                            : undefined
                                    }
                                    style={{ marginTop: Spacing.lg }}
                                />

                                <Text style={[Typography.h3, { color: colors.text, marginTop: Spacing.lg, marginBottom: Spacing.sm }]}>
                                    Ngày trong tuần
                                </Text>
                                <Text style={[Typography.caption, { color: colors.textSecondary, marginBottom: Spacing.sm }]}>
                                    Không chọn ngày nào thì kịch bản sẽ chạy mỗi ngày.
                                </Text>
                                <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs }}>
                                    {weekdayOptions.map((option) => {
                                        const isSelected = selectedWeekdays.includes(option.value);
                                        return (
                                            <Pressable
                                                key={option.value}
                                                onPress={() => toggleWeekday(option.value)}
                                                style={{
                                                    minWidth: 44,
                                                    paddingVertical: Spacing.sm,
                                                    paddingHorizontal: Spacing.md,
                                                    borderRadius: BorderRadius.md,
                                                    backgroundColor: isSelected ? colors.primaryLight : colors.surface,
                                                    borderWidth: 1.5,
                                                    borderColor: isSelected ? colors.primary : colors.border,
                                                    alignItems: 'center',
                                                }}
                                            >
                                                <Text style={[Typography.captionMedium, { color: isSelected ? colors.primary : colors.textSecondary }]}>
                                                    {option.label}
                                                </Text>
                                            </Pressable>
                                        );
                                    })}
                                </View>
                            </>
                        )}

                        {step === 1 && (
                            <>
                                <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>THÌ...</Text>
                                <Text style={[Typography.body, { color: colors.textSecondary, marginBottom: Spacing.lg }]}>
                                    Bật hoặc tắt một hay nhiều thiết bị
                                </Text>

                                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>
                                    Thiết bị mục tiêu ({selectedDeviceIds.length})
                                </Text>
                                <View style={{ gap: Spacing.sm }}>
                                    {devices.length ? (
                                        devices.map((device) => {
                                            const isSelected = selectedDeviceIds.includes(device.id);
                                            return (
                                                <Card
                                                    key={device.id}
                                                    onPress={() => toggleDeviceSelection(device.id)}
                                                    style={{
                                                        borderWidth: isSelected ? 2 : 1,
                                                        borderColor: isSelected ? colors.primary : colors.border,
                                                    }}
                                                >
                                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                                        <View
                                                            style={{
                                                                width: 44,
                                                                height: 44,
                                                                borderRadius: 12,
                                                                backgroundColor: isSelected ? colors.primaryLight : colors.surface,
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                            }}
                                                        >
                                                            <Feather name={getDeviceIcon(device.type)} size={20} color={isSelected ? colors.primary : colors.icon} />
                                                        </View>
                                                        <View style={{ flex: 1 }}>
                                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{device.name}</Text>
                                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                                {device.roomName} • {device.type}
                                                            </Text>
                                                        </View>
                                                        <Feather
                                                            name={isSelected ? 'check-circle' : 'circle'}
                                                            size={20}
                                                            color={isSelected ? colors.primary : colors.textTertiary}
                                                        />
                                                    </View>
                                                    {isSelected && (
                                                        <View style={{ flexDirection: 'row', gap: Spacing.sm, marginTop: Spacing.md }}>
                                                            {[
                                                                { label: 'Bật / Mở', value: 'true' as const },
                                                                { label: 'Tắt / Đóng', value: 'false' as const },
                                                            ].map((option) => {
                                                                const selectedAction = (deviceActionValues[device.id] ?? 'true') === option.value;
                                                                return (
                                                                    <Pressable
                                                                        key={option.value}
                                                                        onPress={() => setDeviceActionValue(device.id, option.value)}
                                                                        style={{
                                                                            flex: 1,
                                                                            paddingVertical: Spacing.sm,
                                                                            borderRadius: BorderRadius.md,
                                                                            backgroundColor: selectedAction ? colors.primaryLight : colors.surface,
                                                                            borderWidth: 1.5,
                                                                            borderColor: selectedAction ? colors.primary : colors.border,
                                                                            alignItems: 'center',
                                                                        }}
                                                                    >
                                                                        <Text
                                                                            style={[
                                                                                Typography.captionMedium,
                                                                                { color: selectedAction ? colors.primary : colors.textSecondary },
                                                                            ]}
                                                                        >
                                                                            {option.label}
                                                                        </Text>
                                                                    </Pressable>
                                                                );
                                                            })}
                                                        </View>
                                                    )}
                                                </Card>
                                            );
                                        })
                                    ) : (
                                        <Card>
                                            <Text style={[Typography.body, { color: colors.textSecondary }]}>
                                                Chưa có thiết bị nào khả dụng trong nhà này.
                                            </Text>
                                        </Card>
                                    )}
                                </View>
                            </>
                        )}

                        {step === 2 && (
                            <>
                                <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.lg }]}>Xem lại</Text>
                                <Input
                                    label="Tên tự động hóa"
                                    placeholder="Ví dụ: Tắt đèn tầng 1 lúc 23:00"
                                    value={automationName}
                                    onChangeText={setAutomationName}
                                    icon="zap"
                                    autoCapitalize="sentences"
                                />
                                <Card style={{ marginBottom: Spacing.md }}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md }}>
                                        <Text style={[Typography.captionMedium, { color: colors.primary }]}>NẾU</Text>
                                        <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
                                    </View>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                        <Feather name="clock" size={20} color={colors.primary} />
                                        <View>
                                            <Text style={[Typography.body, { color: colors.text }]}>Theo thời gian</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                Lúc {timeValue}{selectedWeekdayLabels ? ` - ${selectedWeekdayLabels}` : ' - mỗi ngày'}
                                            </Text>
                                        </View>
                                    </View>
                                </Card>
                                <View style={{ alignItems: 'center', marginBottom: Spacing.sm }}>
                                    <Feather name="arrow-down" size={20} color={colors.textTertiary} />
                                </View>
                                <Card style={{ marginBottom: Spacing.lg }}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md }}>
                                        <Text style={[Typography.captionMedium, { color: colors.warning }]}>THÌ</Text>
                                        <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
                                    </View>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                        <Feather name="power" size={20} color={colors.warning} />
                                        <View style={{ flex: 1 }}>
                                            <Text style={[Typography.body, { color: colors.text }]}>{actionSummary}</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                {selectedDeviceIds.length} thiết bị: {deviceSummary}
                                            </Text>
                                            <View style={{ gap: Spacing.xs, marginTop: Spacing.sm }}>
                                                {selectedDevices.map((device) => (
                                                    <Text key={device.id} style={[Typography.caption, { color: colors.textSecondary }]}>
                                                        {device.name}: {(deviceActionValues[device.id] ?? 'true') === 'true' ? 'Bật / Mở' : 'Tắt / Đóng'}
                                                    </Text>
                                                ))}
                                            </View>
                                        </View>
                                    </View>
                                </Card>
                            </>
                        )}

                        <View style={{ height: Spacing.xxl }} />
                    </>
                )}
            </ScrollView>

            <View style={{ flexDirection: 'row', gap: Spacing.sm, padding: Spacing.md, borderTopWidth: 1, borderTopColor: colors.border }}>
                {step > 0 && (
                    <Button title="Quay lại" onPress={() => setStep((currentStep) => currentStep - 1)} variant="outline" style={{ flex: 1 }} />
                )}
                {step < 2 ? (
                    <Button
                        title="Tiếp theo"
                        onPress={() => setStep((currentStep) => currentStep + 1)}
                        disabled={loadingOptions || !homeId || (step === 0 ? !canAdvanceFromStep0 : !canAdvanceFromStep1)}
                        style={{ flex: 1 }}
                    />
                ) : (
                    <Button
                        title="Tạo tự động hóa"
                        onPress={handleCreateAutomation}
                        loading={saving}
                        disabled={!canSubmit}
                        style={{ flex: 1 }}
                        icon={<Feather name="check" size={16} color="#FFFFFF" />}
                    />
                )}
            </View>
        </SafeAreaView>
    );
}
