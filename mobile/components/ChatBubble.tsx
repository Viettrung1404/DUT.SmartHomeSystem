import React from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';

export interface ChatMessage {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: string;
    statusTag?: 'executed' | 'skipped' | 'failed' | 'thinking';
    statusText?: string;
}

interface ChatBubbleProps {
    message: ChatMessage;
}

export function ChatBubble({ message }: ChatBubbleProps) {
    const { colors } = useTheme();
    const statusColor = (() => {
        switch (message.statusTag) {
            case 'executed':
                return colors.success;
            case 'failed':
                return colors.error;
            case 'thinking':
                return colors.primary;
            default:
                return colors.textTertiary;
        }
    })();

    return (
        <View
            style={{
                alignSelf: message.isUser ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                marginBottom: Spacing.sm,
            }}
        >
            <View
                style={{
                    backgroundColor: message.isUser ? colors.primary : colors.card,
                    borderRadius: BorderRadius.lg,
                    borderTopRightRadius: message.isUser ? BorderRadius.xs : BorderRadius.lg,
                    borderTopLeftRadius: message.isUser ? BorderRadius.lg : BorderRadius.xs,
                    padding: Spacing.md,
                    borderWidth: message.isUser ? 0 : 1,
                    borderColor: colors.border,
                }}
            >
                <Text
                    style={[
                        Typography.body,
                        { color: message.isUser ? '#FFFFFF' : colors.text },
                    ]}
                >
                    {message.text}
                </Text>
                {message.statusText ? (
                    <Text
                        style={[
                            Typography.caption,
                            {
                                color: message.isUser ? 'rgba(255,255,255,0.82)' : statusColor,
                                marginTop: Spacing.xs,
                            },
                        ]}
                    >
                        {message.statusText}
                    </Text>
                ) : null}
            </View>
            <Text
                style={[
                    Typography.caption,
                    {
                        color: colors.textTertiary,
                        marginTop: Spacing.xxs,
                        alignSelf: message.isUser ? 'flex-end' : 'flex-start',
                    },
                ]}
            >
                {message.timestamp}
            </Text>
        </View>
    );
}
