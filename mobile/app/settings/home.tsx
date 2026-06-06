import React, { useCallback, useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView } from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { homesAPI, HomeResponse } from '@/services/api';

export default function SettingsHomeScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [homes, setHomes] = useState<HomeResponse[]>([]);
    const [loading, setLoading] = useState(true);

    useFocusEffect(
        useCallback(() => {
            let isMounted = true;

            async function loadHomes() {
                try {
                    setLoading(true);
                    const response = await homesAPI.list();
                    if (isMounted) {
                        setHomes(response);
                    }
                } catch (error) {
                    console.error('Failed to load homes in settings:', error);
                    if (isMounted) {
                        setHomes([]);
                    }
                } finally {
                    if (isMounted) {
                        setLoading(false);
                    }
                }
            }

            void loadHomes();

            return () => {
                isMounted = false;
            };
        }, []),
    );

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Thông tin nhà" showBack />
            {loading ? (
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <ActivityIndicator size="large" color={colors.primary} />
                </View>
            ) : (
                <ScrollView contentContainerStyle={{ padding: Spacing.md, gap: Spacing.md }}>
                    {homes.length === 0 ? (
                        <Card>
                            <Text style={[Typography.body, { color: colors.textSecondary }]}>
                                Chưa có nhà nào được tạo cho tài khoản này.
                            </Text>
                        </Card>
                    ) : (
                        homes.map((home) => (
                            <Card key={home.id}>
                                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.xs }]}>{home.name}</Text>
                                <Text style={[Typography.caption, { color: colors.textSecondary, marginBottom: Spacing.md }]}>
                                    {home.address || 'Chưa có địa chỉ'}
                                </Text>
                                <View style={{ gap: Spacing.sm }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>Phòng: {home.room_count}</Text>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>Thiết bị: {home.device_count}</Text>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>Đang bật: {home.active_devices}</Text>
                                </View>
                            </Card>
                        ))
                    )}

                    <Button title="Quản lý phòng và thiết bị" onPress={() => router.push('/rooms/manage')} />
                </ScrollView>
            )}
        </SafeAreaView>
    );
}
