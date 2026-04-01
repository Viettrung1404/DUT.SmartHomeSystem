import React from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export interface SecurityAlert {
    id: string;
    message: string;
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
    icon?: string;
}

interface SecurityStatusCardProps {
    alert: SecurityAlert;
}

export function SecurityStatusCard({ alert }: SecurityStatusCardProps) {
    const { colors } = useTheme();
    const severityColors = { low: colors.riskLow, medium: colors.riskMedium, high: colors.riskHigh };
    const iconName = (alert.icon === 'door-open' ? 'log-in' : alert.icon === 'wifi-off' ? 'wifi-off' : alert.icon || 'alert-circle') as keyof typeof Feather.glyphMap;

    return (
        <Card
            style={{
                borderLeftWidth: 3,
                borderLeftColor: severityColors[alert.severity],
            }}
        >
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                <View
                    style={{
                        width: 40,
                        height: 40,
                        borderRadius: 20,
                        backgroundColor: severityColors[alert.severity] + '15',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Feather name={iconName} size={18} color={severityColors[alert.severity]} />
                </View>
                <View style={{ flex: 1 }}>
                    <Text style={[Typography.bodySmall, { color: colors.text }]}>{alert.message}</Text>
                    <Text style={[Typography.caption, { color: colors.textTertiary, marginTop: 2 }]}>{alert.timestamp}</Text>
                </View>
                <Badge variant="risk" riskLevel={alert.severity} />
            </View>
        </Card>
    );
}
