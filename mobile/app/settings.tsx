import React from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme, ThemeMode } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export default function SettingsScreen() {
    const { colors, mode, setMode, isDark } = useTheme();

    const themeOptions: { key: ThemeMode; label: string; icon: keyof typeof Feather.glyphMap }[] = [
        { key: 'light', label: 'Sáng', icon: 'sun' },
        { key: 'dark', label: 'Tối', icon: 'moon' },
        { key: 'system', label: 'Hệ thống', icon: 'smartphone' },
    ];

    const menuItems = [
        { label: 'Thông tin nhà', icon: 'home', description: 'Quản lý nhà và phòng' },
        { label: 'Tài khoản', icon: 'user', description: 'Thông tin cá nhân' },
        { label: 'Thông báo', icon: 'bell', description: 'Cài đặt thông báo' },
        { label: 'Kết nối', icon: 'wifi', description: 'WiFi, MQTT, Gateway' },
        { label: 'Bảo mật', icon: 'shield', description: 'Mật khẩu và xác thực' },
        { label: 'Giới thiệu', icon: 'info', description: 'Phiên bản 1.0.0' },
    ];

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Cài đặt" showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
                {/* Theme Selector */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Giao diện</Text>
                <Card style={{ marginBottom: Spacing.lg }}>
                    <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                        {themeOptions.map((opt) => (
                            <Pressable
                                key={opt.key}
                                onPress={() => setMode(opt.key)}
                                style={{
                                    flex: 1,
                                    paddingVertical: Spacing.md,
                                    borderRadius: BorderRadius.md,
                                    backgroundColor: mode === opt.key ? colors.primaryLight : colors.surface,
                                    alignItems: 'center',
                                    borderWidth: 2,
                                    borderColor: mode === opt.key ? colors.primary : colors.border,
                                }}
                            >
                                <Feather
                                    name={opt.icon}
                                    size={20}
                                    color={mode === opt.key ? colors.primary : colors.icon}
                                />
                                <Text
                                    style={[
                                        Typography.captionMedium,
                                        { color: mode === opt.key ? colors.primary : colors.textSecondary, marginTop: Spacing.xs },
                                    ]}
                                >
                                    {opt.label}
                                </Text>
                            </Pressable>
                        ))}
                    </View>
                </Card>

                {/* Menu Items */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Cài đặt chung</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {menuItems.map((item, i) => {
                        const iconName = item.icon as keyof typeof Feather.glyphMap;
                        return (
                            <Card key={i} onPress={() => { }}>
                                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                    <View
                                        style={{
                                            width: 40, height: 40, borderRadius: 12,
                                            backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                                        }}
                                    >
                                        <Feather name={iconName} size={18} color={colors.primary} />
                                    </View>
                                    <View style={{ flex: 1 }}>
                                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.label}</Text>
                                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>{item.description}</Text>
                                    </View>
                                    <Feather name="chevron-right" size={18} color={colors.textTertiary} />
                                </View>
                            </Card>
                        );
                    })}
                </View>

                {/* Logout */}
                <Card onPress={() => { }}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: Spacing.sm }}>
                        <Feather name="log-out" size={18} color={colors.error} />
                        <Text style={[Typography.bodyMedium, { color: colors.error }]}>Đăng xuất</Text>
                    </View>
                </Card>
                <View style={{ height: Spacing.xl }} />
            </ScrollView>
        </SafeAreaView>
    );
}
