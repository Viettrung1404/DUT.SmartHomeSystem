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
    onConfigure?: () => void;
}

export function QuickAction({ icon, label, onPress, active = false, onConfigure }: QuickActionProps) {
    const { colors } = useTheme();

    return (
        <View style={{ flex: 1 }}>
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
            {onConfigure && (
                <Pressable
                    onPress={onConfigure}
                    hitSlop={8}
                    style={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        width: 26,
                        height: 26,
                        borderRadius: 13,
                        backgroundColor: colors.surface,
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderWidth: 1,
                        borderColor: colors.border,
                    }}
                >
                    <Feather name="settings" size={14} color={colors.iconMuted} />
                </Pressable>
            )}
        </View>
    );
}
