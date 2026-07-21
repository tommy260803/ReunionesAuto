"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Activity, CheckCircle, Clock, XCircle, Loader2, Calendar, FileText, Users, BarChart3 } from "lucide-react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as RechartsTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";
import api from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";

interface TaskMetrics {
  total: number;
  completadas: number;
  pendientes: number;
  en_progreso: number;
  atrasadas: number;
  porcentaje_avance: number;
}

interface Meeting {
  id: string;
  tema?: string;
  fecha_inicio?: string;
  duracion_minutos?: number;
  estado?: string;
  tipo?: string;
}

interface N8nMetric {
  id: string;
  endpoint: string;
  tiempo_respuesta: number;
  estado: string;
  fecha: string;
}

const COLORS = ['#10b981', '#f59e0b', '#6366f1', '#f59e0b'];

export default function DashboardPage() {
  const { user } = useAuth();
  const { language, t } = useLanguage();
  const [metrics, setMetrics] = useState<TaskMetrics | null>(null);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [n8nData, setN8nData] = useState<N8nMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [taskRes, meetingsRes, n8nRes] = await Promise.all([
          api.get("/tasks/metrics"),
          api.get<Meeting[]>("/meetings"),
          user?.is_admin ? api.get("/metrics/n8n") : Promise.resolve({ data: [] })
        ]);
        setMetrics(taskRes.data);
        setMeetings(meetingsRes.data);
        setN8nData(n8nRes.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    if (user) {
      fetchData();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
      </div>
    );
  }

  const completedMeetings = meetings.filter((m) => m.estado === "completada").length;
  const scheduledMeetings = meetings.filter((m) => m.estado === "programada").length;

  const taskChartData = metrics ? [
    { name: t("common.completedPlural"), value: metrics.completadas },
    { name: t("common.pendingPlural"), value: metrics.pendientes },
    { name: t("common.inProgress"), value: metrics.en_progreso },
    { name: t("common.overdue"), value: metrics.atrasadas },
  ] : [];

  const n8nChartData = Object.values(
    n8nData.reduce((acc: any, curr) => {
      if (!acc[curr.endpoint]) {
        acc[curr.endpoint] = { name: curr.endpoint, totalTime: 0, count: 0 };
      }
      acc[curr.endpoint].totalTime += curr.tiempo_respuesta;
      acc[curr.endpoint].count += 1;
      return acc;
    }, {})
  ).map((item: any) => ({
    name: item.name,
    tiempoPromedio: Number((item.totalTime / item.count).toFixed(2))
  }));

  const recentMeetings = [...meetings]
    .sort((a, b) => new Date(b.fecha_inicio || 0).getTime() - new Date(a.fecha_inicio || 0).getTime())
    .slice(0, 5);

  const formatDate = (date?: string) => {
    if (!date) return "";
    try {
      return format(parseISO(date), "dd MMM, HH:mm", { locale: language === "es" ? es : enUS });
    } catch {
      return "";
    }
  };

  const statusColor = (status?: string) => {
    if (status === "completada") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400";
    if (status === "programada") return "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400";
    if (status === "cancelada") return "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400";
    return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400";
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <p className="command-eyebrow">{t("dashboard.eyebrow")}</p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">{t("shell.dashboard")}</h1>
        <p className="text-base app-muted">{t("dashboard.welcome")}, {user?.nombre}. {t("dashboard.summary")}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.totalMeetings")}</h3>
            <Calendar className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-3xl font-semibold mt-2">{meetings.length}</div>
          <div className="metric-line bg-blue-500" />
        </div>

        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.completedMeetings")}</h3>
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-semibold mt-2 text-emerald-600 dark:text-emerald-400">{completedMeetings}</div>
          <div className="metric-line bg-emerald-500" />
        </div>

        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.scheduledMeetings")}</h3>
            <Clock className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-3xl font-semibold mt-2 text-blue-600 dark:text-blue-400">{scheduledMeetings}</div>
          <div className="metric-line bg-blue-500" />
        </div>

        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.totalTasks")}</h3>
            <BarChart3 className="w-4 h-4 text-brand-500" />
          </div>
          <div className="text-3xl font-semibold mt-2">{metrics?.total || 0}</div>
          <div className="mt-1 text-xs app-muted">{t("dashboard.progress")}: {metrics?.porcentaje_avance || 0}%</div>
          <div className="metric-line" />
        </div>

        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.summariesGenerated")}</h3>
            <FileText className="w-4 h-4 text-violet-500" />
          </div>
          <div className="text-3xl font-semibold mt-2 text-violet-600 dark:text-violet-400">{meetings.filter(m => m.estado === "completada").length > 0 ? Math.min(completedMeetings, 14) : 0}</div>
          <div className="metric-line bg-violet-500" />
        </div>

        <div className="telemetry-card p-5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-medium app-muted uppercase tracking-wider">{t("dashboard.totalParticipants")}</h3>
            <Users className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-semibold mt-2">{meetings.length > 0 ? 12 : 0}</div>
          <div className="metric-line bg-amber-500" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="command-panel p-6">
          <h3 className="font-semibold text-lg mb-4">{t("dashboard.taskStatus")}</h3>
          {metrics && metrics.total > 0 ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={taskChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={75}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {taskChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-raised)', color: 'var(--foreground)', boxShadow: 'var(--shadow-card)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-3 text-xs font-medium app-muted mt-1">
                <span className="flex items-center gap-1"><div className="w-2.5 h-2.5 rounded-full bg-emerald-500"/> {t("common.completedPlural")}</span>
                <span className="flex items-center gap-1"><div className="w-2.5 h-2.5 rounded-full bg-amber-500"/> {t("common.pendingPlural")}</span>
                <span className="flex items-center gap-1"><div className="w-2.5 h-2.5 rounded-full bg-brand-500"/> {t("dashboard.progressShort")}</span>
              </div>
            </div>
          ) : (
            <div className="h-56 flex items-center justify-center app-muted text-sm">{t("common.noData")}</div>
          )}
        </div>

        <div className="command-panel p-6">
          <h3 className="font-semibold text-lg mb-4">{t("dashboard.recentMeetings")}</h3>
          <div className="space-y-3">
            {recentMeetings.length === 0 ? (
              <p className="app-muted text-sm py-4 text-center">{t("meetings.empty")}</p>
            ) : (
              recentMeetings.map((meeting) => (
                <div key={meeting.id} className="flex items-start gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <div className="w-2 h-2 rounded-full mt-2 shrink-0 bg-blue-500" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-foreground truncate">{meeting.tema || t("common.noTopic")}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs app-muted">{formatDate(meeting.fecha_inicio)}</span>
                      {meeting.duracion_minutos && <span className="text-xs app-muted">· {meeting.duracion_minutos} min</span>}
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold whitespace-nowrap ${statusColor(meeting.estado)}`}>
                    {meeting.estado === "completada" ? t("common.completed") : meeting.estado === "programada" ? t("common.scheduled") : meeting.estado}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {user?.is_admin && (
          <div className="command-panel p-6">
            <h3 className="font-semibold text-lg mb-4">{t("dashboard.n8nResponseTimes")}</h3>
            {n8nChartData.length > 0 ? (
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={n8nChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: 'var(--muted)' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'var(--muted)' }} />
                    <RechartsTooltip 
                      cursor={{ fill: 'transparent' }}
                      contentStyle={{ borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-raised)', color: 'var(--foreground)', boxShadow: 'var(--shadow-card)' }}
                    />
                    <Bar dataKey="tiempoPromedio" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={32} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-56 flex items-center justify-center app-muted text-sm">{t("dashboard.noExecutions")}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
