import React, { useEffect, useRef } from 'react';
import { View, Text, Animated } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from './ui/Card';
import { Toggle } from './ui/Toggle';
import { Badge } from './ui/Badge';
import { Spacing } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export interface DeviceCardModel {
    id: string;
    name: string;
    type: string;
    icon?: string;
    isOnline: boolean;
    isOn: boolean;
    brightness?: number;
    temperature?: number;
    humidity?: number;
    battery?: number;
    speed?: string;
    door?: string;
    distanceCm?: number;
    distanceAlert?: boolean;
    gasDetected?: boolean;
    rainDetected?: boolean;
    distanceLight?: string;
    buzzer?: string;
}

interface DeviceCardProps {
    device: DeviceCardModel;
    onToggle: (id: string, value: boolean) => void;
    onPress: (device: DeviceCardModel) => void;
}

export function DeviceCard({ device, onToggle, onPress }: DeviceCardProps) {
    const { colors } = useTheme();
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const readOnlyTypes = new Set([
        'temperature_humidity',
        'distance_sensor',
        'gas_sensor',
        'rain_sensor',
        'sensor',
    ]);
    const noToggleTypes = new Set(['door', 'rain_servo']);
    const deviceType = device.type?.toLowerCase?.() ?? device.type;
    const isToggleAllowed = !readOnlyTypes.has(deviceType) && !noToggleTypes.has(deviceType);

    // Pulse animation when status changes
    useEffect(() => {
        Animated.sequence([
            Animated.timing(pulseAnim, { toValue: 1.03, duration: 150, useNativeDriver: true }),
            Animated.timing(pulseAnim, { toValue: 1, duration: 150, useNativeDriver: true }),
        ]).start();
    }, [device.isOn]);

    const iconName = (device.icon || 'circle') as keyof typeof Feather.glyphMap;

    return (
        <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <Card
                onPress={() => onPress(device)}
                style={{ opacity: device.isOnline ? 1 : 0.5 }}
            >
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <View
                        style={{
                            width: 44,
                            height: 44,
                            borderRadius: 12,
                            backgroundColor: device.isOn ? colors.primaryLight : colors.surface,
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderWidth: 1,
                            borderColor: device.isOn ? colors.primary + '40' : colors.border,
                        }}
                    >
                        <Feather
                            name={iconName}
                            size={20}
                            color={device.isOn ? colors.primary : colors.iconMuted}
                        />
                    </View>
                    {isToggleAllowed && (
                        <Toggle
                            value={device.isOn}
                            onToggle={(val) => {
                                onToggle(device.id, val);
                            }}
                            disabled={!device.isOnline}
                            size="sm"
                        />
                    )}
                </View>

                <View style={{ marginTop: Spacing.md }}>
                    <Text style={[Typography.bodyMedium, { color: colors.text }]} numberOfLines={1}>
                        {device.name}
                    </Text>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginTop: Spacing.xs }}>
                        <Badge variant={device.isOnline ? 'online' : 'offline'} />
                        {device.brightness !== undefined && device.isOn && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                {device.brightness}%
                            </Text>
                        )}
                        {device.speed && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Quat: {device.speed}
                            </Text>
                        )}
                        {device.door && deviceType !== 'rain_servo' && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Cua: {device.door}
                            </Text>
                        )}
                        {device.distanceCm !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                {device.distanceCm}cm
                            </Text>
                        )}
                        {device.gasDetected !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Gas: {device.gasDetected ? 'Co' : 'Khong'}
                            </Text>
                        )}
                        {device.rainDetected !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Mua: {device.rainDetected ? 'Co' : 'Khong'}
                            </Text>
                        )}
                        {device.distanceLight && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Den: {device.distanceLight}
                            </Text>
                        )}
                        {device.buzzer && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                Coi: {device.buzzer}
                            </Text>
                        )}
                        {device.temperature !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                {device.temperature}°C
                            </Text>
                        )}
                        {device.humidity !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                💧{device.humidity}%
                            </Text>
                        )}
                        {device.battery !== undefined && (
                            <Text style={[Typography.caption, { color: colors.textSecondary }]}>
                                🔋{device.battery}%
                            </Text>
                        )}
                    </View>
                </View>
            </Card>
        </Animated.View>
    );
}
