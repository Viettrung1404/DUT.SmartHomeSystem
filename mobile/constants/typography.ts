/**
 * Typography scale for Smart Home app.
 * Uses system fonts on each platform for best Vietnamese rendering.
 */

import { Platform, TextStyle } from 'react-native';

const fontFamily = Platform.select({
    ios: 'System',
    android: 'Roboto',
    default: 'System',
});

const fontFamilyMono = Platform.select({
    ios: 'Menlo',
    android: 'monospace',
    default: 'monospace',
});

type TypographyVariant = {
    fontSize: number;
    lineHeight: number;
    fontWeight: TextStyle['fontWeight'];
    letterSpacing?: number;
};

export const Typography: Record<string, TypographyVariant> = {
    // Display
    displayLarge: {
        fontSize: 32,
        lineHeight: 40,
        fontWeight: '700',
        letterSpacing: -0.5,
    },
    displayMedium: {
        fontSize: 28,
        lineHeight: 36,
        fontWeight: '700',
        letterSpacing: -0.3,
    },

    // Headings
    h1: {
        fontSize: 24,
        lineHeight: 32,
        fontWeight: '700',
        letterSpacing: -0.2,
    },
    h2: {
        fontSize: 20,
        lineHeight: 28,
        fontWeight: '600',
    },
    h3: {
        fontSize: 18,
        lineHeight: 26,
        fontWeight: '600',
    },

    // Body
    bodyLarge: {
        fontSize: 16,
        lineHeight: 24,
        fontWeight: '400',
    },
    body: {
        fontSize: 14,
        lineHeight: 22,
        fontWeight: '400',
    },
    bodyMedium: {
        fontSize: 14,
        lineHeight: 22,
        fontWeight: '500',
    },
    bodySmall: {
        fontSize: 13,
        lineHeight: 20,
        fontWeight: '400',
    },

    // Caption / Label
    caption: {
        fontSize: 12,
        lineHeight: 16,
        fontWeight: '400',
        letterSpacing: 0.2,
    },
    captionMedium: {
        fontSize: 12,
        lineHeight: 16,
        fontWeight: '500',
        letterSpacing: 0.2,
    },
    label: {
        fontSize: 11,
        lineHeight: 14,
        fontWeight: '600',
        letterSpacing: 0.5,
    },

    // Button
    button: {
        fontSize: 15,
        lineHeight: 20,
        fontWeight: '600',
    },
    buttonSmall: {
        fontSize: 13,
        lineHeight: 18,
        fontWeight: '600',
    },

    // Number / Data
    number: {
        fontSize: 20,
        lineHeight: 24,
        fontWeight: '700',
        letterSpacing: -0.3,
    },
    numberLarge: {
        fontSize: 28,
        lineHeight: 32,
        fontWeight: '700',
        letterSpacing: -0.5,
    },
};

export { fontFamily, fontFamilyMono };
