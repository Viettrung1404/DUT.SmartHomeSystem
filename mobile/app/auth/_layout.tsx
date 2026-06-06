import React from 'react';
import { Stack, Redirect } from 'expo-router';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthLayout() {
    const { colors } = useTheme();
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return null;
    }

    if (isAuthenticated) {
        return <Redirect href="/(tabs)" />;
    }

    return (
        <Stack
            screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: colors.background },
            }}
        >
            <Stack.Screen name="login" />
            <Stack.Screen name="register" />
        </Stack>
    );
}
