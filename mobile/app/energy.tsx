import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { EnergyChart } from '@/components/EnergyChart';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { energyAPI, homesAPI, EnergySummaryResponse } from '@/services/api';

const EMPTY_ENERGY: EnergySummaryResponse = {
    total: 0,
    data: [],
    breakdown: [],
    comparison: 0,
};

export default function EnergyScreen() {
    const { colors } = useTheme();
    const [daily, setDaily] = useState<EnergySummaryResponse>(EMPTY_ENERGY);
    const [weekly, setWeekly] = useState<EnergySummaryResponse>(EMPTY_ENERGY);
    const [monthly, setMonthly] = useState<EnergySummaryResponse>(EMPTY_ENERGY);

    useEffect(() => {
        loadEnergy();
    }, []);

    const loadEnergy = async () => {
        try {
            const homes = await homesAPI.list();
            if (!homes.length) return;

            const homeId = homes[0].id;
            const [dailyRes, weeklyRes, monthlyRes] = await Promise.all([
                energyAPI.daily(homeId),
                energyAPI.weekly(homeId),
                energyAPI.monthly(homeId),
            ]);

            setDaily(dailyRes);
            setWeekly(weeklyRes);
            setMonthly(monthlyRes);
        } catch (error) {
            console.error('Failed to load energy data:', error);
        }
    };

    const todayTotal = daily.total || 0;
    const comparisonPct = daily.comparison || 0;
    const yesterdayTotal = comparisonPct !== -100 ? todayTotal / (1 + comparisonPct / 100) : 0;
    const isEnergyUp = comparisonPct > 0;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Phân tích điện năng" showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {/* Summary */}
                <View style={{ flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md }}>
                    <Card style={{ flex: 1 }}>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Hôm nay</Text>
                        <Text style={[Typography.numberLarge, { color: colors.text, marginTop: Spacing.xs }]}>
                            {todayTotal.toFixed(1)}
                        </Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
                    </Card>
                    <Card style={{ flex: 1 }}>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Hôm qua</Text>
                        <Text style={[Typography.numberLarge, { color: colors.text, marginTop: Spacing.xs }]}>
                            {yesterdayTotal.toFixed(1)}
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
                            {isEnergyUp ? '+' : ''}{comparisonPct.toFixed(1)}%
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
                    <EnergyChart dailyData={daily.data} weeklyData={weekly.data} monthlyData={monthly.data} />
                </View>

                {/* Breakdown */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>
                    Theo thiết bị
                </Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {daily.breakdown.map((item, i) => {
                        const iconName = (item.device_type === 'ac'
                            ? 'wind'
                            : item.device_type === 'light'
                                ? 'sun'
                                : item.device_type === 'fan'
                                    ? 'wind'
                                    : item.device_type === 'sensor'
                                        ? 'activity'
                                        : 'cpu') as keyof typeof Feather.glyphMap;
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
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.device_name}</Text>
                                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.usage.toFixed(1)} kWh</Text>
                                        </View>
                                        {/* Progress bar */}
                                        <View style={{ height: 6, backgroundColor: colors.border, borderRadius: 3 }}>
                                            <View
                                                style={{
                                                    height: '100%', width: `${item.percentage}%`, backgroundColor: colors.primary,
                                                    borderRadius: 3, opacity: 0.5 + (item.percentage / 100) * 0.5,
                                                }}
                                            />
                                        </View>
                                    </View>
                                    <Text style={[Typography.captionMedium, { color: colors.textSecondary }]}>{item.percentage.toFixed(0)}%</Text>
                                </View>
                            </Card>
                        );
                    })}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
