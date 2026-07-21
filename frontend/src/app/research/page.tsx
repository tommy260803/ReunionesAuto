"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Loader2, BarChart3, FlaskConical, MessageSquare, FileText, ArrowRight } from "lucide-react";

interface DashboardStats {
  total_analyses: number;
  completed_analyses: number;
  total_experiments: number;
  active_experiments: number;
  total_evaluations: number;
  pending_evaluations: number;
  total_prompts: number;
  active_prompts: number;
}

export default function ResearchDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const safeGet = async <T,>(url: string): Promise<T[]> => {
      try { const res = await api.get<T[]>(url); return res.data || []; } catch { return []; }
    };

    const fetchStats = async () => {
      try {
        const [analyses, experiments, evaluations, prompts] = await Promise.all([
          safeGet<any>("/api/v1/research/analyses"),
          safeGet<any>("/experiments/sessions"),
          safeGet<any>("/evaluations/summaries"),
          safeGet<any>("/prompts"),
        ]);

        setStats({
          total_analyses: analyses.length,
          completed_analyses: analyses.filter((a: any) => a.estado === "COMPLETADO").length,
          total_experiments: experiments.length,
          active_experiments: experiments.filter((e: any) => e.estado === "ACTIVO" || e.estado === "EN_CURSO").length,
          total_evaluations: evaluations.length,
          pending_evaluations: evaluations.filter((e: any) => e.estado === "PENDIENTE").length,
          total_prompts: prompts.length,
          active_prompts: prompts.filter((p: any) => p.activo).length,
        });
      } catch (error) {
        console.error("Error fetching dashboard stats:", error);
      } finally {
        setLoading(false);
      }
    };

    if (user) fetchStats();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard de Investigación</h1>
        <p className="mt-2 text-gray-600">Bienvenido{user?.nombre ? `, ${user.nombre}` : ""}. Gestiona tus análisis estadísticos y experimentos.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Análisis"
          value={stats?.total_analyses || 0}
          subtitle={`${stats?.completed_analyses || 0} completados`}
          icon={<BarChart3 className="w-5 h-5" />}
          color="indigo"
          href="/research/analyses"
        />
        <StatCard
          title="Experimentos"
          value={stats?.total_experiments || 0}
          subtitle={`${stats?.active_experiments || 0} activos`}
          icon={<FlaskConical className="w-5 h-5" />}
          color="emerald"
          href="/research/experiments"
        />
        <StatCard
          title="Evaluaciones"
          value={stats?.total_evaluations || 0}
          subtitle={`${stats?.pending_evaluations || 0} pendientes`}
          icon={<MessageSquare className="w-5 h-5" />}
          color="amber"
          href="/research/evaluations"
        />
        <StatCard
          title="Prompts"
          value={stats?.total_prompts || 0}
          subtitle={`${stats?.active_prompts || 0} activos`}
          icon={<FileText className="w-5 h-5" />}
          color="purple"
          href="/research/prompts"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <QuickActionCard
          title="Nuevo Análisis"
          description="Crear un análisis estadístico"
          href="/research/analyses/new"
          color="indigo"
        />
        <QuickActionCard
          title="Nueva Sesión Experimental"
          description="Iniciar un experimento"
          href="/research/experiments/new"
          color="emerald"
        />
        <QuickActionCard
          title="Evaluar Resumen"
          description="Evaluación ciega de calidad"
          href="/research/evaluations/blind"
          color="amber"
        />
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon, color, href }: {
  title: string;
  value: number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  href: string;
}) {
  const colors: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    purple: "bg-purple-50 text-purple-600",
  };

  return (
    <a href={href} className="block group">
      <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-gray-300 transition-all">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
            <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
          </div>
          <div className={`h-10 w-10 rounded-xl ${colors[color] || colors.indigo} flex items-center justify-center`}>
            {icon}
          </div>
        </div>
      </div>
    </a>
  );
}

function QuickActionCard({ title, description, href, color }: {
  title: string;
  description: string;
  href: string;
  color: string;
}) {
  const borders: Record<string, string> = {
    indigo: "hover:border-indigo-300 hover:bg-indigo-50/50",
    emerald: "hover:border-emerald-300 hover:bg-emerald-50/50",
    amber: "hover:border-amber-300 hover:bg-amber-50/50",
  };

  return (
    <a href={href} className={`block bg-white border border-gray-200 rounded-2xl p-5 shadow-sm transition-all ${borders[color] || ""}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{description}</p>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-400" />
      </div>
    </a>
  );
}
