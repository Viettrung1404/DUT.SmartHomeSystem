/**
 * ThemeContext — Dark / Light / System auto-detect with manual toggle.
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { useColorScheme as useSystemColorScheme } from 'react-native';
import { LightTheme, DarkTheme, ThemeColors } from '@/constants/theme';

export type ThemeMode = 'light' | 'dark' | 'system';

interface ThemeContextValue {
    mode: ThemeMode;
    isDark: boolean;
    colors: ThemeColors;
    setMode: (mode: ThemeMode) => void;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
    mode: 'system',
    isDark: false,
    colors: LightTheme,
    setMode: () => { },
    toggleTheme: () => { },
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const systemScheme = useSystemColorScheme();
    const [mode, setMode] = useState<ThemeMode>('system');

    const isDark = useMemo(() => {
        if (mode === 'system') return systemScheme === 'dark';
        return mode === 'dark';
    }, [mode, systemScheme]);

    const colors = useMemo(() => (isDark ? DarkTheme : LightTheme), [isDark]);

    const toggleTheme = useCallback(() => {
        setMode((prev) => {
            if (prev === 'system') return isDark ? 'light' : 'dark';
            return prev === 'dark' ? 'light' : 'dark';
        });
    }, [isDark]);

    const value = useMemo(
        () => ({ mode, isDark, colors, setMode, toggleTheme }),
        [mode, isDark, colors, setMode, toggleTheme],
    );

    return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
    return useContext(ThemeContext);
}
