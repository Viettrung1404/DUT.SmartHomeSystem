/**
 * Smart Home Design System
 * Emerald Green dual-theme (Light / Dark)
 * 8pt spacing grid, 16px border radius
 */

export const LightTheme = {
  background: '#F8FAFC',
  surface: '#FFFFFF',
  card: '#FFFFFF',
  cardHover: '#F1F5F9',
  primary: '#10B981',
  primaryLight: '#ECFDF5',
  primaryDark: '#059669',
  secondary: '#6366F1',
  text: '#0F172A',
  textSecondary: '#475569',
  textTertiary: '#94A3B8',
  border: '#E2E8F0',
  borderLight: '#F1F5F9',
  icon: '#475569',
  iconMuted: '#94A3B8',
  success: '#16A34A',
  successLight: '#DCFCE7',
  warning: '#F59E0B',
  warningLight: '#FEF3C7',
  error: '#EF4444',
  errorLight: '#FEE2E2',
  shadow: 'rgba(15, 23, 42, 0.08)',
  shadowMd: 'rgba(15, 23, 42, 0.12)',
  overlay: 'rgba(15, 23, 42, 0.5)',
  tabBar: '#FFFFFF',
  tabBarBorder: '#E2E8F0',
  statusBar: 'dark' as const,
  // AI specific
  aiBackground: '#ECFDF5',
  aiBorder: '#A7F3D0',
  aiGlow: 'rgba(16, 185, 129, 0.2)',
  // Chart
  chartGrid: '#E2E8F0',
  chartLabel: '#64748B',
  chartBar1: '#10B981',
  chartBar2: '#34D399',
  chartBar3: '#6EE7B7',
  // Risk levels
  riskLow: '#16A34A',
  riskMedium: '#F59E0B',
  riskHigh: '#EF4444',
};

export const DarkTheme = {
  background: '#0F172A',
  surface: '#1E293B',
  card: '#1E293B',
  cardHover: '#334155',
  primary: '#34D399',
  primaryLight: '#052E2B',
  primaryDark: '#10B981',
  secondary: '#818CF8',
  text: '#F1F5F9',
  textSecondary: '#94A3B8',
  textTertiary: '#64748B',
  border: '#334155',
  borderLight: '#1E293B',
  icon: '#94A3B8',
  iconMuted: '#64748B',
  success: '#22C55E',
  successLight: '#052E16',
  warning: '#FBBF24',
  warningLight: '#422006',
  error: '#F87171',
  errorLight: '#450A0A',
  shadow: 'rgba(0, 0, 0, 0.3)',
  shadowMd: 'rgba(0, 0, 0, 0.5)',
  overlay: 'rgba(0, 0, 0, 0.6)',
  tabBar: '#1E293B',
  tabBarBorder: '#334155',
  statusBar: 'light' as const,
  // AI specific
  aiBackground: '#052E2B',
  aiBorder: '#34D399',
  aiGlow: 'rgba(52, 211, 153, 0.3)',
  // Chart
  chartGrid: '#334155',
  chartLabel: '#94A3B8',
  chartBar1: '#34D399',
  chartBar2: '#10B981',
  chartBar3: '#059669',
  // Risk levels
  riskLow: '#22C55E',
  riskMedium: '#FBBF24',
  riskHigh: '#F87171',
};

export type ThemeColors = typeof LightTheme | typeof DarkTheme;

export const Spacing = {
  xxs: 2,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

export const BorderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
} as const;

export const Shadow = {
  sm: {
    shadowOffset: { width: 0, height: 1 },
    shadowRadius: 3,
    shadowOpacity: 1,
    elevation: 2,
  },
  md: {
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 12,
    shadowOpacity: 1,
    elevation: 4,
  },
  lg: {
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 24,
    shadowOpacity: 1,
    elevation: 8,
  },
} as const;

export const Fonts = {
  rounded: 'System',
  mono: 'monospace',
} as const;
