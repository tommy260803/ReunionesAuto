"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { useAuth } from "@/context/AuthContext";

export interface MeetingDraft {
  tema: string;
  fecha_inicio: string;
  duracion_minutos: number;
  tipo: "virtual" | "presencial" | "mixta";
  direccion?: string | null;
  correos: string[];
}

export interface Recipient {
  correo: string;
  usuario_id?: string | null;
  rol?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  estado?: "borrador" | "confirmada" | "cancelado" | "error";
  meeting?: MeetingDraft & { id?: string; join_url?: string; duracion?: number };
  destinatarios?: Recipient[];
}

interface ChatContextType {
  messages: ChatMessage[];
  draft: MeetingDraft | null;
  draftHistory: MeetingDraft[];
  hydrated: boolean;
  addMessage: (message: Omit<ChatMessage, "id" | "createdAt">) => void;
  updateDraft: (draft: MeetingDraft) => void;
  restorePreviousDraft: () => void;
  cancelDraft: () => void;
  newChat: () => void;
}

const ChatContext = createContext<ChatContextType | null>(null);

const greeting = (name?: string): ChatMessage => ({
  id: "welcome",
  role: "assistant",
  createdAt: new Date().toISOString(),
  content: `Hola ${name || ""}. Describe la reunión que quieres preparar y te mostraré un borrador antes de crearla.`,
});

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState<MeetingDraft | null>(null);
  const [draftHistory, setDraftHistory] = useState<MeetingDraft[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const previousStorageKey = useRef<string | null>(null);
  const storageKey = user ? `zoom2.chat.v1.${user.id}` : null;

  useEffect(() => {
    if (!storageKey) {
      if (previousStorageKey.current) sessionStorage.removeItem(previousStorageKey.current);
      previousStorageKey.current = null;
      setMessages([]);
      setDraft(null);
      setDraftHistory([]);
      setHydrated(false);
      return;
    }
    previousStorageKey.current = storageKey;
    try {
      const saved = sessionStorage.getItem(storageKey);
      if (saved) {
        const state = JSON.parse(saved) as { messages?: ChatMessage[]; draft?: MeetingDraft | null; draftHistory?: MeetingDraft[] };
        setMessages(state.messages?.length ? state.messages : [greeting(user?.nombre)]);
        setDraft(state.draft || null);
        setDraftHistory(state.draftHistory || []);
      } else {
        setMessages([greeting(user?.nombre)]);
        setDraft(null);
        setDraftHistory([]);
      }
    } catch {
      setMessages([greeting(user?.nombre)]);
      setDraft(null);
      setDraftHistory([]);
    } finally {
      setHydrated(true);
    }
  }, [storageKey, user?.nombre]);

  useEffect(() => {
    if (!storageKey || !hydrated) return;
    sessionStorage.setItem(storageKey, JSON.stringify({ messages, draft, draftHistory }));
  }, [draft, draftHistory, hydrated, messages, storageKey]);

  const addMessage = (message: Omit<ChatMessage, "id" | "createdAt">) => {
    setMessages((current) => [...current, { ...message, id: crypto.randomUUID(), createdAt: new Date().toISOString() }]);
  };
  const updateDraft = (nextDraft: MeetingDraft) => {
    if (draft && JSON.stringify(draft) !== JSON.stringify(nextDraft)) {
      setDraftHistory((history) => [...history, draft]);
    }
    setDraft(nextDraft);
  };
  const restorePreviousDraft = () => {
    if (!draftHistory.length) return;
    const previous = draftHistory[draftHistory.length - 1];
    setDraftHistory((history) => history.slice(0, -1));
    setDraft(previous);
  };
  const cancelDraft = () => {
    setDraft(null);
    setDraftHistory([]);
  };
  const newChat = () => {
    cancelDraft();
    setMessages([greeting(user?.nombre)]);
  };

  return <ChatContext.Provider value={{ messages, draft, draftHistory, hydrated, addMessage, updateDraft, restorePreviousDraft, cancelDraft, newChat }}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat debe utilizarse dentro de ChatProvider");
  return context;
}
