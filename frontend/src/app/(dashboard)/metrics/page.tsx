"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, Clock3, Loader2, ServerCrash } from "lucide-react";

interface Log { id: string; endpoint: string; tiempo_respuesta: number; estado: string; fecha: string; codigo_estado?: number; detalles?: string; }
interface MetricsStats { total_peticiones: number; exitosas: number; fallidas: number; tasa_exito: number; tiempo_promedio: number; por_dia: { fecha: string; cantidad: number }[]; por_endpoint: { endpoint: string; tiempo_promedio: number; cantidad: number }[]; logs: Log[]; }

export default function MetricsPage() {
  const { user, loading: authLoading } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const [stats, setStats] = useState<MetricsStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user?.is_admin) { router.replace("/dashboard"); return; }
    if (user?.is_admin) {
      api.get<MetricsStats>("/metrics/n8n/stats")
        .then((response) => setStats(response.data))
        .catch(() => setError(t("metrics.loadError")));
    }
  }, [authLoading, router, t, user?.is_admin]);

  if (authLoading || !stats && !error) return <div className="flex h-[calc(100vh-8rem)] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-600" /></div>;
  if (!user?.is_admin) return null;

  const cards = [
    { label: t("metrics.successRate"), value: `${stats?.tasa_exito || 0}%`, icon: CheckCircle2, color: "text-emerald-600" },
    { label: t("metrics.avgTime"), value: `${stats?.tiempo_promedio || 0}s`, icon: Clock3, color: "text-brand-600" },
    { label: t("metrics.requests"), value: stats?.total_peticiones || 0, icon: Activity, color: "text-violet-600" },
    { label: t("metrics.errors"), value: stats?.fallidas || 0, icon: ServerCrash, color: "text-red-600" },
  ];

  return (
    <div className="space-y-7">
      <div>
        <p className="command-eyebrow">{t("metrics.eyebrow")}</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">{t("metrics.title")}</h1>
        <p className="mt-2 text-base app-muted">{t("metrics.subtitle")}</p>
      </div>

      {error ? <div role="alert" className="p-4 rounded-lg bg-red-50 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-900">{error}</div> : <>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {cards.map((card) => <section key={card.label} className="telemetry-card p-5 transition-all duration-200"><card.icon className={`w-5 h-5 ${card.color}`} /><p className="text-3xl font-semibold mt-4">{card.value}</p><p className="text-sm app-muted mt-1">{card.label}</p><div className="metric-line" /></section>)}
        </div>

        <div className="grid xl:grid-cols-2 gap-6">
          <section className="command-panel p-6">
            <h2 className="font-semibold mb-5">{t("metrics.last7Days")}</h2>
            <div className="h-72"><ResponsiveContainer><LineChart data={stats?.por_dia}><CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} /><XAxis dataKey="fecha" tickFormatter={(value) => value.slice(5)} tick={{ fill: "var(--muted)", fontSize: 12 }} /><YAxis allowDecimals={false} tick={{ fill: "var(--muted)", fontSize: 12 }} /><Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }} /><Line type="monotone" dataKey="cantidad" stroke="#6366f1" strokeWidth={3} /></LineChart></ResponsiveContainer></div>
          </section>

          <section className="command-panel p-6">
            <h2 className="font-semibold mb-5">{t("metrics.avgLatencyEndpoint")}</h2>
            <div className="h-72"><ResponsiveContainer><BarChart data={stats?.por_endpoint}><CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} /><XAxis dataKey="endpoint" tick={{ fontSize: 12, fill: "var(--muted)" }} /><YAxis tick={{ fontSize: 12, fill: "var(--muted)" }} /><Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }} /><Bar dataKey="tiempo_promedio" fill="#6366f1" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div>
          </section>
        </div>

        <section className="command-panel overflow-hidden">
          <div className="border-b border-border p-5"><h2 className="font-semibold">{t("metrics.recentLogs")}</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-xs uppercase text-slate-500 border-b border-border"><tr><th className="p-4 text-left">{t("metrics.endpoint")}</th><th className="p-4 text-left">{t("common.status")}</th><th className="p-4 text-left">{t("metrics.code")}</th><th className="p-4 text-left">{t("metrics.avgTime")}</th><th className="p-4 text-left">{t("common.date")}</th><th className="p-4 text-left">{t("metrics.details")}</th></tr></thead>
              <tbody className="divide-y divide-border">
                {stats?.logs.map((log) => <tr key={log.id}><td className="p-4 font-medium">{log.endpoint}</td><td className="p-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${log.estado === "exitoso" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>{log.estado}</span></td><td className="p-4 text-slate-500">{log.codigo_estado || "-"}</td><td className="p-4 text-slate-500">{log.tiempo_respuesta}s</td><td className="p-4 text-slate-500">{new Date(log.fecha).toLocaleString()}</td><td className="p-4 text-slate-500 max-w-xs truncate">{log.detalles || "-"}</td></tr>)}
              </tbody>
            </table>
          </div>
        </section>
      </>}
    </div>
  );
}
