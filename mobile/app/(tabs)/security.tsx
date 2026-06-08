import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/ui/Header';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { SecurityStatusCard } from '@/components/SecurityStatusCard';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';
import { faceAPI, homesAPI, securityAPI } from '@/services/api';
import { SecurityAlert } from '@/components/SecurityStatusCard';

interface SelectedFaceImage {
    name: string;
    base64: string;
}

function readFileAsDataUrl(file: any): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new (globalThis as any).FileReader();
        reader.onload = () => resolve(String(reader.result ?? ''));
        reader.onerror = () => reject(new Error('Không thể đọc file ảnh'));
        reader.readAsDataURL(file);
    });
}

export default function SecurityScreen() {
    const { colors } = useTheme();
    const webFileInputRef = useRef<any>(null);
    const [homeId, setHomeId] = useState('');
    const [homeName, setHomeName] = useState('');
    const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
    const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high'>('low');
    const [personId, setPersonId] = useState('');
    const [selectedImages, setSelectedImages] = useState<SelectedFaceImage[]>([]);
    const [enrollLoading, setEnrollLoading] = useState(false);
    const [enrollMessage, setEnrollMessage] = useState('');
    const [enrollError, setEnrollError] = useState('');

    useEffect(() => {
        loadSecurity();
    }, []);

    const loadSecurity = async () => {
        try {
            const homes = await homesAPI.list();
            if (!homes.length) {
                setHomeId('');
                setHomeName('');
                return;
            }

            const primaryHome = homes[0];
            setHomeId(primaryHome.id);
            setHomeName(primaryHome.name);
            const [summary, events] = await Promise.all([
                securityAPI.summary(primaryHome.id),
                securityAPI.events(primaryHome.id, 20),
            ]);

            const normalizedRisk = (summary.risk_level === 'high' || summary.risk_level === 'medium')
                ? summary.risk_level
                : 'low';
            setRiskLevel(normalizedRisk);
            setAlerts(
                events.map((event) => ({
                    id: event.id,
                    message: event.description,
                    timestamp: new Date(event.timestamp).toLocaleString('vi-VN'),
                    severity: event.severity === 'high' || event.severity === 'medium' ? event.severity : 'low',
                    icon: event.event_type === 'door' ? 'door-open' : event.event_type === 'camera_offline' ? 'wifi-off' : 'alert-circle',
                })),
            );
        } catch (error) {
            console.error('Failed to load security data:', error);
            setAlerts([]);
            setRiskLevel('low');
        }
    };

    const handlePickImages = () => {
        setEnrollError('');
        setEnrollMessage('');

        if (Platform.OS !== 'web') {
            setEnrollError('Chọn ảnh 5 tấm hiện chỉ hỗ trợ trên bản web của app.');
            return;
        }

        webFileInputRef.current?.click?.();
    };

    const handleWebFileChange = async (event: any) => {
        const files = Array.from(event?.target?.files ?? []) as any[];
        if (!files.length) return;

        try {
            const nextImages = await Promise.all(
                files.slice(0, 5).map(async (file) => ({
                    name: String(file?.name ?? 'image.jpg'),
                    base64: await readFileAsDataUrl(file),
                })),
            );
            setSelectedImages(nextImages);
            setEnrollError('');
            setEnrollMessage(`Đã chọn ${nextImages.length} ảnh. Hãy chọn đủ 5 ảnh để ghi đè gallery hiện tại.`);
        } catch (error) {
            console.error('Failed to read selected face images:', error);
            setEnrollError('Không thể đọc ảnh đã chọn.');
        } finally {
            event.target.value = '';
        }
    };

    const handleEnrollBatch = async () => {
        if (!homeId) {
            setEnrollError('Chưa có nhà nào để enroll ảnh.');
            return;
        }

        if (selectedImages.length !== 5) {
            setEnrollError('Cần đúng 5 ảnh để replace gallery hiện tại.');
            return;
        }

        const finalPersonId = personId.trim() || homeId;
        try {
            setEnrollLoading(true);
            setEnrollError('');
            setEnrollMessage('Đang xoá ảnh cũ và ghi 5 ảnh mới...');
            const response = await faceAPI.enrollBatch(
                homeId,
                finalPersonId,
                selectedImages.map((image) => image.base64),
            );

            setEnrollMessage(
                `Đã xoá ${response.deleted_count} file cũ và lưu ${response.saved_count} ảnh mới cho nhà ${homeName || homeId}.`,
            );
            setSelectedImages([]);
        } catch (error) {
            console.error('Failed to replace face gallery:', error);
            setEnrollError(error instanceof Error ? error.message : 'Không thể enroll 5 ảnh.');
        } finally {
            setEnrollLoading(false);
        }
    };

    // Mock security overview
    const doorStatus = [
        { name: 'Cửa trước', locked: true, online: true },
        { name: 'Cửa sau', locked: true, online: true },
        { name: 'Cửa garage', locked: true, online: false },
    ];

    const cameras = [
        { name: 'Camera phòng khách', online: true },
        { name: 'Camera ban công', online: true },
        { name: 'Camera garage', online: false },
    ];

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
            <Header title="Trung tâm An ninh" />
            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ padding: Spacing.md }}>
                {/* Risk Level */}
                <Card style={{ marginBottom: Spacing.md, alignItems: 'center', paddingVertical: Spacing.lg }}>
                    <View
                        style={{
                            width: 64, height: 64, borderRadius: 32,
                            backgroundColor: (riskLevel === 'high' ? colors.riskHigh : riskLevel === 'medium' ? colors.riskMedium : colors.riskLow) + '15',
                            alignItems: 'center', justifyContent: 'center', marginBottom: Spacing.md,
                        }}
                    >
                        <Feather
                            name="shield"
                            size={28}
                            color={riskLevel === 'high' ? colors.riskHigh : riskLevel === 'medium' ? colors.riskMedium : colors.riskLow}
                        />
                    </View>
                    <Badge variant="risk" riskLevel={riskLevel} />
                    <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.sm, textAlign: 'center' }]}>
                        {riskLevel === 'high' ? 'Có vấn đề cần xử lý ngay' : riskLevel === 'medium' ? 'Cần chú ý một số cảnh báo' : 'Mọi thứ an toàn'}
                    </Text>
                </Card>

                {/* Face Enrollment */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Enroll 5 ảnh</Text>
                <Card style={{ marginBottom: Spacing.md }}>
                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>Thay toàn bộ bộ ảnh cho nhà hiện tại</Text>
                    <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.xs }]}>Nhà: {homeName || 'Chưa có nhà'}{homeId ? ` • ${homeId}` : ''}</Text>

                    <View style={{ marginTop: Spacing.md }}>
                        <Input
                            label="Person ID"
                            placeholder="Để trống để dùng UUID nhà"
                            value={personId}
                            onChangeText={setPersonId}
                            icon="user"
                        />
                    </View>

                    {Platform.OS === 'web' && React.createElement('input' as any, {
                        ref: webFileInputRef,
                        type: 'file',
                        accept: 'image/*',
                        multiple: true,
                        style: { display: 'none' },
                        onChange: handleWebFileChange,
                    })}

                    <View style={{ flexDirection: 'row', gap: Spacing.sm, flexWrap: 'wrap' }}>
                        <Button
                            title="Chọn 5 ảnh"
                            onPress={handlePickImages}
                            variant="outline"
                            icon={<Feather name="image" size={16} color={colors.primary} />}
                            style={{ flexGrow: 1, minWidth: 150 }}
                        />
                        <Button
                            title="Xoá & enroll"
                            onPress={handleEnrollBatch}
                            loading={enrollLoading}
                            disabled={selectedImages.length !== 5 || !homeId}
                            icon={<Feather name="shield" size={16} color="#FFFFFF" />}
                            style={{ flexGrow: 1, minWidth: 150 }}
                        />
                    </View>

                    <Text style={[Typography.caption, { color: colors.textSecondary, marginTop: Spacing.sm }]}>
                        {selectedImages.length}/5 ảnh đã chọn. Chỉ khi đủ 5 ảnh mới ghi đè gallery hiện tại.
                    </Text>

                    {selectedImages.length > 0 && (
                        <View style={{ marginTop: Spacing.sm, gap: Spacing.xs }}>
                            {selectedImages.map((image, index) => (
                                <View
                                    key={`${image.name}-${index}`}
                                    style={{
                                        paddingVertical: Spacing.xs,
                                        paddingHorizontal: Spacing.sm,
                                        backgroundColor: colors.surface,
                                        borderRadius: BorderRadius.md,
                                        borderWidth: 1,
                                        borderColor: colors.border,
                                    }}
                                >
                                    <Text style={[Typography.caption, { color: colors.text }]} numberOfLines={1}>
                                        {index + 1}. {image.name}
                                    </Text>
                                </View>
                            ))}
                        </View>
                    )}

                    {!!enrollMessage && (
                        <Text style={[Typography.caption, { color: colors.success, marginTop: Spacing.sm }]}>
                            {enrollMessage}
                        </Text>
                    )}
                    {!!enrollError && (
                        <Text style={[Typography.caption, { color: colors.error, marginTop: Spacing.sm }]}>
                            {enrollError}
                        </Text>
                    )}
                </Card>

                {/* Doors & Locks */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Cửa & Khóa</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.lg }}>
                    {doorStatus.map((door, i) => (
                        <Card key={i}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <View
                                    style={{
                                        width: 40, height: 40, borderRadius: 20,
                                        backgroundColor: door.locked ? colors.successLight : colors.warningLight,
                                        alignItems: 'center', justifyContent: 'center',
                                    }}
                                >
                                    <Feather name={door.locked ? 'lock' : 'unlock'} size={18} color={door.locked ? colors.success : colors.warning} />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{door.name}</Text>
                                    <Text style={[Typography.caption, { color: door.locked ? colors.success : colors.warning }]}>
                                        {door.locked ? 'Đã khóa' : 'Chưa khóa'}
                                    </Text>
                                </View>
                                <Badge variant={door.online ? 'online' : 'offline'} />
                            </View>
                        </Card>
                    ))}
                </View>

                {/* Cameras */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Camera</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.lg }}>
                    {cameras.map((cam, i) => (
                        <Card key={i}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                                <View
                                    style={{
                                        width: 40, height: 40, borderRadius: 20,
                                        backgroundColor: cam.online ? colors.primaryLight : colors.errorLight,
                                        alignItems: 'center', justifyContent: 'center',
                                    }}
                                >
                                    <Feather name="video" size={18} color={cam.online ? colors.primary : colors.error} />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[Typography.bodyMedium, { color: colors.text }]}>{cam.name}</Text>
                                </View>
                                <Badge variant={cam.online ? 'online' : 'offline'} label={cam.online ? 'Trực tuyến' : 'Ngoại tuyến'} />
                            </View>
                            {cam.online && (
                                <View
                                    style={{
                                        height: 120, backgroundColor: colors.surface, borderRadius: BorderRadius.md,
                                        marginTop: Spacing.sm, alignItems: 'center', justifyContent: 'center',
                                        borderWidth: 1, borderColor: colors.border,
                                    }}
                                >
                                    <Feather name="play-circle" size={32} color={colors.textTertiary} />
                                    <Text style={[Typography.caption, { color: colors.textTertiary, marginTop: Spacing.xs }]}>Nhấn để xem</Text>
                                </View>
                            )}
                        </Card>
                    ))}
                </View>

                {/* Alert History */}
                <Text style={[Typography.h3, { color: colors.text, marginBottom: Spacing.sm }]}>Lịch sử cảnh báo</Text>
                <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
                    {alerts.map((alert) => (
                        <SecurityStatusCard key={alert.id} alert={alert} />
                    ))}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
