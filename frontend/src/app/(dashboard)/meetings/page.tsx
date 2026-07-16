"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Calendar, Clock, Loader2, Pencil, Trash2, Users, Video, X } from "lucide-react";

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

  const statusLabel = (status?: string) => status === "completada" ? t("common.completed") : status === "programada" ? t("common.scheduled") : status === "cancelada" ? t("common.cancelled") : t("common.unknown");
  const typeLabel = (type?: string) => type === "virtual" ? t("common.virtual") : type === "presencial" ? t("common.inPerson") : type === "mixta" ? t("common.mixed") : "-";

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold tracking-tight text-foreground">{t("meetings.title")}</h1><p className="text-slate-500">{t("meetings.subtitle")}</p></div>
      {error && <div className="p-4 bg-red-50 dark:bg-red-950/30 text-red-600 rounded-xl border border-red-100 dark:border-red-900">{error}</div>}
      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 dark:bg-slate-900/50 border-b border-border"><tr><th className="px-6 py-4">{t("meetings.topic")}</th><th className="px-6 py-4">{t("meetings.dateTime")}</th><th className="px-6 py-4">{t("common.type")}</th><th className="px-6 py-4">{t("common.status")}</th><th className="px-6 py-4 text-right">{t("common.actions")}</th></tr></thead>
            <tbody className="divide-y divide-border">
              {meetings.length === 0 ? <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">{t("meetings.empty")}</td></tr> : meetings.map((meeting) => <tr key={meeting.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                <td className="px-6 py-4 font-medium text-foreground">{meeting.tema || t("common.noTopic")}</td>
                <td className="px-6 py-4 text-slate-600 dark:text-slate-300"><div className="flex items-center gap-2"><Calendar className="w-4 h-4 text-slate-400" />{meeting.fecha_inicio ? format(parseISO(meeting.fecha_inicio), "dd MMM yyyy, HH:mm", { locale: language === "es" ? es : enUS }) : "-"}</div>{meeting.duracion_minutos ? <span className="text-xs text-slate-500 flex items-center gap-1 mt-1"><Clock className="w-3 h-3" />{meeting.duracion_minutos} min</span> : null}</td>
                <td className="px-6 py-4"><span className="inline-flex items-center gap-1.5"><Video className="w-4 h-4 text-slate-400" />{typeLabel(meeting.tipo)}</span></td>
                <td className="px-6 py-4"><span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${statusColor(meeting.estado)}`}>{statusLabel(meeting.estado)}</span></td>
                <td className="px-6 py-4 text-right"><a href="/participants" className="inline-flex p-2 text-brand-600 hover:bg-brand-50 rounded-lg" title={t("meetings.viewParticipants")}><Users className="w-4 h-4" /></a>{user?.is_admin && <><button onClick={() => openEditor(meeting)} className="p-2 text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg" title={t("common.edit")}><Pencil className="w-4 h-4" /></button><button onClick={() => deleteMeeting(meeting)} className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg" title={t("common.delete")}><Trash2 className="w-4 h-4" /></button></>}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </div>

      {editing && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"><form onSubmit={saveMeeting} className="w-full max-w-lg bg-card border border-border rounded-2xl shadow-xl"><div className="p-5 border-b border-border flex justify-between"><h2 className="text-lg font-semibold">{t("meetings.editTitle")}</h2><button type="button" onClick={() => setEditing(null)}><X className="w-5 h-5" /></button></div><div className="p-5 space-y-4"><label className="block text-sm font-medium">{t("meetings.topic")}<input required value={form.tema} onChange={(e) => setForm({ ...form, tema: e.target.value })} className="mt-1 w-full input-field" /></label><div className="grid sm:grid-cols-2 gap-4"><label className="text-sm font-medium">{t("meetings.dateTime")}<input type="datetime-local" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} className="mt-1 w-full input-field" /></label><label className="text-sm font-medium">{t("meetings.durationMin")}<input type="number" min="1" value={form.duracion_minutos} onChange={(e) => setForm({ ...form, duracion_minutos: e.target.value })} className="mt-1 w-full input-field" /></label></div><div className="grid sm:grid-cols-2 gap-4"><label className="text-sm font-medium">{t("common.type")}<select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} className="mt-1 w-full input-field"><option value="virtual">{t("common.virtual")}</option><option value="presencial">{t("common.inPerson")}</option><option value="mixta">{t("common.mixed")}</option></select></label><label className="text-sm font-medium">{t("common.status")}<select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })} className="mt-1 w-full input-field"><option value="programada">{t("common.scheduled")}</option><option value="completada">{t("common.completed")}</option><option value="cancelada">{t("common.cancelled")}</option></select></label></div></div><div className="p-5 pt-0 flex justify-end gap-3"><button type="button" onClick={() => setEditing(null)} className="px-4 py-2.5 rounded-xl border border-border">{t("common.cancel")}</button><button disabled={saving} className="btn-primary">{saving ? t("common.saving") : t("meetings.saveChanges")}</button></div></form></div>}
    </div>
  );
}
