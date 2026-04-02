import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, useWindowDimensions } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export interface AIInsight {
    id: string;
    message: string;
    type: 'warning' | 'info' | 'suggestion';
    icon?: string;
}

interface AIInsightCardProps {
    insight: AIInsight;
    onAccept: (id: string) => void;
    onDismiss: (id: string) => void;
}

export function AIInsightCard({ insight, onAccept, onDismiss }: AIInsightCardProps) {
    const { colors } = useTheme();
    const { width } = useWindowDimensions();
    const scale = Math.min(1.2, Math.max(0.85, width / 375));
    const shrink = 0.5;
    const scaled = (value: number) => Math.round(value * scale * shrink);
    const scaledFont = (value: number | undefined) => (typeof value === 'number' ? value * scale * shrink : value);
    const cardWidth = Math.min(Math.round(width * 0.82 * shrink), Math.round(360 * scale * shrink));
    const glowAnim = useRef(new Animated.Value(0.4)).current;

    // Pulse glow effect
    useEffect(() => {
        const animation = Animated.loop(
            Animated.sequence([
                Animated.timing(glowAnim, { toValue: 1, duration: 2000, useNativeDriver: true }),
                Animated.timing(glowAnim, { toValue: 0.4, duration: 2000, useNativeDriver: true }),
            ]),
        );
        animation.start();
        return () => animation.stop();
    }, []);

    const iconName = (insight.icon || 'info') as keyof typeof Feather.glyphMap;
    const typeIcon = insight.type === 'warning' ? 'alert-triangle' : insight.type === 'suggestion' ? 'zap' : 'info';

    return (
        <Card variant="ai" style={{ width: cardWidth, marginRight: scaled(Spacing.md) }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: scaled(Spacing.sm), marginBottom: scaled(Spacing.sm) }}>
                <Animated.View
                    style={{
                        width: scaled(32),
                        height: scaled(32),
                        borderRadius: scaled(16),
                        backgroundColor: colors.primary + '20',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: glowAnim,
                    }}
                >
                    <Feather name={typeIcon as any} size={scaled(16)} color={colors.primary} />
                </Animated.View>
                <Text
                    style={[
                        Typography.captionMedium,
                        { color: colors.primary, fontSize: scaledFont(Typography.captionMedium.fontSize) },
                    ]}
                >
                    Trợ lý AI
                </Text>
            </View>

            <Text
                style={[
                    Typography.body,
                    { color: colors.text, marginBottom: scaled(Spacing.md), fontSize: scaledFont(Typography.body.fontSize) },
                ]}
            >
                {insight.message}
            </Text>

            <View style={{ flexDirection: 'row', gap: scaled(Spacing.sm) }}>
                <Button
                    title="Đồng ý"
                    onPress={() => onAccept(insight.id)}
                    variant="primary"
                    size="sm"
                    style={{ flex: 1 }}
                />
                <Button
                    title="Bỏ qua"
                    onPress={() => onDismiss(insight.id)}
                    variant="ghost"
                    size="sm"
                    style={{ flex: 1 }}
                />
            </View>
        </Card>
    );
}
