import React from 'react';
import { Pressable, Text, ActivityIndicator, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';

interface ButtonProps {
    title: string;
    onPress: () => void;
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    style?: ViewStyle;
}

export function Button({
    title,
    onPress,
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    icon,
    style,
}: ButtonProps) {
    const { colors } = useTheme();

    const heights = { sm: 36, md: 48, lg: 56 };
    const paddings = { sm: Spacing.sm, md: Spacing.md, lg: Spacing.lg };

    const bgColors: Record<string, string> = {
        primary: colors.primary,
        secondary: colors.secondary,
        ghost: 'transparent',
        danger: colors.error,
        outline: 'transparent',
    };

    const textColors: Record<string, string> = {
        primary: '#FFFFFF',
        secondary: '#FFFFFF',
        ghost: colors.primary,
        danger: '#FFFFFF',
        outline: colors.primary,
    };

    const buttonStyle: ViewStyle = {
        height: heights[size],
        paddingHorizontal: paddings[size],
        backgroundColor: disabled ? colors.border : bgColors[variant],
        borderRadius: BorderRadius.md,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: Spacing.sm,
        borderWidth: variant === 'outline' ? 1.5 : 0,
        borderColor: variant === 'outline' ? colors.primary : undefined,
        opacity: disabled ? 0.5 : 1,
    };

    const textStyle: TextStyle = {
        ...Typography[size === 'sm' ? 'buttonSmall' : 'button'],
        color: disabled ? colors.textTertiary : textColors[variant],
    };

    return (
        <Pressable
            onPress={onPress}
            disabled={disabled || loading}
            style={({ pressed }) => [buttonStyle, pressed && { opacity: 0.8 }, style]}
        >
            {loading ? (
                <ActivityIndicator size="small" color={textColors[variant]} />
            ) : (
                <>
                    {icon}
                    <Text style={textStyle}>{title}</Text>
                </>
            )}
        </Pressable>
    );
}
