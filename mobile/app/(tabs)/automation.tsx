import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { AutomationCard, AutomationCardModel } from '@/components/AutomationCard';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { automationsAPI, homesAPI } from '@/services/api';

export default function AutomationScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [automations, setAutomations] = useState<AutomationCardModel[]>([]);

    useEffect(() => {
        loadAutomations();
    }, []);

    const loadAutomations = async () => {
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
                    conditionSummary: automation.conditions.map((c) => `${c.condition_type}: ${c.value}`).join(', ') || 'Không có điều kiện',
                    actionSummary: automation.actions.map((a) => `${a.action}${a.value ? ` (${a.value})` : ''}`).join(', ') || 'Không có hành động',
                    icon: 'zap',
                    lastRun: undefined,
                })),
            );
        } catch (error) {
            console.error('Failed to load automations:', error);
            setAutomations([]);
        }
    };

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

            {/* FAB */}
            <Pressable
                onPress={() => router.push('/automation/create')}
                style={{
                    position: 'absolute',
                    bottom: 24,
                    right: 24,
                    width: 56,
                    height: 56,
                    borderRadius: 28,
                    backgroundColor: colors.primary,
                    alignItems: 'center',
                    justifyContent: 'center',
                    shadowColor: colors.primary,
                    shadowOffset: { width: 0, height: 4 },
                    shadowOpacity: 0.4,
                    shadowRadius: 12,
                    elevation: 8,
                }}
            >
                <Feather name="plus" size={24} color="#FFFFFF" />
            </Pressable>
        </SafeAreaView>
    );
}
