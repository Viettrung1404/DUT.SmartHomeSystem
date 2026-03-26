import React from 'react';
import { View, Text, ViewStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';

interface BadgeProps {
    variant?: 'online' | 'offline' | 'count' | 'risk';
    count?: number;
    label?: string;
    riskLevel?: 'low' | 'medium' | 'high';
    size?: 'sm' | 'md';
    style?: ViewStyle;
}

export function Badge({ variant = 'online', count, label, riskLevel, size = 'sm', style }: BadgeProps) {
    const { colors } = useTheme();

    if (variant === 'online' || variant === 'offline') {
        const isOnline = variant === 'online';
        const dotSize = size === 'sm' ? 8 : 10;
        return (
            <View style={[{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs }, style]}>
                <View
                    style={{
                        width: dotSize,
                        height: dotSize,
                        borderRadius: dotSize / 2,
                        backgroundColor: isOnline ? colors.success : colors.textTertiary,
                    }}
                />
                {label !== undefined && (
                    <Text style={[Typography.caption, { color: isOnline ? colors.success : colors.textTertiary }]}>
                        {label ?? (isOnline ? 'Online' : 'Offline')}
                    </Text>
                )}
            </View>
        );
    }

    if (variant === 'count' && count !== undefined) {
        return (
            <View
                style={[
                    {
                        backgroundColor: colors.primary,
                        borderRadius: BorderRadius.full,
                        minWidth: 20,
                        height: 20,
                        alignItems: 'center',
                        justifyContent: 'center',
                        paddingHorizontal: Spacing.xs,
                    },
                    style,
                ]}
            >
                <Text style={[Typography.label, { color: '#FFFFFF' }]}>{count}</Text>
            </View>
        );
    }

    if (variant === 'risk' && riskLevel) {
        const riskColors = { low: colors.riskLow, medium: colors.riskMedium, high: colors.riskHigh };
        const riskLabels = { low: 'Thấp', medium: 'Trung bình', high: 'Cao' };
        return (
            <View
                style={[
                    {
                        backgroundColor: riskColors[riskLevel] + '20',
                        borderRadius: BorderRadius.sm,
                        paddingHorizontal: Spacing.sm,
                        paddingVertical: Spacing.xxs,
                        flexDirection: 'row',
                        alignItems: 'center',
                        gap: Spacing.xs,
                    },
                    style,
                ]}
            >
                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: riskColors[riskLevel] }} />
                <Text style={[Typography.captionMedium, { color: riskColors[riskLevel] }]}>{riskLabels[riskLevel]}</Text>
            </View>
        );
    }

    return null;
}
