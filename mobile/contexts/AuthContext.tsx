/**
 * Auth context — manages user authentication state for the mobile app.
 * Wraps the API service for login/register/logout.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react';
import {
    authAPI,
    setTokens,
    clearTokens,
    getAccessToken,
    getRefreshToken,
    hydrateTokensFromStorage,
    UserResponse,
    LoginResponse,
} from '@/services/api';

interface AuthState {
    user: UserResponse | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    isLoggingOut: boolean;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, fullName: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const logoutInFlightRef = useRef(false);
    const [state, setState] = useState<AuthState>({
        user: null,
        isAuthenticated: false,
        isLoading: true,
        isLoggingOut: false,
    });

    // Restore tokens first so web refresh keeps the login session.
    useEffect(() => {
        void bootstrapAuth();
    }, []);

    async function bootstrapAuth() {
        await hydrateTokensFromStorage();
        await loadUser();
    }

    async function loadUser() {
        if (logoutInFlightRef.current) {
            return;
        }

        if (!getAccessToken()) {
            setState((current) => ({ ...current, user: null, isAuthenticated: false, isLoading: false }));
            return;
        }

        try {
            const user = await authAPI.me();
            if (logoutInFlightRef.current) {
                return;
            }
            setState((current) => ({ ...current, user, isAuthenticated: true, isLoading: false }));
        } catch {
            clearTokens();
            if (logoutInFlightRef.current) {
                return;
            }
            setState((current) => ({ ...current, user: null, isAuthenticated: false, isLoading: false }));
        }
    }

    async function login(email: string, password: string) {
        const tokenData: LoginResponse = await authAPI.login(email, password);
        setTokens(tokenData.access_token, tokenData.refresh_token);
        const user = await authAPI.me();
        logoutInFlightRef.current = false;
        setState((current) => ({ ...current, user, isAuthenticated: true, isLoading: false }));
    }

    async function register(email: string, fullName: string, password: string) {
        await authAPI.register(email, fullName, password);
        // Auto-login after register
        await login(email, password);
    }

    async function logout() {
        if (logoutInFlightRef.current) {
            return;
        }

        logoutInFlightRef.current = true;
        const accessToken = getAccessToken();
        const refreshToken = getRefreshToken();
        clearTokens();
        setState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            isLoggingOut: true,
        });

        try {
            if (accessToken) {
                await authAPI.logout(accessToken, refreshToken);
            }
        } catch (error) {
            console.warn('Logout request failed, clearing local session anyway:', error);
        } finally {
            logoutInFlightRef.current = false;
            setState((current) => ({ ...current, isLoggingOut: false }));
        }
    }

    async function refreshUser() {
        if (logoutInFlightRef.current) {
            return;
        }
        await loadUser();
    }

    return (
        <AuthContext.Provider value={{ ...state, login, register, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextType {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
