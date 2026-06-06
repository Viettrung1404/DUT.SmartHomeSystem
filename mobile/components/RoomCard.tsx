import React from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export interface RoomCardModel {
    id: string;
    name: string;
    icon?: string;
    isOnline: boolean;
    activeDevices: number;
    deviceCount: number;
}

interface RoomCardProps {
    room: RoomCardModel;
    onPress: (room: RoomCardModel) => void;
}

export function RoomCard({ room, onPress }: RoomCardProps) {
    const { colors } = useTheme();
    const iconName = room.icon && room.icon in Feather.glyphMap
        ? (room.icon as keyof typeof Feather.glyphMap)
        : 'home';

    return (
        <Card onPress={() => onPress(room)} style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <View
                    style={{
                        width: 44,
                        height: 44,
                        borderRadius: 12,
                        backgroundColor: colors.primaryLight,
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Feather name={iconName} size={20} color={colors.primary} />
                </View>
                <Badge variant={room.isOnline ? 'online' : 'offline'} />
            </View>

            <Text style={[Typography.bodyMedium, { color: colors.text, marginTop: Spacing.md }]} numberOfLines={1}>
                {room.name}
            </Text>

            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginTop: Spacing.xs }}>
                <Feather name="cpu" size={12} color={colors.textTertiary} />
                <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                    {room.activeDevices}/{room.deviceCount} thiết bị
                </Text>
            </View>
        </Card>
    );
}
