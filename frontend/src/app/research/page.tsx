"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

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
    const fetchStats = async () => {
      try {
        // Fetch statistics from API
        const [analysesRes, experimentsRes, evaluationsRes, promptsRes] = await Promise.all([
          api.get("/research/analyses"),
          api.get("/experiments"),
          api.get("/evaluations"),
          api.get("/prompts"),
        ]);

        const analyses = analysesRes.data || [];
        const experiments = experimentsRes.data || [];
        const evaluations = evaluationsRes.data || [];
        const prompts = promptsRes.data || [];

        setStats({
          total_analyses: analyses.length,
          completed_analyses: analyses.filter((a: any) => a.estado === "COMPLETADO").length,
          total_experiments: experiments.length,
          active_experiments: experiments.filter((e: any) => e.estado === "ACTIVO").length,
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

    if (user) {
      fetchStats();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard de Investigación</h1>
        <p className="mt-2 text-gray-600">
          Bienvenido, {user?.nombre}. Gestiona tus análisis estadísticos y experimentos.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Análisis Totales"
          value={stats?.total_analyses || 0}
          subtitle={`${stats?.completed_analyses || 0} completados`}
          color="indigo"
          link="/research/analyses"
        />
        <StatCard
          title="Experimentos"
          value={stats?.total_experiments || 0}
          subtitle={`${stats?.active_experiments || 0} activos`}
          color="green"
          link="/research/experiments"
        />
        <StatCard
          title="Evaluaciones"
          value={stats?.total_evaluations || 0}
          subtitle={`${stats?.pending_evaluations || 0} pendientes`}
          color="yellow"
          link="/research/evaluations"
        />
        <StatCard
          title="Prompts"
          value={stats?.total_prompts || 0}
          subtitle={`${stats?.active_prompts || 0} activos`}
          color="purple"
          link="/research/prompts"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickActionButton
            title="Nuevo Análisis"
            description="Crear un análisis estadístico"
            link="/research/analyses/new"
            icon="📊"
          />
          <QuickActionButton
            title="Nueva Sesión Experimental"
            description="Iniciar un experimento"
            link="/research/experiments/new"
            icon="🧪"
          />
          <QuickActionButton
            title="Evaluar Resumen"
            description="Evaluar calidad de resumen"
            link="/research/evaluations/new"
            icon="✓"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h2>
        <div className="space-y-4">
          <ActivityItem
            title="Análisis completado"
            description="Comparación de prompts v1.0 vs v1.1"
            time="Hace 2 horas"
            type="success"
          />
          <ActivityItem
            title="Evaluación pendiente"
            description="Resumen de reunión #12345"
            time="Hace 5 horas"
            type="warning"
          />
          <ActivityItem
            title="Experimento iniciado"
            description="Sesión experimental #456"
            time="Ayer"
            type="info"
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  color,
  link,
}: {
  title: string;
  value: number;
  subtitle: string;
  color: string;
  link: string;
}) {
  const colorClasses = {
    indigo: "bg-indigo-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    purple: "bg-purple-500",
  };

  return (
    <a href={link} className="block">
      <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          </div>
          <div className={`h-12 w-12 ${colorClasses[color as keyof typeof colorClasses]} rounded-lg flex items-center justify-center text-white text-xl`}>
            📈
          </div>
        </div>
      </div>
    </a>
  );
}

function QuickActionButton({
  title,
  description,
  link,
  icon,
}: {
  title: string;
  description: string;
  link: string;
  icon: string;
}) {
  return (
    <a href={link} className="block">
      <div className="border border-gray-200 rounded-lg p-4 hover:border-indigo-500 hover:bg-indigo-50 transition-colors">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{icon}</div>
          <div>
            <h3 className="font-medium text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">{description}</p>
          </div>
        </div>
      </div>
    </a>
  );
}

function ActivityItem({
  title,
  description,
  time,
  type,
}: {
  title: string;
  description: string;
  time: string;
  type: "success" | "warning" | "info";
}) {
  const typeClasses = {
    success: "bg-green-100 text-green-800",
    warning: "bg-yellow-100 text-yellow-800",
    info: "bg-blue-100 text-blue-800",
  };

  return (
    <div className="flex items-start space-x-3">
      <div className={`h-8 w-8 rounded-full ${typeClasses[type]} flex items-center justify-center flex-shrink-0`}>
        {type === "success" && "✓"}
        {type === "warning" && "!"}
        {type === "info" && "i"}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      <div className="text-sm text-gray-400">{time}</div>
    </div>
  );
}
