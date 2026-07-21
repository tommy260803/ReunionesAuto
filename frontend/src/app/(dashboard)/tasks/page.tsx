"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Calendar, Download, Loader2, Plus, X, Clock, CheckCircle, AlertTriangle } from "lucide-react";
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
  const columns = [
    { key: "pendiente", title: t("common.pendingPlural"), color: "text-slate-600", icon: Clock, dotColor: "bg-slate-400" },
    { key: "en_progreso", title: t("common.inProgress"), color: "text-brand-600", icon: AlertTriangle, dotColor: "bg-brand-500" },
    { key: "completada", title: t("common.completedPlural"), color: "text-emerald-600", icon: CheckCircle, dotColor: "bg-emerald-500" }
  ];

  const completedCount = tasks.filter((t) => normalizeStatus(t.estado) === "completada").length;
  const overdueCount = tasks.filter((t) => isOverdue(t)).length;

  if (loading) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t("tasks.title")}</h1>
          <p className="text-slate-500">{t("tasks.subtitle")}</p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="flex gap-2 text-xs font-medium mr-2">
            <span className="telemetry-card px-2.5 py-1.5 inline-flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              {completedCount}/{tasks.length}
            </span>
            {overdueCount > 0 && (
              <span className="telemetry-card px-2.5 py-1.5 inline-flex items-center gap-1 text-red-600 dark:text-red-400">
                <AlertTriangle className="w-3.5 h-3.5" />
                {overdueCount} {t("common.overdue").toLowerCase()}
              </span>
            )}
          </div>
          {user?.is_admin && (
            <button onClick={exportPdf} className="px-4 py-2.5 rounded-xl border border-border font-medium inline-flex gap-2 items-center text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <Download className="w-4 h-4" />
              {t("common.report")}
            </button>
          )}
          <button onClick={() => setModalOpen(true)} className="btn-primary inline-flex gap-2 items-center text-sm">
            <Plus className="w-5 h-5" />
            {t("tasks.newTask")}
          </button>
        </div>
      </div>

      {error && <div className="p-4 bg-red-50 dark:bg-red-950/30 text-red-600 rounded-xl border border-red-100 dark:border-red-900">{error}</div>}

      <div className="border-b border-border flex gap-5">
        {(["kanban", "grid", "metrics"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 text-sm font-medium transition-colors ${
              activeTab === tab ? "border-b-2 border-brand-600 text-brand-600" : "text-slate-500 hover:text-foreground"
            }`}
          >
            {tab === "kanban" ? t("tasks.kanban") : tab === "grid" ? t("tasks.grid") : t("tasks.metrics")}
          </button>
        ))}
      </div>

      {activeTab === "kanban" && (
        <div className="flex gap-5 overflow-x-auto pb-4">
          {columns.map((column) => {
            const items = tasks.filter((task) => normalizeStatus(task.estado) === column.key);
            const ColIcon = column.icon;
            return (
              <section key={column.key} className="min-w-80 flex-1 rounded-2xl border border-border bg-slate-50/50 dark:bg-slate-900/30 p-4">
                <h2 className={`font-semibold ${column.color} mb-4 flex items-center gap-2`}>
                  <div className={`w-2 h-2 rounded-full ${column.dotColor}`} />
                  {column.title}
                  <span className="ml-auto text-xs bg-slate-200 dark:bg-slate-800 px-2 py-1 rounded-full font-medium">{items.length}</span>
                </h2>
                <div className="space-y-3">
                  {items.map((task) => (
                    <article key={task.id} className={`bg-card border rounded-xl p-4 shadow-sm transition-all hover:shadow-md ${isOverdue(task) ? "border-red-200 dark:border-red-900" : "border-border"}`}>
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="font-medium text-sm text-foreground leading-snug">{task.descripcion}</p>
                        <select
                          value={normalizeStatus(task.estado)}
                          onChange={(e) => updateTask(task.id, { estado: e.target.value })}
                          className="text-xs input-field py-1 px-1.5 min-w-[6rem]"
                        >
                          {statusOptions.map((option) => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                          ))}
                        </select>
                      </div>
                      <p className="text-xs text-brand-600 dark:text-brand-400 truncate">{task.asignado_a_correo || t("tasks.unassigned")}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <p className={`text-xs flex gap-1 items-center ${isOverdue(task) ? "text-red-600 dark:text-red-400" : "app-muted"}`}>
                          <Calendar className="w-3 h-3" />
                          {dateLabel(task.fecha_vencimiento)}
                        </p>
                        {task.reunion_nombre && (
                          <p className="text-xs app-muted truncate flex-1">{task.reunion_nombre}</p>
                        )}
                      </div>
                    </article>
                  ))}
                  {items.length === 0 && (
                    <p className="text-sm app-muted text-center py-8">{t("tasks.noTasks")}</p>
                  )}
                </div>
              </section>
            );
          })}
        </div>
      )}

      {activeTab === "grid" && (
        <div className="bg-card border border-border rounded-2xl overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase app-muted border-b border-border">
              <tr>
                <th className="p-4 text-left">{t("tasks.task")}</th>
                <th className="p-4 text-left">{t("tasks.meeting")}</th>
                <th className="p-4 text-left">{t("tasks.assignedTo")}</th>
                <th className="p-4 text-left">{t("tasks.dueDate")}</th>
                <th className="p-4 text-left">{t("common.status")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {tasks.map((task) => (
                <tr key={task.id} className={`hover:bg-slate-50/50 dark:hover:bg-slate-800/30 ${isOverdue(task) ? "bg-red-50/30 dark:bg-red-950/10" : ""}`}>
                  <td className="p-4 font-medium">{task.descripcion}</td>
                  <td className="p-4 app-muted">{task.reunion_nombre || t("tasks.noMeeting")}</td>
                  <td className="p-4">
                    <input type="email" defaultValue={task.asignado_a_correo || ""} onBlur={(e) => e.target.value !== (task.asignado_a_correo || "") && updateTask(task.id, { asignado_a_correo: e.target.value || undefined })} className="input-field py-1.5" placeholder={t("tasks.unassigned")} />
                  </td>
                  <td className="p-4">
                    <span className={`text-sm ${isOverdue(task) ? "text-red-600 font-medium" : ""}`}>
                      {dateLabel(task.fecha_vencimiento)}
                    </span>
                  </td>
                  <td className="p-4">
                    <select value={normalizeStatus(task.estado)} onChange={(e) => updateTask(task.id, { estado: e.target.value })} className="input-field py-1.5">
                      {statusOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "metrics" && (
        <div className="grid lg:grid-cols-2 gap-6">
          <section className="command-panel p-6">
            <h2 className="font-semibold mb-4">{t("tasks.tasksByStatus")}</h2>
            <div className="h-72">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={statusChart} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3}>
                    {statusChart.map((entry, index) => (
                      <Cell key={entry.name} fill={["#64748b", "#4f46e5", "#10b981"][index]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-raised)', color: 'var(--foreground)', boxShadow: 'var(--shadow-card)' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 text-xs font-medium app-muted mt-2">
              <span className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-slate-500"/> {t("common.pendingPlural")}</span>
              <span className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-brand-500"/> {t("common.inProgress")}</span>
              <span className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-emerald-500"/> {t("common.completedPlural")}</span>
            </div>
          </section>
          <section className="command-panel p-6">
            <h2 className="font-semibold mb-4">{t("tasks.workload")}</h2>
            <div className="h-72">
              <ResponsiveContainer>
                <BarChart data={workload} layout="vertical" margin={{ left: 80 }}>
                  <XAxis type="number" allowDecimals={false} axisLine={false} tickLine={false} />
                  <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-raised)', color: 'var(--foreground)', boxShadow: 'var(--shadow-card)' }} />
                  <Bar dataKey="value" fill="#4f46e5" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm p-4 flex items-center justify-center">
          <form onSubmit={createTask} className="w-full max-w-md bg-card rounded-2xl border border-border shadow-xl">
            <div className="p-5 border-b border-border flex justify-between">
              <h2 className="font-semibold text-lg">{t("tasks.newTask")}</h2>
              <button type="button" onClick={() => setModalOpen(false)}><X className="w-5 h-5" /></button>
            </div>
            <div className="p-5 space-y-4">
              <label className="block text-sm font-medium">
                {t("tasks.meeting")}
                <select required value={form.reunion_id} onChange={(e) => setForm({ ...form, reunion_id: e.target.value })} className="mt-1 w-full input-field">
                  <option value="">{t("tasks.selectMeeting")}</option>
                  {meetings.map((meeting) => (
                    <option key={meeting.id} value={meeting.id}>{meeting.tema || t("common.noTopic")}</option>
                  ))}
                </select>
              </label>
              <label className="block text-sm font-medium">
                {t("common.description")}
                <textarea required value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} className="mt-1 w-full input-field" rows={3} />
              </label>
              <label className="block text-sm font-medium">
                {t("tasks.assignTo")}
                <input type="email" value={form.asignado_a_correo} onChange={(e) => setForm({ ...form, asignado_a_correo: e.target.value })} className="mt-1 w-full input-field" />
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="text-sm font-medium">
                  {t("common.status")}
                  <select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })} className="mt-1 w-full input-field">
                    {statusOptions.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </label>
                <label className="text-sm font-medium">
                  {t("tasks.dueDate")}
                  <input type="date" value={form.fecha_vencimiento} onChange={(e) => setForm({ ...form, fecha_vencimiento: e.target.value })} className="mt-1 w-full input-field" />
                </label>
              </div>
            </div>
            <div className="p-5 pt-0 flex justify-end gap-3">
              <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2.5 rounded-xl border border-border text-sm font-medium">{t("common.cancel")}</button>
              <button disabled={creating} className="btn-primary">{creating ? t("common.saving") : t("tasks.create")}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
