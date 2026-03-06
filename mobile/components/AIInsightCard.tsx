import React, { useEffect, useRef } from 'react';
import { View, Text, Animated } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { AIInsight } from '@/services/mockData';

interface AIInsightCardProps {
    insight: AIInsight;
    onAccept: (id: string) => void;
    onDismiss: (id: string) => void;
}

export function AIInsightCard({ insight, onAccept, onDismiss }: AIInsightCardProps) {
    const { colors } = useTheme();
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
        <Card variant="ai" style={{ width: 300, marginRight: Spacing.md }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.sm }}>
                <Animated.View
                    style={{
                        width: 32,
                        height: 32,
                        borderRadius: 16,
                        backgroundColor: colors.primary + '20',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: glowAnim,
                    }}
                >
                    <Feather name={typeIcon as any} size={16} color={colors.primary} />
                </Animated.View>
                <Text style={[Typography.captionMedium, { color: colors.primary }]}>Trợ lý AI</Text>
            </View>

            <Text style={[Typography.body, { color: colors.text, marginBottom: Spacing.md }]}>
                {insight.message}
            </Text>

            <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
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
