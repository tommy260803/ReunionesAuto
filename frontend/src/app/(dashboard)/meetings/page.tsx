"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Calendar, Clock, Loader2, Pencil, Trash2, Users, Video, X, CheckCircle, AlertCircle } from "lucide-react";

interface Meeting { id: string; tema?: string; fecha_inicio?: string; duracion_minutos?: number; estado?: string; tipo?: string; join_url?: string; }

const emptyForm = { tema: "", fecha_inicio: "", duracion_minutos: "", tipo: "virtual", estado: "programada" };

export default function MeetingsPage() {
  const { user } = useAuth();
  const { language, t } = useLanguage();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [editing, setEditing] = useState<Meeting | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const fetchMeetings = async () => {
    try {
      const { data } = await api.get<Meeting[]>("/meetings");
      setMeetings(data);
    } catch {
      setError(t("meetings.loadError"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMeetings(); }, []);

  const openEditor = (meeting: Meeting) => {
    setEditing(meeting);
    setForm({
      tema: meeting.tema || "",
      fecha_inicio: meeting.fecha_inicio ? meeting.fecha_inicio.slice(0, 16) : "",
      duracion_minutos: meeting.duracion_minutos?.toString() || "",
      tipo: meeting.tipo || "virtual",
      estado: meeting.estado || "programada",
    });
    setError("");
  };

  const saveMeeting = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editing) return;
    setSaving(true);
    try {
      await api.patch(`/meetings/${editing.id}`, { ...form, fecha_inicio: form.fecha_inicio ? new Date(form.fecha_inicio).toISOString() : null, duracion_minutos: form.duracion_minutos ? Number(form.duracion_minutos) : null });
      setEditing(null);
      await fetchMeetings();
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || t("meetings.updateError"));
    } finally {
      setSaving(false);
    }
  };

  const deleteMeeting = async (meeting: Meeting) => {
    if (!confirm(`${t("meetings.deleteConfirmPrefix")} "${meeting.tema || t("common.noTopic")}"? ${t("meetings.deleteConfirmSuffix")}`)) return;
    try {
      await api.delete(`/meetings/${meeting.id}`);
      await fetchMeetings();
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || t("meetings.deleteError"));
    }
  };

  const statusColor = (status?: string) => {
    if (status === "completada") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400";
    if (status === "programada") return "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400";
    if (status === "cancelada") return "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400";
    return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400";
  };

  const statusIcon = (status?: string) => {
    if (status === "completada") return <CheckCircle className="w-3.5 h-3.5" />;
    if (status === "programada") return <Clock className="w-3.5 h-3.5" />;
    if (status === "cancelada") return <AlertCircle className="w-3.5 h-3.5" />;
    return null;
  };

  const statusLabel = (status?: string) => status === "completada" ? t("common.completed") : status === "programada" ? t("common.scheduled") : status === "cancelada" ? t("common.cancelled") : t("common.unknown");
  const typeLabel = (type?: string) => type === "virtual" ? t("common.virtual") : type === "presencial" ? t("common.inPerson") : type === "mixta" ? t("common.mixed") : "-";

  const typeColor = (type?: string) => {
    if (type === "virtual") return "bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400";
    if (type === "presencial") return "bg-orange-50 text-orange-600 dark:bg-orange-950/30 dark:text-orange-400";
    if (type === "mixta") return "bg-violet-50 text-violet-600 dark:bg-violet-950/30 dark:text-violet-400";
    return "bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400";
  };

  const formatDate = (date?: string) => {
    if (!date) return "";
    try {
      return format(parseISO(date), "dd MMM yyyy, HH:mm", { locale: language === "es" ? es : enUS });
    } catch {
      return "";
    }
  };

  const completedCount = meetings.filter((m) => m.estado === "completada").length;
  const scheduledCount = meetings.filter((m) => m.estado === "programada").length;

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">{t("meetings.title")}</h1>
          <p className="text-slate-500">{t("meetings.subtitle")}</p>
        </div>
        <div className="flex gap-2">
          <span className="telemetry-card px-3 py-2 text-sm font-medium inline-flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            {completedCount} {t("common.completedPlural").toLowerCase()}
          </span>
          <span className="telemetry-card px-3 py-2 text-sm font-medium inline-flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            {scheduledCount} {t("common.scheduled").toLowerCase()}
          </span>
        </div>
      </div>

      {error && <div className="p-4 bg-red-50 dark:bg-red-950/30 text-red-600 rounded-xl border border-red-100 dark:border-red-900">{error}</div>}

      {meetings.length === 0 ? (
        <div className="telemetry-card p-12 text-center">
          <Calendar className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
          <p className="text-slate-500 text-lg">{t("meetings.empty")}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {meetings.map((meeting) => (
            <div key={meeting.id} className="telemetry-card p-5 flex flex-col sm:flex-row sm:items-center gap-4 transition-all duration-200">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-foreground truncate">{meeting.tema || t("common.noTopic")}</h3>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold ${statusColor(meeting.estado)}`}>
                    {statusIcon(meeting.estado)}
                    {statusLabel(meeting.estado)}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-sm app-muted">
                  <span className="inline-flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {formatDate(meeting.fecha_inicio) || t("common.noDate")}
                  </span>
                  {meeting.duracion_minutos && (
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {meeting.duracion_minutos} min
                    </span>
                  )}
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${typeColor(meeting.tipo)}`}>
                    <Video className="w-3 h-3" />
                    {typeLabel(meeting.tipo)}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <a href="/participants" className="inline-flex p-2 text-brand-600 hover:bg-brand-50 rounded-lg transition-colors" title={t("meetings.viewParticipants")}>
                  <Users className="w-4 h-4" />
                </a>
                {user?.is_admin && (
                  <>
                    <button onClick={() => openEditor(meeting)} className="p-2 text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors" title={t("common.edit")}>
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button onClick={() => deleteMeeting(meeting)} className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title={t("common.delete")}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {editing && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"><form onSubmit={saveMeeting} className="w-full max-w-lg bg-card border border-border rounded-2xl shadow-xl"><div className="p-5 border-b border-border flex justify-between"><h2 className="text-lg font-semibold">{t("meetings.editTitle")}</h2><button type="button" onClick={() => setEditing(null)}><X className="w-5 h-5" /></button></div><div className="p-5 space-y-4"><label className="block text-sm font-medium">{t("meetings.topic")}<input required value={form.tema} onChange={(e) => setForm({ ...form, tema: e.target.value })} className="mt-1 w-full input-field" /></label><div className="grid sm:grid-cols-2 gap-4"><label className="text-sm font-medium">{t("meetings.dateTime")}<input type="datetime-local" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} className="mt-1 w-full input-field" /></label><label className="text-sm font-medium">{t("meetings.durationMin")}<input type="number" min="1" value={form.duracion_minutos} onChange={(e) => setForm({ ...form, duracion_minutos: e.target.value })} className="mt-1 w-full input-field" /></label></div><div className="grid sm:grid-cols-2 gap-4"><label className="text-sm font-medium">{t("common.type")}<select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} className="mt-1 w-full input-field"><option value="virtual">{t("common.virtual")}</option><option value="presencial">{t("common.inPerson")}</option><option value="mixta">{t("common.mixed")}</option></select></label><label className="text-sm font-medium">{t("common.status")}<select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })} className="mt-1 w-full input-field"><option value="programada">{t("common.scheduled")}</option><option value="completada">{t("common.completed")}</option><option value="cancelada">{t("common.cancelled")}</option></select></label></div></div><div className="p-5 pt-0 flex justify-end gap-3"><button type="button" onClick={() => setEditing(null)} className="px-4 py-2.5 rounded-xl border border-border text-sm font-medium">{t("common.cancel")}</button><button disabled={saving} className="btn-primary">{saving ? t("common.saving") : t("meetings.saveChanges")}</button></div></form></div>}
    </div>
  );
}
