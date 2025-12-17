export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  isVoice?: boolean;
  meta?: {
    mood?: string;
    language?: string;
    handled_by?: string;
  };
}

export interface SuggestedAction {
  label: string;
  value: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  image_url?: string;
  mood_tag?: string;
}

export interface CartItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface CartSummary {
  success: boolean;
  cart: CartItem[];
  subtotal: number;
  tax: number;
  total: number;
  item_count: number;
}

export interface StatsPayload {
  total_products: number;
  total_orders: number;
  active_sessions: number;
  [key: string]: number;
}

export interface ChatPayload {
  success: boolean;
  message: string;
  session_id: string;
  data: Record<string, any>;
  suggested_actions: SuggestedAction[];
  context: {
    language?: string;
    mood?: string;
    intent?: string;
    handled_by?: string;
  };
}

export interface VoiceTranscript {
  id: string;
  text: string;
  origin: "user" | "assistant";
  created_at: string;
}
