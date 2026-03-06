import React from 'react';
import { Tabs } from 'expo-router';
import { View, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Feather } from '@expo/vector-icons';
import { BorderRadius } from '@/constants/theme';

export default function TabLayout() {
  const { colors } = useTheme();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.iconMuted,
        tabBarStyle: {
          backgroundColor: colors.tabBar,
          borderTopColor: colors.tabBarBorder,
          borderTopWidth: 1,
          height: 82,
          paddingTop: 8,
          paddingBottom: 80,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '500',
          marginTop: 2,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Trang chủ',
          tabBarIcon: ({ color, size }) => <Feather name="home" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="rooms"
        options={{
          title: 'Phòng',
          tabBarIcon: ({ color, size }) => <Feather name="grid" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="automation"
        options={{
          title: 'Tự động',
          tabBarIcon: ({ color, size }) => <Feather name="zap" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="security"
        options={{
          title: 'An ninh',
          tabBarIcon: ({ color, size }) => <Feather name="shield" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="assistant"
        options={{
          title: 'Trợ lý',
          tabBarIcon: ({ color, size }) => <Feather name="message-circle" size={22} color={color} />,
        }}
      />
    </Tabs>
  );
}
