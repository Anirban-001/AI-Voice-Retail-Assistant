import { useState, useCallback, useRef } from 'react';

interface UseVoiceOptions {
  onTranscript?: (text: string) => void;
  onError?: (error: string) => void;
  onStateChange?: (isActive: boolean) => void;
}

export function useVoice({ onTranscript, onError, onStateChange }: UseVoiceOptions = {}) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startListening = useCallback(async () => {
    try {
      // Try to use Web Speech API first
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          setIsListening(true);
          setTranscript('🎤 Listening...');
          onStateChange?.(true);
        };

        recognition.onresult = (event: any) => {
          const current = event.resultIndex;
          const transcriptText = event.results[current][0].transcript;
          
          setTranscript(transcriptText);
          
          if (event.results[current].isFinal) {
            onTranscript?.(transcriptText);
          }
        };

        recognition.onerror = (event: any) => {
          const errorMsg = `Speech recognition error: ${event.error}`;
          setError(errorMsg);
          onError?.(errorMsg);
          setIsListening(false);
          onStateChange?.(false);
        };

        recognition.onend = () => {
          setIsListening(false);
          onStateChange?.(false);
        };

        recognition.start();
        recognitionRef.current = recognition;
        
      } else {
        // Fallback to MediaRecorder for audio capture
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunksRef.current = [];
        
        const mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          
          // Convert to base64 and pass to callback
          const reader = new FileReader();
          reader.readAsDataURL(audioBlob);
          reader.onloadend = () => {
            const base64Audio = reader.result?.toString().split(',')[1];
            if (base64Audio) {
              // In production, this would be sent to backend for Deepgram processing
              setTranscript('Audio recorded - send to backend for transcription');
              onTranscript?.('Audio recorded');
            }
          };

          stream.getTracks().forEach(track => track.stop());
          setIsListening(false);
          onStateChange?.(false);
        };

        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder;
        setIsListening(true);
        setTranscript('🎤 Recording...');
        onStateChange?.(true);
      }
      
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to access microphone';
      setError(errorMsg);
      onError?.(errorMsg);
      setIsListening(false);
      onStateChange?.(false);
    }
  }, [onTranscript, onError, onStateChange]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
    
    setIsListening(false);
    onStateChange?.(false);
  }, [onStateChange]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    clearError
  };
}
