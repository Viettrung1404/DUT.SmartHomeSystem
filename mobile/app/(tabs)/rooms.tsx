import React from 'react';
import { View, Text, FlatList } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { RoomCard } from '@/components/RoomCard';
import { Spacing } from '@/constants/theme';
import { mockRooms, Room } from '@/services/mockData';

export default function RoomsScreen() {
    const { colors } = useTheme();
    const router = useRouter();

    const handleRoomPress = (room: Room) => {
        router.push({ pathname: '/room/[id]', params: { id: room.id } });
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title="Phòng" subtitle={`${mockRooms.length} phòng`} />
            <FlatList
                data={mockRooms}
                keyExtractor={(item) => item.id}
                numColumns={2}
                contentContainerStyle={{ padding: Spacing.md, gap: Spacing.sm }}
                columnWrapperStyle={{ gap: Spacing.sm }}
                renderItem={({ item }) => (
                    <RoomCard room={item} onPress={handleRoomPress} />
                )}
                showsVerticalScrollIndicator={false}
            />
        </SafeAreaView>
    );
}
