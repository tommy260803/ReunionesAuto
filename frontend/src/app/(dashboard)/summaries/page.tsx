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
  Bot,
  Headphones,
  Video,
  Cloud,
  AlertCircle,
  CheckCircle,
  XCircle,
  CircleStop,
  RefreshCw,
  ListTodo,
  Calendar,
  Clock,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

interface Meeting {
  id: string;
  tema: string;
  fecha_inicio: string;
  tipo: string;
  duracion_minutos?: number;
  id_externo?: string;
}

interface Summary {
  id: string;
  reunion_id: string;
  resumen: string;
  fecha_creacion: string;
}

interface SummaryDetail {
  resumen_ejecutivo?: string;
  decisiones?: string;
  riesgos?: string;
  proximos_pasos?: string;
}

interface Job {
  id: string;
  reunion_id: string;
  estado: string;
  fuente: string;
  resumen_texto?: string;
  error_detalle?: string;
  fecha_actualizacion?: string;
}

const AUDIO_TYPES = [
  "audio/mp4",
  "audio/m4a",
  "audio/mpeg",
  "audio/mp3",
  "audio/wav",
  "audio/webm",
  "audio/ogg",
  "video/mp4",
  "video/webm",
  "video/ogg",
];

const AUDIO_EXTENSIONS = [".m4a", ".mp3", ".mp4", ".wav", ".webm", ".ogg"];

const TERMINAL_STATES = ["finalizado", "error", "cancelado"];

export default function SummariesPage() {
  const { language, t } = useLanguage();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string>("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [summaryDetail, setSummaryDetail] = useState<SummaryDetail | null>(null);
  const [job, setJob] = useState<Job | null>(null);

  const [loading, setLoading] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [activeMode, setActiveMode] = useState<"zoom" | "manual" | null>(null);

  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const [isDragging, setIsDragging] = useState(false);
  const [isDraggingAudio, setIsDraggingAudio] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
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
      setActiveMode(null);
      setError("");
      setSuccessMsg("");
      fetchSummary(selectedMeetingId);
      fetchJob(selectedMeetingId);
    }
  }, [selectedMeetingId]);

  useEffect(() => {
    if (summary) {
      stopPolling();
      setGenerating(false);
      return;
    }
    if (job && !TERMINAL_STATES.includes(job.estado)) {
      startPolling(job.reunion_id);
    } else if (job?.estado === "finalizado") {
      stopPolling();
      setGenerating(false);
      fetchSummary(job.reunion_id);
      setSuccessMsg(t("summaries.success"));
    } else if (job?.estado === "error") {
      stopPolling();
      setGenerating(false);
      setSuccessMsg("");
      setError(job.error_detalle || t("summaries.generateError"));
    }
  }, [job?.id, job?.estado, summary?.id]);

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
    setSummaryDetail(null);
    try {
      const { data } = await api.get<Summary>(`/summaries/meeting/${meetingId}`);
      setSummary(data);
      stopPolling();
      setGenerating(false);
      try {
        const detail = await api.get<SummaryDetail>(`/summaries/meeting/${meetingId}/detail`);
        setSummaryDetail(detail.data);
      } catch {
        // detail es opcional
      }
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error("Error loading summary", err);
      }
    } finally {
      setLoadingSummary(false);
    }
  };

  const fetchJob = async (meetingId: string) => {
    try {
      const { data } = await api.get<Job>(`/automation/summary/job/${meetingId}`);
      setJob(data);
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error("Error loading job", err);
      }
      setJob(null);
    }
  };

  const handleGenerateZoom = async () => {
    if (!selectedMeetingId) return;
    setGenerating(true);
    setActiveMode("zoom");
    setError("");
    setSuccessMsg(t("summaries.statusObteniendoTranscript"));
    try {
      await api.post("/automation/summary/zoom-recording", { reunion_id: selectedMeetingId });
      await fetchJob(selectedMeetingId);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.generateError"));
      setSuccessMsg("");
      setGenerating(false);
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

  const handleCancelJob = async () => {
    if (!job) return;
    try {
      await api.post(`/automation/summary/job/${job.id}/cancel`);
      stopPolling();
      setJob(null);
      setGenerating(false);
      setError("");
      setSuccessMsg(t("summaries.cancelled"));
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.cancelError"));
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
        headers: { "Content-Type": "multipart/form-data" },
      });
      startPolling(selectedMeetingId);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.uploadError"));
      setGenerating(false);
      setSuccessMsg("");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const uploadAudio = async (file: File) => {
    if (!selectedMeetingId) return;
    if (!AUDIO_TYPES.includes(file.type) && !AUDIO_EXTENSIONS.some((ext) => file.name.toLowerCase().endsWith(ext))) {
      setError(t("summaries.onlyAudio"));
      return;
    }
    setGenerating(true);
    setActiveMode("manual");
    setError("");
    setSuccessMsg(t("summaries.uploadingRecording"));
    const formData = new FormData();
    formData.append("reunion_id", selectedMeetingId);
    formData.append("file", file);
    try {
      await api.post("/automation/summary/recording", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchJob(selectedMeetingId);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("summaries.uploadError"));
      setSuccessMsg("");
      setGenerating(false);
    } finally {
      if (audioInputRef.current) audioInputRef.current.value = "";
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadAudio(file);
  };

  const handleDragOver = (e: React.DragEvent, audio: boolean = false) => {
    e.preventDefault();
    if (audio) setIsDraggingAudio(true);
    else setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent, audio: boolean = false) => {
    e.preventDefault();
    if (audio) setIsDraggingAudio(false);
    else setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent, audio: boolean = false) => {
    e.preventDefault();
    if (audio) setIsDraggingAudio(false);
    else setIsDragging(false);
    if (generating) return;
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (audio) uploadAudio(file);
      else uploadFile(file);
    }
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
    if (pollingTimeoutRef.current) clearTimeout(pollingTimeoutRef.current);
  };

  const startPolling = (meetingId: string) => {
    stopPolling();
    setGenerating(true);
    const startTime = Date.now();
    const maxDuration = 300 * 1000;

    pollingIntervalRef.current = setInterval(async () => {
      try {
        await fetchJob(meetingId);
        const { data } = await api.get<Summary>(`/summaries/meeting/${meetingId}`);
        if (data && data.resumen) {
          stopPolling();
          setSummary(data);
          setGenerating(false);
          setSuccessMsg(t("summaries.success"));
        }
      } catch (err: any) {
        if (err.response?.status !== 404) {
          stopPolling();
          setGenerating(false);
          setError(t("summaries.pollError"));
          setSuccessMsg("");
        }
      }
      if (Date.now() - startTime > maxDuration) {
        stopPolling();
        setGenerating(false);
        setError(t("summaries.timeout"));
        setSuccessMsg("");
      }
    }, 3000);

    pollingTimeoutRef.current = setTimeout(() => {
      stopPolling();
      setGenerating(false);
      setError(t("summaries.timeout"));
      setSuccessMsg("");
    }, maxDuration);
  };

  const statusLabel = (estado: string) => {
    const map: Record<string, string> = {
      pendiente: t("summaries.statusPendiente"),
      subiendo: t("summaries.statusSubiendo"),
      obteniendo_transcript: t("summaries.statusObteniendoTranscript"),
      transcribiendo: t("summaries.statusTranscribiendo"),
      generando: t("summaries.statusGenerando"),
      finalizado: t("summaries.statusFinalizado"),
      error: t("summaries.statusError"),
    };
    return map[estado] || estado;
  };

  const sourceLabel = (fuente: string) => {
    const map: Record<string, string> = {
      zoom_vtt: t("summaries.sourceZoomVtt"),
      manual: t("summaries.sourceManual"),
      zoom_audio: t("summaries.sourceZoom"),
    };
    return map[fuente] || fuente;
  };

  const selectedMeeting = meetings.find((m) => m.id === selectedMeetingId);
  const displayedJob = summary && job ? { ...job, estado: "finalizado", error_detalle: undefined } : job;
  const meetingGroups = [
    { type: "virtual", label: t("summaries.virtualMeetings"), color: "text-blue-600 dark:text-blue-400", icon: Video, count: meetings.filter((m) => (m.tipo || "").toLowerCase() === "virtual").length },
    { type: "presencial", label: t("summaries.inPersonMeetings"), color: "text-orange-600 dark:text-orange-400", icon: FileText, count: meetings.filter((m) => (m.tipo || "").toLowerCase() === "presencial").length },
    { type: "mixta", label: t("summaries.mixedMeetings"), color: "text-violet-600 dark:text-violet-400", icon: Sparkles, count: meetings.filter((m) => (m.tipo || "").toLowerCase() === "mixta").length },
  ];

  const formatDate = (date?: string) => {
    if (!date) return "";
    try {
      return format(parseISO(date), "dd MMM yyyy, HH:mm", { locale: language === "es" ? es : enUS });
    } catch {
      return "";
    }
  };

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
        <Link
          href="/chat"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-sm shrink-0"
        >
          <Bot className="w-5 h-5" />
          {t("summaries.chatbot")}
        </Link>
      </div>

      {(error || successMsg) && (
        <div className={`p-4 rounded-xl border ${error ? "bg-red-50 text-red-600 border-red-100 dark:bg-red-950/30 dark:border-red-900" : "bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-950/30 dark:border-emerald-900"}`}>
          <div className="flex items-center gap-2">
            {generating && !error && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
            {error || successMsg}
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {meetingGroups.map((group) => {
          const GroupIcon = group.icon;
          const groupMeetings = meetings.filter((meeting) => (meeting.tipo || "").toLowerCase() === group.type);
          return (
            <section key={group.type} className="bg-card border border-border rounded-2xl p-4 shadow-sm min-h-44">
              <h3 className={`font-semibold ${group.color} mb-3 flex items-center gap-2`}>
                <GroupIcon className="w-4 h-4" />
                {group.label}
                <span className="ml-auto text-xs bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-medium text-slate-600 dark:text-slate-400">{group.count}</span>
              </h3>
              <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                {groupMeetings.length === 0 ? (
                  <p className="text-sm app-muted py-3">{t("summaries.noMeetings")}</p>
                ) : (
                  groupMeetings.map((meeting) => (
                    <button
                      key={meeting.id}
                      onClick={() => setSelectedMeetingId(meeting.id)}
                      className={`w-full text-left p-3 rounded-xl border transition-colors ${
                        selectedMeetingId === meeting.id
                          ? "bg-brand-50 border-brand-200 dark:bg-brand-950/40 dark:border-brand-800"
                          : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800"
                      }`}
                    >
                      <span className="block font-medium text-sm truncate">{meeting.tema || t("common.noTopic")}</span>
                      <span className="text-xs app-muted flex items-center gap-1 mt-1">
                        <Calendar className="w-3 h-3" />
                        {meeting.fecha_inicio ? format(parseISO(meeting.fecha_inicio), "dd MMM yyyy", { locale: language === "es" ? es : enUS }) : t("common.noDate")}
                      </span>
                    </button>
                  ))
                )}
              </div>
            </section>
          );
        })}
      </div>

      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden min-h-[400px] flex flex-col">
        <div className="p-5 border-b border-border bg-slate-50/50 dark:bg-slate-900/50 flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h3 className="font-semibold flex items-center gap-2 text-foreground">
              <FileText className="w-5 h-5 text-brand-500" />
              {t("summaries.summaryTitle")}
            </h3>
            {selectedMeeting && (
              <div className="flex items-center gap-3 mt-1 text-xs app-muted">
                <span>{selectedMeeting.tema || t("common.noTopic")}</span>
                {selectedMeeting.fecha_inicio && (
                  <span className="inline-flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {formatDate(selectedMeeting.fecha_inicio)}
                  </span>
                )}
                {selectedMeeting.duracion_minutos && (
                  <span className="inline-flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {selectedMeeting.duracion_minutos} min
                  </span>
                )}
              </div>
            )}
          </div>
          {displayedJob && (
            <div className="flex items-center gap-2 text-sm">
              <span className="app-muted">{t("summaries.statusLabel")}:</span>
              <span
                className={`font-medium flex items-center gap-1 ${
                  displayedJob.estado === "error"
                    ? "text-red-600"
                    : displayedJob.estado === "finalizado"
                    ? "text-emerald-600"
                    : "text-blue-600"
                }`}
              >
                {displayedJob.estado === "error" && <XCircle className="w-4 h-4" />}
                {displayedJob.estado === "finalizado" && <CheckCircle className="w-4 h-4" />}
                {!["error", "finalizado"].includes(displayedJob.estado) && <Loader2 className="w-4 h-4 animate-spin" />}
                {statusLabel(displayedJob.estado)}
              </span>
              <span className="app-muted">|</span>
              <span className="app-muted">{t("summaries.sourceLabel")}:</span>
              <span className="font-medium text-slate-700 dark:text-slate-300">{sourceLabel(displayedJob.fuente)}</span>
              {!TERMINAL_STATES.includes(displayedJob.estado) && (
                <button
                  onClick={handleCancelJob}
                  className="ml-2 inline-flex items-center gap-1 rounded-lg border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-900 dark:hover:bg-red-950/50"
                >
                  <CircleStop className="h-3.5 w-3.5" />
                  {t("summaries.cancelProcess")}
                </button>
              )}
            </div>
          )}
        </div>

        <div className="p-6 flex-1 flex flex-col">
          <input type="file" accept={AUDIO_EXTENSIONS.join(",")} className="hidden" ref={audioInputRef} onChange={handleAudioUpload} />
          {loadingSummary ? (
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-brand-600" />
            </div>
          ) : summary ? (
            <div className="flex-1 space-y-5">
              <div className="bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 rounded-xl p-5">
                <h4 className="text-sm font-semibold text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Resumen
                </h4>
                <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">{summary.resumen}</p>
              </div>

              {summaryDetail && (
                <div className="grid gap-4 md:grid-cols-2">
                  {summaryDetail.resumen_ejecutivo && (
                    <div className="bg-white dark:bg-slate-900 border border-border rounded-xl p-4 md:col-span-2">
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-brand-500" />
                        {language === "es" ? "Resumen Ejecutivo" : "Executive Summary"}
                      </h4>
                      <p className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{summaryDetail.resumen_ejecutivo}</p>
                    </div>
                  )}
                  {summaryDetail.decisiones && (
                    <div className="bg-white dark:bg-slate-900 border border-border rounded-xl p-4">
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                        {t("summaries.decisiones")}
                      </h4>
                      <p className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{summaryDetail.decisiones}</p>
                    </div>
                  )}
                  {summaryDetail.riesgos && (
                    <div className="bg-white dark:bg-slate-900 border border-border rounded-xl p-4">
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-amber-500" />
                        {t("summaries.riesgos")}
                      </h4>
                      <p className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{summaryDetail.riesgos}</p>
                    </div>
                  )}
                  {summaryDetail.proximos_pasos && (
                    <div className="bg-white dark:bg-slate-900 border border-border rounded-xl p-4 md:col-span-2">
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <RefreshCw className="w-4 h-4 text-blue-500" />
                        {t("summaries.proximosPasos")}
                      </h4>
                      <p className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{summaryDetail.proximos_pasos}</p>
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                <p className="text-xs app-muted">
                  {t("summaries.generatedAt")}: {summary.fecha_creacion ? format(parseISO(summary.fecha_creacion), "dd MMM, yyyy HH:mm", { locale: language === "es" ? es : enUS }) : "—"}
                </p>
                {selectedMeeting?.tipo !== "presencial" && (
                  <button
                    onClick={() => audioInputRef.current?.click()}
                    disabled={generating}
                    className="self-start btn-primary inline-flex items-center gap-2 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600"
                  >
                    <Headphones className="w-4 h-4" />
                    {t("summaries.replaceRecording")}
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-5 py-8">
              {selectedMeeting?.tipo === "presencial" ? (
                <div
                  className={`w-full max-w-md border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center transition-all duration-200 ${
                    isDragging ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20" : "border-border hover:border-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/30"
                  } ${generating ? "opacity-50 pointer-events-none" : ""}`}
                  onDragOver={(e) => handleDragOver(e)}
                  onDragLeave={(e) => handleDragLeave(e)}
                  onDrop={(e) => handleDrop(e)}
                >
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragging ? "bg-brand-100 text-brand-600" : "bg-slate-100 dark:bg-slate-800 text-slate-400"}`}>
                    {generating ? <Loader2 className="w-8 h-8 animate-spin" /> : <UploadCloud className="w-8 h-8" />}
                  </div>
                  <h4 className="text-lg font-medium text-foreground mb-2">{generating ? t("summaries.processingMinutes") : t("summaries.uploadMinutes")}</h4>
                  <p className="text-sm app-muted mb-6 text-center">{generating ? t("summaries.processingText") : t("summaries.dropText")}</p>
                  <input type="file" accept=".pdf" className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
                  {!generating && (
                    <button onClick={() => fileInputRef.current?.click()} className="btn-primary bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 shadow-orange-500/20">
                      {t("summaries.selectPdf")}
                    </button>
                  )}
                </div>
              ) : (
                <>
                  <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center">
                    <MessageSquare className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-medium text-foreground mb-1">{t("summaries.noSummary")}</h4>
                    <p className="text-sm app-muted max-w-sm mx-auto">{t("summaries.noSummaryText")}</p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 w-full max-w-md">
                    <button
                      onClick={handleGenerateZoom}
                      disabled={generating}
                      className="btn-primary inline-flex items-center justify-center gap-2 flex-1 bg-blue-600 hover:bg-blue-500"
                    >
                      {generating && activeMode === "zoom" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Cloud className="w-4 h-4" />}
                      {generating && activeMode === "zoom" ? t("summaries.statusObteniendoTranscript") : t("summaries.useZoom")}
                    </button>
                    <button
                      onClick={() => audioInputRef.current?.click()}
                      disabled={generating}
                      className="btn-primary inline-flex items-center justify-center gap-2 flex-1 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600"
                    >
                      {generating && activeMode === "manual" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Headphones className="w-4 h-4" />}
                      {generating && activeMode === "manual" ? t("summaries.statusSubiendo") : t("summaries.uploadRecording")}
                    </button>
                  </div>
                  <div className="text-xs app-muted">{t("summaries.processingTranscript")}</div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
