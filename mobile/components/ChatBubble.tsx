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
}

interface ChatBubbleProps {
    message: ChatMessage;
}

export function ChatBubble({ message }: ChatBubbleProps) {
    const { colors } = useTheme();

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
