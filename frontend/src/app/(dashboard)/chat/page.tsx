"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import api from "@/lib/api";
import { useChat, MeetingDraft, Recipient } from "@/context/ChatContext";
import { useLanguage } from "@/context/LanguageContext";
import { Bot, CalendarDays, Check, ChevronDown, Clock3, Link2, Loader2, MapPin, RotateCcw, Send, Sparkles, User, Users, X } from "lucide-react";

interface AutomationResponse {
  estado: "borrador" | "confirmada" | "cancelado";
  respuesta: string;
  meeting?: MeetingDraft & { id?: string; join_url?: string; duracion?: number };
  destinatarios?: Recipient[];
}

export default function ChatPage() {
  const { messages, draft, draftHistory, hydrated, addMessage, updateDraft, restorePreviousDraft, cancelDraft, newChat } = useChat();
  const { language, t } = useLanguage();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [typeOption, setTypeOption] = useState("");
  const [emailsOption, setEmailsOption] = useState("");
  const [addressOption, setAddressOption] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const activeDraftMessageId = draft ? [...messages].reverse().find((message) => message.estado === "borrador")?.id : undefined;

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const appendError = (detail: string) => addMessage({ role: "assistant", estado: "error", content: detail });
  const normalizeDraft = (meeting?: AutomationResponse["meeting"], recipients?: Recipient[]): MeetingDraft | null => {
    if (!meeting?.tema || !meeting.fecha_inicio) return null;
    return { tema: meeting.tema, fecha_inicio: meeting.fecha_inicio, duracion_minutos: meeting.duracion_minutos || meeting.duracion || 60, tipo: meeting.tipo || "virtual", direccion: meeting.direccion || null, correos: meeting.correos || (recipients || []).filter((recipient) => recipient.rol !== "organizador").map((recipient) => recipient.correo) };
  };

  const sendDraft = async (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim() || loading) return;
    const parts = [input.trim()];
    if (typeOption) parts.push(`${t("chat.typeInstruction")} ${typeOption}.`);
    if (emailsOption.trim()) parts.push(`${t("chat.inviteInstruction")} ${emailsOption.trim()}.`);
    if (addressOption.trim()) parts.push(`${t("chat.addressInstruction")} ${addressOption.trim()}.`);
    const message = parts.join(" ");
    addMessage({ role: "user", content: message });
    setInput("");
    setTypeOption("");
    setEmailsOption("");
    setAddressOption("");
    setLoading(true);
    try {
      const { data } = await api.post<AutomationResponse>("/automation/chat", { accion: "borrador", mensaje: message, borrador: draft });
      const nextDraft = normalizeDraft(data.meeting, data.destinatarios);
      if (!nextDraft) throw new Error(t("chat.invalidDraft"));
      updateDraft(nextDraft);
      addMessage({ role: "assistant", content: data.respuesta, estado: "borrador", meeting: data.meeting, destinatarios: data.destinatarios });
    } catch (error: any) {
      appendError(error.response?.data?.detail || error.message || t("chat.draftError"));
    } finally {
      setLoading(false);
    }
  };

  const confirmDraft = async () => {
    if (!draft || loading) return;
    addMessage({ role: "user", content: t("chat.confirmUserMessage") });
    setLoading(true);
    try {
      const { data } = await api.post<AutomationResponse>("/automation/chat", { accion: "confirmar", borrador: draft });
      addMessage({ role: "assistant", content: data.respuesta, estado: "confirmada", meeting: data.meeting, destinatarios: data.destinatarios });
      cancelDraft();
    } catch (error: any) {
      appendError(error.response?.data?.detail || t("chat.confirmError"));
    } finally {
      setLoading(false);
    }
  };

  const discardDraft = async () => {
    if (!draft || loading) return;
    setLoading(true);
    try {
      const { data } = await api.post<AutomationResponse>("/automation/chat", { accion: "cancelar" });
      cancelDraft();
      addMessage({ role: "assistant", content: data.respuesta, estado: "cancelado" });
    } catch (error: any) {
      appendError(error.response?.data?.detail || t("chat.discardError"));
    } finally {
      setLoading(false);
    }
  };

  const restoreDraft = () => {
    const previous = draftHistory[draftHistory.length - 1];
    if (!previous || loading) return;
    restorePreviousDraft();
    addMessage({ role: "assistant", content: t("chat.restored"), estado: "borrador", meeting: previous, destinatarios: previous.correos.map((correo) => ({ correo, rol: "participante" })) });
  };

  if (!hydrated) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return <div className="command-canvas h-[calc(100dvh-4rem)] md:h-[calc(100dvh-5rem)] -m-4 md:-m-8 flex flex-col overflow-hidden bg-background relative">
    <header className="absolute top-0 left-0 right-0 z-10 bg-card/95 backdrop-blur-md border-b border-border px-5 py-4 flex justify-between items-center">
      <div><p className="command-eyebrow">{t("chat.eyebrow")}</p><h1 className="mt-0.5 text-lg font-semibold flex items-center gap-2"><Bot className="w-5 h-5 text-brand-600" />{t("chat.title")} <span className="ml-2 status-beacon text-xs">{t("common.online")}</span></h1></div>
      <button onClick={newChat} className="min-h-10 text-sm font-semibold px-3 rounded-lg border border-border hover:bg-slate-50 dark:hover:bg-slate-800 inline-flex gap-2 items-center"><RotateCcw className="w-4 h-4" />{t("chat.newChat")}</button>
    </header>
    <div className="flex-1 min-h-0 overflow-y-auto pt-28 pb-44 px-4"><div className="max-w-3xl mx-auto flex flex-col space-y-7">
      {messages.map((message) => <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
        <div className={`flex gap-3 max-w-[92%] sm:max-w-[82%] ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
          <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${message.role === "assistant" ? "bg-gradient-to-br from-brand-500 to-indigo-600 text-white" : "bg-slate-200 dark:bg-slate-800"}`}>{message.role === "assistant" ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}</div>
          <div className={`rounded-xl text-sm leading-relaxed shadow-sm ${message.role === "user" ? "bg-brand-600 text-white rounded-tr-none px-5 py-3.5" : message.estado === "error" ? "bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-red-800 dark:text-red-200 rounded-tl-none overflow-hidden" : "command-panel text-foreground rounded-tl-none"}`}>
            <p className={message.role === "assistant" ? "px-5 pt-4" : "whitespace-pre-wrap"}>{message.content}</p>
            {message.meeting && <MeetingCard meeting={message.meeting} recipients={message.destinatarios || []} status={message.estado} onConfirm={message.id === activeDraftMessageId ? confirmDraft : undefined} onRestore={message.id === activeDraftMessageId && draftHistory.length ? restoreDraft : undefined} onCancel={message.id === activeDraftMessageId ? discardDraft : undefined} disabled={loading} language={language} />}
          </div>
        </div>
      </div>)}
      {loading && <div className="flex gap-3"><div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-indigo-600 text-white flex items-center justify-center"><Sparkles className="w-4 h-4" /></div><div className="bg-card border border-border rounded-2xl rounded-tl-none px-5 py-4 flex gap-1"><i className="w-2 h-2 rounded-full bg-brand-400 animate-bounce" /><i className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:150ms]" /><i className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:300ms]" /></div></div>}
      <div ref={messagesEndRef} />
    </div></div>
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background to-transparent pt-10 pb-5 px-4"><div className="max-w-3xl mx-auto">
      {draft && <div className="mb-3 px-4 py-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 text-amber-900 dark:text-amber-200 rounded-lg text-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3"><span>{t("chat.pendingDraft")}</span><div className="flex gap-3 shrink-0">{draftHistory.length > 0 && <button onClick={restoreDraft} className="font-semibold underline underline-offset-4">{t("chat.restorePrevious")}</button>}<button onClick={discardDraft} className="font-semibold underline underline-offset-4">{t("chat.cancelDraft")}</button></div></div>}
      <form onSubmit={sendDraft} className="bg-card border border-border shadow-lg rounded-2xl overflow-hidden focus-within:ring-2 focus-within:ring-brand-500"><button type="button" onClick={() => setShowOptions((visible) => !visible)} className="w-full px-4 py-2 text-xs font-semibold text-slate-500 border-b border-border flex justify-between"><span>{t("chat.meetingOptions")}</span><ChevronDown className={`w-4 h-4 transition-transform ${showOptions ? "rotate-180" : ""}`} /></button>{showOptions && <div className="grid sm:grid-cols-3 gap-3 p-4 border-b border-border bg-slate-50/60 dark:bg-slate-900/30"><select value={typeOption} onChange={(e) => setTypeOption(e.target.value)} className="input-field text-sm"><option value="">{t("chat.typeNoChange")}</option><option value="virtual">{t("common.virtual")}</option><option value="presencial">{t("common.inPerson")}</option><option value="mixta">{t("common.mixed")}</option></select><input value={emailsOption} onChange={(e) => setEmailsOption(e.target.value)} className="input-field text-sm" placeholder={t("chat.extraGuests")} /><input value={addressOption} onChange={(e) => setAddressOption(e.target.value)} className="input-field text-sm" placeholder={t("chat.addressIfNeeded")} /></div>}<div className="relative flex items-end"><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} placeholder={draft ? t("chat.modifyPlaceholder") : t("chat.preparePlaceholder")} className="w-full max-h-32 min-h-[60px] py-4 pl-5 pr-14 bg-transparent outline-none resize-none" disabled={loading} rows={1} /><button disabled={loading || !input.trim()} className="absolute right-3 bottom-3 p-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl disabled:opacity-50"><Send className="w-5 h-5" /></button></div></form>
    </div></div>
  </div>;
}

function MeetingCard({ meeting, recipients, status, onConfirm, onRestore, onCancel, disabled, language }: { meeting: MeetingDraft & { id?: string; join_url?: string; duracion?: number }; recipients: Recipient[]; status?: string; onConfirm?: () => void; onRestore?: () => void; onCancel?: () => void; disabled: boolean; language: string }) {
  const { t } = useLanguage();
  const duration = meeting.duracion_minutos || meeting.duracion || 60;
  const isDraft = status === "borrador";
  const actionsAvailable = isDraft && onConfirm && onCancel;
  const formatDate = (value?: string) => {
    if (!value) return t("chat.undefinedDate");
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString(language === "es" ? "es-PE" : "en-US", { dateStyle: "full", timeStyle: "short" });
  };
  const typeLabel = meeting.tipo === "presencial" ? t("common.inPerson") : meeting.tipo === "mixta" ? t("common.mixed") : t("common.virtual");
  const roleLabel = (role?: string) => role === "organizador" ? t("common.organizer") : role === "ponente" ? t("common.speaker") : role === "participante" ? t("common.participant") : role;

  return <section className="m-4 border border-brand-100 dark:border-brand-900/50 rounded-xl overflow-hidden bg-brand-50/40 dark:bg-brand-950/20"><div className="px-4 py-3 bg-brand-100/60 dark:bg-brand-950/40 flex justify-between gap-3"><span className="font-semibold text-brand-800 dark:text-brand-300">{isDraft ? t("chat.draftMeeting") : t("chat.confirmedMeeting")}</span><span className="text-xs uppercase tracking-wide font-bold text-brand-600">{typeLabel}</span></div><dl className="p-4 grid gap-3 text-sm"><div className="flex gap-2"><CalendarDays className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" /><div><dt className="text-xs text-slate-500">{t("chat.topicAndDate")}</dt><dd className="font-medium">{meeting.tema}<br />{formatDate(meeting.fecha_inicio)}</dd></div></div><div className="flex gap-2"><Clock3 className="w-4 h-4 text-brand-600 shrink-0" /><div><dt className="text-xs text-slate-500">{t("common.duration")}</dt><dd>{duration} {t("common.minutes")}</dd></div></div>{meeting.direccion && <div className="flex gap-2"><MapPin className="w-4 h-4 text-brand-600 shrink-0" /><div><dt className="text-xs text-slate-500">{t("common.address")}</dt><dd>{meeting.direccion}</dd></div></div>}{meeting.join_url && <div className="flex gap-2"><Link2 className="w-4 h-4 text-brand-600 shrink-0" /><a href={meeting.join_url} target="_blank" rel="noreferrer" className="text-brand-700 dark:text-brand-300 underline break-all">{t("chat.openZoomLink")}</a></div>}<div className="flex gap-2"><Users className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" /><div><dt className="text-xs text-slate-500">{t("common.participants")}</dt><dd className="flex flex-wrap gap-1.5 mt-1">{recipients.length ? recipients.map((recipient) => <span key={`${recipient.correo}-${recipient.rol}`} className="px-2 py-1 rounded-full bg-white dark:bg-slate-900 border border-brand-100 dark:border-brand-900 text-xs">{recipient.correo}{recipient.rol ? ` · ${roleLabel(recipient.rol)}` : ""}</span>) : <span>{t("chat.noExternalGuests")}</span>}</dd></div></div></dl>{actionsAvailable && <div className="px-4 pb-4 flex gap-2 flex-wrap">{onRestore && <button disabled={disabled} onClick={onRestore} className="px-3 py-2 rounded-lg border border-border text-sm font-semibold inline-flex gap-2 items-center disabled:opacity-50"><RotateCcw className="w-4 h-4" />{t("chat.restorePrevious")}</button>}<button disabled={disabled} onClick={onConfirm} className="btn-primary inline-flex gap-2 items-center"><Check className="w-4 h-4" />{t("chat.confirmMeeting")}</button><button disabled={disabled} onClick={onCancel} className="px-3 py-2 rounded-lg border border-red-200 text-red-600 text-sm font-semibold inline-flex gap-2 items-center disabled:opacity-50"><X className="w-4 h-4" />{t("chat.cancelDraft")}</button></div>}</section>;
}
