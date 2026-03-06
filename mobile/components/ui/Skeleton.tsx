import React, { useEffect, useRef } from 'react';
import { View, Animated, ViewStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius } from '@/constants/theme';

interface SkeletonProps {
    width: number | string;
    height: number;
    borderRadius?: number;
    style?: ViewStyle;
}

export function Skeleton({ width, height, borderRadius = BorderRadius.md, style }: SkeletonProps) {
    const { colors } = useTheme();
    const shimmer = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        const animation = Animated.loop(
            Animated.sequence([
                Animated.timing(shimmer, { toValue: 1, duration: 1000, useNativeDriver: true }),
                Animated.timing(shimmer, { toValue: 0, duration: 1000, useNativeDriver: true }),
            ]),
        );
        animation.start();
        return () => animation.stop();
    }, []);

    const opacity = shimmer.interpolate({
        inputRange: [0, 1],
        outputRange: [0.3, 0.7],
    });

    return (
        <Animated.View
            style={[
                {
                    width: width as any,
                    height,
                    borderRadius,
                    backgroundColor: colors.border,
                    opacity,
                },
                style,
            ]}
        />
    );
}

export function SkeletonCard({ style }: { style?: ViewStyle }) {
    const { colors } = useTheme();
    return (
        <View
            style={[
                {
                    backgroundColor: colors.card,
                    borderRadius: BorderRadius.lg,
                    padding: 16,
                    gap: 12,
                },
                style,
            ]}
        >
            <Skeleton width="60%" height={16} />
            <Skeleton width="100%" height={12} />
            <Skeleton width="40%" height={12} />
        </View>
    );
}
