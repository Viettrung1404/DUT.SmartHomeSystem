import React, { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { EnergyDataPoint } from '@/services/api';

interface EnergyChartProps {
    dailyData: EnergyDataPoint[];
    weeklyData: EnergyDataPoint[];
    monthlyData: EnergyDataPoint[];
}

type Period = 'day' | 'week' | 'month';

export function EnergyChart({ dailyData, weeklyData, monthlyData }: EnergyChartProps) {
    const { colors } = useTheme();
    const [period, setPeriod] = useState<Period>('day');

    const data = period === 'day' ? dailyData : period === 'week' ? weeklyData : monthlyData;
    const maxValue = Math.max(...data.map((d) => d.value), 1);
    const total = data.reduce((sum, d) => sum + d.value, 0);
    const unit = period === 'month' ? 'kWh' : 'kWh';

    const periods: { key: Period; label: string }[] = [
        { key: 'day', label: 'Ngày' },
        { key: 'week', label: 'Tuần' },
        { key: 'month', label: 'Tháng' },
    ];

    return (
        <Card>
            {/* Period selector */}
            <View
                style={{
                    flexDirection: 'row',
                    backgroundColor: colors.surface,
                    borderRadius: BorderRadius.md,
                    padding: 3,
                    marginBottom: Spacing.lg,
                }}
            >
                {periods.map((p) => (
                    <Pressable
                        key={p.key}
                        onPress={() => setPeriod(p.key)}
                        style={{
                            flex: 1,
                            paddingVertical: Spacing.sm,
                            borderRadius: BorderRadius.sm,
                            backgroundColor: period === p.key ? colors.primary : 'transparent',
                            alignItems: 'center',
                        }}
                    >
                        <Text
                            style={[
                                Typography.captionMedium,
                                { color: period === p.key ? '#FFFFFF' : colors.textSecondary },
                            ]}
                        >
                            {p.label}
                        </Text>
                    </Pressable>
                ))}
            </View>

            {/* Total */}
            <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: Spacing.xs, marginBottom: Spacing.md }}>
                <Text style={[Typography.numberLarge, { color: colors.text }]}>{total.toFixed(1)}</Text>
                <Text style={[Typography.bodySmall, { color: colors.textSecondary }]}>{unit}</Text>
            </View>

            {/* Chart bars */}
            <View style={{ flexDirection: 'row', alignItems: 'flex-end', height: 120, gap: Spacing.xs }}>
                {data.map((point, index) => {
                    const barHeight = Math.max(4, (point.value / maxValue) * 100);
                    return (
                        <View key={index} style={{ flex: 1, alignItems: 'center' }}>
                            <Text style={[Typography.caption, { color: colors.textTertiary, marginBottom: Spacing.xxs, fontSize: 9 }]}>
                                {point.value.toFixed(1)}
                            </Text>
                            <View
                                style={{
                                    width: '70%',
                                    height: barHeight,
                                    borderRadius: BorderRadius.xs,
                                    backgroundColor: colors.chartBar1,
                                    opacity: 0.5 + (point.value / maxValue) * 0.5,
                                }}
                            />
                            <Text style={[Typography.caption, { color: colors.chartLabel, marginTop: Spacing.xs, fontSize: 10 }]}>
                                {point.label}
                            </Text>
                        </View>
                    );
                })}
            </View>
        </Card>
    );
}
