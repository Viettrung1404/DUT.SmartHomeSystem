import React, { useCallback, useState } from 'react';
import { View, FlatList, ActivityIndicator } from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { RoomCard, RoomCardModel } from '@/components/RoomCard';
import { Spacing } from '@/constants/theme';
import { homesAPI, roomsAPI } from '@/services/api';
import { resolveRoomIcon } from '@/utils/roomIcons';

export default function RoomsScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [rooms, setRooms] = useState<RoomCardModel[]>([]);
    const [loading, setLoading] = useState(true);

    const loadRooms = useCallback(async () => {
        try {
            setLoading(true);
            const homes = await homesAPI.list();
            if (!homes.length) {
                setRooms([]);
                return;
            }

            const response = await roomsAPI.list(homes[0].id);
            setRooms(
                response.map((room) => ({
                    id: room.id,
                    name: room.name,
                    icon: resolveRoomIcon(room.name, room.icon),
                    isOnline: room.is_online,
                    activeDevices: room.active_devices,
                    deviceCount: room.device_count,
                })),
            );
        } catch (error) {
            console.error('Failed to load rooms:', error);
            setRooms([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            void loadRooms();
        }, [loadRooms]),
    );

    const handleRoomPress = (room: RoomCardModel) => {
        router.push({ pathname: '/room/[id]', params: { id: room.id } });
    };

    if (loading) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
                <Header title="Phòng" subtitle="Đang tải..." />
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <ActivityIndicator size="large" color={colors.primary} />
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header
                title="Phòng"
                subtitle={`${rooms.length} phòng`}
                rightIcon="settings"
                onRightPress={() => router.push('/rooms/manage')}
            />
            <FlatList
                data={rooms}
                keyExtractor={(item) => item.id}
                numColumns={2}
                contentContainerStyle={{ padding: Spacing.md, gap: Spacing.sm }}
                columnWrapperStyle={{ gap: Spacing.sm }}
                renderItem={({ item }) => <RoomCard room={item} onPress={handleRoomPress} />}
                showsVerticalScrollIndicator={false}
            />
        </SafeAreaView>
    );
}
