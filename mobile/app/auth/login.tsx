import React, { useState } from 'react';
import { View, Text, ScrollView, KeyboardAvoidingView, Platform, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Spacing, BorderRadius } from '@/constants/theme';
import { Typography } from '@/constants/typography';
import { Feather } from '@expo/vector-icons';

export default function LoginScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

    const handleLogin = () => {
        const newErrors: typeof errors = {};
        if (!email) newErrors.email = 'Vui lòng nhập email';
        else if (!email.includes('@')) newErrors.email = 'Email không hợp lệ';
        if (!password) newErrors.password = 'Vui lòng nhập mật khẩu';
        else if (password.length < 6) newErrors.password = 'Mật khẩu ít nhất 6 ký tự';

        setErrors(newErrors);
        if (Object.keys(newErrors).length > 0) return;

        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            router.replace('/(tabs)');
        }, 1500);
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={{ flex: 1 }}
            >
                <ScrollView
                    contentContainerStyle={{
                        flexGrow: 1,
                        justifyContent: 'center',
                        padding: Spacing.lg,
                    }}
                    keyboardShouldPersistTaps="handled"
                >
                    {/* Logo / Brand */}
                    <View style={{ alignItems: 'center', marginBottom: Spacing.xxl }}>
                        <View
                            style={{
                                width: 72,
                                height: 72,
                                borderRadius: 20,
                                backgroundColor: colors.primaryLight,
                                alignItems: 'center',
                                justifyContent: 'center',
                                marginBottom: Spacing.md,
                            }}
                        >
                            <Feather name="home" size={32} color={colors.primary} />
                        </View>
                        <Text style={[Typography.displayMedium, { color: colors.text }]}>Smart Home</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Chào mừng bạn trở lại
                        </Text>
                    </View>

                    {/* Form */}
                    <View
                        style={{
                            backgroundColor: colors.card,
                            borderRadius: BorderRadius.xl,
                            padding: Spacing.lg,
                            borderWidth: 1,
                            borderColor: colors.border,
                        }}
                    >
                        <Input
                            label="Email"
                            placeholder="email@example.com"
                            value={email}
                            onChangeText={(t) => { setEmail(t); setErrors((e) => ({ ...e, email: undefined })); }}
                            error={errors.email}
                            icon="mail"
                            keyboardType="email-address"
                        />
                        <Input
                            label="Mật khẩu"
                            placeholder="Nhập mật khẩu"
                            value={password}
                            onChangeText={(t) => { setPassword(t); setErrors((e) => ({ ...e, password: undefined })); }}
                            error={errors.password}
                            icon="lock"
                            secureTextEntry
                        />

                        <Pressable style={{ alignSelf: 'flex-end', marginBottom: Spacing.lg, marginTop: -Spacing.sm }}>
                            <Text style={[Typography.captionMedium, { color: colors.primary }]}>Quên mật khẩu?</Text>
                        </Pressable>

                        <Button title="Đăng nhập" onPress={handleLogin} loading={loading} size="lg" />
                    </View>

                    {/* Register link */}
                    <View style={{ flexDirection: 'row', justifyContent: 'center', marginTop: Spacing.lg, gap: Spacing.xs }}>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Chưa có tài khoản?</Text>
                        <Pressable onPress={() => router.push('/auth/register')}>
                            <Text style={[Typography.bodyMedium, { color: colors.primary }]}>Đăng ký</Text>
                        </Pressable>
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
