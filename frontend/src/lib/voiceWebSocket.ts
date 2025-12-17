/**
 * WebSocket client for real-time voice communication
 */

export interface VoiceMessage {
  type: 'text' | 'audio' | 'response' | 'transcript' | 'error' | 'connected';
  content?: string;
  data?: string;
  mime_type?: string;
  text?: string;
  audio?: string;
  is_final?: boolean;
  error?: string;
}

export interface VoiceWSOptions {
  onMessage?: (message: VoiceMessage) => void;
  onTranscript?: (text: string, isFinal: boolean) => void;
  onResponse?: (text: string, audio?: string) => void;
  onError?: (error: string) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export class VoiceWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private options: VoiceWSOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectDelay = 1000;

  constructor(sessionId: string, options: VoiceWSOptions = {}) {
    this.sessionId = sessionId;
    this.options = options;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Determine WebSocket URL based on current location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/voice/${this.sessionId}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('Voice WebSocket connected');
          this.reconnectAttempts = 0;
          this.options.onConnect?.();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: VoiceMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
          }
        };

        this.ws.onerror = (error) => {
          console.error('Voice WebSocket error:', error);
          this.options.onError?.('WebSocket connection error');
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('Voice WebSocket closed');
          this.options.onDisconnect?.();
          
          // Attempt to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            setTimeout(() => {
              this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };

      } catch (err) {
        reject(err);
      }
    });
  }

  private handleMessage(message: VoiceMessage) {
    this.options.onMessage?.(message);

    switch (message.type) {
      case 'connected':
        console.log('Voice session connected');
        break;

      case 'transcript':
        if (message.text) {
          this.options.onTranscript?.(message.text, message.is_final || false);
        }
        break;

      case 'response':
        if (message.text) {
          this.options.onResponse?.(message.text, message.audio);
        }
        break;

      case 'error':
        if (message.error) {
          this.options.onError?.(message.error);
        }
        break;
    }
  }

  sendText(text: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'text',
        content: text
      }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  sendAudio(audioBase64: string, mimeType: string = 'audio/webm') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'audio',
        data: audioBase64,
        mime_type: mimeType
      }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export function createVoiceWebSocket(sessionId: string, options: VoiceWSOptions): VoiceWebSocket {
  return new VoiceWebSocket(sessionId, options);
}
