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

export default function RegisterScreen() {
    const { colors } = useTheme();
    const router = useRouter();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleRegister = () => {
        const newErrors: Record<string, string> = {};
        if (!name) newErrors.name = 'Vui lòng nhập họ tên';
        if (!email) newErrors.email = 'Vui lòng nhập email';
        else if (!email.includes('@')) newErrors.email = 'Email không hợp lệ';
        if (!password) newErrors.password = 'Vui lòng nhập mật khẩu';
        else if (password.length < 6) newErrors.password = 'Mật khẩu ít nhất 6 ký tự';
        if (password !== confirmPassword) newErrors.confirmPassword = 'Mật khẩu không khớp';

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
                    {/* Header */}
                    <View style={{ alignItems: 'center', marginBottom: Spacing.xl }}>
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
                            <Feather name="user-plus" size={32} color={colors.primary} />
                        </View>
                        <Text style={[Typography.displayMedium, { color: colors.text }]}>Tạo tài khoản</Text>
                        <Text style={[Typography.body, { color: colors.textSecondary, marginTop: Spacing.xs }]}>
                            Bắt đầu trải nghiệm nhà thông minh
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
                            label="Họ và tên"
                            placeholder="Nhập họ tên"
                            value={name}
                            onChangeText={(t) => { setName(t); setErrors((e) => ({ ...e, name: '' })); }}
                            error={errors.name}
                            icon="user"
                            autoCapitalize="words"
                        />
                        <Input
                            label="Email"
                            placeholder="email@example.com"
                            value={email}
                            onChangeText={(t) => { setEmail(t); setErrors((e) => ({ ...e, email: '' })); }}
                            error={errors.email}
                            icon="mail"
                            keyboardType="email-address"
                        />
                        <Input
                            label="Mật khẩu"
                            placeholder="Ít nhất 6 ký tự"
                            value={password}
                            onChangeText={(t) => { setPassword(t); setErrors((e) => ({ ...e, password: '' })); }}
                            error={errors.password}
                            icon="lock"
                            secureTextEntry
                        />
                        <Input
                            label="Xác nhận mật khẩu"
                            placeholder="Nhập lại mật khẩu"
                            value={confirmPassword}
                            onChangeText={(t) => { setConfirmPassword(t); setErrors((e) => ({ ...e, confirmPassword: '' })); }}
                            error={errors.confirmPassword}
                            icon="lock"
                            secureTextEntry
                        />

                        <Button title="Đăng ký" onPress={handleRegister} loading={loading} size="lg" />
                    </View>

                    {/* Login link */}
                    <View style={{ flexDirection: 'row', justifyContent: 'center', marginTop: Spacing.lg, gap: Spacing.xs }}>
                        <Text style={[Typography.body, { color: colors.textSecondary }]}>Đã có tài khoản?</Text>
                        <Pressable onPress={() => router.back()}>
                            <Text style={[Typography.bodyMedium, { color: colors.primary }]}>Đăng nhập</Text>
                        </Pressable>
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
