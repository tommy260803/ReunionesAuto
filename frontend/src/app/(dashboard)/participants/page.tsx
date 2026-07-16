"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2, Plus, Save, Search, Users, X } from "lucide-react";

interface Meeting { id: string; tema?: string; fecha_inicio?: string; }
interface Participant { id: string; correo: string; rol: string; estado_invitacion: string; }

export default function ParticipantsPage() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState("");
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [originalParticipants, setOriginalParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [adding, setAdding] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newParticipant, setNewParticipant] = useState({ correo: "", rol: "participante" });
  const [error, setError] = useState("");

  const fetchParticipants = async (meetingId = selectedMeetingId) => {
    if (!meetingId) { setParticipants([]); setOriginalParticipants([]); return; }
    try {
      const { data } = await api.get<Participant[]>(`/participants/meeting/${meetingId}`);
      setParticipants(data);
      setOriginalParticipants(data);
    } catch {
      setError(t("participants.loadError"));
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get<Meeting[]>("/meetings");
        setMeetings(data);
        setSelectedMeetingId(data[0]?.id || "");
      } catch {
        setError(t("meetings.loadError"));
      } finally {
        setLoading(false);
      }
    })();
  }, [t]);

  useEffect(() => { fetchParticipants(); }, [selectedMeetingId]);

  const updateParticipant = (id: string, changes: Partial<Participant>) => {
    setParticipants((items) => items.map((participant) => participant.id === id ? { ...participant, ...changes } : participant));
  };

  const changes = participants.filter((participant) => {
    const original = originalParticipants.find((item) => item.id === participant.id);
    return original && (original.correo !== participant.correo || original.rol !== participant.rol);
  });

  const saveChanges = async () => {
    setSaving(true);
    try {
      await Promise.all(changes.map(({ id, correo, rol }) => api.patch(`/participants/${id}`, { correo, rol })));
      setOriginalParticipants(participants);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || t("participants.saveError"));
    } finally {
      setSaving(false);
    }
  };

  const addParticipant = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedMeetingId) return;
    setAdding(true);
    try {
      await api.post("/participants", { reunion_id: selectedMeetingId, ...newParticipant });
      setNewParticipant({ correo: "", rol: "participante" });
      setShowAddForm(false);
      await fetchParticipants();
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || t("participants.addError"));
    } finally {
      setAdding(false);
    }
  };

  const invitationColor = (status: string) => status === "aceptado" ? "bg-emerald-100 text-emerald-700" : status === "rechazado" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700";
  const roleLabel = (role: string) => role === "organizador" ? t("common.organizer") : role === "ponente" ? t("common.speaker") : t("common.participant");
  const invitationLabel = (status: string) => status === "aceptado" ? t("common.accepted") : status === "rechazado" ? t("common.rejected") : t("common.pending").toLowerCase();

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold tracking-tight">{t("participants.title")}</h1><p className="text-slate-500">{t("participants.subtitle")}</p></div>
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      <div className="grid lg:grid-cols-[18rem_1fr] gap-6">
        <div className="bg-card border border-border rounded-2xl p-4 h-fit"><h2 className="font-semibold flex gap-2 items-center mb-3"><Search className="w-4 h-4" />{t("participants.meetings")}</h2><div className="space-y-1">{meetings.length === 0 ? <p className="text-sm text-slate-500 p-3">{t("participants.noMeetings")}</p> : meetings.map((meeting) => <button key={meeting.id} onClick={() => { setSelectedMeetingId(meeting.id); setShowAddForm(false); }} className={`w-full text-left rounded-xl p-3 text-sm ${selectedMeetingId === meeting.id ? "bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-400" : "hover:bg-slate-50 dark:hover:bg-slate-800"}`}>{meeting.tema || t("common.noTopic")}</button>)}</div></div>
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-border flex flex-col sm:flex-row gap-3 justify-between sm:items-center"><h2 className="font-semibold flex gap-2 items-center"><Users className="w-5 h-5 text-brand-500" />{t("participants.guests")}</h2>{user?.is_admin && <div className="flex gap-2"><button disabled={!selectedMeetingId} onClick={() => setShowAddForm(true)} className="px-3 py-2 rounded-xl border border-border text-sm font-medium inline-flex gap-2 items-center disabled:opacity-50"><Plus className="w-4 h-4" />{t("participants.add")}</button><button disabled={!changes.length || saving} onClick={saveChanges} className="btn-primary disabled:opacity-50 inline-flex gap-2 items-center"><Save className="w-4 h-4" />{saving ? t("common.saving") : `${t("participants.saveChanges")}${changes.length ? ` (${changes.length})` : ""}`}</button></div>}</div>
          {showAddForm && <form onSubmit={addParticipant} className="p-4 border-b border-border bg-slate-50/50 dark:bg-slate-900/30 flex flex-col sm:flex-row gap-3 sm:items-end"><label className="flex-1 text-sm font-medium">{t("common.emailShort")}<input type="email" required value={newParticipant.correo} onChange={(e) => setNewParticipant({ ...newParticipant, correo: e.target.value })} className="input-field mt-1 w-full" placeholder="persona@empresa.com" /></label><label className="text-sm font-medium">{t("common.role")}<select value={newParticipant.rol} onChange={(e) => setNewParticipant({ ...newParticipant, rol: e.target.value })} className="input-field mt-1 w-full"><option value="participante">{t("common.participant")}</option><option value="organizador">{t("common.organizer")}</option><option value="ponente">{t("common.speaker")}</option></select></label><button disabled={adding} className="btn-primary">{adding ? t("participants.adding") : t("participants.addGuest")}</button><button type="button" onClick={() => setShowAddForm(false)} className="p-2.5 rounded-xl border border-border"><X className="w-4 h-4" /></button></form>}
          {!selectedMeetingId ? <p className="p-8 text-center text-slate-500">{t("participants.selectMeeting")}</p> : <div className="overflow-x-auto"><table className="w-full text-sm"><thead className="text-xs uppercase text-slate-500 border-b border-border"><tr><th className="p-4 text-left">{t("common.emailShort")}</th><th className="p-4 text-left">{t("common.role")}</th><th className="p-4 text-left">{t("common.status")}</th></tr></thead><tbody className="divide-y divide-border">{participants.length === 0 ? <tr><td colSpan={3} className="p-8 text-center text-slate-500">{t("participants.empty")}</td></tr> : participants.map((participant) => <tr key={participant.id}><td className="p-4">{user?.is_admin ? <input type="email" value={participant.correo} onChange={(e) => updateParticipant(participant.id, { correo: e.target.value })} className="input-field py-1.5" /> : participant.correo}</td><td className="p-4">{user?.is_admin ? <select value={participant.rol} onChange={(e) => updateParticipant(participant.id, { rol: e.target.value })} className="input-field py-1.5"><option value="participante">{t("common.participant")}</option><option value="organizador">{t("common.organizer")}</option><option value="ponente">{t("common.speaker")}</option></select> : roleLabel(participant.rol)}</td><td className="p-4"><span className={`px-2.5 py-1 rounded-full text-xs font-medium ${invitationColor(participant.estado_invitacion)}`}>{invitationLabel(participant.estado_invitacion)}</span></td></tr>)}</tbody></table></div>}
        </div>
      </div>
    </div>
  );
}
