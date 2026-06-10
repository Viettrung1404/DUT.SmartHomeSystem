import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, ScrollView, FlatList, Pressable, ActivityIndicator, useWindowDimensions, Image, TextInput, Alert } from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { AIInsight, AIInsightCard } from '@/components/AIInsightCard';
import { QuickAction } from '@/components/QuickAction';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { homesAPI, roomsAPI, suggestionsAPI, devicesAPI, faceAPI, DeviceResponse } from '@/services/api';
import { useWebSocket } from '@/hooks/use-websocket';
import { resolveRoomIcon } from '@/utils/roomIcons';
import {
  QUICK_ACTIONS,
  QuickActionId,
  loadQuickActionConfig,
  normalizeDeviceType,
  isLightDevice,
  isToggleableDevice,
  isDoorDevice,
} from '@/services/quickActions';

const settingsRoute = '/settings';
const roomsRoute = '/rooms';

interface DashboardHome {
  id: string;
  name: string;
  deviceCount: number;
  activeDevices: number;
}

interface DashboardRoom {
  id: string;
  name: string;
  icon: string;
  activeDevices: number;
  deviceCount: number;
}

export default function DashboardScreen() {
  const { colors, toggleTheme, isDark } = useTheme();
  const router = useRouter();
  const { width } = useWindowDimensions();
  const scale = Math.min(1.2, Math.max(0.85, width / 375));
  const scaled = (value: number) => Math.round(value * scale);
  const scaledIcon = (value: number) => Math.round(value * scale);
  const spacing = {
    xxs: scaled(Spacing.xxs),
    xs: scaled(Spacing.xs),
    sm: scaled(Spacing.sm),
    md: scaled(Spacing.md),
    lg: scaled(Spacing.lg),
    xl: scaled(Spacing.xl),
  };
  const [home, setHome] = useState<DashboardHome | null>(null);
  const [homeId, setHomeId] = useState<string | null>(null);
  const [roomIds, setRoomIds] = useState<string[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [rooms, setRooms] = useState<DashboardRoom[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [quickActionBusy, setQuickActionBusy] = useState<QuickActionId | null>(null);
  const [faceImages, setFaceImages] = useState<ImagePicker.ImagePickerAsset[]>([]);
  const [facePersonId, setFacePersonId] = useState('');
  const [faceEnrollBusy, setFaceEnrollBusy] = useState(false);
  const [faceEnrollMessage, setFaceEnrollMessage] = useState<string | null>(null);
  const { subscribe } = useWebSocket(homeId);

  const roomCardWidth = (() => {
    const horizontalPadding = spacing.md * 2;
    const gap = spacing.sm;
    const available = Math.max(0, width - horizontalPadding);
    const minCardWidth = scaled(140);
    const maxCardWidth = scaled(200);
    const columns = Math.max(2, Math.floor((available + gap) / (minCardWidth + gap)));
    return Math.min(maxCardWidth, Math.floor((available - gap * (columns - 1)) / columns));
  })();

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const homes = await homesAPI.list();
      if (!homes.length) {
        setHome(null);
        setRooms([]);
        setInsights([]);
        return;
      }

      const primaryHome = homes[0];
      const roomData = await roomsAPI.list(primaryHome.id);
      setHomeId(primaryHome.id);
      setRoomIds(roomData.map((room) => room.id));

      setHome({
        id: primaryHome.id,
        name: primaryHome.name,
        deviceCount: primaryHome.device_count,
        activeDevices: primaryHome.active_devices,
      });

      setRooms(
        roomData.map((room) => ({
          id: room.id,
          name: room.name,
          icon: resolveRoomIcon(room.name, room.icon),
          activeDevices: room.active_devices,
          deviceCount: room.device_count,
        })),
      );

      const loadedDevices = await loadDevices(primaryHome.id, roomData.map((room) => room.id));
      updateCounts(loadedDevices);

      try {
        const suggestionData = await suggestionsAPI.listMine(10, 0);
        setInsights(
          suggestionData.suggestions.map((suggestion) => ({
            id: String(suggestion.id),
            message: suggestion.suggestion_json?.description || suggestion.suggestion_text,
            type: suggestion.action_type === 'ALERT' ? 'warning' : suggestion.action_type === 'SCHEDULE' ? 'suggestion' : 'info',
            icon: suggestion.action_type === 'ALERT' ? 'alert-triangle' : suggestion.action_type === 'SCHEDULE' ? 'clock' : 'zap',
          })),
        );
      } catch {
        setInsights([]);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      setHome(null);
      setRooms([]);
      setInsights([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      void loadDashboard();
    }, [loadDashboard]),
  );

  const handleInsightAction = async (id: string, accepted: boolean) => {
    const suggestionId = Number(id);
    if (!Number.isNaN(suggestionId)) {
      try {
        await suggestionsAPI.accept(suggestionId, accepted);
      } catch (error) {
        console.error('Failed to submit suggestion decision:', error);
      }
    }
    setInsights((prev) => prev.filter((item) => item.id !== id));
  };

  const loadDevices = async (_homeId: string, roomIdList: string[]) => {
    try {
      const deviceGroups = await Promise.all(roomIdList.map((roomId) => devicesAPI.list(roomId)));
      const next = deviceGroups.flat();
      setDevices(next);
      return next;
    } catch (error) {
      console.error('Failed to load devices for quick actions:', error);
      setDevices([]);
      return [] as DeviceResponse[];
    }
  };

  const ensureDevices = async (): Promise<DeviceResponse[]> => {
    if (devices.length) return devices;
    if (!homeId) return [];

    const roomsToUse = roomIds.length ? roomIds : (await roomsAPI.list(homeId)).map((room) => room.id);
    return loadDevices(homeId, roomsToUse);
  };

  const updateCounts = (nextDevices: DeviceResponse[]) => {
    const activeCount = nextDevices.filter((device) => device.status).length;
    const totalCount = nextDevices.length;
    const roomActiveMap = new Map<string, number>();
    const roomTotalMap = new Map<string, number>();

    nextDevices.forEach((device) => {
      roomTotalMap.set(device.room_id, (roomTotalMap.get(device.room_id) ?? 0) + 1);
      if (device.status) {
        roomActiveMap.set(device.room_id, (roomActiveMap.get(device.room_id) ?? 0) + 1);
      }
    });

    setHome((prev) => (prev ? { ...prev, activeDevices: activeCount, deviceCount: totalCount || prev.deviceCount } : prev));
    setRooms((prev) =>
      prev.map((room) => ({
        ...room,
        activeDevices: roomActiveMap.get(room.id) ?? 0,
        deviceCount: roomTotalMap.get(room.id) ?? room.deviceCount,
      })),
    );
  };

  const toggleDevices = async (deviceIds: string[], status: boolean, allDevices: DeviceResponse[]) => {
    const allowedIds = new Set(deviceIds);
    const targets = allDevices.filter((device) => allowedIds.has(device.id) && device.online_status);
    await Promise.allSettled(targets.map((device) => devicesAPI.toggle(device.id, status)));
    setDevices((prev) => {
      const next = prev.map((device) => (allowedIds.has(device.id) ? { ...device, status } : device));
      updateCounts(next);
      return next;
    });
  };

  const commandDoors = async (command: 'open' | 'close', allDevices: DeviceResponse[]) => {
    const doors = allDevices.filter((device) => isDoorDevice(normalizeDeviceType(device.type)) && device.online_status);
    await Promise.allSettled(doors.map((device) => devicesAPI.command(device.id, command)));
  };

  const handleQuickAction = async (actionId: QuickActionId) => {
    if (!homeId || quickActionBusy) return;
    setQuickActionBusy(actionId);

    try {
      const allDevices = await ensureDevices();
      if (!allDevices.length) return;

      if (actionId === 'doors_open' || actionId === 'doors_close') {
        await commandDoors(actionId === 'doors_open' ? 'open' : 'close', allDevices);
        return;
      }

      const config = await loadQuickActionConfig(homeId);
      const normalized = allDevices.map((device) => ({
        device,
        type: normalizeDeviceType(device.type),
      }));

      if (actionId === 'lights_off') {
        const lights = normalized.filter((item) => isLightDevice(item.type)).map((item) => item.device.id);
        const configured = config[actionId];
        const targetIds = configured?.length ? configured.filter((id) => lights.includes(id)) : lights;
        await toggleDevices(targetIds, false, allDevices);
        return;
      }

      if (actionId === 'leave_home') {
        const toggleableIds = normalized.filter((item) => isToggleableDevice(item.type)).map((item) => item.device.id);
        const lightIds = normalized.filter((item) => isLightDevice(item.type)).map((item) => item.device.id);
        const configured = config[actionId];
        const configIds = configured?.length ? configured : toggleableIds;
        const targetIds = Array.from(new Set([...lightIds, ...configIds]));
        await toggleDevices(targetIds, false, allDevices);
        return;
      }

      if (actionId === 'arrive_home') {
        const toggleableIds = normalized.filter((item) => isToggleableDevice(item.type)).map((item) => item.device.id);
        const configured = config[actionId];
        const targetIds = configured?.length ? configured : toggleableIds;
        await toggleDevices(targetIds, true, allDevices);
      }
    } finally {
      setQuickActionBusy(null);
    }
  };

  const handleConfigureAction = (actionId: QuickActionId) => {
    router.push({ pathname: '/quick-actions/[action]', params: { action: actionId } } as never);
  };

  const handlePickFaceImages = async () => {
    setFaceEnrollMessage(null);
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Can quyen thu vien anh', 'Hay cho phep ung dung truy cap anh de chon 5 anh khuon mat.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: 'images',
      allowsMultipleSelection: true,
      selectionLimit: 5,
      orderedSelection: true,
      base64: true,
      quality: 0.85,
    });

    if (result.canceled) return;
    const selected = result.assets.slice(0, 5);
    setFaceImages(selected);
    if (selected.length !== 5) {
      setFaceEnrollMessage('Hay chon dung 5 anh de enroll.');
    }
  };

  const handleEnrollFaceImages = async () => {
    if (!homeId) return;
    if (faceImages.length !== 5) {
      setFaceEnrollMessage('Can dung 5 anh de enroll.');
      return;
    }

    const imagesBase64 = faceImages.map((image) => image.base64).filter((value): value is string => Boolean(value));
    if (imagesBase64.length !== 5) {
      setFaceEnrollMessage('Khong doc duoc du lieu anh. Hay chon lai 5 anh.');
      return;
    }

    const personId = facePersonId.trim();
    if (!personId) {
      setFaceEnrollMessage('Nhap ten nguoi de phan biet khi verify.');
      return;
    }

    setFaceEnrollBusy(true);
    setFaceEnrollMessage(null);
    try {
      const response = await faceAPI.enrollBatch(homeId, personId, imagesBase64);
      setFaceEnrollMessage(`Da enroll ${response.saved_count}/5 anh cho ${response.person_id}.`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Enroll that bai';
      setFaceEnrollMessage(message);
    } finally {
      setFaceEnrollBusy(false);
    }
  };

  useEffect(() => {
    if (!homeId) return;
    const unsubscribe = subscribe('device_update', (message) => {
      if (!message.device_id) return;
      const data = message.data ?? {};
      setDevices((prev) => {
        let changed = false;
        const next = prev.map((device) => {
          if (device.id !== message.device_id) return device;
          const nextDevice = { ...device };
          if (typeof data.status === 'boolean' && data.status !== device.status) {
            nextDevice.status = data.status;
            changed = true;
          }
          if (typeof data.online === 'boolean' && data.online !== device.online_status) {
            nextDevice.online_status = data.online;
            changed = true;
          }
          return nextDevice;
        });
        if (changed) updateCounts(next);
        return next;
      });
    });

    return unsubscribe;
  }, [homeId, subscribe]);

  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  if (!home) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.lg }}>
          <Text style={[Typography.h3, { color: colors.text }]}>Chưa có nhà nào</Text>
          <Text style={[Typography.bodySmall, { color: colors.textSecondary, marginTop: spacing.xs, textAlign: 'center' }]}>
            Hãy tạo nhà mới để bắt đầu quản lý thiết bị.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={{ padding: spacing.md, paddingBottom: 0 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <View>
              <Text style={[Typography.caption, { color: colors.textSecondary }]}>Xin chào, Trung 👋</Text>
              <Text style={[Typography.h1, { color: colors.text, marginTop: spacing.xxs }]}>{home.name}</Text>
            </View>
            <View style={{ flexDirection: 'row', gap: spacing.sm }}>
              <Pressable
                onPress={toggleTheme}
                style={{
                  width: scaled(40), height: scaled(40), borderRadius: scaled(20),
                  backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
                  borderWidth: 1, borderColor: colors.border,
                }}
              >
                <Feather name={isDark ? 'sun' : 'moon'} size={scaledIcon(18)} color={colors.icon} />
              </Pressable>
              <Pressable
                onPress={() => router.push(settingsRoute)}
                style={{
                  width: scaled(40), height: scaled(40), borderRadius: scaled(20),
                  backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
                  borderWidth: 1, borderColor: colors.border,
                }}
              >
                <Feather name="settings" size={scaledIcon(18)} color={colors.icon} />
              </Pressable>
            </View>
          </View>

          {/* Weather mini */}
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.xs, marginTop: spacing.sm }}>
            <Feather name="cloud" size={scaledIcon(14)} color={colors.textSecondary} />
            <Text style={[Typography.caption, { color: colors.textSecondary }]}>Đà Nẵng • 30°C • Nhiều mây</Text>
          </View>
        </View>

        {/* Stats Row */}
        <View style={{ padding: spacing.md }}>
          <Card>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.xs }}>
              <Feather name="cpu" size={scaledIcon(14)} color={colors.primary} />
              <Text style={[Typography.caption, { color: colors.textSecondary }]}>Thiết bị</Text>
            </View>
            <Text style={[Typography.number, { color: colors.text, marginTop: spacing.xs }]}>
              {home.activeDevices} <Text style={[Typography.caption, { color: colors.textSecondary }]}>/ {home.deviceCount}</Text>
            </Text>
            <Text style={[Typography.caption, { color: colors.success, marginTop: spacing.xxs }]}>đang hoạt động</Text>
          </Card>
        </View>

        {/* AI Insights */}
        <View style={{ paddingLeft: spacing.md, marginBottom: spacing.md }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md }}>
            <View
              style={{
                width: scaled(28), height: scaled(28), borderRadius: scaled(14),
                backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Feather name="cpu" size={scaledIcon(14)} color={colors.primary} />
            </View>
            <Text style={[Typography.h3, { color: colors.text }]}>AI Gợi ý</Text>
          </View>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={insights}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <AIInsightCard
                insight={item}
                onAccept={(id) => handleInsightAction(id, true)}
                onDismiss={(id) => handleInsightAction(id, false)}
              />
            )}
          />
        </View>

        {/* Quick Actions */}
        <View style={{ padding: spacing.md, paddingTop: 0 }}>
          <Text style={[Typography.h3, { color: colors.text, marginBottom: spacing.md }]}>Điều khiển nhanh</Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm }}>
            {QUICK_ACTIONS.map((action) => (
              <View key={action.id} style={{ width: '48%' }}>
                <QuickAction
                  icon={action.icon}
                  label={action.label}
                  onPress={() => handleQuickAction(action.id)}
                  active={quickActionBusy === action.id}
                  onConfigure={action.configurable ? () => handleConfigureAction(action.id) : undefined}
                />
              </View>
            ))}
          </View>
        </View>

        {/* Rooms preview */}
        <View style={{ padding: spacing.md, paddingTop: 0 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
            <Text style={[Typography.h3, { color: colors.text }]}>Phòng</Text>
            <Pressable onPress={() => router.push(roomsRoute)}>
              <Text style={[Typography.captionMedium, { color: colors.primary }]}>Xem tất cả</Text>
            </Pressable>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {rooms.map((room) => {
              const iconName = room.icon && room.icon in Feather.glyphMap
                ? (room.icon as keyof typeof Feather.glyphMap)
                : 'home';
              return (
                <Pressable
                  key={room.id}
                  onPress={() => router.push({ pathname: '/room/[id]' as never, params: { id: room.id } } as never)}
                  style={{
                    backgroundColor: colors.card,
                    borderRadius: BorderRadius.lg,
                    padding: spacing.md,
                    marginRight: spacing.sm,
                    width: roomCardWidth,
                    borderWidth: 1,
                    borderColor: colors.border,
                  }}
                >
                  <View style={{
                    width: scaled(36), height: scaled(36), borderRadius: scaled(10),
                    backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                    marginBottom: spacing.sm,
                  }}>
                    <Feather name={iconName} size={scaledIcon(16)} color={colors.primary} />
                  </View>
                  <Text style={[Typography.bodySmall, { color: colors.text }]} numberOfLines={1}>{room.name}</Text>
                  <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: spacing.xxs }]}>
                    {room.activeDevices}/{room.deviceCount} bật
                  </Text>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>

        {/* Face enroll */}
        <View style={{ padding: spacing.md, paddingTop: 0 }}>
          <Card>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm }}>
              <View
                style={{
                  width: scaled(32), height: scaled(32), borderRadius: scaled(10),
                  backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                }}
              >
                <Feather name="user-check" size={scaledIcon(16)} color={colors.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[Typography.h3, { color: colors.text }]}>Enroll khuon mat</Text>
                <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: spacing.xxs }]}>
                  Nhap ten de moi nha co the verify nhieu nguoi rieng biet.
                </Text>
              </View>
            </View>

            <TextInput
              value={facePersonId}
              onChangeText={setFacePersonId}
              placeholder="Ten nguoi"
              placeholderTextColor={colors.textTertiary}
              autoCapitalize="none"
              style={{
                minHeight: scaled(44),
                borderWidth: 1,
                borderColor: colors.border,
                borderRadius: BorderRadius.md,
                paddingHorizontal: spacing.md,
                color: colors.text,
                backgroundColor: colors.surface,
                marginTop: spacing.sm,
              }}
            />

            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.md }}>
              {Array.from({ length: 5 }).map((_, index) => {
                const image = faceImages[index];
                return (
                  <Pressable
                    key={index}
                    onPress={handlePickFaceImages}
                    style={{
                      width: scaled(56),
                      height: scaled(56),
                      borderRadius: BorderRadius.md,
                      borderWidth: 1,
                      borderColor: colors.border,
                      backgroundColor: colors.cardHover,
                      alignItems: 'center',
                      justifyContent: 'center',
                      overflow: 'hidden',
                    }}
                  >
                    {image ? (
                      <Image source={{ uri: image.uri }} style={{ width: '100%', height: '100%' }} />
                    ) : (
                      <Feather name="image" size={scaledIcon(18)} color={colors.iconMuted} />
                    )}
                  </Pressable>
                );
              })}
            </View>

            {faceEnrollMessage ? (
              <Text
                style={[
                  Typography.caption,
                  {
                    color: faceEnrollMessage.startsWith('Da enroll') ? colors.success : colors.error,
                    marginTop: spacing.sm,
                  },
                ]}
              >
                {faceEnrollMessage}
              </Text>
            ) : null}

            <View style={{ flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md }}>
              <Button
                title={`Chon anh (${faceImages.length}/5)`}
                variant="outline"
                onPress={handlePickFaceImages}
                icon={<Feather name="image" size={scaledIcon(16)} color={colors.primary} />}
                style={{ flex: 1 }}
              />
              <Button
                title="Enroll"
                onPress={handleEnrollFaceImages}
                loading={faceEnrollBusy}
                disabled={faceImages.length !== 5 || !homeId || !facePersonId.trim()}
                icon={<Feather name="upload-cloud" size={scaledIcon(16)} color="#FFFFFF" />}
                style={{ flex: 1 }}
              />
            </View>
          </Card>
        </View>

        <View style={{ height: spacing.xl }} />
      </ScrollView>
    </SafeAreaView>
  );
}
