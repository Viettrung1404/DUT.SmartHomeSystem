import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { EnergyChart } from '@/components/EnergyChart';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { mockHome, mockEnergyDaily, mockEnergyWeekly, mockEnergyMonthly } from '@/services/mockData';

export default function EnergyScreen() {
    const { colors } = useTheme();

    const energyChange = ((mockHome.energyToday - mockHome.energyYesterday) / mockHome.energyYesterday * 100).toFixed(1);
    const isEnergyUp = mockHome.energyToday > mockHome.energyYesterday;

    // Breakdown mock
    const breakdown = [
        { name: 'Máy lạnh', usage: 4.2, pct: 34, icon: 'wind' },
        { name: 'Đèn', usage: 3.1, pct: 25, icon: 'sun' },
        { name: 'Bếp', usage: 2.8, pct: 23, icon: 'coffee' },
        { name: 'Khác', usage: 2.3, pct: 18, icon: 'more-horizontal' },
    ];

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Phân tích điện năng" showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {/* Summary */}
                <View style={{ flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md }}>
                    <Card style={{ flex: 1 }}>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Hôm nay</Text>
                        <Text style={[Typography.numberLarge, { color: colors.text, marginTop: Spacing.xs }]}>
                            {mockHome.energyToday}
                        </Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
                    </Card>
                    <Card style={{ flex: 1 }}>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Hôm qua</Text>
                        <Text style={[Typography.numberLarge, { color: colors.text, marginTop: Spacing.xs }]}>
                            {mockHome.energyYesterday}
                        </Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
                    </Card>
                    <Card style={{ flex: 1 }}>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>So sánh</Text>
                        <Text
                            style={[
                                Typography.numberLarge,
                                { color: isEnergyUp ? colors.error : colors.success, marginTop: Spacing.xs },
                            ]}
                        >
                            {isEnergyUp ? '+' : ''}{energyChange}%
                        </Text>
                        <Feather
                            name={isEnergyUp ? 'trending-up' : 'trending-down'}
                            size={14}
                            color={isEnergyUp ? colors.error : colors.success}
                        />
                    </Card>
                </View>

                {/* Chart */}
                <View style={{ marginBottom: Spacing.md }}>
                    <EnergyChart dailyData={mockEnergyDaily} weeklyData={mockEnergyWeekly} monthlyData={mockEnergyMonthly} />
                </View>

                {/* Breakdown */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>
                    Theo thiết bị
                </Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {breakdown.map((item, i) => {
                        const iconName = item.icon as keyof typeof Feather.glyphMap;
                        return (
                            <Card key={i}>
                                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                    <View
                                        style={{
                                            width: 40, height: 40, borderRadius: 12,
                                            backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                                        }}
                                    >
                                        <Feather name={iconName} size={18} color={colors.primary} />
                                    </View>
                                    <View style={{ flex: 1 }}>
                                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: Spacing.xs }}>
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.name}</Text>
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.usage} kWh</Text>
                                        </View>
                                        {/* Progress bar */}
                                        <View style={{ height: 6, backgroundColor: colors.border, borderRadius: 3 }}>
                                            <View
                                                style={{
                                                    height: '100%', width: `${item.pct}%`, backgroundColor: colors.primary,
                                                    borderRadius: 3, opacity: 0.5 + (item.pct / 100) * 0.5,
                                                }}
                                            />
                                        </View>
                                    </View>
                                    <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}>{item.pct}%</Text>
                                </View>
                            </Card>
                        );
                    })}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
