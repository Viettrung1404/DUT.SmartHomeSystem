import React, { useState } from 'react';
import { View, Text, FlatList } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { DeviceCard } from '@/components/DeviceCard';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { mockRooms, mockDevices, Device } from '@/services/mockData';

export default function RoomDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const router = useRouter();
    const room = mockRooms.find((r) => r.id === id);
    const [devices, setDevices] = useState<Device[]>(mockDevices[id || '1'] || []);

    if (!room) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={[Typography.body, { color: colors.textSecondary }]}>Không tìm thấy phòng</Text>
            </SafeAreaView>
        );
    }

    const handleToggle = (deviceId: string, value: boolean) => {
        setDevices((prev) =>
            prev.map((d) => (d.id === deviceId ? { ...d, isOn: value } : d)),
        );
    };

    const handleDevicePress = (device: Device) => {
        router.push({ pathname: '/device/[id]', params: { id: device.id } });
    };

    const onlineCount = devices.filter((d) => d.isOnline).length;
    const activeCount = devices.filter((d) => d.isOn).length;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <Header title={room.name} showBack subtitle={`${devices.length} thiết bị`} />

            {/* Room Stats */}
            <View style={{ flexDirection: 'row', gap: Spacing.sm, paddingHorizontal: Spacing.md, marginBottom: Spacing.md }}>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.primary }]}>{activeCount}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Đang bật</Text>
                    </View>
                </Card>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.success }]}>{onlineCount}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>Online</Text>
                    </View>
                </Card>
                <Card style={{ flex: 1, paddingVertical: Spacing.sm }}>
                    <View style={{ alignItems: 'center' }}>
                        <Text style={[Typography.number, { color: colors.warning }]}>{room.energyToday}</Text>
                        <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
                    </View>
                </Card>
            </View>

            {/* Devices Grid */}
            <FlatList
                data={devices}
                keyExtractor={(item) => item.id}
                numColumns={2}
                contentContainerStyle={{ paddingHorizontal: Spacing.md, gap: Spacing.sm }}
                columnWrapperStyle={{ gap: Spacing.sm }}
                renderItem={({ item }) => (
                    <View style={{ flex: 1 }}>
                        <DeviceCard device={item} onToggle={handleToggle} onPress={handleDevicePress} />
                    </View>
                )}
                showsVerticalScrollIndicator={false}
            />
        </SafeAreaView>
    );
}
