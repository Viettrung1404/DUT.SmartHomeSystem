import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, FlatList, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SecurityStatusCard } from '@/components/SecurityStatusCard';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { homesAPI, securityAPI } from '@/services/api';
import { SecurityAlert } from '@/components/SecurityStatusCard';

export default function SecurityScreen() {
    const { colors } = useTheme();
    const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
    const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high'>('low');

    useEffect(() => {
        loadSecurity();
    }, []);

    const loadSecurity = async () => {
        try {
            const homes = await homesAPI.list();
            if (!homes.length) return;

            const homeId = homes[0].id;
            const [summary, events] = await Promise.all([
                securityAPI.summary(homeId),
                securityAPI.events(homeId, 20),
            ]);

            const normalizedRisk = (summary.risk_level === 'high' || summary.risk_level === 'medium')
                ? summary.risk_level
                : 'low';
            setRiskLevel(normalizedRisk);
            setAlerts(
                events.map((event) => ({
                    id: event.id,
                    message: event.description,
                    timestamp: new Date(event.timestamp).toLocaleString('vi-VN'),
                    severity: event.severity === 'high' || event.severity === 'medium' ? event.severity : 'low',
                    icon: event.event_type === 'door' ? 'door-open' : event.event_type === 'camera_offline' ? 'wifi-off' : 'alert-circle',
                })),
            );
        } catch (error) {
            console.error('Failed to load security data:', error);
            setAlerts([]);
            setRiskLevel('low');
        }
    };

    // Mock security overview
    const doorStatus = [
        { name: 'Cửa trước', locked: true, online: true },
        { name: 'Cửa sau', locked: true, online: true },
        { name: 'Cửa garage', locked: true, online: false },
    ];

    const cameras = [
        { name: 'Camera phòng khách', online: true },
        { name: 'Camera ban công', online: true },
        { name: 'Camera garage', online: false },
    ];

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title="Trung tâm An ninh" />
            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ padding: Spacing.md }}>
                {/* Risk Level */}
                <Card style={{ marginBottom: Spacing.md, alignItems: 'center', paddingVertical: Spacing.lg }}>
                    <View
                        style={{
                            width: 64, height: 64, borderRadius: 32,
                            backgroundColor: (riskLevel === 'high' ? colors.riskHigh : riskLevel === 'medium' ? colors.riskMedium : colors.riskLow) + '15',
                            alignItems: 'center', justifyContent: 'center', marginBottom: Spacing.md,
                        }}
                    >
                        <Feather
                            name="shield"
                            size={28}
                            color={riskLevel === 'high' ? colors.riskHigh : riskLevel === 'medium' ? colors.riskMedium : colors.riskLow}
                        />
                    </View>
                    <Badge variant="risk" riskLevel={riskLevel} />
                    <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.sm, textAlign: 'center' }]}>
                        {riskLevel === 'high' ? 'Có vấn đề cần xử lý ngay' : riskLevel === 'medium' ? 'Cần chú ý một số cảnh báo' : 'Mọi thứ an toàn'}
                    </Text>
                </Card>

                {/* Doors & Locks */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Cửa & Khóa</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.lg }}>
                    {doorStatus.map((door, i) => (
                        <Card key={i}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <View
                                    style={{
                                        width: 40, height: 40, borderRadius: 20,
                                        backgroundColor: door.locked ? colors.successLight : colors.warningLight,
                                        alignItems: 'center', justifyContent: 'center',
                                    }}
                                >
                                    <Feather name={door.locked ? 'lock' : 'unlock'} size={18} color={door.locked ? colors.success : colors.warning} />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{door.name}</Text>
                                    <Text style={[Typography.caption, { color: door.locked ? colors.success : colors.warning }]}>
                                        {door.locked ? 'Đã khóa' : 'Chưa khóa'}
                                    </Text>
                                </View>
                                <Badge variant={door.online ? 'online' : 'offline'} />
                            </View>
                        </Card>
                    ))}
                </View>

                {/* Cameras */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Camera</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.lg }}>
                    {cameras.map((cam, i) => (
                        <Card key={i}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <View
                                    style={{
                                        width: 40, height: 40, borderRadius: 20,
                                        backgroundColor: cam.online ? colors.primaryLight : colors.errorLight,
                                        alignItems: 'center', justifyContent: 'center',
                                    }}
                                >
                                    <Feather name="video" size={18} color={cam.online ? colors.primary : colors.error} />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{cam.name}</Text>
                                </View>
                                <Badge variant={cam.online ? 'online' : 'offline'} label={cam.online ? 'Trực tuyến' : 'Ngoại tuyến'} />
                            </View>
                            {cam.online && (
                                <View
                                    style={{
                                        height: 120, backgroundColor: colors.surface, borderRadius: BorderRadius.md,
                                        marginTop: Spacing.sm, alignItems: 'center', justifyContent: 'center',
                                        borderWidth: 1, borderColor: colors.border,
                                    }}
                                >
                                    <Feather name="play-circle" size={32} color={colors.textTertiary} />
                                    <Text style={[Typography.caption, { color: colors.textTertiary, marginTop: Spacing.xs }]}>Nhấn để xem</Text>
                                </View>
                            )}
                        </Card>
                    ))}
                </View>

                {/* Alert History */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Lịch sử cảnh báo</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {alerts.map((alert) => (
                        <SecurityStatusCard key={alert.id} alert={alert} />
                    ))}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
