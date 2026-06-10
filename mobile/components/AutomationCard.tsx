import React from 'react';
import { Pressable, View, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Toggle } from './ui/Toggle';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export interface AutomationCardModel {
    id: string;
    name: string;
    isEnabled: boolean;
    conditionSummary: string;
    actionSummary: string;
    icon?: string;
    lastRun?: string;
}

interface AutomationCardProps {
    automation: AutomationCardModel;
    onToggle: (id: string, value: boolean) => void;
    onDelete?: (automation: AutomationCardModel) => void;
    deleting?: boolean;
}

export function AutomationCard({ automation, onToggle, onDelete, deleting = false }: AutomationCardProps) {
    const { colors } = useTheme();
    const iconName = (automation.icon || 'zap') as keyof typeof Feather.glyphMap;

    return (
        <Card style={{ opacity: automation.isEnabled ? 1 : 0.6 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                <View
                    style={{
                        width: 44,
                        height: 44,
                        borderRadius: 12,
                        backgroundColor: automation.isEnabled ? colors.primaryLight : colors.surface,
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Feather
                        name={iconName}
                        size={20}
                        color={automation.isEnabled ? colors.primary : colors.iconMuted}
                    />
                </View>

                <View style={{ flex: 1 }}>
                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{automation.name}</Text>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs, marginTop: Spacing.xxs }}>
                        <Text style={[Typography.caption, { color: colors.primary }]}>NẾU</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>{automation.conditionSummary}</Text>
                    </View>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs, marginTop: 1 }}>
                        <Text style={[Typography.caption, { color: colors.warning }]}>THÌ</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]} numberOfLines={1}>
                            {automation.actionSummary}
                        </Text>
                    </View>
                    {automation.lastRun && (
                        <Text style={[Typography.caption, { color: colors.textTertiary, marginTop: Spacing.xxs }]}>
                            Lần cuối: {automation.lastRun}
                        </Text>
                    )}
                </View>

                <View style={{ alignItems: 'center', gap: Spacing.sm }}>
                    <Pressable
                        onPress={() => onDelete?.(automation)}
                        disabled={deleting}
                        hitSlop={8}
                        style={({ pressed }) => ({
                            width: 36,
                            height: 36,
                            borderRadius: 18,
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: colors.errorLight,
                            borderWidth: 1,
                            borderColor: colors.error,
                            opacity: deleting ? 0.5 : 1,
                            transform: [{ scale: pressed ? 0.96 : 1 }],
                        })}
                    >
                        <Feather name="trash-2" size={18} color={colors.error} />
                    </Pressable>

                    <Toggle
                        value={automation.isEnabled}
                        onToggle={(val) => onToggle(automation.id, val)}
                        size="sm"
                    />
                </View>
            </View>
        </Card>
    );
}
