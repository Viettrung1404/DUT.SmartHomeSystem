import React, { useState } from 'react';
import { View, Text, ScrollView, FlatList, Pressable } from 'react-native';
import { useRouter, type Href } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from '@/components/ui/Card';
import { AIInsightCard } from '@/components/AIInsightCard';
import { QuickAction } from '@/components/QuickAction';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { mockHome, mockAIInsights, mockRooms } from '@/services/mockData';

export default function DashboardScreen() {
  const { colors, toggleTheme, isDark } = useTheme();
  const router = useRouter();
  const [insights, setInsights] = useState(mockAIInsights);
  const settingsRoute = '/settings' as unknown as Href;
  const energyRoute = '/energy' as unknown as Href;
  const roomsRoute = '/(tabs)/rooms' as unknown as Href;

  const energyChange = ((mockHome.energyToday - mockHome.energyYesterday) / mockHome.energyYesterday * 100).toFixed(0);
  const isEnergyUp = mockHome.energyToday > mockHome.energyYesterday;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={{ padding: Spacing.md, paddingBottom: 0 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <View>
              <Text style={[Typography.caption, { color: colors.textSecondary }]}>Xin chào, Trung 👋</Text>
              <Text style={[Typography.h1, { color: colors.text, marginTop: Spacing.xxs }]}>{mockHome.name}</Text>
            </View>
            <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
              <Pressable
                onPress={toggleTheme}
                style={{
                  width: 40, height: 40, borderRadius: 20,
                  backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
                  borderWidth: 1, borderColor: colors.border,
                }}
              >
                <Feather name={isDark ? 'sun' : 'moon'} size={18} color={colors.icon} />
              </Pressable>
              <Pressable
                onPress={() => router.push(settingsRoute)}
                style={{
                  width: 40, height: 40, borderRadius: 20,
                  backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
                  borderWidth: 1, borderColor: colors.border,
                }}
              >
                <Feather name="settings" size={18} color={colors.icon} />
              </Pressable>
            </View>
          </View>

          {/* Weather mini */}
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs, marginTop: Spacing.sm }}>
            <Feather name="cloud" size={14} color={colors.textSecondary} />
            <Text style={[Typography.caption, { color: colors.textSecondary }]}>Đà Nẵng • 30°C • Nhiều mây</Text>
          </View>
        </View>

        {/* Stats Row */}
        <View style={{ flexDirection: 'row', gap: Spacing.sm, padding: Spacing.md }}>
          {/* Energy card */}
          <Card
            onPress={() => router.push(energyRoute)}
            style={{ flex: 1 }}
          >
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs }}>
              <Feather name="zap" size={14} color={colors.warning} />
              <Text style={[Typography.caption, { color: colors.textSecondary }]}>Điện hôm nay</Text>
            </View>
            <Text style={[Typography.number, { color: colors.text, marginTop: Spacing.xs }]}>
              {mockHome.energyToday} <Text style={[Typography.caption, { color: colors.textSecondary }]}>kWh</Text>
            </Text>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 2, marginTop: Spacing.xxs }}>
              <Feather name={isEnergyUp ? 'trending-up' : 'trending-down'} size={12} color={isEnergyUp ? colors.error : colors.success} />
              <Text style={[Typography.caption, { color: isEnergyUp ? colors.error : colors.success }]}>
                {isEnergyUp ? '+' : ''}{energyChange}%
              </Text>
            </View>
          </Card>
          {/* Devices card */}
          <Card style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.xs }}>
              <Feather name="cpu" size={14} color={colors.primary} />
              <Text style={[Typography.caption, { color: colors.textSecondary }]}>Thiết bị</Text>
            </View>
            <Text style={[Typography.number, { color: colors.text, marginTop: Spacing.xs }]}>
              {mockHome.activeDevices} <Text style={[Typography.caption, { color: colors.textSecondary }]}>/ {mockHome.deviceCount}</Text>
            </Text>
            <Text style={[Typography.caption, { color: colors.success, marginTop: Spacing.xxs }]}>đang hoạt động</Text>
          </Card>
        </View>

        {/* AI Insights */}
        <View style={{ paddingLeft: Spacing.md, marginBottom: Spacing.md }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md }}>
            <View
              style={{
                width: 28, height: 28, borderRadius: 14,
                backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Feather name="cpu" size={14} color={colors.primary} />
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
                onAccept={(id) => setInsights((p) => p.filter((i) => i.id !== id))}
                onDismiss={(id) => setInsights((p) => p.filter((i) => i.id !== id))}
              />
            )}
          />
        </View>

        {/* Quick Actions */}
        <View style={{ padding: Spacing.md, paddingTop: 0 }}>
          <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.md }]}>Điều khiển nhanh</Text>
          <View style={{ flexDirection: 'row', gap: Spacing.sm }}>
            <QuickAction icon="sunset" label="Tắt toàn bộ đèn" onPress={() => { }} />
            <QuickAction icon="moon" label="Chế độ đêm" onPress={() => { }} />
            <QuickAction icon="log-out" label="Rời khỏi nhà" onPress={() => { }} />
            <QuickAction icon="home" label="Về nhà" onPress={() => { }} />
          </View>
        </View>

        {/* Rooms preview */}
        <View style={{ padding: Spacing.md, paddingTop: 0 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.md }}>
            <Text style={[Typography.h3, { color: colors.text }]}>Phòng</Text>
            <Pressable onPress={() => router.push(roomsRoute)}>
              <Text style={[Typography.captionMedium, { color: colors.primary }]}>Xem tất cả</Text>
            </Pressable>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {mockRooms.slice(0, 4).map((room) => {
              const iconName = (room.icon || 'home') as keyof typeof Feather.glyphMap;
              return (
                <Pressable
                  key={room.id}
                  onPress={() => router.push({ pathname: '/room/[id]' as never, params: { id: room.id } } as never)}
                  style={{
                    backgroundColor: colors.card,
                    borderRadius: BorderRadius.lg,
                    padding: Spacing.md,
                    marginRight: Spacing.sm,
                    width: 140,
                    borderWidth: 1,
                    borderColor: colors.border,
                  }}
                >
                  <View style={{
                    width: 36, height: 36, borderRadius: 10,
                    backgroundColor: colors.primaryLight, alignItems: 'center', justifyContent: 'center',
                    marginBottom: Spacing.sm,
                  }}>
                    <Feather name={iconName} size={16} color={colors.primary} />
                  </View>
                  <Text style={[Typography.bodySmall, { color: colors.text }]} numberOfLines={1}>{room.name}</Text>
                  <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: 2 }]}>
                    {room.activeDevices}/{room.deviceCount} bật
                  </Text>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>

        <View style={{ height: Spacing.xl }} />
      </ScrollView>
    </SafeAreaView>
  );
}
