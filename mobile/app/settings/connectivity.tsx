import React, { useCallback, useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { API_BASE_URL, devicesAPI, getAccessToken, homesAPI, roomsAPI } from '@/services/api';

interface ConnectivityState {
    backendStatus: 'online' | 'offline';
    homeCount: number;
    roomCount: number;
    deviceCount: number;
    checkedAt: string | null;
}

export default function SettingsConnectivityScreen() {
    const { colors } = useTheme();
    const [state, setState] = useState<ConnectivityState>({
        backendStatus: 'offline',
        homeCount: 0,
        roomCount: 0,
        deviceCount: 0,
        checkedAt: null,
    });
    const [loading, setLoading] = useState(true);

    useFocusEffect(
        useCallback(() => {
            let isMounted = true;

            async function loadConnectivity() {
                try {
                    setLoading(true);
                    const homes = await homesAPI.list();
                    const roomGroups = await Promise.all(homes.map((home) => roomsAPI.list(home.id)));
                    const allRooms = roomGroups.flat();
                    const deviceGroups = await Promise.all(allRooms.map((room) => devicesAPI.list(room.id)));
                    if (!isMounted) return;

                    setState({
                        backendStatus: 'online',
                        homeCount: homes.length,
                        roomCount: allRooms.length,
                        deviceCount: deviceGroups.flat().length,
                        checkedAt: new Date().toLocaleString('vi-VN'),
                    });
                } catch (error) {
                    console.error('Failed to load connectivity data:', error);
                    if (!isMounted) return;

                    setState({
                        backendStatus: 'offline',
                        homeCount: 0,
                        roomCount: 0,
                        deviceCount: 0,
                        checkedAt: new Date().toLocaleString('vi-VN'),
                    });
                } finally {
                    if (isMounted) {
                        setLoading(false);
                    }
                }
            }

            void loadConnectivity();

            return () => {
                isMounted = false;
            };
        }, []),
    );

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Kết nối" showBack />
            {loading ? (
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <ActivityIndicator size="large" color={colors.primary} />
                </View>
            ) : (
                <ScrollView contentContainerStyle={{ padding: Spacing.md, gap: Spacing.md }}>
                    <Card>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Trạng thái đồng bộ</Text>
                        <Text style={[Typography.bodyMedium, { color: state.backendStatus === 'online' ? colors.success : colors.error }]}>
                            Backend: {state.backendStatus === 'online' ? 'Đang kết nối' : 'Không thể kết nối'}
                        </Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Kiểm tra lúc: {state.checkedAt ?? 'Chưa có'}
                        </Text>
                    </Card>

                    <Card>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Cấu hình hiện tại</Text>
                        <View style={{ gap: Spacing.sm }}>
                            <View>
                                <Text style={[Typography.captionMedium, { color: colors.textTertiary }]}>API base URL</Text>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>{API_BASE_URL}</Text>
                            </View>
                            <View>
                                <Text style={[Typography.captionMedium, { color: colors.textTertiary }]}>Trạng thái token</Text>
                                <Text style={[Typography.bodyMedium, { color: colors.text }]}>
                                    {getAccessToken() ? 'Đã đăng nhập' : 'Chưa đăng nhập'}
                                </Text>
                            </View>
                        </View>
                    </Card>

                    <Card>
                        <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Thống kê đồng bộ</Text>
                        <View style={{ gap: Spacing.sm }}>
                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>Nhà: {state.homeCount}</Text>
                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>Phòng: {state.roomCount}</Text>
                            <Text style={[Typography.bodyMedium, { color: colors.text }]}>Thiết bị: {state.deviceCount}</Text>
                        </View>
                    </Card>
                </ScrollView>
            )}
        </SafeAreaView>
    );
}
