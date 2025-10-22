// Allow overriding the WebSocket URL via Vite env (VITE_WS_URL). If unset, don't try to connect.
const WS_BASE_URL = typeof process !== 'undefined' && (process.env as any).VITE_WS_URL
    ? (process.env as any).VITE_WS_URL.replace(/\/+$/, '')
    : null;

type QueueUpdateCallback = (data: any) => void;

class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private callbacks: QueueUpdateCallback[] = [];
    private manualClose = false;

    /**
     * Connect to the WS endpoint. Resolves when connection opens, rejects after max attempts.
     */
    async connect(): Promise<void> {
        if (!WS_BASE_URL) {
            // WS disabled in this environment (VITE_WS_URL not set)
            return Promise.reject(new Error('WebSocket disabled (VITE_WS_URL not set)'));
        }

        if (this.ws && this.ws.readyState === WebSocket.OPEN) return;
        this.manualClose = false;

        return new Promise((resolve, reject) => {
            const tryOpen = () => {
                try {
                    this.ws = new WebSocket(`${WS_BASE_URL}/queue`);
                } catch (err) {
                    // Most likely the environment doesn't allow WS or invalid URL
                    console.debug('WebSocket create failed:', err);
                    scheduleRetry(err);
                    return;
                }

                this.ws.onopen = () => {
                    this.reconnectAttempts = 0;
                    // wire message handler
                    this.ws!.onmessage = (event: MessageEvent) => {
                        try {
                            const data = JSON.parse(event.data);
                            this.callbacks.forEach(cb => cb(data));
                        } catch (err) {
                            console.debug('Invalid WS message received', err);
                        }
                    };

                    this.ws!.onclose = (ev) => {
                        if (this.manualClose) return;
                        if (this.reconnectAttempts < this.maxReconnectAttempts) {
                            const delay = 1000 * Math.pow(2, this.reconnectAttempts);
                            this.reconnectAttempts++;
                            console.debug(`WebSocket closed; will retry in ${delay}ms (attempt ${this.reconnectAttempts})`);
                            setTimeout(tryOpen, delay);
                        } else {
                            console.debug('WebSocket closed and max reconnect attempts reached');
                        }
                    };

                    this.ws!.onerror = (err) => {
                        // Log at debug level to avoid spamming the console during dev when backend is down
                        console.debug('WebSocket error event:', err);
                        // close to trigger reconnect logic
                        try { this.ws?.close(); } catch (_) {}
                    };

                    resolve();
                };

                this.ws.onerror = (err) => {
                    // If opening fails, schedule retry
                    console.debug('WebSocket connection error on open:', err);
                    scheduleRetry(err);
                };
            };

            const scheduleRetry = (err?: any) => {
                if (this.manualClose) return reject(err);
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    const delay = 1000 * Math.pow(2, this.reconnectAttempts);
                    this.reconnectAttempts++;
                    console.debug(`WebSocket connect failed; retrying in ${delay}ms (attempt ${this.reconnectAttempts})`);
                    setTimeout(tryOpen, delay);
                } else {
                    console.debug('WebSocket connect failed: max attempts reached');
                    reject(err);
                }
            };

            tryOpen();
        });
    }

    subscribe(callback: QueueUpdateCallback) {
        this.callbacks.push(callback);
        // Try to connect in the background if not connected; no need to await here
        if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
            this.connect().catch(() => {
                // swallow errors here; callers can await connect() if they need to know outcome
                console.debug('Background WS connect failed during subscribe');
            });
        }
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
            if (this.callbacks.length === 0) {
                try { this.ws?.close(); } catch (_) {}
                this.ws = null;
            }
        };
    }

    disconnect() {
        this.manualClose = true;
        if (this.ws) {
            try { this.ws.close(); } catch (_) {}
            this.ws = null;
        }
        this.callbacks = [];
    }

    get isConnected() {
        return !!(this.ws && this.ws.readyState === WebSocket.OPEN);
    }
}

export const wsService = new WebSocketService();
