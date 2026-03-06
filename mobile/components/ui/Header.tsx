import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

interface HeaderProps {
    title: string;
    subtitle?: string;
    showBack?: boolean;
    rightIcon?: keyof typeof Feather.glyphMap;
    onRightPress?: () => void;
}

export function Header({ title, subtitle, showBack = false, rightIcon, onRightPress }: HeaderProps) {
    const { colors } = useTheme();
    const router = useRouter();

    return (
        <View
            style={{
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingHorizontal: Spacing.md,
                paddingTop: Spacing.sm,
                paddingBottom: Spacing.md,
            }}
        >
            <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                {showBack && (
                    <Pressable
                        onPress={() => router.back()}
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: colors.surface,
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginRight: Spacing.sm,
                        }}
                    >
                        <Feather name="chevron-left" size={22} color={colors.text} />
                    </Pressable>
                )}
                <View style={{ flex: 1 }}>
                    <Text style={[Typography.h2, { color: colors.text }]} numberOfLines={1}>{title}</Text>
                    {subtitle && (
                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: 2 }]}>{subtitle}</Text>
                    )}
                </View>
            </View>
            {rightIcon && onRightPress && (
                <Pressable
                    onPress={onRightPress}
                    style={{
                        width: 40,
                        height: 40,
                        borderRadius: 20,
                        backgroundColor: colors.surface,
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Feather name={rightIcon} size={20} color={colors.text} />
                </Pressable>
            )}
        </View>
    );
}
