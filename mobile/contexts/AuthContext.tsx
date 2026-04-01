/**
 * Auth context — manages user authentication state for the mobile app.
 * Wraps the API service for login/register/logout.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, setTokens, clearTokens, getAccessToken, UserResponse, LoginResponse } from '@/services/api';

interface AuthState {
    user: UserResponse | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, fullName: string, password: string) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [state, setState] = useState<AuthState>({
        user: null,
        isAuthenticated: false,
        isLoading: true,
    });

    // Try to load user on mount (if tokens exist)
    useEffect(() => {
        loadUser();
    }, []);

    async function loadUser() {
        if (!getAccessToken()) {
            setState({ user: null, isAuthenticated: false, isLoading: false });
            return;
        }

        try {
            const user = await authAPI.me();
            setState({ user, isAuthenticated: true, isLoading: false });
        } catch {
            setState({ user: null, isAuthenticated: false, isLoading: false });
        }
    }

    async function login(email: string, password: string) {
        const tokenData: LoginResponse = await authAPI.login(email, password);
        setTokens(tokenData.access_token, tokenData.refresh_token);
        const user = await authAPI.me();
        setState({ user, isAuthenticated: true, isLoading: false });
    }

    async function register(email: string, fullName: string, password: string) {
        await authAPI.register(email, fullName, password);
        // Auto-login after register
        await login(email, password);
    }

    function logout() {
        clearTokens();
        setState({ user: null, isAuthenticated: false, isLoading: false });
    }

    async function refreshUser() {
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
