import React, { useCallback, useState } from 'react';
import { View, Text, FlatList } from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { AutomationCard, AutomationCardModel } from '@/components/AutomationCard';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { automationsAPI, homesAPI } from '@/services/api';

const weekdayLabels: Record<number, string> = {
    0: 'CN',
    1: 'T2',
    2: 'T3',
    3: 'T4',
    4: 'T5',
    5: 'T6',
    6: 'T7',
};

function formatCondition(condition: { condition_type: string; value: string }) {
    if (condition.condition_type !== 'weekday_time') {
        return `${condition.condition_type}: ${condition.value}`;
    }

    try {
        const payload = JSON.parse(condition.value) as { time?: string; days_of_week?: number[] };
        const days = (payload.days_of_week || [])
            .map((day) => weekdayLabels[day])
            .filter(Boolean)
            .join(', ');
        return `time: ${payload.time || '--:--'}${days ? ` (${days})` : ''}`;
    } catch {
        return `${condition.condition_type}: ${condition.value}`;
    }
}

export default function AutomationScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [automations, setAutomations] = useState<AutomationCardModel[]>([]);

    const loadAutomations = useCallback(async () => {
        try {
            const homes = await homesAPI.list();
            if (!homes.length) {
                setAutomations([]);
                return;
            }

            const homeId = homes[0].id;
            const response = await automationsAPI.list(homeId);

            setAutomations(
                response.map((automation) => ({
                    id: automation.id,
                    name: automation.name,
                    isEnabled: automation.enabled,
                    conditionSummary: automation.conditions.map(formatCondition).join(', ') || 'Không có điều kiện',
                    actionSummary: automation.actions.map((a) => `${a.action}${a.value ? ` (${a.value})` : ''}`).join(', ') || 'Không có hành động',
                    icon: 'zap',
                    lastRun: undefined,
                })),
            );
        } catch (error) {
            console.error('Failed to load automations:', error);
            setAutomations([]);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            void loadAutomations();
        }, [loadAutomations]),
    );

    const handleToggle = async (id: string, value: boolean) => {
        setAutomations((prev) =>
            prev.map((a) => (a.id === id ? { ...a, isEnabled: value } : a)),
        );

        try {
            await automationsAPI.update(id, { enabled: value });
        } catch (error) {
            console.error('Failed to update automation:', error);
            setAutomations((prev) =>
                prev.map((a) => (a.id === id ? { ...a, isEnabled: !value } : a)),
            );
        }
    };

    const activeCount = automations.filter((a) => a.isEnabled).length;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header
                title="Tự động hóa"
                subtitle={`${activeCount}/${automations.length} đang hoạt động`}
                rightIcon="plus"
                onRightPress={() => router.push('/automation/create')}
            />

            <FlatList
                data={automations}
                keyExtractor={(item) => item.id}
                contentContainerStyle={{ padding: Spacing.md, gap: Spacing.sm }}
                renderItem={({ item }) => (
                    <AutomationCard automation={item} onToggle={handleToggle} />
                )}
                showsVerticalScrollIndicator={false}
                ListEmptyComponent={
                    <View style={{ alignItems: 'center', paddingTop: Spacing.xxl }}>
                        <Feather name="zap-off" size={48} color={colors.textTertiary} />
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.md }]}>
                            Chưa có kịch bản tự động nào
                        </Text>
                    </View>
                }
            />
        </SafeAreaView>
    );
}
