import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

interface QuickActionProps {
    icon: keyof typeof Feather.glyphMap;
    label: string;
    onPress: () => void;
    active?: boolean;
}

export function QuickAction({ icon, label, onPress, active = false }: QuickActionProps) {
    const { colors } = useTheme();

    return (
        <Pressable
            onPress={onPress}
            style={({ pressed }) => ({
                alignItems: 'center',
                justifyContent: 'center',
                padding: Spacing.md,
                borderRadius: BorderRadius.lg,
                backgroundColor: active ? colors.primaryLight : colors.card,
                borderWidth: 1,
                borderColor: active ? colors.primary + '40' : colors.border,
                flex: 1,
                opacity: pressed ? 0.8 : 1,
            })}
        >
            <View
                style={{
                    width: 44,
                    height: 44,
                    borderRadius: 22,
                    backgroundColor: active ? colors.primary + '20' : colors.surface,
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: Spacing.sm,
                }}
            >
                <Feather name={icon} size={20} color={active ? colors.primary : colors.icon} />
            </View>
            <Text
                style={[Typography.caption, { color: active ? colors.primary : colors.textSecondary, textAlign: 'center' }]}
                numberOfLines={2}
            >
                {label}
            </Text>
        </Pressable>
    );
}
