import React, { useEffect, useRef } from 'react';
import { Pressable, View, Animated, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius } from '@/constants/theme';

interface ToggleProps {
    value: boolean;
    onToggle: (value: boolean) => void;
    disabled?: boolean;
    size?: 'sm' | 'md';
}

export function Toggle({ value, onToggle, disabled = false, size = 'md' }: ToggleProps) {
    const { colors } = useTheme();
    const animValue = useRef(new Animated.Value(value ? 1 : 0)).current;

    const dims = size === 'sm' ? { w: 44, h: 26, thumb: 20, margin: 3 } : { w: 52, h: 30, thumb: 24, margin: 3 };

    useEffect(() => {
        Animated.spring(animValue, {
            toValue: value ? 1 : 0,
            useNativeDriver: false,
            tension: 60,
            friction: 8,
        }).start();
    }, [value]);

    const translateX = animValue.interpolate({
        inputRange: [0, 1],
        outputRange: [dims.margin, dims.w - dims.thumb - dims.margin],
    });

    const bgColor = animValue.interpolate({
        inputRange: [0, 1],
        outputRange: [colors.border, colors.primary],
    });

    return (
        <Pressable
            onPress={() => !disabled && onToggle(!value)}
            style={{ opacity: disabled ? 0.4 : 1 }}
        >
            <Animated.View
                style={{
                    width: dims.w,
                    height: dims.h,
                    borderRadius: dims.h / 2,
                    backgroundColor: bgColor,
                    justifyContent: 'center',
                }}
            >
                <Animated.View
                    style={{
                        width: dims.thumb,
                        height: dims.thumb,
                        borderRadius: dims.thumb / 2,
                        backgroundColor: '#FFFFFF',
                        transform: [{ translateX }],
                        shadowColor: '#000',
                        shadowOffset: { width: 0, height: 2 },
                        shadowOpacity: 0.15,
                        shadowRadius: 3,
                        elevation: 3,
                    }}
                />
            </Animated.View>
        </Pressable>
    );
}
