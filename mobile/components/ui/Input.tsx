import React from 'react';
import { View, TextInput, Text, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

interface InputProps {
    label?: string;
    placeholder?: string;
    value: string;
    onChangeText: (text: string) => void;
    error?: string;
    secureTextEntry?: boolean;
    icon?: keyof typeof Feather.glyphMap;
    style?: ViewStyle;
    keyboardType?: 'default' | 'email-address' | 'numeric';
    autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
}

export function Input({
    label,
    placeholder,
    value,
    onChangeText,
    error,
    secureTextEntry,
    icon,
    style,
    keyboardType = 'default',
    autoCapitalize = 'none',
}: InputProps) {
    const { colors } = useTheme();

    return (
        <View style={[{ marginBottom: Spacing.md }, style]}>
            {label && (
                <Text style={[Typography.captionMedium, { color: colors.textSecondary, marginBottom: Spacing.xs }]}>
                    {label}
                </Text>
            )}
            <View
                style={{
                    flexDirection: 'row',
                    alignItems: 'center',
                    backgroundColor: colors.surface,
                    borderRadius: BorderRadius.md,
                    borderWidth: 1.5,
                    borderColor: error ? colors.error : colors.border,
                    paddingHorizontal: Spacing.md,
                    height: 52,
                }}
            >
                {icon && <Feather name={icon} size={18} color={colors.iconMuted} style={{ marginRight: Spacing.sm }} />}
                <TextInput
                    value={value}
                    onChangeText={onChangeText}
                    placeholder={placeholder}
                    placeholderTextColor={colors.textTertiary}
                    secureTextEntry={secureTextEntry}
                    keyboardType={keyboardType}
                    autoCapitalize={autoCapitalize}
                    style={[
                        Typography.body,
                        {
                            flex: 1,
                            color: colors.text,
                            padding: 0,
                        },
                    ]}
                />
            </View>
            {error && (
                <Text style={[Typography.caption, { color: colors.error, marginTop: Spacing.xs }]}>{error}</Text>
            )}
        </View>
    );
}
