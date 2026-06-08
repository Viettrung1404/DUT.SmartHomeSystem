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
import { useVoice } from '@/hooks/useVoice';

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

    const handleTranscriptReceived = (text: string) => {
        const cleaned = text.trim();
        if (cleaned.length < 2) {
            // Transcript quá ngắn hoặc rỗng, quay lại idle không gửi API
            return;
        }
        sendMessage(cleaned, true);
    };

    const {
        state: voiceState,
        setState: setVoiceState,
        partialTranscript,
        error: voiceError,
        clearError: clearVoiceError,
        startListening,
        stopListening,
        speak,
        stopSpeaking,
    } = useVoice({
        onTranscriptReceived: handleTranscriptReceived,
        locale: 'vi-VN',
    });

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

    // Stop speaking (TTS) on screen unmount
    useEffect(() => {
        return () => {
            stopSpeaking();
        };
    }, [stopSpeaking]);

    const appendAssistantMessage = (text: string) => {
        const aiMsg: ChatMessage = {
            id: `a${Date.now()}`,
            text,
            isUser: false,
            timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, aiMsg]);
    };

    const sendMessage = async (text: string, fromVoice = false) => {
        const trimmed = text.trim();
        if (!trimmed || isSending) return;

        // Dừng âm thanh trả lời cũ (nếu có)
        await stopSpeaking();

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
            if (fromVoice) {
                setVoiceState('thinking');
            }
            const response = await aiChatAPI.ask({
                home_id: homeId,
                message: trimmed,
                session_id: sessionId,
                timezone: 'Asia/Ho_Chi_Minh',
            });
            const citation = buildCitation(response);
            appendAssistantMessage(citation ? `${response.answer}\n\n${citation}` : response.answer);

            if (fromVoice) {
                await speak(response.answer);
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Không thể gọi trợ lý AI.';
            appendAssistantMessage(message);
            if (fromVoice) {
                setVoiceState('idle');
            }
        } finally {
            setIsSending(false);
            if (!fromVoice) {
                setVoiceState('idle');
            }
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

                {/* Voice Status Bar */}
                {(voiceState !== 'idle' || voiceError) && (
                    <View
                        style={{
                            flexDirection: 'row',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            paddingHorizontal: Spacing.md,
                            paddingVertical: 10,
                            backgroundColor: voiceError ? colors.errorLight : colors.surface,
                            borderTopWidth: 1,
                            borderTopColor: voiceError ? colors.error : colors.border,
                        }}
                    >
                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, flex: 1 }}>
                            {voiceError ? (
                                <Feather name="alert-circle" size={16} color={colors.error} />
                            ) : voiceState === 'listening' ? (
                                <ActivityIndicator size="small" color={colors.error} />
                            ) : voiceState === 'speaking' ? (
                                <Feather name="volume-2" size={16} color={colors.success} />
                            ) : (
                                <ActivityIndicator size="small" color={colors.primary} />
                            )}

                            <Text
                                style={[
                                    Typography.caption,
                                    {
                                        color: voiceError
                                            ? colors.error
                                            : voiceState === 'listening'
                                            ? colors.error
                                            : voiceState === 'speaking'
                                            ? colors.success
                                            : colors.textSecondary,
                                        flex: 1,
                                    },
                                ]}
                                numberOfLines={1}
                            >
                                {voiceError
                                    ? voiceError
                                    : voiceState === 'listening'
                                    ? `Đang nghe: "${partialTranscript || 'Đang chờ...'}"`
                                    : voiceState === 'transcribing'
                                    ? 'Đang xử lý giọng nói...'
                                    : voiceState === 'thinking'
                                    ? 'Trợ lý đang suy nghĩ...'
                                    : 'Trợ lý đang trả lời bằng giọng nói...'}
                            </Text>
                        </View>
                        <Pressable
                            onPress={async () => {
                                if (voiceError) {
                                    clearVoiceError();
                                } else if (voiceState === 'listening' || voiceState === 'transcribing') {
                                    await stopListening();
                                    setVoiceState('idle');
                                } else if (voiceState === 'speaking') {
                                    await stopSpeaking();
                                }
                            }}
                            style={{
                                padding: Spacing.xs,
                                borderRadius: BorderRadius.sm,
                                backgroundColor: colors.borderLight,
                            }}
                        >
                            <Feather name="x" size={16} color={colors.textSecondary} />
                        </Pressable>
                    </View>
                )}

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
                        onPress={async () => {
                            if (voiceState === 'listening') {
                                await stopListening();
                            } else if (voiceState === 'speaking') {
                                await stopSpeaking();
                                await startListening();
                            } else {
                                await startListening();
                            }
                        }}
                        disabled={voiceState === 'transcribing' || voiceState === 'thinking'}
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: voiceState === 'listening' ? colors.error : colors.surface,
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderWidth: 1,
                            borderColor: voiceState === 'listening' ? colors.error : colors.border,
                            opacity: (voiceState === 'transcribing' || voiceState === 'thinking') ? 0.6 : 1,
                        }}
                    >
                        <Feather
                            name={voiceState === 'listening' ? "mic-off" : "mic"}
                            size={18}
                            color={voiceState === 'listening' ? "#FFFFFF" : colors.primary}
                        />
                    </Pressable>
                    <TextInput
                        value={input}
                        onChangeText={(t) => {
                            setInput(t);
                            if (voiceError) {
                                clearVoiceError();
                            }
                        }}
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
