import React, { useRef, useEffect } from 'react';
import { View, Text, Animated, PanResponder, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';

interface SliderProps {
    value: number; // 0-100
    onValueChange: (value: number) => void;
    label?: string;
    unit?: string;
    min?: number;
    max?: number;
    step?: number;
    disabled?: boolean;
}

export function Slider({
    value,
    onValueChange,
    label,
    unit = '%',
    min = 0,
    max = 100,
    step = 1,
    disabled = false,
}: SliderProps) {
    const { colors } = useTheme();
    const sliderWidth = useRef(0);
    const animValue = useRef(new Animated.Value(0)).current;

    const normalizedValue = ((value - min) / (max - min)) * 100;

    useEffect(() => {
        Animated.timing(animValue, {
            toValue: normalizedValue,
            duration: 150,
            useNativeDriver: false,
        }).start();
    }, [normalizedValue]);

    const panResponder = useRef(
        PanResponder.create({
            onStartShouldSetPanResponder: () => !disabled,
            onMoveShouldSetPanResponder: () => !disabled,
            onPanResponderMove: (_, gestureState) => {
                if (sliderWidth.current === 0) return;
                const pct = Math.max(0, Math.min(100, (gestureState.moveX - 40) / sliderWidth.current * 100));
                const newValue = Math.round((pct / 100) * (max - min) / step) * step + min;
                onValueChange(Math.max(min, Math.min(max, newValue)));
            },
        }),
    ).current;

    const widthPct = animValue.interpolate({
        inputRange: [0, 100],
        outputRange: ['0%', '100%'],
    });

    return (
        <View style={{ opacity: disabled ? 0.4 : 1 }}>
            {label && (
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: Spacing.sm }}>
                    <Text style={[Typography.bodySmall, { color: colors.textSecondary }]}>{label}</Text>
                    <Text style={[Typography.bodyMedium, { color: colors.primary }]}>
                        {value}{unit}
                    </Text>
                </View>
            )}
            <View
                style={{
                    height: 8,
                    backgroundColor: colors.border,
                    borderRadius: BorderRadius.full,
                    overflow: 'hidden',
                }}
                onLayout={(e) => { sliderWidth.current = e.nativeEvent.layout.width; }}
                {...panResponder.panHandlers}
            >
                <Animated.View
                    style={{
                        height: '100%',
                        width: widthPct,
                        backgroundColor: colors.primary,
                        borderRadius: BorderRadius.full,
                    }}
                />
            </View>
            <View
                style={{
                    height: 36,
                    marginTop: -22,
                }}
                {...panResponder.panHandlers}
            />
        </View>
    );
}
