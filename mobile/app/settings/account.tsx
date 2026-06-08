import React, { useCallback, useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { homesAPI } from '@/services/api';

interface AccountStats {
    homeCount: number;
    activeDevices: number;
}

export default function SettingsAccountScreen() {
    const { colors } = useTheme();
    const { user, refreshUser } = useAuth();
    const [stats, setStats] = useState<AccountStats>({ homeCount: 0, activeDevices: 0 });
    const [loading, setLoading] = useState(true);

    useFocusEffect(
        useCallback(() => {
            let isMounted = true;

            async function loadAccountData() {
                try {
                    setLoading(true);
                    await refreshUser();
                    const homes = await homesAPI.list();
                    if (!isMounted) return;
                    setStats({
                        homeCount: homes.length,
                        activeDevices: homes.reduce((sum, home) => sum + home.active_devices, 0),
                    });
                } catch (error) {
                    console.error('Failed to load account settings:', error);
                    if (isMounted) {
                        setStats({ homeCount: 0, activeDevices: 0 });
                    }
                } finally {
                    if (isMounted) {
                        setLoading(false);
                    }
                }
            }

            void loadAccountData();

            return () => {
                isMounted = false;
            };
        }, [refreshUser]),
    );

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Tài khoản" showBack />
            {loading ? (
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <ActivityIndicator size="large" color={colors.primary} />
                </View>
            ) : (
                <ScrollView contentContainerStyle={{ padding: Spacing.md, gap: Spacing.md }}>
                    <Card>
                        <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.sm }]}>
                            {user?.full_name ?? 'Chưa có thông tin'}
                        </Text>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>{user?.email ?? 'Không có email'}</Text>
                    </Card>

                    <Card>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Thông tin tài khoản</Text>
                        <View style={{ gap: Spacing.sm }}>
                            <View>
                                <Text style={[Typography.captionMedium, { color: colors.textTertiary }]}>User ID</Text>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>{user?.id ?? 'Không rõ'}</Text>
                            </View>
                            <View>
                                <Text style={[Typography.captionMedium, { color: colors.textTertiary }]}>Số nhà đang quản lý</Text>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>{stats.homeCount}</Text>
                            </View>
                            <View>
                                <Text style={[Typography.captionMedium, { color: colors.textTertiary }]}>Thiết bị đang hoạt động</Text>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>{stats.activeDevices}</Text>
                            </View>
                        </View>
                    </Card>
                </ScrollView>
            )}
        </SafeAreaView>
    );
}
