import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, FlatList, Pressable, ActivityIndicator, useWindowDimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from '@/components/ui/Card';
import { AIInsight, AIInsightCard } from '@/components/AIInsightCard';
import { QuickAction } from '@/components/QuickAction';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { homesAPI, roomsAPI, suggestionsAPI, devicesAPI, DeviceResponse } from '@/services/api';
import { useWebSocket } from '@/hooks/use-websocket';
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

const ROOM_ICON_RULES: Array<{ match: RegExp; icon: keyof typeof Feather.glyphMap }> = [
  { match: /khach|living/, icon: 'tv' },
  { match: /ngu|bed/, icon: 'moon' },
  { match: /bep|kitchen/, icon: 'coffee' },
  { match: /tam|bath/, icon: 'droplet' },
  { match: /ban cong|balcony/, icon: 'sun' },
  { match: /gara|garage/, icon: 'truck' },
  { match: /lam viec|office/, icon: 'briefcase' },
  { match: /tre|kids|child/, icon: 'smile' },
  { match: /kho|storage/, icon: 'archive' },
];

function normalizeRoomName(name: string) {
  return name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function resolveRoomIcon(name: string, icon?: string | null) {
  if (icon) return icon;
  const normalized = normalizeRoomName(name);
  const rule = ROOM_ICON_RULES.find((item) => item.match.test(normalized));
  return rule?.icon ?? 'home';
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

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
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
  };

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
              const iconName = (room.icon || 'home') as keyof typeof Feather.glyphMap;
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

        <View style={{ height: spacing.xl }} />
      </ScrollView>
    </SafeAreaView>
  );
}
