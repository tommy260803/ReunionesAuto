"use client";

import { useEffect, useState, useRef } from "react";
import api from "@/lib/api";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { useLanguage } from "@/context/LanguageContext";
import { 
  Loader2, 
  FileText, 
  UploadCloud, 
  Sparkles, 
  MessageSquare,
  Bot
} from "lucide-react";
import Link from "next/link";

interface Meeting {
  id: string;
  tema: string;
  fecha_inicio: string;
  tipo: string;
}

interface Summary {
  id: string;
  reunion_id: string;
  resumen: string;
  fecha_creacion: string;
}

export default function SummariesPage() {
  const { language, t } = useLanguage();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string>("");
  const [summary, setSummary] = useState<Summary | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [generating, setGenerating] = useState(false);
  
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchMeetings();
    return () => {
      stopPolling();
    };
  }, []);

  useEffect(() => {
    if (selectedMeetingId) {
      stopPolling();
      setGenerating(false);
      fetchSummary(selectedMeetingId);
    }
  }, [selectedMeetingId]);

  const fetchMeetings = async () => {
    try {
      const { data } = await api.get<Meeting[]>("/meetings");
      setMeetings(data);
      if (data.length > 0) setSelectedMeetingId(data[0].id);
    } catch (err) {
      setError(t("summaries.loadMeetingsError"));
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async (meetingId: string) => {
    setLoadingSummary(true);
    setSummary(null);
    setError("");
    setSuccessMsg("");
    
    try {
      const { data } = await api.get<Summary>(`/summaries/meeting/${meetingId}`);
      setSummary(data);
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error("Error loading summary", err);
      }
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleGenerateVirtual = async () => {
    if (!selectedMeetingId) return;
    setGenerating(true);
    setError("");
    setSuccessMsg("");
    
    try {
      await api.post("/automation/summary/virtual", { reunion_id: selectedMeetingId });
      setSuccessMsg(t("summaries.success"));
      fetchSummary(selectedMeetingId);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.generateError"));
    } finally {
      setGenerating(false);
    }
  };

  const uploadFile = async (file: File) => {
    if (!selectedMeetingId) return;
    
    if (file.type !== "application/pdf") {
      setError(t("summaries.onlyPdf"));
      return;
    }

    setGenerating(true);
    setError("");
    setSuccessMsg(t("summaries.uploading"));
    
    const formData = new FormData();
    formData.append("reunion_id", selectedMeetingId);
    formData.append("file", file);
    
    try {
      await api.post("/automation/summary/presencial", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      // Start polling
      startPolling(selectedMeetingId);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.uploadError"));
      setGenerating(false);
      setSuccessMsg("");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (generating) return;
    
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
    if (pollingTimeoutRef.current) clearTimeout(pollingTimeoutRef.current);
  };

  const startPolling = (meetingId: string) => {
    stopPolling();
    
    const startTime = Date.now();
    const maxDuration = 120 * 1000; // 2 minutes maximum
    
    pollingIntervalRef.current = setInterval(async () => {
      try {
        const { data } = await api.get<Summary>(`/summaries/meeting/${meetingId}`);
        if (data && data.resumen) {
          // Success, the summary was generated.
          stopPolling();
          setSummary(data);
          setGenerating(false);
          setSuccessMsg(t("summaries.success"));
        }
      } catch (err: any) {
        // Ignore 404, it means the summary is not ready yet.
        if (err.response?.status !== 404) {
          stopPolling();
          setGenerating(false);
          setError(t("summaries.pollError"));
          setSuccessMsg("");
        }
      }
      
      // Timeout check
      if (Date.now() - startTime > maxDuration) {
        stopPolling();
        setGenerating(false);
        setError(t("summaries.timeout"));
        setSuccessMsg("");
      }
    }, 3000); // Polling cada 3 segundos
  };

  const selectedMeeting = meetings.find(m => m.id === selectedMeetingId);
  const meetingGroups = [
    { type: "virtual", label: t("summaries.virtualMeetings"), color: "text-blue-600" },
    { type: "presencial", label: t("summaries.inPersonMeetings"), color: "text-orange-600" },
    { type: "mixta", label: t("summaries.mixedMeetings"), color: "text-violet-600" },
  ];

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">{t("summaries.title")}</h1>
          <p className="text-slate-500">{t("summaries.subtitle")}</p>
        </div>
        
        {/* Chatbot trigger button */}
        <Link href="/chat" className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-sm shrink-0">
          <Bot className="w-5 h-5" />
          {t("summaries.chatbot")}
        </Link>
      </div>

      {(error || successMsg) && (
        <div className={`p-4 rounded-xl border ${error ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-700 border-emerald-100'}`}>
          <div className="flex items-center gap-2">
            {generating && !error && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
            {error || successMsg}
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {meetingGroups.map((group) => {
          const groupMeetings = meetings.filter((meeting) => (meeting.tipo || "").toLowerCase() === group.type);
          return <section key={group.type} className="bg-card border border-border rounded-2xl p-4 shadow-sm min-h-44">
            <h3 className={`font-semibold ${group.color} mb-3`}>{group.label}</h3>
            <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
              {groupMeetings.length === 0 ? <p className="text-sm text-slate-500 py-3">{t("summaries.noMeetings")}</p> : groupMeetings.map((meeting) => <button key={meeting.id} onClick={() => setSelectedMeetingId(meeting.id)} className={`w-full text-left p-3 rounded-xl border transition-colors ${selectedMeetingId === meeting.id ? "bg-brand-50 border-brand-200 dark:bg-brand-950/40 dark:border-brand-800" : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800"}`}><span className="block font-medium text-sm truncate">{meeting.tema || t("common.noTopic")}</span><span className="text-xs text-slate-500">{meeting.fecha_inicio ? format(parseISO(meeting.fecha_inicio), "dd MMM yyyy", { locale: language === "es" ? es : enUS }) : t("common.noDate")}</span></button>)}
            </div>
          </section>;
        })}
      </div>
      <div>
          <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden min-h-[400px] flex flex-col">
            <div className="p-5 border-b border-border bg-slate-50/50 dark:bg-slate-900/50 flex justify-between items-center">
              <h3 className="font-semibold flex items-center gap-2 text-foreground">
                <FileText className="w-5 h-5 text-brand-500" />
                {t("summaries.summaryTitle")}
              </h3>
            </div>

            <div className="p-6 flex-1 flex flex-col">
              {loadingSummary ? (
                <div className="flex-1 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-brand-600" />
                </div>
              ) : summary ? (
                <div className="flex-1 space-y-4">
                  <div className="bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 rounded-xl p-5">
                    <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                      {summary.resumen}
                    </p>
                  </div>
                  <p className="text-xs text-slate-400 text-right">
                    {t("summaries.generatedAt")}: {summary.fecha_creacion ? format(parseISO(summary.fecha_creacion), "dd MMM, yyyy HH:mm", { locale: language === "es" ? es : enUS }) : "—"}
                  </p>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center space-y-5 py-8">
                  
                  {selectedMeeting?.tipo === 'virtual' || selectedMeeting?.tipo === 'mixta' ? (
                    <>
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center">
                        <MessageSquare className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                      </div>
                      <div>
                        <h4 className="text-lg font-medium text-foreground mb-1">{t("summaries.noSummary")}</h4>
                        <p className="text-sm text-slate-500 max-w-sm mx-auto">
                          {t("summaries.noSummaryText")}
                        </p>
                      </div>
                      <button 
                        onClick={handleGenerateVirtual}
                        disabled={generating}
                        className="btn-primary inline-flex items-center gap-2 max-w-xs"
                      >
                        {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                        {generating ? t("summaries.processingTranscript") : t("summaries.generateAi")}
                      </button>
                    </>
                  ) : (
                    <div 
                      className={`w-full max-w-md border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center transition-all duration-200 ${
                        isDragging 
                          ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20" 
                          : "border-border hover:border-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/30"
                      } ${generating ? "opacity-50 pointer-events-none" : ""}`}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${
                        isDragging ? "bg-brand-100 text-brand-600" : "bg-slate-100 dark:bg-slate-800 text-slate-400"
                      }`}>
                        {generating ? <Loader2 className="w-8 h-8 animate-spin" /> : <UploadCloud className="w-8 h-8" />}
                      </div>
                      
                      <h4 className="text-lg font-medium text-foreground mb-2">
                        {generating ? t("summaries.processingMinutes") : t("summaries.uploadMinutes")}
                      </h4>
                      
                      <p className="text-sm text-slate-500 mb-6 text-center">
                        {generating 
                          ? t("summaries.processingText") 
                          : t("summaries.dropText")}
                      </p>
                      
                      <input 
                        type="file" 
                        accept=".pdf" 
                        className="hidden" 
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                      />
                      
                      {!generating && (
                        <button 
                          onClick={() => fileInputRef.current?.click()}
                          className="btn-primary bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 shadow-orange-500/20"
                        >
                          {t("summaries.selectPdf")}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
      </div>
    </div>
  );
}
