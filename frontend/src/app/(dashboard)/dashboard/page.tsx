"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Activity, CheckCircle, Clock, XCircle, Loader2 } from "lucide-react";
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

interface TaskMetrics {
  total: number;
  completadas: number;
  pendientes: number;
  en_progreso: number;
  atrasadas: number;
  porcentaje_avance: number;
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
  const { t } = useLanguage();
  const [metrics, setMetrics] = useState<TaskMetrics | null>(null);
  const [n8nData, setN8nData] = useState<N8nMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [taskRes, n8nRes] = await Promise.all([
          api.get("/tasks/metrics"),
          user?.is_admin ? api.get("/metrics/n8n") : Promise.resolve({ data: [] })
        ]);
        setMetrics(taskRes.data);
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

  const taskChartData = metrics ? [
    { name: t("common.completedPlural"), value: metrics.completadas },
    { name: t("common.pendingPlural"), value: metrics.pendientes },
    { name: t("common.inProgress"), value: metrics.en_progreso },
    { name: t("common.overdue"), value: metrics.atrasadas },
  ] : [];

  // Group n8n metrics by endpoint for the average response-time chart.
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <p className="command-eyebrow">{t("dashboard.eyebrow")}</p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">{t("shell.dashboard")}</h1>
        <p className="text-base app-muted">{t("dashboard.welcome")}, {user?.nombre}. {t("dashboard.summary")}</p>
      </div>

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="telemetry-card p-5 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-500">{t("dashboard.totalTasks")}</h3>
              <Activity className="w-5 h-5 text-brand-500" />
            </div>
            <div className="text-3xl font-semibold mt-3">{metrics.total}</div>
            <div className="mt-1 text-sm app-muted">{t("dashboard.progress")}: {metrics.porcentaje_avance}%</div>
            <div className="metric-line" />
          </div>
          
          <div className="telemetry-card p-5 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-500">{t("common.completedPlural")}</h3>
              <CheckCircle className="w-5 h-5 text-emerald-500" />
            </div>
            <div className="text-3xl font-bold mt-2 text-emerald-600 dark:text-emerald-400">{metrics.completadas}</div>
            <div className="metric-line bg-emerald-500" />
          </div>

          <div className="telemetry-card p-5 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-500">{t("common.pendingPlural")}</h3>
              <Clock className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-3xl font-bold mt-2 text-amber-600 dark:text-amber-400">{metrics.pendientes}</div>
            <div className="metric-line bg-amber-500" />
          </div>

          <div className="telemetry-card p-5 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-500">{t("common.inProgress")}</h3>
              <Activity className="w-5 h-5 text-brand-500" />
            </div>
            <div className="text-3xl font-bold mt-2 text-brand-600 dark:text-brand-400">{metrics.en_progreso}</div>
            <div className="metric-line" />
          </div>

          <div className="telemetry-card p-5 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-500">{t("common.overdue")}</h3>
              <XCircle className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-3xl font-bold mt-2 text-amber-600 dark:text-amber-400">{metrics.atrasadas}</div>
            <div className="metric-line bg-amber-500" />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {/* Task chart */}
        <div className="command-panel p-6">
          <h3 className="font-semibold text-lg mb-4">{t("dashboard.taskStatus")}</h3>
          {metrics && metrics.total > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={taskChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
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
              <div className="flex justify-center gap-4 text-xs font-medium text-slate-500 mt-2">
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-emerald-500"/> {t("common.completedPlural")}</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-amber-500"/> {t("common.pendingPlural")}</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-brand-500"/> {t("dashboard.progressShort")}</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-amber-500"/> {t("common.overdue")}</span>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">{t("common.noData")}</div>
          )}
        </div>

        {/* n8n chart */}
        {user?.is_admin && (
          <div className="command-panel p-6">
            <h3 className="font-semibold text-lg mb-4">{t("dashboard.n8nResponseTimes")}</h3>
            {n8nChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={n8nChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--muted)' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--muted)' }} />
                    <RechartsTooltip 
                      cursor={{ fill: 'transparent' }}
                      contentStyle={{ borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-raised)', color: 'var(--foreground)', boxShadow: 'var(--shadow-card)' }}
                    />
                    <Bar dataKey="tiempoPromedio" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-400 text-sm">{t("dashboard.noExecutions")}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
