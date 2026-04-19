import React, { useState } from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

interface StepItem {
    type: string;
    label: string;
    icon: keyof typeof Feather.glyphMap;
}

const conditions: StepItem[] = [
    { type: 'time', label: 'Theo thời gian', icon: 'clock' },
    { type: 'device', label: 'Trạng thái thiết bị', icon: 'cpu' },
    { type: 'motion', label: 'Phát hiện chuyển động', icon: 'activity' },
    { type: 'energy', label: 'Mức điện năng', icon: 'zap' },
    { type: 'temperature', label: 'Nhiệt độ', icon: 'thermometer' },
];

const actions: StepItem[] = [
    { type: 'toggle', label: 'Bật/Tắt thiết bị', icon: 'power' },
    { type: 'brightness', label: 'Thay đổi độ sáng', icon: 'sun' },
    { type: 'temperature', label: 'Đặt nhiệt độ', icon: 'thermometer' },
    { type: 'lock', label: 'Khóa/Mở khóa', icon: 'lock' },
    { type: 'notify', label: 'Gửi thông báo', icon: 'bell' },
    { type: 'scene', label: 'Kích hoạt kịch bản', icon: 'play' },
];

export default function CreateAutomationScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [step, setStep] = useState(0); // 0: condition, 1: action, 2: review
    const [selectedCondition, setSelectedCondition] = useState<StepItem | null>(null);
    const [selectedAction, setSelectedAction] = useState<StepItem | null>(null);
    const [timeValue, setTimeValue] = useState('22:00');

    const stepTitles = ['Điều kiện (NẾU)', 'Hành động (THÌ)', 'Xem lại'];

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Tạo tự động hóa" showBack />

            {/* Step Indicator */}
            <View style={{ flexDirection: 'row', paddingHorizontal: Spacing.md, marginBottom: Spacing.md, gap: Spacing.xs }}>
                {stepTitles.map((title, i) => (
                    <View key={i} style={{ flex: 1, alignItems: 'center' }}>
                        <View
                            style={{
                                width: 32, height: 32, borderRadius: 16,
                                backgroundColor: i <= step ? colors.primary : colors.surface,
                                alignItems: 'center', justifyContent: 'center',
                                borderWidth: 2, borderColor: i <= step ? colors.primary : colors.border,
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
                                    position: 'absolute', top: 15, left: '75%', right: '-75%',
                                    height: 2, backgroundColor: i < step ? colors.primary : colors.border,
                                }}
                            />
                        )}
                    </View>
                ))}
            </View>

            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {/* Step 0: Condition */}
                {step === 0 && (
                    <>
                        <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>NẾU...</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginBottom: Spacing.lg }]}>
                            Chọn điều kiện kích hoạt tự động hóa
                        </Text>
                        <View style={{ gap: Spacing.sm }}>
                            {conditions.map((c) => (
                                <Card
                                    key={c.type}
                                    onPress={() => setSelectedCondition(c)}
                                    style={{
                                        borderWidth: selectedCondition?.type === c.type ? 2 : 1,
                                        borderColor: selectedCondition?.type === c.type ? colors.primary : colors.border,
                                    }}
                                >
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                        <View
                                            style={{
                                                width: 44, height: 44, borderRadius: 12,
                                                backgroundColor: selectedCondition?.type === c.type ? colors.primaryLight : colors.surface,
                                                alignItems: 'center', justifyContent: 'center',
                                            }}
                                        >
                                            <Feather name={c.icon} size={20} color={selectedCondition?.type === c.type ? colors.primary : colors.icon} />
                                        </View>
                                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>{c.label}</Text>
                                        {selectedCondition?.type === c.type && (
                                            <Feather name="check-circle" size={20} color={colors.primary} style={{ marginLeft: 'auto' }} />
                                        )}
                                    </View>
                                </Card>
                            ))}
                        </View>
                    </>
                )}

                {/* Step 1: Action */}
                {step === 1 && (
                    <>
                        <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>THÌ...</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginBottom: Spacing.lg }]}>
                            Chọn hành động sẽ thực hiện
                        </Text>
                        <View style={{ gap: Spacing.sm }}>
                            {actions.map((a) => (
                                <Card
                                    key={a.type}
                                    onPress={() => setSelectedAction(a)}
                                    style={{
                                        borderWidth: selectedAction?.type === a.type ? 2 : 1,
                                        borderColor: selectedAction?.type === a.type ? colors.primary : colors.border,
                                    }}
                                >
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                        <View
                                            style={{
                                                width: 44, height: 44, borderRadius: 12,
                                                backgroundColor: selectedAction?.type === a.type ? colors.primaryLight : colors.surface,
                                                alignItems: 'center', justifyContent: 'center',
                                            }}
                                        >
                                            <Feather name={a.icon} size={20} color={selectedAction?.type === a.type ? colors.primary : colors.icon} />
                                        </View>
                                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>{a.label}</Text>
                                        {selectedAction?.type === a.type && (
                                            <Feather name="check-circle" size={20} color={colors.primary} style={{ marginLeft: 'auto' }} />
                                        )}
                                    </View>
                                </Card>
                            ))}
                        </View>
                    </>
                )}

                {/* Step 2: Review */}
                {step === 2 && (
                    <>
                        <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.lg }]}>Xem lại</Text>
                        <Card style={{ marginBottom: Spacing.md }}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md }}>
                                <Text style={[Typography.captionMedium, { color: colors.primary }]}>NẾU</Text>
                                <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
                            </View>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <Feather name={selectedCondition?.icon || 'circle'} size={20} color={colors.primary} />
                                <Text style={[Typography.body, { color: colors.text }]}>{selectedCondition?.label}</Text>
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
                                <Text style={[Typography.body, { color: colors.text }]}>{selectedAction?.label}</Text>
                            </View>
                        </Card>
                    </>
                )}

                <View style={{ height: Spacing.xxl }} />
            </ScrollView>

            {/* Bottom Buttons */}
            <View style={{ flexDirection: 'row', gap: Spacing.sm, padding: Spacing.md, borderTopWidth: 1, borderTopColor: colors.border }}>
                {step > 0 && (
                    <Button title="Quay lại" onPress={() => setStep((s) => s - 1)} variant="outline" style={{ flex: 1 }} />
                )}
                {step < 2 ? (
                    <Button
                        title="Tiếp theo"
                        onPress={() => setStep((s) => s + 1)}
                        disabled={step === 0 ? !selectedCondition : !selectedAction}
                        style={{ flex: 1 }}
                    />
                ) : (
                    <Button
                        title="Tạo tự động hóa"
                        onPress={() => router.back()}
                        style={{ flex: 1 }}
                        icon={<Feather name="check" size={16} color="#FFFFFF" />}
                    />
                )}
            </View>
        </SafeAreaView>
    );
}
