/**
 * Custom hook for API calls with loading/error states.
 */

import { useState, useCallback } from 'react';

interface UseApiState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
}

export function useApi<T>() {
    const [state, setState] = useState<UseApiState<T>>({
        data: null,
        loading: false,
        error: null,
    });

    const execute = useCallback(async (apiCall: () => Promise<T>): Promise<T | null> => {
        setState({ data: null, loading: true, error: null });
        try {
            const data = await apiCall();
            setState({ data, loading: false, error: null });
            return data;
        } catch (err: any) {
            const message = err.message || 'Đã xảy ra lỗi';
            setState({ data: null, loading: false, error: message });
            return null;
        }
    }, []);

    const reset = useCallback(() => {
        setState({ data: null, loading: false, error: null });
    }, []);

    return { ...state, execute, reset };
}
