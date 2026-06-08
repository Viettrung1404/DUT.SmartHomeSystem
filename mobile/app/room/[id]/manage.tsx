import React, { useCallback, useState } from 'react';
import { View, FlatList, Pressable, ActivityIndicator, Text, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/theme';
import { devicesAPI, roomsAPI } from '@/services/api';

interface DeviceItem {
    id: string;
    name: string;
    type: string;
}

const DEVICE_TYPES = [
    'light',
    'fan',
    'lock',
    'camera',
    'curtain',
    'sensor',
    'door',
    'buzzer',
    'distance_light',
    'temperature_humidity',
    'distance_sensor',
    'gas_sensor',
    'rain_sensor',
    'rain_servo',
] as const;

type DeviceType = (typeof DEVICE_TYPES)[number];

const DEVICE_TYPE_LABELS: Record<DeviceType, string> = {
    light: 'Đèn',
    fan: 'Quạt',
    lock: 'Khóa',
    camera: 'Camera',
    curtain: 'Rèm',
    sensor: 'Cảm biến',
    door: 'Cửa',
    buzzer: 'Còi',
    distance_light: 'Đèn khoảng cách',
    temperature_humidity: 'Nhiệt độ / độ ẩm',
    distance_sensor: 'Siêu âm',
    gas_sensor: 'Gas',
    rain_sensor: 'Mưa',
    rain_servo: 'Mái che mưa',
};

function normalizeEditableType(type: string): DeviceType {
    const normalizedType = type?.toLowerCase?.() ?? type;
    return DEVICE_TYPES.includes(normalizedType as DeviceType)
        ? (normalizedType as DeviceType)
        : 'light';
}

export default function RoomDeviceManageScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const { colors } = useTheme();
    const [roomName, setRoomName] = useState('');
    const [devices, setDevices] = useState<DeviceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [name, setName] = useState('');
    const [type, setType] = useState<DeviceType>('light');
    const [editingId, setEditingId] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

    const loadDevices = useCallback(async (roomId: string) => {
        try {
            setLoading(true);
            const room = await roomsAPI.get(roomId);
            setRoomName(room.name);
            const response = await devicesAPI.list(roomId);
            setDevices(
                response.map((device) => ({
                    id: device.id,
                    name: device.name,
                    type: device.type?.toLowerCase?.() ?? device.type,
                })),
            );
        } catch (error) {
            console.error('Failed to load devices:', error);
            setDevices([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            if (!id) return;
            void loadDevices(id);
        }, [id, loadDevices]),
    );

    const resetForm = () => {
        setName('');
        setType('light');
        setEditingId(null);
    };

    const handleSubmit = async () => {
        if (!id || !name.trim()) return;
        setSaving(true);
        try {
            if (editingId) {
                await devicesAPI.update(editingId, { name: name.trim(), type });
            } else {
                const created = await devicesAPI.create(id, name.trim(), type);
                Alert.alert(
                    'Đã thêm thiết bị',
                    `ID: ${created.id}\nVào Phòng -> chọn phòng -> chọn thiết bị để xem thông tin chi tiết và ID.`,
                );
            }
            resetForm();
            await loadDevices(id);
        } catch (error) {
            console.error('Failed to save device:', error);
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (device: DeviceItem) => {
        setEditingId(device.id);
        setName(device.name);
        setType(normalizeEditableType(device.type));
    };

    const handleDelete = async (deviceId: string) => {
        setSaving(true);
        try {
            await devicesAPI.delete(deviceId);
            if (editingId === deviceId) resetForm();
            await loadDevices(id as string);
        } catch (error) {
            console.error('Failed to delete device:', error);
        } finally {
            setSaving(false);
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title={`Thiết bị · ${roomName || 'Phòng'}`} showBack />

            <View style={{ padding: Spacing.md }}>
                <Card>
                    <Input
                        label="Tên thiết bị"
                        placeholder="Ví dụ: Đèn trần"
                        value={name}
                        onChangeText={setName}
                        icon="cpu"
                        autoCapitalize="words"
                    />
                    <View style={{ marginBottom: Spacing.sm }}>
                        <Text style={[Typography.captionMedium, { color: colors.textSecondary, marginBottom: Spacing.xs }]}>
                            Loại thiết bị
                        </Text>
                        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm }}>
                            {DEVICE_TYPES.map((option) => {
                                const isSelected = type === option;
                                return (
                                    <Pressable
                                        key={option}
                                        onPress={() => setType(option)}
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
                                            {DEVICE_TYPE_LABELS[option]}
                                        </Text>
                                    </Pressable>
                                );
                            })}
                        </View>
                    </View>
                    <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
                        <Button
                            title={editingId ? 'Cập nhật thiết bị' : 'Thêm thiết bị'}
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
                    data={devices}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={{ paddingHorizontal: Spacing.md, gap: Spacing.sm, paddingBottom: Spacing.lg }}
                    renderItem={({ item }) => (
                        <Card>
                            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                                <View>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{item.name}</Text>
                                    <Text style={[Typography.caption, { color: colors.textSecondary }]}>Loại: {item.type}</Text>
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
