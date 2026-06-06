import React, { useEffect, useRef, useState } from 'react';
import {
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
import {
    assistantAPI,
    AssistantChatResponse,
    homesAPI,
} from '@/services/api';

const quickCommands = [
    'Tat den phong ngu',
    'Bat quat phong khach',
    'Nhiet do phong khach bao nhieu',
    'Co mua chua',
    'Khoa cua chinh',
    'Tat tat ca thiet bi',
];

function createTimestamp() {
    return new Date().toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
    });
}

function describeCommand(command?: string | null) {
    switch (command) {
        case 'turn_on':
            return 'bat';
        case 'turn_off':
            return 'tat';
        case 'open':
            return 'mo';
        case 'close':
            return 'dong';
        case 'lock':
            return 'khoa';
        case 'unlock':
            return 'mo khoa';
        default:
            return command || 'thuc thi';
    }
}

function buildStatusText(response: AssistantChatResponse) {
    const execution = response.execution;
    const groundedDevice = typeof response.grounding?.device?.name === 'string'
        ? response.grounding.device.name
        : null;
    const fallbackDevice = typeof response.action_draft?.device_name === 'string'
        ? response.action_draft.device_name
        : null;
    const deviceLabel = groundedDevice || fallbackDevice;

    if (execution.status === 'executed') {
        const actionLabel = describeCommand(execution.command);
        return deviceLabel ? `Da thuc thi: ${actionLabel} ${deviceLabel}` : 'Da gui lenh thanh cong';
    }

    if (execution.status === 'failed') {
        return `Khong thuc thi duoc: ${execution.reason || 'Loi khong xac dinh'}`;
    }

    return `Chua thuc thi: ${execution.reason || 'Can lam ro them yeu cau'}`;
}

function buildAssistantReply(response: AssistantChatResponse) {
    const reply = response.reply_text?.trim() || '';
    const followUp = response.follow_up_question?.trim() || '';
    if (reply && followUp && !reply.includes(followUp)) {
        return `${reply}\n\n${followUp}`;
    }
    return reply || followUp || 'Tro ly da nhan yeu cau.';
}

const initialMessages: ChatMessage[] = [
    {
        id: 'welcome',
        text: 'Xin chao! Toi co the giup gi cho ban?',
        isUser: false,
        timestamp: createTimestamp(),
    },
];

export default function AssistantScreen() {
    const { colors } = useTheme();
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [input, setInput] = useState('');
    const [activeHomeId, setActiveHomeId] = useState<string | null>(null);
    const [homeLoadError, setHomeLoadError] = useState<string | null>(null);
    const [isSending, setIsSending] = useState(false);
    const flatListRef = useRef<FlatList>(null);

    useEffect(() => {
        let isMounted = true;

        const loadHomes = async () => {
            try {
                const homes = await homesAPI.list();
                if (!isMounted) return;
                setActiveHomeId(homes[0]?.id ?? null);
                if (!homes.length) {
                    setHomeLoadError('Chua co nha nao duoc lien ket voi tai khoan nay');
                }
            } catch (error) {
                if (!isMounted) return;
                const message = error instanceof Error ? error.message : 'Khong tai duoc danh sach nha';
                setHomeLoadError(message);
            }
        };

        void loadHomes();

        return () => {
            isMounted = false;
        };
    }, []);

    const replaceMessage = (messageId: string, nextMessage: ChatMessage) => {
        setMessages((prev) => prev.map((item) => (item.id === messageId ? nextMessage : item)));
    };

    const sendMessage = async (rawText: string) => {
        const text = rawText.trim();
        if (!text || isSending) return;

        const userMessage: ChatMessage = {
            id: `u-${Date.now()}`,
            text,
            isUser: true,
            timestamp: createTimestamp(),
        };
        const pendingId = `a-${Date.now()}`;
        const pendingMessage: ChatMessage = {
            id: pendingId,
            text: 'Dang xu ly yeu cau...',
            isUser: false,
            timestamp: createTimestamp(),
            statusTag: 'thinking',
            statusText: 'Dang goi AI assistant',
        };

        setMessages((prev) => [...prev, userMessage, pendingMessage]);
        setInput('');
        setIsSending(true);

        try {
            const response = await assistantAPI.chat(text, activeHomeId ?? undefined, true);
            replaceMessage(pendingId, {
                id: pendingId,
                text: buildAssistantReply(response),
                isUser: false,
                timestamp: createTimestamp(),
                statusTag: response.execution.status,
                statusText: buildStatusText(response),
            });
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Khong gui duoc yeu cau den tro ly';
            replaceMessage(pendingId, {
                id: pendingId,
                text: 'Tro ly tam thoi khong san sang. Vui long thu lai sau.',
                isUser: false,
                timestamp: createTimestamp(),
                statusTag: 'failed',
                statusText: message,
            });
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
                    <View style={{ flex: 1 }}>
                        <Text style={[Typography.h3, { color: colors.text }]}>Tro ly AI</Text>
                        <Text
                            style={[
                                Typography.caption,
                                { color: homeLoadError ? colors.warning : colors.success },
                            ]}
                        >
                            {homeLoadError ? homeLoadError : 'Dang ket noi voi backend va AI server'}
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
                                onPress={() => void sendMessage(item)}
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
                                    opacity: isSending ? 0.7 : 1,
                                }}
                            >
                                <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                    {item}
                                </Text>
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
                            opacity: 0.7,
                        }}
                    >
                        <Feather name="mic" size={18} color={colors.primary} />
                    </Pressable>
                    <TextInput
                        value={input}
                        onChangeText={setInput}
                        placeholder="Nhap lenh..."
                        placeholderTextColor={colors.textTertiary}
                        editable={!isSending}
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
                        onSubmitEditing={() => void sendMessage(input)}
                        returnKeyType="send"
                    />
                    <Pressable
                        onPress={() => void sendMessage(input)}
                        disabled={isSending}
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 20,
                            backgroundColor: colors.primary,
                            alignItems: 'center',
                            justifyContent: 'center',
                            opacity: isSending ? 0.7 : 1,
                        }}
                    >
                        <Feather name="send" size={16} color="#FFFFFF" />
                    </Pressable>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
