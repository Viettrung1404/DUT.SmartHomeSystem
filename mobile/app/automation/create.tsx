import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { automationsAPI, devicesAPI, homesAPI, roomsAPI } from '@/services/api';

interface StepItem {
    type: string;
    label: string;
    icon: keyof typeof Feather.glyphMap;
    available: boolean;
    helperText?: string;
}

interface SelectableDevice {
    id: string;
    name: string;
    type: string;
    roomName: string;
}

const conditions: StepItem[] = [
    { type: 'time', label: 'Theo thời gian', icon: 'clock', available: true },
    {
        type: 'device',
        label: 'Trạng thái thiết bị',
        icon: 'cpu',
        available: false,
        helperText: 'Backend hiện mới tự chạy điều kiện theo giờ.',
    },
    {
        type: 'motion',
        label: 'Phát hiện chuyển động',
        icon: 'activity',
        available: false,
        helperText: 'Luồng chuyển động chưa được engine xử lý.',
    },
    {
        type: 'temperature',
        label: 'Nhiệt độ',
        icon: 'thermometer',
        available: false,
        helperText: 'Điều kiện nhiệt độ chưa được engine xử lý.',
    },
];

const actions: StepItem[] = [
    { type: 'toggle', label: 'Bật/Tắt thiết bị', icon: 'power', available: true },
    {
        type: 'set_speed',
        label: 'Chọn tốc độ quạt',
        icon: 'wind',
        available: false,
        helperText: 'Engine chưa thực thi set_speed từ automation.',
    },
    {
        type: 'open_close',
        label: 'Mở/Đóng cửa',
        icon: 'unlock',
        available: false,
        helperText: 'Dùng Toggle cho khóa/cửa ở phiên bản hiện tại.',
    },
    {
        type: 'set_position',
        label: 'Chọn chế độ che mưa',
        icon: 'droplet',
        available: false,
        helperText: 'Engine chưa thực thi set_position từ automation.',
    },
    {
        type: 'set_angle',
        label: 'Đặt góc che mưa',
        icon: 'sliders',
        available: false,
        helperText: 'Engine chưa thực thi set_angle từ automation.',
    },
    {
        type: 'notify',
        label: 'Gửi thông báo',
        icon: 'bell',
        available: false,
        helperText: 'Thông báo chủ động chưa được nối backend.',
    },
    {
        type: 'scene',
        label: 'Kích hoạt kịch bản',
        icon: 'play',
        available: false,
        helperText: 'Scene chưa có backend thực thi.',
    },
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
    const [selectedCondition, setSelectedCondition] = useState<StepItem | null>(null);
    const [selectedAction, setSelectedAction] = useState<StepItem | null>(null);
    const [timeValue, setTimeValue] = useState('22:00');
    const [automationName, setAutomationName] = useState('');
    const [actionValue, setActionValue] = useState<'true' | 'false'>('true');
    const [homeId, setHomeId] = useState<string | null>(null);
    const [devices, setDevices] = useState<SelectableDevice[]>([]);
    const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
    const [loadingOptions, setLoadingOptions] = useState(true);
    const [saving, setSaving] = useState(false);

    const stepTitles = ['Điều kiện (NẾU)', 'Hành động (THÌ)', 'Xem lại'];
    const selectedDevice = useMemo(
        () => devices.find((device) => device.id === selectedDeviceId) ?? null,
        [devices, selectedDeviceId],
    );
    const canAdvanceFromStep0 = !!selectedCondition && selectedCondition.available && isValidTime(timeValue);
    const canAdvanceFromStep1 = !!selectedAction && selectedAction.available && !!selectedDeviceId;
    const canSubmit =
        !!homeId &&
        !!selectedCondition &&
        !!selectedAction &&
        !!selectedDeviceId &&
        isValidTime(timeValue) &&
        automationName.trim().length > 0;

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
                setSelectedCondition((prev) => prev ?? conditions[0]);
                setSelectedAction((prev) => prev ?? actions[0]);
                setSelectedDeviceId((prev) => prev ?? flattenedDevices[0]?.id ?? null);
            } catch (error) {
                console.error('Failed to load automation options:', error);
                if (isMounted) {
                    setHomeId(null);
                    setDevices([]);
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
        if (!selectedDevice || automationName.trim()) return;
        setAutomationName(`Tự động ${actionValue === 'true' ? 'bật' : 'tắt'} ${selectedDevice.name}`);
    }, [actionValue, automationName, selectedDevice]);

    const handleCreateAutomation = async () => {
        if (!canSubmit || !homeId || !selectedDeviceId) return;

        try {
            setSaving(true);
            await automationsAPI.create({
                home_id: homeId,
                name: automationName.trim(),
                conditions: [{ condition_type: 'time', value: timeValue.trim() }],
                actions: [{ device_id: selectedDeviceId, action: 'toggle', value: actionValue }],
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
                    <View key={i} style={{ flex: 1, alignItems: 'center' }}>
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
                        {i < stepTitles.length - 1 && (
                            <View
                                style={{
                                    position: 'absolute',
                                    top: 15,
                                    left: '75%',
                                    right: '-75%',
                                    height: 2,
                                    backgroundColor: i < step ? colors.primary : colors.border,
                                }}
                            />
                        )}
                    </View>
                ))}
            </View>

            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {loadingOptions ? (
                    <View style={{ paddingVertical: Spacing.xxl, alignItems: 'center', gap: Spacing.md }}>
                        <ActivityIndicator size="large" color={colors.primary} />
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>
                            Đang tải thiết bị và cấu hình nhà...
                        </Text>
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
                                    Chọn điều kiện kích hoạt tự động hóa
                                </Text>
                                <View style={{ gap: Spacing.sm }}>
                                    {conditions.map((condition) => (
                                        <Card
                                            key={condition.type}
                                            onPress={() => condition.available && setSelectedCondition(condition)}
                                            style={{
                                                borderWidth: selectedCondition?.type === condition.type ? 2 : 1,
                                                borderColor: selectedCondition?.type === condition.type ? colors.primary : colors.border,
                                                opacity: condition.available ? 1 : 0.6,
                                            }}
                                        >
                                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                                <View
                                                    style={{
                                                        width: 44,
                                                        height: 44,
                                                        borderRadius: 12,
                                                        backgroundColor:
                                                            selectedCondition?.type === condition.type ? colors.primaryLight : colors.surface,
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                    }}
                                                >
                                                    <Feather
                                                        name={condition.icon}
                                                        size={20}
                                                        color={selectedCondition?.type === condition.type ? colors.primary : colors.icon}
                                                    />
                                                </View>
                                                <View style={{ flex: 1 }}>
                                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{condition.label}</Text>
                                                    {!condition.available && condition.helperText && (
                                                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                            {condition.helperText}
                                                        </Text>
                                                    )}
                                                </View>
                                                {selectedCondition?.type === condition.type && (
                                                    <Feather name="check-circle" size={20} color={colors.primary} style={{ marginLeft: 'auto' }} />
                                                )}
                                            </View>
                                        </Card>
                                    ))}
                                </View>
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
                            </>
                        )}

                        {step === 1 && (
                            <>
                                <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>THÌ...</Text>
                                <Text style={[Typography.body, { color: colors.textSecondary, marginBottom: Spacing.lg }]}>
                                    Chọn hành động sẽ thực hiện
                                </Text>
                                <View style={{ gap: Spacing.sm }}>
                                    {actions.map((action) => (
                                        <Card
                                            key={action.type}
                                            onPress={() => action.available && setSelectedAction(action)}
                                            style={{
                                                borderWidth: selectedAction?.type === action.type ? 2 : 1,
                                                borderColor: selectedAction?.type === action.type ? colors.primary : colors.border,
                                                opacity: action.available ? 1 : 0.6,
                                            }}
                                        >
                                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                                <View
                                                    style={{
                                                        width: 44,
                                                        height: 44,
                                                        borderRadius: 12,
                                                        backgroundColor: selectedAction?.type === action.type ? colors.primaryLight : colors.surface,
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                    }}
                                                >
                                                    <Feather
                                                        name={action.icon}
                                                        size={20}
                                                        color={selectedAction?.type === action.type ? colors.primary : colors.icon}
                                                    />
                                                </View>
                                                <View style={{ flex: 1 }}>
                                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{action.label}</Text>
                                                    {!action.available && action.helperText && (
                                                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                            {action.helperText}
                                                        </Text>
                                                    )}
                                                </View>
                                                {selectedAction?.type === action.type && (
                                                    <Feather name="check-circle" size={20} color={colors.primary} style={{ marginLeft: 'auto' }} />
                                                )}
                                            </View>
                                        </Card>
                                    ))}
                                </View>

                                <Text style={[Typography.h3, { color: colors.text, marginTop: Spacing.lg, marginBottom: Spacing.sm }]}>
                                    Thiết bị mục tiêu
                                </Text>
                                <View style={{ gap: Spacing.sm }}>
                                    {devices.length ? (
                                        devices.map((device) => {
                                            const isSelected = selectedDeviceId === device.id;
                                            return (
                                                <Card
                                                    key={device.id}
                                                    onPress={() => setSelectedDeviceId(device.id)}
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
                                                        {isSelected && <Feather name="check-circle" size={20} color={colors.primary} />}
                                                    </View>
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

                                <Text style={[Typography.h3, { color: colors.text, marginTop: Spacing.lg, marginBottom: Spacing.sm }]}>
                                    Hành động
                                </Text>
                                <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                                    {[
                                        { label: 'Bật / Mở', value: 'true' as const },
                                        { label: 'Tắt / Đóng', value: 'false' as const },
                                    ].map((option) => {
                                        const isSelected = actionValue === option.value;
                                        return (
                                            <Pressable
                                                key={option.value}
                                                onPress={() => setActionValue(option.value)}
                                                style={{
                                                    flex: 1,
                                                    paddingVertical: Spacing.md,
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

                        {step === 2 && (
                            <>
                                <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.lg }]}>Xem lại</Text>
                                <Input
                                    label="Tên tự động hóa"
                                    placeholder="Ví dụ: Bật đèn sân lúc 18:30"
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
                                        <Feather name={selectedCondition?.icon || 'circle'} size={20} color={colors.primary} />
                                        <View>
                                            <Text style={[Typography.body, { color: colors.text }]}>{selectedCondition?.label}</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                Lúc {timeValue}
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
                                        <Feather name={selectedAction?.icon || 'circle'} size={20} color={colors.warning} />
                                        <View>
                                            <Text style={[Typography.body, { color: colors.text }]}>{selectedAction?.label}</Text>
                                            <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                                                {selectedDevice?.name ?? 'Chưa chọn thiết bị'} • {actionValue === 'true' ? 'Bật / Mở' : 'Tắt / Đóng'}
                                            </Text>
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
