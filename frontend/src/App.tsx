import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { Activity, Loader2, Sparkles, ShoppingCart } from "lucide-react";

import { Shell } from "./components/layout/Shell";
import { Panel, PanelHeader } from "./components/layout/Panels";
import { ChatTimeline } from "./components/chat/ChatTimeline";
import { Composer } from "./components/chat/Composer";
import { VoiceConsole } from "./components/voice/VoiceConsole";
import { Waveform } from "./components/voice/Waveform";
import { ProductShelf } from "./components/products/ProductShelf";
import { InsightGrid } from "./components/metrics/InsightGrid";
import { MoodCard } from "./components/session/MoodCard";
import { api } from "./lib/api";
import { timestamp } from "./lib/utils";
import type { ChatMessage, Product } from "./lib/types";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: "intro",
      role: "assistant",
      content:
        "Welcome to the Agentic Retail Studio. Brief me on floor priorities, guest mood, or merchandising cues to get precise recommendations.",
      timestamp: timestamp()
    }
  ]);
  const [products, setProducts] = useState<Product[]>([]);
  const [stats, setStats] = useState<Record<string, number>>({});
  const [cartCount, setCartCount] = useState(0);
  const [moodSnapshot, setMoodSnapshot] = useState({ mood: "neutral", confidence: 0, tone: "professional" });
  const [isSending, setIsSending] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const recognitionRef = useRef<any>(null);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [isVoiceStopped, setIsVoiceStopped] = useState(false);

  const hydrateProducts = useCallback(async () => {
    try {
      const catalog = await api.getProducts({ limit: 6 });
      if (catalog.success) {
        setProducts(catalog.products);
      }
    } catch (err) {
      console.error("Unable to load products", err);
    }
  }, []);

  const hydrateStats = useCallback(async () => {
    try {
      const payload = await api.getStats();
      if (payload.success) {
        setStats(payload.stats);
      }
    } catch (err) {
      console.error("Unable to load stats", err);
    }
  }, []);

  useEffect(() => {
    const boot = async () => {
      try {
        const session = await api.createSession();
        setSessionId(session.session_id);
        setUserId(session.user_id);
        await Promise.all([hydrateProducts(), hydrateStats()]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to initialize session");
      } finally {
        setLoading(false);
      }
    };

    boot();
  }, [hydrateProducts, hydrateStats]);

  useEffect(() => {
    if (!sessionId) return;
    hydrateStats();
    const interval = window.setInterval(hydrateStats, 20000);
    return () => window.clearInterval(interval);
  }, [sessionId, hydrateStats]);

  const handleSend = useCallback(
    async (value: string, isVoiceMessage: boolean = false) => {
      if (!sessionId) return;
      setError(null);

      const outboundTimestamp = timestamp();
      const outgoing: ChatMessage = {
        id: `${sessionId}-${outboundTimestamp}`,
        role: "user",
        content: value,
        timestamp: outboundTimestamp,
        isVoice: isVoiceMessage
      };

      setMessages((prev) => [...prev, outgoing]);
      setIsSending(true);

      try {
        const response = await api.sendChat(sessionId, value);

        const assistantTimestamp = timestamp();
        const assistantMessage: ChatMessage = {
          id: `${response.session_id}-${assistantTimestamp}`,
          role: "assistant",
          content: response.message,
          timestamp: assistantTimestamp,
          meta: {
            mood: response.context?.mood,
            language: response.context?.language,
            handled_by: response.context?.handled_by
          }
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // ALWAYS speak the response using TTS
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel(); // Cancel any ongoing speech
          const utterance = new SpeechSynthesisUtterance(response.message);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          window.speechSynthesis.speak(utterance);
        }

        const moodData = response.data?.mood;
        const normalizedMood =
          response.context?.mood || (typeof moodData === "string" ? moodData : moodData?.mood) || "neutral";

        setMoodSnapshot({
          mood: normalizedMood,
          confidence: typeof moodData === "object" ? moodData?.confidence ?? 0 : 0,
          tone: (typeof moodData === "object" ? moodData?.suggested_tone : undefined) || "professional"
        });

        const recommended =
          (Array.isArray(response.data?.recommendations)
            ? response.data?.recommendations
            : Array.isArray(response.data?.products)
              ? response.data?.products
              : undefined) || [];

        if (recommended.length) {
          setProducts(recommended as Product[]);
        }

        if (response.data?.cart?.item_count) {
          setCartCount(response.data.cart.item_count);
        }
      } catch (err) {
        console.error(err);
        setError(err instanceof Error ? err.message : "Unable to reach orchestrator");
        setMessages((prev) => [
          ...prev,
          {
            id: `${Date.now()}`,
            role: "assistant",
            content: "I hit a snag talking to the agent mesh. Give it another shot in a moment.",
            timestamp: timestamp()
          }
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [sessionId]
  );

  const handleAddToCart = useCallback(
    async (productId: string) => {
      if (!sessionId) return;
      try {
        const cart = await api.addToCart(sessionId, productId);
        setCartCount(cart.item_count);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to update cart");
      }
    },
    [sessionId]
  );

  const handleVoiceToggle = useCallback(async () => {
    if (!sessionId) return;

    if (!isStreaming) {
      // START recording - do NOT send input yet
      setIsStreaming(true);
      setIsVoiceStopped(false);
      setLiveTranscript("");
      setVoiceTranscript("🎤 Initializing voice...");
      setError(null);

      try {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        
        if (SpeechRecognition) {
          const recognition = new SpeechRecognition();
          recognition.continuous = false; // Set to false so it stops automatically when user pauses
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onstart = () => {
            setVoiceTranscript("🎤 Listening... Speak now!");
            setIsRecording(true);
          };

          recognition.onresult = (event: any) => {
            const current = event.resultIndex;
            const transcript = event.results[current][0].transcript;
            
            // Show live transcription in the input box (but don't send yet)
            setLiveTranscript(transcript);
            setVoiceTranscript(`🎤 ${transcript}`);
          };

          recognition.onerror = (event: any) => {
            console.error("Speech recognition error:", event.error);
            setError(`Speech recognition error: ${event.error}`);
            setVoiceTranscript("Voice error. Click mic to try again.");
            setIsStreaming(false);
            setIsRecording(false);
          };

          recognition.onend = () => {
            // Recognition stopped - show STOP button message
            setIsRecording(false);
            setVoiceTranscript(`"${liveTranscript}" - Click STOP to send or MIC to try again`);
            setIsVoiceStopped(true); // Ready for stop button click
          };

          recognition.start();
          recognitionRef.current = recognition;
          
        } else {
          setError("Speech Recognition not supported in this browser");
          setIsStreaming(false);
        }
      } catch (err) {
        console.error("Voice init error:", err);
        setError("Failed to initialize voice");
        setIsStreaming(false);
      }
    } else {
      // STOP recording - don't send input yet, wait for stop button
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      // isVoiceStopped is now true, stop button will handle sending
    }
  }, [sessionId, liveTranscript, isStreaming]);

  const handleVoiceStop = useCallback(async () => {
    if (!sessionId || !isVoiceStopped || !liveTranscript) return;

    try {
      setVoiceTranscript("Processing your message...");
      setIsStreaming(false);

      // NOW send to backend only after user clicks STOP
      const response = await api.voiceText(sessionId, liveTranscript);
      
      // Display AI response
      setVoiceTranscript(`AI: ${response.message}`);
      
      // Add to chat
      handleSend(liveTranscript, true);
      
      // Speak the response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.message);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        window.speechSynthesis.speak(utterance);
      }
      
      // Clear transcript
      setLiveTranscript("");
      setIsVoiceStopped(false);
      
    } catch (err) {
      console.error("Voice processing error:", err);
      setError("Failed to process voice input");
      setVoiceTranscript("Error processing voice. Try again.");
      setIsVoiceStopped(false);
    }
  }, [sessionId, isVoiceStopped, liveTranscript, handleSend]);

  const heroBadges = useMemo(
    () => [
      { label: "Session", value: sessionId ? sessionId.slice(0, 8) : "···" },
      { label: "Floor Lead", value: userId ?? "guest" },
      { label: "Cart", value: `${cartCount} item${cartCount === 1 ? "" : "s"}` },
      { label: "Mood", value: moodSnapshot.mood }
    ],
    [sessionId, userId, cartCount, moodSnapshot.mood]
  );

  return (
    <Shell>
      <section className="space-y-5">
        <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.4em] text-white/50">
          <span className="flex items-center gap-2">
            <Sparkles size={14} /> Agentic Retail Studio
          </span>
          <span className="h-px w-6 bg-white/20" />
          <span>Voice + Mood Orchestration</span>
        </div>
        <div className="grid gap-6 md:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4">
            <h1 className="font-display text-4xl md:text-5xl leading-tight">
              Deploy a conversational floor director that can sense intent, mood, and inventory in real time.
            </h1>
            <p className="text-white/70 text-base max-w-3xl">
              Brief the agent mesh like you would a seasoned retail lead. It synthesizes Groq planning, Supabase inventory,
              and Deepgram voice so the store feels alive.
            </p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/5 p-5 flex flex-col gap-3">
            {heroBadges.map((badge) => (
              <div key={badge.label} className="flex items-center justify-between text-sm">
                <span className="text-white/50">{badge.label}</span>
                <span className="font-semibold text-white">{badge.value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {error ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <div className="flex flex-col gap-6">
          <Panel className="flex flex-col gap-5 min-h-[480px]">
            <PanelHeader
              title="Conversation Studio"
              subtitle={isStreaming ? "🎤 Voice Active" : "Chat & Voice Interface"}
              action={
                isSending ? (
                  <span className="flex items-center gap-2 text-xs text-white/70">
                    <Loader2 size={14} className="animate-spin" /> Syncing agents
                  </span>
                ) : (
                  <span className="text-xs text-white/60">{messages.length} turns logged</span>
                )
              }
            />
            <div className="flex-1 overflow-y-auto pr-1 scroll-hide">
              <ChatTimeline messages={messages} />
            </div>
            
            {isStreaming && (
              <div className="flex items-center justify-center py-2 gap-4">
                <Waveform active={isStreaming} />
              </div>
            )}
            
            <Composer 
              disabled={!sessionId || loading || isSending} 
              onSend={handleSend}
              isVoiceActive={isStreaming}
              onVoiceToggle={handleVoiceToggle}
              voiceStatus={isStreaming ? voiceTranscript : undefined}
              liveTranscript={liveTranscript}
              onTranscriptChange={setLiveTranscript}
              isVoiceStopped={isVoiceStopped}
              onVoiceStop={handleVoiceStop}
            />
          </Panel>
        </div>

        <div className="flex flex-col gap-6">
          <MoodCard
            mood={moodSnapshot.mood}
            confidence={moodSnapshot.confidence}
            tone={moodSnapshot.tone}
          />

          <InsightGrid stats={stats} />

          <ProductShelf products={products} onAdd={handleAddToCart} />

          <Panel>
            <PanelHeader title="Checkout Pulse" />
            <div className="rounded-2xl border border-white/10 bg-black/30 px-4 py-5 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.4em] text-white/40">Cart Status</p>
                <p className="text-3xl font-semibold flex items-center gap-2">
                  <ShoppingCart size={20} /> {cartCount} item{cartCount === 1 ? "" : "s"}
                </p>
              </div>
              <div className="text-sm text-white/70 flex items-center gap-2">
                <Activity size={16} /> Session linked
              </div>
            </div>
          </Panel>
        </div>
      </div>
    </Shell>
  );
}
