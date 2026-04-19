/**
 * WebSocket hook for real-time device status updates.
 * Connects to /ws/home/{homeId} and dispatches events.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { API_BASE_URL } from '@/services/api';

export type WSEventType = 'device_update' | 'security_alert' | 'automation_triggered';

export interface WSMessage {
    type: WSEventType;
    device_id?: string;
    data: Record<string, any>;
}

type WSCallback = (message: WSMessage) => void;

export function useWebSocket(homeId: string | null) {
    const ws = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const listeners = useRef<Map<WSEventType, Set<WSCallback>>>(new Map());
    const reconnectTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

    const connect = useCallback(() => {
        if (!homeId) return;

        // Convert http(s) to ws(s)
        const wsUrl = API_BASE_URL.replace('http', 'ws') + `/ws/home/${homeId}`;

        try {
            const socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                console.log('[WS] Connected to', homeId);
                setIsConnected(true);
            };

            socket.onmessage = (event) => {
                try {
                    const message: WSMessage = JSON.parse(event.data);
                    const callbacks = listeners.current.get(message.type);
                    if (callbacks) {
                        callbacks.forEach((cb) => cb(message));
                    }
                } catch (e) {
                    console.warn('[WS] Parse error:', e);
                }
            };

            socket.onclose = () => {
                console.log('[WS] Disconnected');
                setIsConnected(false);
                // Auto-reconnect after 3 seconds
                reconnectTimer.current = setTimeout(connect, 3000);
            };

            socket.onerror = (error) => {
                console.warn('[WS] Error:', error);
            };

            ws.current = socket;
        } catch (e) {
            console.warn('[WS] Connection failed:', e);
            reconnectTimer.current = setTimeout(connect, 5000);
        }
    }, [homeId]);

    useEffect(() => {
        connect();
        return () => {
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
            if (ws.current) {
                ws.current.close();
                ws.current = null;
            }
        };
    }, [connect]);

    const subscribe = useCallback((type: WSEventType, callback: WSCallback) => {
        if (!listeners.current.has(type)) {
            listeners.current.set(type, new Set());
        }
        listeners.current.get(type)!.add(callback);

        // Return unsubscribe function
        return () => {
            listeners.current.get(type)?.delete(callback);
        };
    }, []);

    return { isConnected, subscribe };
}
