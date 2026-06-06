import React from 'react';
import { View, Text, ScrollView, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme, ThemeMode } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

interface MenuItem {
    label: string;
    icon: keyof typeof Feather.glyphMap;
    description: string;
    route: string;
}

export default function SettingsScreen() {
    const { colors, mode, setMode } = useTheme();
    const { logout } = useAuth();
    const router = useRouter();

    const themeOptions: { key: ThemeMode; label: string; icon: keyof typeof Feather.glyphMap }[] = [
        { key: 'light', label: 'Sáng', icon: 'sun' },
        { key: 'dark', label: 'Tối', icon: 'moon' },
        { key: 'system', label: 'Hệ thống', icon: 'smartphone' },
    ];

    const menuItems: MenuItem[] = [
        {
            label: 'Thông tin nhà',
            icon: 'home',
            description: 'Tổng quan nhà, phòng và thiết bị',
            route: '/settings/home',
        },
        {
            label: 'Tài khoản',
            icon: 'user',
            description: 'Hồ sơ và trạng thái đăng nhập',
            route: '/settings/account',
        },
        {
            label: 'Thông báo',
            icon: 'bell',
            description: 'Mở Suggestions để xem gợi ý mới',
            route: '/suggestions',
        },
        {
            label: 'Kết nối',
            icon: 'wifi',
            description: 'API, phiên đăng nhập và thống kê đồng bộ',
            route: '/settings/connectivity',
        },
        {
            label: 'Bảo mật',
            icon: 'shield',
            description: 'Mở trung tâm an ninh và sự kiện gần đây',
            route: '/security',
        },
        {
            label: 'Giới thiệu',
            icon: 'info',
            description: 'Thông tin phiên bản và runtime',
            route: '/settings/about',
        },
    ];

    const handleLogout = () => {
        Alert.alert('Đăng xuất', 'Bạn có muốn đăng xuất khỏi ứng dụng không?', [
            { text: 'Ở lại', style: 'cancel' },
            {
                text: 'Đăng xuất',
                style: 'destructive',
                onPress: () => {
                    logout();
                    router.replace('/auth/login');
                },
            },
        ]);
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Cài đặt" showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md }} showsVerticalScrollIndicator={false}>
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
                                <Feather name={opt.icon} size={20} color={mode === opt.key ? colors.primary : colors.icon} />
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

                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Cài đặt chung</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {menuItems.map((item) => (
                        <Card key={item.label} onPress={() => router.push(item.route as never)}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <View
                                    style={{
                                        width: 40,
                                        height: 40,
                                        borderRadius: 12,
                                        backgroundColor: colors.primaryLight,
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <Feather name={item.icon} size={18} color={colors.primary} />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.label}</Text>
                                    <Text style={[Typography.caption, { color: colors.textSecondary }]}>{item.description}</Text>
                                </View>
                                <Feather name="chevron-right" size={18} color={colors.textTertiary} />
                            </View>
                        </Card>
                    ))}
                </View>

                <Card onPress={handleLogout}>
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
