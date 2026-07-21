"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import api from "@/lib/api";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { useLanguage } from "@/context/LanguageContext";
import {
  Loader2,
  FileText,
  UploadCloud,
  ScrollText,
  Plus,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Trash2,
  Pencil,
  Eye,
  Download,
  X,
  ChevronRight,
  Video,
  Sparkles,
  FileUp,
  Type,
} from "lucide-react";
import Link from "next/link";

interface Meeting {
  id: string;
  tema: string;
  fecha_inicio: string;
  tipo: string;
  duracion_minutos?: number;
}

interface Acta {
  id: string;
  reunion_id: string;
  numero?: number;
  titulo: string;
  tipo_reunion: string;
  contenido?: string;
  formato_origen: string;
  estado: string;
  fecha_reunion?: string;
  participantes?: string;
  orden_dia?: string;
  decisiones?: string;
  tareas_extraidas?: string;
  proximos_pasos?: string;
  observaciones?: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

const ALLOWED_FILE_TYPES = [".pdf", ".docx"];
const MAX_FILE_SIZE = 20 * 1024 * 1024;

export default function ActasPage() {
  const { language, t } = useLanguage();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [actas, setActas] = useState<Acta[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string>("");
  const [selectedActa, setSelectedActa] = useState<Acta | null>(null);

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showTextModal, setShowTextModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const [filterType, setFilterType] = useState<string>("all");

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedActa) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [selectedActa]);

  const fetchData = async () => {
    try {
      const [meetingsRes, actasRes] = await Promise.all([
        api.get<Meeting[]>("/meetings"),
        api.get<Acta[]>("/actas"),
      ]);
      setMeetings(meetingsRes.data);
      setActas(actasRes.data);
      if (meetingsRes.data.length > 0 && !selectedMeetingId) {
        setSelectedMeetingId(meetingsRes.data[0].id);
      }
    } catch {
      setError(t("actas.loadError"));
    } finally {
      setLoading(false);
    }
  };

  const filteredActas = actas.filter(
    (a) => filterType === "all" || a.tipo_reunion === filterType
  );

  const handleUploadFile = async (file: File) => {
    if (!selectedMeetingId) return;
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_FILE_TYPES.includes(ext)) {
      setError(t("actas.uploadHint"));
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError("El archivo excede el límite de 20 MB.");
      return;
    }

    setGenerating(true);
    setError("");
    setSuccessMsg(t("actas.generating"));
    setShowUploadModal(false);

    const formData = new FormData();
    formData.append("reunion_id", selectedMeetingId);
    formData.append("file", file);
    formData.append("titulo", `Acta - ${file.name}`);

    try {
      const { data } = await api.post<Acta>("/actas/generate", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSuccessMsg(t("actas.generated"));
      setActas((prev) => [data, ...prev]);
      setSelectedActa(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("actas.generateError"));
    } finally {
      setGenerating(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleUploadFromText = async (text: string, titulo: string) => {
    if (!selectedMeetingId || !text.trim()) return;

    setGenerating(true);
    setError("");
    setSuccessMsg(t("actas.generating"));
    setShowTextModal(false);

    const formData = new FormData();
    formData.append("reunion_id", selectedMeetingId);
    formData.append("titulo", titulo || "Acta de Reunión");
    formData.append("texto", text);

    try {
      const { data } = await api.post<Acta>(
        "/actas/generate-from-text",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setSuccessMsg(t("actas.generated"));
      setActas((prev) => [data, ...prev]);
      setSelectedActa(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("actas.generateError"));
    } finally {
      setGenerating(false);
    }
  };

  const handleFinalize = async (actaId: string) => {
    try {
      const { data } = await api.post<Acta>(`/actas/${actaId}/finalize`);
      setActas((prev) =>
        prev.map((a) => (a.id === actaId ? { ...a, estado: "finalizada" } : a))
      );
      if (selectedActa?.id === actaId) {
        setSelectedActa({ ...selectedActa, estado: "finalizada" });
      }
      setSuccessMsg(t("actas.finalizedSuccess"));
    } catch (err: any) {
      setError(err.response?.data?.detail || t("actas.finalizeError"));
    }
  };

  const handleDelete = async (actaId: string) => {
    if (!confirm(t("actas.deleteConfirm"))) return;
    try {
      await api.delete(`/actas/${actaId}`);
      setActas((prev) => prev.filter((a) => a.id !== actaId));
      if (selectedActa?.id === actaId) setSelectedActa(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || t("actas.deleteError"));
    }
  };

  const handleUpdate = async (actaId: string, updates: Partial<Acta>) => {
    try {
      const { data } = await api.patch<Acta>(`/actas/${actaId}`, updates);
      setActas((prev) =>
        prev.map((a) => (a.id === actaId ? { ...a, ...data } : a))
      );
      if (selectedActa?.id === actaId) setSelectedActa(data);
      setShowEditModal(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al actualizar");
    }
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
    const file = e.dataTransfer.files?.[0];
    if (file) handleUploadFile(file);
  };

  const formatDate = (date?: string) => {
    if (!date) return "";
    try {
      return format(parseISO(date), "dd MMM yyyy, HH:mm", {
        locale: language === "es" ? es : enUS,
      });
    } catch {
      return "";
    }
  };

  const tipoLabel = (tipo: string) => {
    const map: Record<string, string> = {
      virtual: t("actas.virtual"),
      presencial: t("actas.inPerson"),
      mixta: t("actas.mixed"),
    };
    return map[tipo] || tipo;
  };

  const tipoColor = (tipo: string) => {
    const map: Record<string, string> = {
      virtual: "bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400",
      presencial:
        "bg-orange-50 text-orange-600 dark:bg-orange-950/30 dark:text-orange-400",
      mixta:
        "bg-violet-50 text-violet-600 dark:bg-violet-950/30 dark:text-violet-400",
    };
    return map[tipo] || "bg-slate-50 text-slate-600";
  };

  const formatBadge = (formato: string) => {
    const map: Record<string, string> = {
      pdf: t("actas.fromPdf"),
      word: t("actas.fromWord"),
      manual: t("actas.fromText"),
      transcripcion: t("actas.fromTranscription"),
    };
    return map[formato] || formato;
  };

  const renderMarkdown = (content: string) => {
    return content.split("\n").map((line, i) => {
      if (line.startsWith("# "))
        return (
          <h1 key={i} className="text-2xl font-bold text-foreground mt-6 mb-3">
            {line.slice(2)}
          </h1>
        );
      if (line.startsWith("## "))
        return (
          <h2
            key={i}
            className="text-lg font-semibold text-foreground mt-5 mb-2 border-b border-border pb-1"
          >
            {line.slice(3)}
          </h2>
        );
      if (line.startsWith("### "))
        return (
          <h3 key={i} className="text-base font-semibold text-foreground mt-4 mb-1">
            {line.slice(4)}
          </h3>
        );
      if (line.startsWith("- **"))
        return (
          <li key={i} className="ml-4 text-sm text-slate-600 dark:text-slate-400">
            <span
              className="font-semibold text-foreground"
              dangerouslySetInnerHTML={{
                __html: line
                  .slice(2)
                  .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
              }}
            />
          </li>
        );
      if (line.startsWith("- "))
        return (
          <li key={i} className="ml-4 text-sm text-slate-600 dark:text-slate-400 list-disc">
            {line.slice(2)}
          </li>
        );
      if (line.trim() === "") return <br key={i} />;
      return (
        <p key={i} className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          {line}
        </p>
      );
    });
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {t("actas.title")}
          </h1>
          <p className="text-slate-500">{t("actas.subtitle")}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowTextModal(true)}
            disabled={!selectedMeetingId}
            className="inline-flex items-center gap-2 bg-slate-600 hover:bg-slate-500 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-sm"
          >
            <Type className="w-4 h-4" />
            {t("actas.fromText")}
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={!selectedMeetingId || generating}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-sm"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileUp className="w-4 h-4" />
            )}
            {t("actas.uploadDocument")}
          </button>
        </div>
      </div>

      <input
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        ref={fileInputRef}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUploadFile(file);
        }}
      />

      {(error || successMsg) && (
        <div
          className={`p-4 rounded-xl border ${
            error
              ? "bg-red-50 text-red-600 border-red-100 dark:bg-red-950/30 dark:border-red-900"
              : "bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-950/30 dark:border-emerald-900"
          }`}
        >
          <div className="flex items-center gap-2">
            {generating && !error && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
            {error || successMsg}
          </div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="lg:w-80 shrink-0 space-y-4">
          <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
            <h3 className="font-semibold text-foreground mb-3 text-sm">
              {t("meetings.title")}
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {meetings.length === 0 ? (
                <p className="text-sm text-slate-500 py-2">{t("summaries.noMeetings")}</p>
              ) : (
                meetings.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setSelectedMeetingId(m.id)}
                    className={`w-full text-left p-3 rounded-xl border transition-colors ${
                      selectedMeetingId === m.id
                        ? "bg-brand-50 border-brand-200 dark:bg-brand-950/40 dark:border-brand-800"
                        : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800"
                    }`}
                  >
                    <span className="block font-medium text-sm truncate">
                      {m.tema || t("common.noTopic")}
                    </span>
                    <span className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                      <Calendar className="w-3 h-3" />
                      {m.fecha_inicio
                        ? format(parseISO(m.fecha_inicio), "dd MMM yyyy", {
                            locale: language === "es" ? es : enUS,
                          })
                        : t("common.noDate")}
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
            <h3 className="font-semibold text-foreground mb-3 text-sm">
              {t("common.filter")} {t("common.type")}
            </h3>
            <div className="flex flex-wrap gap-2">
              {["all", "virtual", "presencial", "mixta"].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                    filterType === type
                      ? "bg-brand-600 text-white"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
                  }`}
                >
                  {type === "all" ? t("actas.allTypes") : tipoLabel(type)}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
            <h3 className="font-semibold text-foreground mb-3 text-sm">
              {t("actas.title")}
              <span className="ml-2 text-xs bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-medium text-slate-600 dark:text-slate-400">
                {filteredActas.length}
              </span>
            </h3>
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {filteredActas.length === 0 ? (
                <p className="text-sm text-slate-500 py-3">{t("actas.noActas")}</p>
              ) : (
                filteredActas.map((acta) => (
                  <button
                    key={acta.id}
                    onClick={() => setSelectedActa(acta)}
                    className={`w-full text-left p-3 rounded-xl border transition-colors ${
                      selectedActa?.id === acta.id
                        ? "bg-brand-50 border-brand-200 dark:bg-brand-950/40 dark:border-brand-800"
                        : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="block font-medium text-sm truncate">
                        {acta.titulo}
                      </span>
                      {acta.estado === "finalizada" ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
                      ) : (
                        <Pencil className="w-4 h-4 text-amber-500 shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-medium ${tipoColor(
                          acta.tipo_reunion
                        )}`}
                      >
                        {tipoLabel(acta.tipo_reunion)}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        #{acta.numero}
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="flex-1 bg-card border border-border rounded-2xl shadow-sm overflow-hidden min-h-[500px] flex flex-col">
          {selectedActa ? (
            <>
              <div className="p-5 border-b border-border bg-slate-50/50 dark:bg-slate-900/50 flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                <div>
                  <h3 className="font-semibold flex items-center gap-2 text-foreground">
                    <ScrollText className="w-5 h-5 text-brand-500" />
                    {selectedActa.titulo}
                    <span className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-medium text-slate-600 dark:text-slate-400">
                      #{selectedActa.numero}
                    </span>
                  </h3>
                  <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium ${tipoColor(
                        selectedActa.tipo_reunion
                      )}`}
                    >
                      {tipoLabel(selectedActa.tipo_reunion)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(selectedActa.fecha_creacion)}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        selectedActa.estado === "finalizada"
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {selectedActa.estado === "finalizada"
                        ? t("actas.finalized")
                        : t("actas.draft")}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {selectedActa.estado === "borrador" && (
                    <button
                      onClick={() => handleFinalize(selectedActa.id)}
                      className="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                    >
                      <CheckCircle className="w-4 h-4" />
                      {t("actas.finalize")}
                    </button>
                  )}
                  <button
                    onClick={() => setShowEditModal(true)}
                    className="inline-flex items-center gap-1.5 bg-slate-600 hover:bg-slate-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                  >
                    <Pencil className="w-4 h-4" />
                    {t("actas.editActa")}
                  </button>
                  <button
                    onClick={() => handleDelete(selectedActa.id)}
                    className="inline-flex items-center gap-1.5 border border-red-200 text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="p-6 flex-1 overflow-y-auto">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  {selectedActa.contenido
                    ? renderMarkdown(selectedActa.contenido)
                    : (
                      <p className="text-slate-500 italic">
                        No hay contenido generado.
                      </p>
                    )}
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-5 py-8 px-4">
              <div
                className={`w-full max-w-md border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center transition-all duration-200 ${
                  isDragging
                    ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20"
                    : "border-border hover:border-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/30"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${
                    isDragging
                      ? "bg-brand-100 text-brand-600"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-400"
                  }`}
                >
                  {generating ? (
                    <Loader2 className="w-8 h-8 animate-spin" />
                  ) : (
                    <ScrollText className="w-8 h-8" />
                  )}
                </div>
                <h4 className="text-lg font-medium text-foreground mb-2">
                  {generating ? t("actas.generating") : t("actas.noActas")}
                </h4>
                <p className="text-sm text-slate-500 mb-6 text-center max-w-sm">
                  {t("actas.noActasText")}
                </p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={!selectedMeetingId || generating}
                    className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
                  >
                    <FileUp className="w-5 h-5" />
                    {t("actas.uploadDocument")}
                  </button>
                  <button
                    onClick={() => setShowTextModal(true)}
                    disabled={!selectedMeetingId || generating}
                    className="inline-flex items-center justify-center gap-2 bg-slate-600 hover:bg-slate-500 text-white px-6 py-3 rounded-xl font-medium transition-colors"
                  >
                    <Type className="w-5 h-5" />
                    {t("actas.fromText")}
                  </button>
                </div>
                <p className="text-xs text-slate-400 mt-4">{t("actas.uploadHint")}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {showTextModal && (
        <TextModal
          onClose={() => setShowTextModal(false)}
          onSubmit={handleUploadFromText}
          generating={generating}
          t={t}
        />
      )}

      {showEditModal && selectedActa && (
        <EditModal
          acta={selectedActa}
          onClose={() => setShowEditModal(false)}
          onSave={(updates) => handleUpdate(selectedActa.id, updates)}
          t={t}
        />
      )}
    </div>
  );
}

function TextModal({
  onClose,
  onSubmit,
  generating,
  t,
}: {
  onClose: () => void;
  onSubmit: (text: string, titulo: string) => void;
  generating: boolean;
  t: (key: string) => string;
}) {
  const [text, setText] = useState("");
  const [titulo, setTitulo] = useState("Acta de Reunión");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-card border border-border rounded-2xl shadow-xl max-h-[90vh] flex flex-col">
        <div className="p-5 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-semibold">{t("actas.fromText")}</h2>
          <button onClick={onClose}>
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5 space-y-4 flex-1 overflow-y-auto">
          <label className="block text-sm font-medium">
            {t("actas.enterTitle")}
            <input
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              className="mt-1 w-full input-field"
            />
          </label>
          <label className="block text-sm font-medium">
            {t("actas.pasteText")}
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              className="mt-1 w-full input-field resize-y"
              placeholder={t("actas.pasteText")}
            />
          </label>
        </div>
        <div className="p-5 border-t border-border flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl border border-border text-sm font-medium hover:bg-slate-50"
          >
            {t("common.cancel")}
          </button>
          <button
            onClick={() => onSubmit(text, titulo)}
            disabled={!text.trim() || generating}
            className="px-4 py-2 rounded-xl bg-brand-600 text-white text-sm font-medium hover:bg-brand-500 disabled:opacity-50 inline-flex items-center gap-2"
          >
            {generating && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("actas.generateActa")}
          </button>
        </div>
      </div>
    </div>
  );
}

function EditModal({
  acta,
  onClose,
  onSave,
  t,
}: {
  acta: Acta;
  onClose: () => void;
  onSave: (updates: Partial<Acta>) => void;
  t: (key: string) => string;
}) {
  const [titulo, setTitulo] = useState(acta.titulo);
  const [contenido, setContenido] = useState(acta.contenido || "");
  const [participantes, setParticipantes] = useState(acta.participantes || "");
  const [observaciones, setObservaciones] = useState(acta.observaciones || "");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-3xl bg-card border border-border rounded-2xl shadow-xl max-h-[90vh] flex flex-col">
        <div className="p-5 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-semibold">{t("actas.editActa")}</h2>
          <button onClick={onClose}>
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5 space-y-4 flex-1 overflow-y-auto">
          <label className="block text-sm font-medium">
            {t("actas.enterTitle")}
            <input
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              className="mt-1 w-full input-field"
            />
          </label>
          <label className="block text-sm font-medium">
            Contenido (Markdown)
            <textarea
              value={contenido}
              onChange={(e) => setContenido(e.target.value)}
              rows={16}
              className="mt-1 w-full input-field resize-y font-mono text-sm"
            />
          </label>
          <label className="block text-sm font-medium">
            {t("actas.participants")}
            <textarea
              value={participantes}
              onChange={(e) => setParticipantes(e.target.value)}
              rows={3}
              className="mt-1 w-full input-field resize-y"
            />
          </label>
          <label className="block text-sm font-medium">
            {t("actas.observations")}
            <textarea
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              rows={3}
              className="mt-1 w-full input-field resize-y"
            />
          </label>
        </div>
        <div className="p-5 border-t border-border flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl border border-border text-sm font-medium hover:bg-slate-50"
          >
            {t("common.cancel")}
          </button>
          <button
            onClick={() =>
              onSave({ titulo, contenido, participantes, observaciones })
            }
            className="px-4 py-2 rounded-xl bg-brand-600 text-white text-sm font-medium hover:bg-brand-500"
          >
            {t("common.save")}
          </button>
        </div>
      </div>
    </div>
  );
}
