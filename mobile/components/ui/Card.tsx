import React from 'react';
import { View, StyleSheet, Pressable, ViewStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Shadow, Spacing } from '@/constants/theme';

interface CardProps {
    children: React.ReactNode;
    style?: ViewStyle;
    onPress?: () => void;
    variant?: 'default' | 'outlined' | 'ai';
    padding?: keyof typeof Spacing;
}

export function Card({ children, style, onPress, variant = 'default', padding = 'md' }: CardProps) {
    const { colors, isDark } = useTheme();

    const cardStyle: ViewStyle = {
        backgroundColor: variant === 'ai' ? colors.aiBackground : colors.card,
        borderRadius: BorderRadius.lg,
        padding: Spacing[padding],
        borderWidth: variant === 'outlined' || variant === 'ai' ? 1 : 0,
        borderColor: variant === 'ai' ? colors.aiBorder : colors.border,
        shadowColor: colors.shadow,
        ...(isDark ? {} : Shadow.sm),
    };

    if (onPress) {
        return (
            <Pressable
                onPress={onPress}
                style={({ pressed }) => [
                    cardStyle,
                    pressed && { opacity: 0.85, backgroundColor: colors.cardHover },
                    style,
                ]}
            >
                {children}
            </Pressable>
        );
    }

    return <View style={[cardStyle, style]}>{children}</View>;
}
