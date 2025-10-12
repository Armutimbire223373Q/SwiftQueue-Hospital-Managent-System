const WS_BASE_URL = 'ws://localhost:8001/ws';

type QueueUpdateCallback = (data: any) => void;

class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private callbacks: QueueUpdateCallback[] = [];

    connect() {
        this.ws = new WebSocket(`${WS_BASE_URL}/queue`);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.callbacks.forEach(callback => callback(data));
        };

        this.ws.onclose = () => {
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, 1000 * Math.pow(2, this.reconnectAttempts)); // Exponential backoff
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.ws?.close();
        };
    }

    subscribe(callback: QueueUpdateCallback) {
        this.callbacks.push(callback);
        if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
            this.connect();
        }
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
            if (this.callbacks.length === 0) {
                this.ws?.close();
                this.ws = null;
            }
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.callbacks = [];
    }
}

export const wsService = new WebSocketService();
