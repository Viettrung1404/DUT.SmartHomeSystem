import { useCallback, useEffect, useRef, useState } from 'react';
import { PermissionsAndroid, Platform } from 'react-native';
import Constants from 'expo-constants';
import * as Speech from 'expo-speech';

export type VoiceState = 'idle' | 'listening' | 'transcribing' | 'thinking' | 'speaking';

export interface UseVoiceProps {
  onTranscriptReceived?: (transcript: string) => void;
  locale?: string;
}

type SpeechErrorEvent = { error?: { message?: string } };
type SpeechResultsEvent = { value?: string[] };

type VoiceModule = {
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onSpeechError?: (event: SpeechErrorEvent) => void;
  onSpeechResults?: (event: SpeechResultsEvent) => void;
  onSpeechPartialResults?: (event: SpeechResultsEvent) => void;
  start: (locale: string) => Promise<void>;
  stop: () => Promise<void>;
  destroy: () => Promise<void>;
  removeAllListeners: () => void;
};

let cachedVoice: VoiceModule | null | undefined;

function getVoiceModule(): VoiceModule | null {
  if (Platform.OS === 'web') return null;

  // Expo Go does not bundle @react-native-voice/voice. Requiring it there crashes
  // at module load time, so only load it inside a dev/custom native build.
  if (Constants.appOwnership === 'expo') return null;

  if (cachedVoice !== undefined) return cachedVoice;

  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    cachedVoice = require('@react-native-voice/voice').default as VoiceModule;
  } catch (error) {
    console.warn('Voice native module is not available:', error);
    cachedVoice = null;
  }

  return cachedVoice;
}

async function requestAndroidPermission(): Promise<boolean> {
  if (Platform.OS !== 'android') return true;

  try {
    const hasPermission = await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.RECORD_AUDIO);
    if (hasPermission) return true;

    const status = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.RECORD_AUDIO, {
      title: 'Quyen su dung Micro',
      message: 'Tro ly AI can truy cap micro de nhan dien giong noi tieng Viet.',
      buttonPositive: 'Dong y',
    });
    return status === PermissionsAndroid.RESULTS.GRANTED;
  } catch (error) {
    console.error('Failed to request microphone permission:', error);
    return false;
  }
}

function cleanSpeechText(text: string): string {
  return text
    .replace(/Nguon:\s*.*$/gim, '')
    .replace(/Nguồn:\s*.*$/gim, '')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1')
    .replace(/\*\*/g, '')
    .replace(/\n+/g, ' ')
    .trim();
}

export function useVoice({ onTranscriptReceived, locale = 'vi-VN' }: UseVoiceProps = {}) {
  const [state, setState] = useState<VoiceState>('idle');
  const [transcript, setTranscript] = useState('');
  const [partialTranscript, setPartialTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);

  const onTranscriptReceivedRef = useRef(onTranscriptReceived);
  useEffect(() => {
    onTranscriptReceivedRef.current = onTranscriptReceived;
  }, [onTranscriptReceived]);

  const stopSpeaking = useCallback(async () => {
    try {
      if (await Speech.isSpeakingAsync()) {
        await Speech.stop();
      }
    } catch (error) {
      console.error('Failed to stop TTS:', error);
    } finally {
      setState('idle');
    }
  }, []);

  useEffect(() => {
    const Voice = getVoiceModule();
    if (!Voice) return;

    Voice.onSpeechStart = () => {
      setError(null);
      setState('listening');
    };

    Voice.onSpeechEnd = () => {
      setState('transcribing');
    };

    Voice.onSpeechError = (event: SpeechErrorEvent) => {
      setError(event.error?.message || 'Khong the nhan dien giong noi. Hay thu lai.');
      setState('idle');
    };

    Voice.onSpeechResults = (event: SpeechResultsEvent) => {
      const text = event.value?.[0]?.trim();
      if (text) {
        setTranscript(text);
        onTranscriptReceivedRef.current?.(text);
      }
      setState('idle');
    };

    Voice.onSpeechPartialResults = (event: SpeechResultsEvent) => {
      setPartialTranscript(event.value?.[0] || '');
    };

    return () => {
      Voice.destroy().then(Voice.removeAllListeners).catch(console.error);
    };
  }, []);

  const startListening = useCallback(async () => {
    if (Platform.OS === 'web') {
      setError('Nhan dien giong noi khong duoc ho tro tren trinh duyet.');
      return;
    }

    const Voice = getVoiceModule();
    if (!Voice) {
      setError('Voice can Expo Dev Client/native build. Expo Go chi ho tro chat bang chu.');
      return;
    }

    await stopSpeaking();

    if (!(await requestAndroidPermission())) {
      setError('Quyen micro bi tu choi.');
      return;
    }

    setTranscript('');
    setPartialTranscript('');
    setError(null);

    try {
      await Voice.start(locale);
      setState('listening');
    } catch (error) {
      setError(error instanceof Error ? error.message : String(error));
      setState('idle');
    }
  }, [locale, stopSpeaking]);

  const stopListening = useCallback(async () => {
    const Voice = getVoiceModule();
    if (!Voice) return;

    try {
      await Voice.stop();
    } catch (error) {
      console.error('Failed to stop voice recognition:', error);
    }
  }, []);

  const speak = useCallback(
    async (text: string) => {
      await stopSpeaking();

      const cleanText = cleanSpeechText(text);
      if (!cleanText) return;

      setState('speaking');

      try {
        Speech.speak(cleanText, {
          language: 'vi-VN',
          onStart: () => setState('speaking'),
          onDone: () => setState('idle'),
          onStopped: () => setState('idle'),
          onError: () => {
            setError('Loi khi phat giong noi.');
            setState('idle');
          },
        });
      } catch (error) {
        console.error('Failed to speak:', error);
        setError('Thiet bi khong ho tro Text-to-Speech.');
        setState('idle');
      }
    },
    [stopSpeaking],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    state,
    setState,
    transcript,
    partialTranscript,
    error,
    clearError,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
}
