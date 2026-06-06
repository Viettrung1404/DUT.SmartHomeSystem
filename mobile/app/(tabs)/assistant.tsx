import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    KeyboardAvoidingView,
    Platform,
    Pressable,
    Text,
    TextInput,
    View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';

import { ChatBubble, ChatMessage } from '@/components/ChatBubble';
import { BorderRadius, Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { useTheme } from '@/contexts/ThemeContext';
import { aiChatAPI, homesAPI } from '@/services/api';

const quickCommands = [
    'Tối qua nhà tôi có gì bất thường không?',
    'Tại sao app gợi ý tắt đèn bếp?',
    'Điều hòa phòng ngủ tuần này chạy nhiều không?',
    'Thiết bị nào hay bị quên tắt nhất?',
    'Thế tuần này thì sao?',
];

const initialMessages: ChatMessage[] = [
    {
        id: 'welcome',
        text: 'Xin chào! Bạn có thể hỏi về cảnh báo, gợi ý, lịch sử thiết bị hoặc thói quen trong nhà.',
        isUser: false,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    },
];

const toolLabels: Record<string, string> = {
    query_guardian_events: 'sự kiện an ninh',
    query_suggestion_logs: 'nhật ký gợi ý',
    query_user_patterns: 'mẫu thói quen',
    query_activity_logs: 'lịch sử thiết bị',
    query_device_status: 'trạng thái thiết bị',
};

function buildCitation(response: Awaited<ReturnType<typeof aiChatAPI.ask>>) {
    if (response.command_executed) {
        return 'Nguồn: lệnh đã thực thi qua Backend.';
    }

    const sourceLabels = Array.from(
        new Set((response.used_tools || []).map((tool) => toolLabels[tool] || tool)),
    );
    const evidenceCount = response.evidence?.length ?? 0;

    if (evidenceCount === 0) {
        return 'Nguồn: đã kiểm tra dữ liệu hệ thống, chưa có bằng chứng phù hợp.';
    }

    const sourceText = sourceLabels.length ? sourceLabels.join(', ') : 'dữ liệu hệ thống';
    return `Nguồn: ${sourceText} (${evidenceCount} bằng chứng).`;
}

export default function AssistantScreen() {
    const { colors } = useTheme();
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [input, setInput] = useState('');
    const [homeId, setHomeId] = useState<string | null>(null);
    const [isReady, setIsReady] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const flatListRef = useRef<FlatList>(null);
    const sessionId = useMemo(() => `mobile-ai-${Date.now()}`, []);

    useEffect(() => {
        let mounted = true;

        homesAPI.list()
            .then((homes) => {
                if (!mounted) return;
                setHomeId(homes[0]?.id ?? null);
            })
            .catch(() => {
                if (!mounted) return;
                setHomeId(null);
            })
            .finally(() => {
                if (!mounted) return;
                setIsReady(true);
            });

        return () => {
            mounted = false;
        };
    }, []);

    const appendAssistantMessage = (text: string) => {
        const aiMsg: ChatMessage = {
            id: `a${Date.now()}`,
            text,
            isUser: false,
            timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, aiMsg]);
    };

    const sendMessage = async (text: string) => {
        const trimmed = text.trim();
        if (!trimmed || isSending) return;

        const userMsg: ChatMessage = {
            id: `u${Date.now()}`,
            text: trimmed,
            isUser: true,
            timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');

        if (!homeId) {
            appendAssistantMessage('Chưa tìm thấy nhà để gửi câu hỏi. Vui lòng tạo hoặc chọn nhà trước.');
            return;
        }

        try {
            setIsSending(true);
            const response = await aiChatAPI.ask({
                home_id: homeId,
                message: trimmed,
                session_id: sessionId,
                timezone: 'Asia/Ho_Chi_Minh',
            });
            const citation = buildCitation(response);
            appendAssistantMessage(citation ? `${response.answer}\n\n${citation}` : response.answer);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Không thể gọi trợ lý AI.';
            appendAssistantMessage(message);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <View style={{ padding: Spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                    <View
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: colors.primaryLight,
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Feather name="cpu" size={20} color={colors.primary} />
                    </View>
                    <View>
                        <Text style={[Typography.h3, { color: colors.text }]}>Trợ lý AI</Text>
                        <Text style={[Typography.caption, { color: isReady && homeId ? colors.success : colors.textSecondary }]}>
                            {isReady && homeId ? 'Đang hoạt động' : 'Đang kết nối'}
                        </Text>
                    </View>
                </View>
            </View>

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={{ flex: 1 }}
                keyboardVerticalOffset={0}
            >
                <View style={{ flex: 1 }}>
                    <FlatList
                        ref={flatListRef}
                        data={messages}
                        keyExtractor={(item) => item.id}
                        contentContainerStyle={{ padding: Spacing.md, paddingBottom: Spacing.xl }}
                        renderItem={({ item }) => <ChatBubble message={item} />}
                        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                        showsVerticalScrollIndicator={false}
                    />
                </View>

                <View style={{ paddingVertical: Spacing.sm, backgroundColor: colors.background }}>
                    <FlatList
                        horizontal
                        showsHorizontalScrollIndicator={false}
                        data={quickCommands}
                        keyExtractor={(item) => item}
                        contentContainerStyle={{ paddingHorizontal: Spacing.md, gap: Spacing.sm }}
                        renderItem={({ item }) => (
                            <Pressable
                                onPress={() => sendMessage(item)}
                                disabled={isSending}
                                style={{
                                    backgroundColor: colors.card,
                                    borderRadius: BorderRadius.full,
                                    paddingHorizontal: Spacing.md,
                                    paddingVertical: 8,
                                    borderWidth: 1,
                                    borderColor: colors.border,
                                    justifyContent: 'center',
                                    height: 36,
                                    opacity: isSending ? 0.6 : 1,
                                }}
                            >
                                <Text style={[Typography.caption, { color: colors.textSecondary }]}>{item}</Text>
                            </Pressable>
                        )}
                    />
                </View>

                <View
                    style={{
                        flexDirection: 'row',
                        alignItems: 'center',
                        gap: Spacing.sm,
                        padding: Spacing.md,
                        borderTopWidth: 1,
                        borderTopColor: colors.border,
                        backgroundColor: colors.card,
                    }}
                >
                    <Pressable
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: colors.surface,
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderWidth: 1,
                            borderColor: colors.border,
                        }}
                    >
                        <Feather name="mic" size={18} color={colors.primary} />
                    </Pressable>
                    <TextInput
                        value={input}
                        onChangeText={setInput}
                        placeholder="Nhập câu hỏi..."
                        placeholderTextColor={colors.textTertiary}
                        style={[
                            Typography.body,
                            {
                                flex: 1,
                                backgroundColor: colors.surface,
                                borderRadius: BorderRadius.full,
                                paddingHorizontal: Spacing.md,
                                paddingVertical: Spacing.sm,
                                color: colors.text,
                                borderWidth: 1,
                                borderColor: colors.border,
                            },
                        ]}
                        onSubmitEditing={() => sendMessage(input)}
                        returnKeyType="send"
                    />
                    <Pressable
                        onPress={() => sendMessage(input)}
                        disabled={isSending}
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: isSending ? colors.textTertiary : colors.primary,
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        {isSending ? (
                            <ActivityIndicator size="small" color="#FFFFFF" />
                        ) : (
                            <Feather name="send" size={16} color="#FFFFFF" />
                        )}
                    </Pressable>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
