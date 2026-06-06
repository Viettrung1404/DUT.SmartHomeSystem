import React, { useEffect, useState } from 'react';
import { View, FlatList, Pressable, ActivityIndicator, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { homesAPI, roomsAPI } from '@/services/api';
import { findRoomPresetKey } from '@/utils/roomIcons';

interface RoomItem {
    id: string;
    name: string;
    icon?: string;
}

const ROOM_PRESETS = [
    { label: 'Phòng khách', value: 'living_room', icon: 'tv' },
    { label: 'Phòng ngủ', value: 'bedroom', icon: 'moon' },
    { label: 'Bếp', value: 'kitchen', icon: 'coffee' },
    { label: 'Phòng tắm', value: 'bathroom', icon: 'droplet' },
    { label: 'Phòng làm việc', value: 'office', icon: 'briefcase' },
    { label: 'Phòng ăn', value: 'dining', icon: 'coffee' },
    { label: 'Phòng trẻ em', value: 'kids', icon: 'smile' },
    { label: 'Sân vườn', value: 'garden', icon: 'sun' },
    { label: 'Garage', value: 'garage', icon: 'truck' },
    { label: 'Ban công', value: 'balcony', icon: 'wind' },
    { label: 'Kho', value: 'storage', icon: 'archive' },
    { label: 'Phòng khác', value: 'other', icon: 'grid' },
] as const;

type RoomPreset = (typeof ROOM_PRESETS)[number];

const findPresetByIcon = (icon?: string) => {
    const matchedKey = findRoomPresetKey(icon);
    if (matchedKey) {
        return ROOM_PRESETS.find((preset) => preset.value === matchedKey || preset.icon === matchedKey) ?? ROOM_PRESETS[ROOM_PRESETS.length - 1];
    }
    return ROOM_PRESETS.find((preset) => preset.icon === icon || preset.value === icon) ?? ROOM_PRESETS[ROOM_PRESETS.length - 1];
};

export default function RoomsManageScreen() {
    const { colors } = useTheme();
    const [homeId, setHomeId] = useState<string | null>(null);
    const [rooms, setRooms] = useState<RoomItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [name, setName] = useState('');
    const [preset, setPreset] = useState<RoomPreset>(ROOM_PRESETS[0]);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        loadRooms();
    }, []);

    const loadRooms = async () => {
        try {
            setLoading(true);
            const homes = await homesAPI.list();
            if (!homes.length) {
                setHomeId(null);
                setRooms([]);
                return;
            }

            const primaryHome = homes[0];
            setHomeId(primaryHome.id);
            const response = await roomsAPI.list(primaryHome.id);
            setRooms(response.map((room) => ({ id: room.id, name: room.name, icon: room.icon })));
        } catch (error) {
            console.error('Failed to load rooms:', error);
            setRooms([]);
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setName('');
        setPreset(ROOM_PRESETS[0]);
        setEditingId(null);
    };

    const handleSubmit = async () => {
        if (!homeId || !name.trim()) return;
        setSaving(true);
        try {
            const payload = { name: name.trim(), icon: preset.icon };
            if (editingId) {
                await roomsAPI.update(editingId, payload);
            } else {
                await roomsAPI.create(homeId, payload.name, payload.icon);
            }
            resetForm();
            await loadRooms();
        } catch (error) {
            console.error('Failed to save room:', error);
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (room: RoomItem) => {
        setEditingId(room.id);
        setName(room.name);
        setPreset(findPresetByIcon(room.icon));
    };

    const handleDelete = async (roomId: string) => {
        setSaving(true);
        try {
            await roomsAPI.delete(roomId);
            if (editingId === roomId) resetForm();
            await loadRooms();
        } catch (error) {
            console.error('Failed to delete room:', error);
        } finally {
            setSaving(false);
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title="Cấu hình phòng" showBack />

            <View style={{ padding: Spacing.md }}>
                <Card>
                    <Input
                        label="Tên phòng"
                        placeholder="Ví dụ: Phòng khách"
                        value={name}
                        onChangeText={setName}
                        icon="grid"
                        autoCapitalize="words"
                    />
                    <View style={{ marginBottom: Spacing.sm }}>
                        <Text style={[Typography.captionMedium, { color: colors.textSecondary, marginBottom: Spacing.xs }]}>Loại phòng</Text>
                        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm }}>
                            {ROOM_PRESETS.map((option) => {
                                const isSelected = preset.value === option.value;
                                return (
                                    <Pressable
                                        key={option.value}
                                        onPress={() => setPreset(option)}
                                        style={{
                                            paddingHorizontal: Spacing.md,
                                            paddingVertical: Spacing.xs,
                                            borderRadius: 999,
                                            borderWidth: 1,
                                            borderColor: isSelected ? colors.primary : colors.border,
                                            backgroundColor: isSelected ? colors.primaryLight : colors.surface,
                                        }}
                                    >
                                        <Text style={[Typography.captionMedium, { color: isSelected ? colors.primary : colors.textSecondary }]}>
                                            {option.label}
                                        </Text>
                                    </Pressable>
                                );
                            })}
                        </View>
                    </View>
                    <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                        <Button
                            title={editingId ? 'Cập nhật phòng' : 'Thêm phòng'}
                            onPress={handleSubmit}
                            loading={saving}
                            disabled={!name.trim()}
                            style={{ flex: 1 }}
                        />
                        {editingId && (
                            <Button
                                title="Hủy"
                                onPress={resetForm}
                                variant="outline"
                                style={{ flex: 1 }}
                            />
                        )}
                    </View>
                </Card>
            </View>

            {loading ? (
                <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                    <ActivityIndicator size="large" color={colors.primary} />
                </View>
            ) : (
                <FlatList
                    data={rooms}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={{ paddingHorizontal: Spacing.md, gap: Spacing.sm, paddingBottom: Spacing.lg }}
                    renderItem={({ item }) => (
                        <Card>
                            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                                <View>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.name}</Text>
                                    <Text style={[Typography.caption, { color: colors.textSecondary }]}>Loại: {findPresetByIcon(item.icon).label}</Text>
                                </View>
                                <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                                    <Pressable onPress={() => handleEdit(item)}>
                                        <Text style={[Typography.captionMedium, { color: colors.primary }]}>Sửa</Text>
                                    </Pressable>
                                    <Pressable onPress={() => handleDelete(item.id)}>
                                        <Text style={[Typography.captionMedium, { color: colors.error }]}>Xóa</Text>
                                    </Pressable>
                                </View>
                            </View>
                        </Card>
                    )}
                    showsVerticalScrollIndicator={false}
                />
            )}
        </SafeAreaView>
    );
}
