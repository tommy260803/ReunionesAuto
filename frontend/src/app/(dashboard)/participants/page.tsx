"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2, Plus, Save, Search, Users, X, User, Mail } from "lucide-react";

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

  const invitationColor = (status: string) => {
    if (status === "aceptado") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400";
    if (status === "rechazado") return "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400";
    return "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400";
  };

  const roleColor = (role: string) => {
    if (role === "organizador") return "bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-400";
    if (role === "ponente") return "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400";
    return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400";
  };

  const roleLabel = (role: string) => role === "organizador" ? t("common.organizer") : role === "ponente" ? t("common.speaker") : t("common.participant");
  const invitationLabel = (status: string) => status === "aceptado" ? t("common.accepted") : status === "rechazado" ? t("common.rejected") : t("common.pending").toLowerCase();

  const getInitials = (correo: string) => {
    const name = correo.split("@")[0];
    const parts = name.split(/[._-]/);
    return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
  };

  const acceptedCount = participants.filter((p) => p.estado_invitacion === "aceptado").length;
  const pendingCount = participants.filter((p) => p.estado_invitacion === "pendiente" || p.estado_invitacion === "enviado").length;
  const organizerCount = participants.filter((p) => p.rol === "organizador").length;

  const selectedMeeting = meetings.find((m) => m.id === selectedMeetingId);

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("participants.title")}</h1>
        <p className="text-slate-500">{t("participants.subtitle")}</p>
      </div>

      {error && <div className="p-4 bg-red-50 dark:bg-red-950/30 text-red-600 rounded-xl border border-red-100 dark:border-red-900">{error}</div>}

      <div className="grid lg:grid-cols-[18rem_1fr] gap-6">
        <div className="bg-card border border-border rounded-2xl p-4 h-fit">
          <h2 className="font-semibold flex gap-2 items-center mb-3">
            <Search className="w-4 h-4" />
            {t("participants.meetings")}
          </h2>
          <div className="space-y-1">
            {meetings.length === 0 ? (
              <p className="text-sm app-muted p-3">{t("participants.noMeetings")}</p>
            ) : (
              meetings.map((meeting) => (
                <button
                  key={meeting.id}
                  onClick={() => { setSelectedMeetingId(meeting.id); setShowAddForm(false); }}
                  className={`w-full text-left rounded-xl p-3 text-sm transition-colors ${
                    selectedMeetingId === meeting.id
                      ? "bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-400 font-medium"
                      : "hover:bg-slate-50 dark:hover:bg-slate-800 app-muted"
                  }`}
                >
                  <span className="truncate block">{meeting.tema || t("common.noTopic")}</span>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-border flex flex-col sm:flex-row gap-3 justify-between sm:items-center">
            <div>
              <h2 className="font-semibold flex gap-2 items-center">
                <Users className="w-5 h-5 text-brand-500" />
                {t("participants.guests")}
              </h2>
              {selectedMeeting && (
                <p className="text-sm app-muted mt-1">{selectedMeeting.tema || t("common.noTopic")}</p>
              )}
            </div>
            {user?.is_admin && (
              <div className="flex gap-2">
                <button
                  disabled={!selectedMeetingId}
                  onClick={() => setShowAddForm(true)}
                  className="px-3 py-2 rounded-xl border border-border text-sm font-medium inline-flex gap-2 items-center disabled:opacity-50 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  <Plus className="w-4 h-4" />
                  {t("participants.add")}
                </button>
                <button
                  disabled={!changes.length || saving}
                  onClick={saveChanges}
                  className="btn-primary disabled:opacity-50 inline-flex gap-2 items-center"
                >
                  <Save className="w-4 h-4" />
                  {saving ? t("common.saving") : `${t("participants.saveChanges")}${changes.length ? ` (${changes.length})` : ""}`}
                </button>
              </div>
            )}
          </div>

          {showAddForm && (
            <form onSubmit={addParticipant} className="p-4 border-b border-border bg-slate-50/50 dark:bg-slate-900/30 flex flex-col sm:flex-row gap-3 sm:items-end">
              <label className="flex-1 text-sm font-medium">
                {t("common.emailShort")}
                <input type="email" required value={newParticipant.correo} onChange={(e) => setNewParticipant({ ...newParticipant, correo: e.target.value })} className="input-field mt-1 w-full" placeholder="persona@empresa.com" />
              </label>
              <label className="text-sm font-medium">
                {t("common.role")}
                <select value={newParticipant.rol} onChange={(e) => setNewParticipant({ ...newParticipant, rol: e.target.value })} className="input-field mt-1 w-full">
                  <option value="participante">{t("common.participant")}</option>
                  <option value="organizador">{t("common.organizer")}</option>
                  <option value="ponente">{t("common.speaker")}</option>
                </select>
              </label>
              <button disabled={adding} className="btn-primary">{adding ? t("participants.adding") : t("participants.addGuest")}</button>
              <button type="button" onClick={() => setShowAddForm(false)} className="p-2.5 rounded-xl border border-border"><X className="w-4 h-4" /></button>
            </form>
          )}

          {participants.length > 0 && (
            <div className="p-4 border-b border-border bg-slate-50/30 dark:bg-slate-90/20 flex gap-4 text-xs font-medium">
              <span className="app-muted">{participants.length} {t("common.participants").toLowerCase()}</span>
              <span className="text-emerald-600 dark:text-emerald-400">{acceptedCount} {t("common.accepted")}</span>
              {pendingCount > 0 && <span className="text-amber-600 dark:text-amber-400">{pendingCount} {t("common.pending").toLowerCase()}</span>}
              {organizerCount > 0 && <span className="text-violet-600 dark:text-violet-400">{organizerCount} {t("common.organizer").toLowerCase()}s</span>}
            </div>
          )}

          {!selectedMeetingId ? (
            <p className="p-8 text-center app-muted">{t("participants.selectMeeting")}</p>
          ) : participants.length === 0 ? (
            <div className="p-8 text-center">
              <Users className="w-10 h-10 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
              <p className="app-muted">{t("participants.empty")}</p>
            </div>
          ) : (
            <div className="p-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {participants.map((participant) => (
                <div key={participant.id} className="flex items-center gap-3 p-3 rounded-xl border border-border hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${roleColor(participant.rol)}`}>
                    {getInitials(participant.correo)}
                  </div>
                  <div className="min-w-0 flex-1">
                    {user?.is_admin ? (
                      <input type="email" value={participant.correo} onChange={(e) => updateParticipant(participant.id, { correo: e.target.value })} className="input-field py-1 text-sm w-full" />
                    ) : (
                      <p className="text-sm font-medium truncate">{participant.correo}</p>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      {user?.is_admin ? (
                        <select value={participant.rol} onChange={(e) => updateParticipant(participant.id, { rol: e.target.value })} className="input-field py-0.5 text-xs w-auto">
                          <option value="participante">{t("common.participant")}</option>
                          <option value="organizador">{t("common.organizer")}</option>
                          <option value="ponente">{t("common.speaker")}</option>
                        </select>
                      ) : (
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${roleColor(participant.rol)}`}>{roleLabel(participant.rol)}</span>
                      )}
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${invitationColor(participant.estado_invitacion)}`}>
                        {invitationLabel(participant.estado_invitacion)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
