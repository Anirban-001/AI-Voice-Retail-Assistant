import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, currency: string = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency
  }).format(value);
}

export function timestamp() {
  return new Date().toISOString();
}

export function arrayBufferToBase64(buffer: ArrayBuffer) {
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000;
  let binary = "";

  for (let i = 0; i < bytes.byteLength; i += chunkSize) {
    const chunk = bytes.subarray(i, Math.min(i + chunkSize, bytes.byteLength));
    binary += String.fromCharCode(...chunk);
  }

  if (typeof window !== "undefined" && typeof window.btoa === "function") {
    return window.btoa(binary);
  }

  // Fallback for environments without btoa
  const nodeBuffer = (globalThis as any)?.Buffer;
  if (nodeBuffer) {
    return nodeBuffer.from(binary, "binary").toString("base64");
  }

  throw new Error("Base64 encoding is not supported in this environment");
}
