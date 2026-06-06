import React, { useState, useRef } from 'react';
import { View, Text, FlatList, TextInput, Pressable, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { ChatBubble, ChatMessage } from '@/components/ChatBubble';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

const quickCommands = [
    'Tắt đèn phòng ngủ',
    'Bật máy lạnh 24°C',
    'Kích hoạt chế độ đi ngủ',
    'Mở rèm phòng khách',
    'Khóa tất cả cửa',
    'Tắt tất cả thiết bị',
];

const initialMessages: ChatMessage[] = [
    {
        id: 'welcome',
        text: 'Xin chào! Tôi có thể giúp gì cho bạn?',
        isUser: false,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    },
];

export default function AssistantScreen() {
    const { colors } = useTheme();
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [input, setInput] = useState('');
    const flatListRef = useRef<FlatList>(null);

    const sendMessage = (text: string) => {
        if (!text.trim()) return;
        const userMsg: ChatMessage = {
            id: `u${Date.now()}`,
            text: text.trim(),
            isUser: true,
            timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');

        // Simulate AI response
        setTimeout(() => {
            const aiMsg: ChatMessage = {
                id: `a${Date.now()}`,
                text: `Đã nhận lệnh: "${text.trim()}". Đang xử lý...`,
                isUser: false,
                timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, aiMsg]);
        }, 1000);
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            {/* Header */}
            <View style={{ padding: Spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                    <View
                        style={{
                            width: 40, height: 40, borderRadius: 20,
                            backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                        }}
                    >
                        <Feather name="cpu" size={20} color={colors.primary} />
                    </View>
                    <View>
                        <Text style={[Typography.h3, { color: colors.text }]}>Trợ lý AI</Text>
                        <Text style={[Typography.caption, { color: colors.success }]}>● Đang hoạt động</Text>
                    </View>
                </View>
            </View>

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={{ flex: 1 }}
                keyboardVerticalOffset={0}
            >
                {/* Messages */}
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

                {/* Quick Commands */}
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
                                style={{
                                    backgroundColor: colors.card,
                                    borderRadius: BorderRadius.full,
                                    paddingHorizontal: Spacing.md,
                                    paddingVertical: 8, // Cố định padding dọc
                                    borderWidth: 1,
                                    borderColor: colors.border,
                                    justifyContent: 'center', // Đảm bảo text luôn ở giữa
                                    height: 36, // Bạn có thể set cứng chiều cao ở đây
                                }}
                            >
                                <Text style={[Typography.caption, { color: colors.textSecondary }]}>{item}</Text>
                            </Pressable>
                        )}
                    />
                </View>

                {/* Input Bar */}
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
                            width: 40, height: 40, borderRadius: 20,
                            backgroundColor: colors.surface, alignItems: 'center', justifyContent: 'center',
                            borderWidth: 1, borderColor: colors.border,
                        }}
                    >
                        <Feather name="mic" size={18} color={colors.primary} />
                    </Pressable>
                    <TextInput
                        value={input}
                        onChangeText={setInput}
                        placeholder="Nhập lệnh..."
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
                        style={{
                            width: 40, height: 40, borderRadius: 20,
                            backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center',
                        }}
                    >
                        <Feather name="send" size={16} color="#FFFFFF" />
                    </Pressable>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
