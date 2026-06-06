import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';
import { AuthProvider } from '@/contexts/AuthContext';

function InnerLayout() {
  const { isDark, colors } = useTheme();

  return (
    <>
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="auth" options={{ animation: 'fade' }} />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen
          name="room/[id]"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="room/[id]/manage"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="rooms/manage"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="device/[id]"
          options={{ animation: 'slide_from_bottom', presentation: 'modal' }}
        />
        <Stack.Screen
          name="automation/create"
          options={{ animation: 'slide_from_bottom', presentation: 'modal' }}
        />
        <Stack.Screen
          name="quick-actions/[action]"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="settings/index"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="settings/home"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="settings/account"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="settings/connectivity"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="settings/about"
          options={{ animation: 'slide_from_right' }}
        />
      </Stack>
      <StatusBar style={isDark ? 'light' : 'dark'} />
    </>
  );
}

export default function RootLayout() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <InnerLayout />
      </AuthProvider>
    </ThemeProvider>
  );
}
