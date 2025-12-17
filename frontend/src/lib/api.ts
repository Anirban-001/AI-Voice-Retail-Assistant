import type { CartSummary, ChatPayload, Product, StatsPayload } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const JSON_HEADERS = {
  "Content-Type": "application/json"
};

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const fullUrl = `${API_BASE_URL}${url}`;
  const response = await fetch(fullUrl, init);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || response.statusText);
  }
  return response.json();
}

export const api = {
  createSession: async (userId?: string, channel: string = "web") => {
    return request<{ success: boolean; session_id: string; user_id: string }>(
      "/api/session",
      {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ user_id: userId, channel })
      }
    );
  },

  sendChat: async (sessionId: string, message: string) => {
    return request<ChatPayload>("/api/chat", {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({
        session_id: sessionId,
        message,
        channel: "web"
      })
    });
  },

  getProducts: async (params?: { category?: string; search?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.category) query.append("category", params.category);
    if (params?.search) query.append("search", params.search);
    if (params?.limit) query.append("limit", String(params.limit));
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request<{ success: boolean; products: Product[] }>(`/api/products${suffix}`);
  },

  getCategories: async () => {
    return request<{ success: boolean; categories: string[] }>("/api/categories");
  },

  getStats: async () => {
    return request<{ success: boolean; stats: StatsPayload }>("/api/stats");
  },

  getCart: async (sessionId: string) => {
    return request<CartSummary>(`/api/cart/${sessionId}`);
  },

  addToCart: async (sessionId: string, productId: string, quantity: number = 1) => {
    return request<{ success: boolean; cart: CartSummary["cart"]; item_count: number }>(
      "/api/cart/add",
      {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ session_id: sessionId, product_id: productId, quantity })
      }
    );
  },

  voiceText: async (sessionId: string, transcription: string, language?: string) => {
    return request<{ success: boolean; message: string; context: Record<string, any> }>(
      "/api/voice/text",
      {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ session_id: sessionId, transcription, language })
      }
    );
  }
};
