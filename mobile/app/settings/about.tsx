import React from 'react';
import { View, Text, ScrollView, Platform } from 'react-native';
import Constants from 'expo-constants';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { API_BASE_URL } from '@/services/api';

export default function SettingsAboutScreen() {
    const { colors } = useTheme();
    const appName = Constants.expoConfig?.name ?? 'Smart Home';
    const appVersion = Constants.expoConfig?.version ?? '1.0.0';
    const sdkVersion = Constants.expoConfig?.sdkVersion ?? 'Không rõ';

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title="Giới thiệu" showBack />
            <ScrollView contentContainerStyle={{ padding: Spacing.md, gap: Spacing.md }}>
                <Card>
                    <Text style={[Typography.h2, { color: colors.text, marginBottom: Spacing.xs }]}>{appName}</Text>
                    <Text style={[Typography.body, { color: colors.textSecondary }]}>
                        Ứng dụng điều khiển nhà thông minh cho mobile.
                    </Text>
                </Card>

                <Card>
                    <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Thông tin bản dựng</Text>
                    <View style={{ gap: Spacing.sm }}>
                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>Version: {appVersion}</Text>
                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>Expo SDK: {sdkVersion}</Text>
                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>Nền tảng: {Platform.OS}</Text>
                        <Text style={[Typography.bodyMedium, { color: colors.text }]}>Backend: {API_BASE_URL}</Text>
                    </View>
                </Card>
            </ScrollView>
        </SafeAreaView>
    );
}
