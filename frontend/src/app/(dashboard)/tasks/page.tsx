"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Calendar, Download, Loader2, Plus, X } from "lucide-react";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";

interface Task { id: string; reunion_id: string; reunion_nombre?: string; descripcion: string; asignado_a_correo?: string; estado: string; fecha_vencimiento?: string; }
interface Meeting { id: string; tema?: string; fecha_inicio?: string; }
type Tab = "kanban" | "grid" | "metrics";

const normalizeStatus = (value: string) => value.replace(" ", "_").toLowerCase();

export default function TasksPage() {
  const { user } = useAuth();
  const { language, t } = useLanguage();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("kanban");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ reunion_id: "", descripcion: "", asignado_a_correo: "", estado: "pendiente", fecha_vencimiento: "" });

  const statusOptions = [{ value: "pendiente", label: t("common.pending") }, { value: "en_progreso", label: t("common.inProgress") }, { value: "completada", label: t("common.completed") }];

  const loadData = async () => {
    try {
      const [taskResponse, meetingResponse] = await Promise.all([api.get<Task[]>("/tasks"), api.get<Meeting[]>("/meetings")]);
      setTasks(taskResponse.data);
      setMeetings(meetingResponse.data);
    } catch {
      setError(t("tasks.loadError"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const updateTask = async (id: string, changes: Partial<Task>) => {
    try {
      await api.patch(`/tasks/${id}`, changes);
      setTasks((items) => items.map((task) => task.id === id ? { ...task, ...changes } : task));
    } catch {
      setError(t("tasks.updateError"));
    }
  };

  const createTask = async (event: React.FormEvent) => {
    event.preventDefault();
    setCreating(true);
    try {
      await api.post("/tasks", { ...form, asignado_a_correo: form.asignado_a_correo || null, fecha_vencimiento: form.fecha_vencimiento ? new Date(form.fecha_vencimiento).toISOString() : null });
      setModalOpen(false);
      setForm({ reunion_id: "", descripcion: "", asignado_a_correo: "", estado: "pendiente", fecha_vencimiento: "" });
      await loadData();
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || t("tasks.createError"));
    } finally {
      setCreating(false);
    }
  };

  const exportPdf = async () => {
    try {
      const response = await api.get("/reports/tasks/pdf", { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "reporte_tareas.pdf";
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setError(t("tasks.reportError"));
    }
  };

  const isOverdue = (task: Task) => Boolean(task.fecha_vencimiento && normalizeStatus(task.estado) !== "completada" && new Date(task.fecha_vencimiento) < new Date(new Date().setHours(0, 0, 0, 0)));
  const dateLabel = (value?: string) => { try { return value ? format(parseISO(value), "dd MMM yyyy", { locale: language === "es" ? es : enUS }) : t("common.noDate"); } catch { return t("common.noDate"); } };
  const statuses = ["pendiente", "en_progreso", "completada"];
  const statusChart = statuses.map((status) => ({ name: statusOptions.find((item) => item.value === status)?.label || status, value: tasks.filter((task) => normalizeStatus(task.estado) === status).length }));
  const workload = Object.entries(tasks.reduce<Record<string, number>>((acc, task) => { const key = task.asignado_a_correo || t("tasks.unassigned"); acc[key] = (acc[key] || 0) + 1; return acc; }, {})).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 8);
  const columns = [{ key: "pendiente", title: t("common.pendingPlural"), color: "text-slate-600" }, { key: "en_progreso", title: t("common.inProgress"), color: "text-brand-600" }, { key: "completada", title: t("common.completedPlural"), color: "text-emerald-600" }];

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4"><div><h1 className="text-3xl font-bold tracking-tight">{t("tasks.title")}</h1><p className="text-slate-500">{t("tasks.subtitle")}</p></div><div className="flex gap-2">{user?.is_admin && <button onClick={exportPdf} className="px-4 py-2.5 rounded-xl border border-border font-medium inline-flex gap-2 items-center"><Download className="w-4 h-4" />{t("common.report")}</button>}<button onClick={() => setModalOpen(true)} className="btn-primary inline-flex gap-2 items-center"><Plus className="w-5 h-5" />{t("tasks.newTask")}</button></div></div>
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      <div className="border-b border-border flex gap-5"><button onClick={() => setActiveTab("kanban")} className={`pb-3 text-sm font-medium ${activeTab === "kanban" ? "border-b-2 border-brand-600 text-brand-600" : "text-slate-500"}`}>{t("tasks.kanban")}</button><button onClick={() => setActiveTab("grid")} className={`pb-3 text-sm font-medium ${activeTab === "grid" ? "border-b-2 border-brand-600 text-brand-600" : "text-slate-500"}`}>{t("tasks.grid")}</button><button onClick={() => setActiveTab("metrics")} className={`pb-3 text-sm font-medium ${activeTab === "metrics" ? "border-b-2 border-brand-600 text-brand-600" : "text-slate-500"}`}>{t("tasks.metrics")}</button></div>

      {activeTab === "kanban" && <div className="flex gap-5 overflow-x-auto pb-4">{columns.map((column) => { const items = tasks.filter((task) => normalizeStatus(task.estado) === column.key); return <section key={column.key} className="min-w-72 flex-1 rounded-2xl border border-border bg-slate-50/50 dark:bg-slate-900/30 p-4"><h2 className={`font-semibold ${column.color} mb-4`}>{column.title} <span className="ml-1 text-xs bg-slate-200 dark:bg-slate-800 px-2 py-1 rounded-full">{items.length}</span></h2><div className="space-y-3">{items.map((task) => <article key={task.id} className="bg-card border border-border rounded-xl p-4 shadow-sm"><select value={normalizeStatus(task.estado)} onChange={(e) => updateTask(task.id, { estado: e.target.value })} className="float-right text-xs input-field py-1">{statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select><p className="font-medium text-sm pr-20">{task.descripcion}</p><p className="text-xs text-brand-600 mt-3 truncate">{task.asignado_a_correo || t("tasks.unassigned")}</p><p className={`text-xs mt-2 flex gap-1 items-center ${isOverdue(task) ? "text-red-600" : "text-slate-500"}`}><Calendar className="w-3 h-3" />{dateLabel(task.fecha_vencimiento)}</p></article>)}{items.length === 0 && <p className="text-sm text-slate-500 text-center py-8">{t("tasks.noTasks")}</p>}</div></section>; })}</div>}
      {activeTab === "grid" && <div className="bg-card border border-border rounded-2xl overflow-x-auto"><table className="w-full text-sm"><thead className="text-xs uppercase text-slate-500 border-b border-border"><tr><th className="p-4 text-left">{t("tasks.task")}</th><th className="p-4 text-left">{t("tasks.meeting")}</th><th className="p-4 text-left">{t("tasks.assignedTo")}</th><th className="p-4 text-left">{t("tasks.dueDate")}</th><th className="p-4 text-left">{t("common.status")}</th></tr></thead><tbody className="divide-y divide-border">{tasks.map((task) => <tr key={task.id}><td className="p-4 font-medium">{task.descripcion}</td><td className="p-4 text-slate-500">{task.reunion_nombre || t("tasks.noMeeting")}</td><td className="p-4"><input type="email" defaultValue={task.asignado_a_correo || ""} onBlur={(e) => e.target.value !== (task.asignado_a_correo || "") && updateTask(task.id, { asignado_a_correo: e.target.value || undefined })} className="input-field py-1.5" placeholder={t("tasks.unassigned")} /></td><td className="p-4"><input type="date" defaultValue={task.fecha_vencimiento?.slice(0, 10) || ""} onBlur={(e) => e.target.value !== (task.fecha_vencimiento?.slice(0, 10) || "") && updateTask(task.id, { fecha_vencimiento: e.target.value ? new Date(e.target.value).toISOString() : undefined })} className="input-field py-1.5" /></td><td className="p-4"><select value={normalizeStatus(task.estado)} onChange={(e) => updateTask(task.id, { estado: e.target.value })} className="input-field py-1.5">{statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></td></tr>)}</tbody></table></div>}
      {activeTab === "metrics" && <div className="grid lg:grid-cols-2 gap-6"><section className="bg-card border border-border rounded-2xl p-5"><h2 className="font-semibold mb-4">{t("tasks.tasksByStatus")}</h2><div className="h-72"><ResponsiveContainer><PieChart><Pie data={statusChart} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95}>{statusChart.map((entry, index) => <Cell key={entry.name} fill={["#64748b", "#4f46e5", "#10b981"][index]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></section><section className="bg-card border border-border rounded-2xl p-5"><h2 className="font-semibold mb-4">{t("tasks.workload")}</h2><div className="h-72"><ResponsiveContainer><BarChart data={workload} layout="vertical" margin={{ left: 80 }}><XAxis type="number" allowDecimals={false} /><YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="value" fill="#4f46e5" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer></div></section></div>}
      {modalOpen && <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm p-4 flex items-center justify-center"><form onSubmit={createTask} className="w-full max-w-md bg-card rounded-2xl border border-border shadow-xl"><div className="p-5 border-b border-border flex justify-between"><h2 className="font-semibold text-lg">{t("tasks.newTask")}</h2><button type="button" onClick={() => setModalOpen(false)}><X className="w-5 h-5" /></button></div><div className="p-5 space-y-4"><label className="block text-sm font-medium">{t("tasks.meeting")}<select required value={form.reunion_id} onChange={(e) => setForm({ ...form, reunion_id: e.target.value })} className="mt-1 w-full input-field"><option value="">{t("tasks.selectMeeting")}</option>{meetings.map((meeting) => <option key={meeting.id} value={meeting.id}>{meeting.tema || t("common.noTopic")}</option>)}</select></label><label className="block text-sm font-medium">{t("common.description")}<textarea required value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} className="mt-1 w-full input-field" rows={3} /></label><label className="block text-sm font-medium">{t("tasks.assignTo")}<input type="email" value={form.asignado_a_correo} onChange={(e) => setForm({ ...form, asignado_a_correo: e.target.value })} className="mt-1 w-full input-field" /></label><div className="grid grid-cols-2 gap-3"><label className="text-sm font-medium">{t("common.status")}<select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })} className="mt-1 w-full input-field">{statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label><label className="text-sm font-medium">{t("tasks.dueDate")}<input type="date" value={form.fecha_vencimiento} onChange={(e) => setForm({ ...form, fecha_vencimiento: e.target.value })} className="mt-1 w-full input-field" /></label></div></div><div className="p-5 pt-0 flex justify-end gap-3"><button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2.5 rounded-xl border border-border">{t("common.cancel")}</button><button disabled={creating} className="btn-primary">{creating ? t("common.saving") : t("tasks.create")}</button></div></form></div>}
    </div>
  );
}
