"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Loader2, ArrowLeft, FlaskConical, ClipboardList, FileDown, BarChart3 } from "lucide-react";

interface ExperimentSession {
  id: string;
  nombre: string;
  descripcion: string | null;
  estado: string;
  fecha_inicio: string;
  fecha_fin: string | null;
}

export default function ExperimentDetailPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const experimentId = params.id as string;

  const [experiment, setExperiment] = useState<ExperimentSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/experiments/sessions/${experimentId}`);
        setExperiment(response.data);
      } catch (error: any) {
        if (error?.response?.status === 404) router.push("/research/experiments");
      } finally {
        setLoading(false);
      }
    };
    if (experimentId) fetchData();
  }, [experimentId]);

  const estadoStyles: Record<string, string> = {
    PLANIFICADO: "bg-gray-100 text-gray-700",
    EN_CURSO: "bg-blue-100 text-blue-700",
    ACTIVO: "bg-emerald-100 text-emerald-700",
    COMPLETADO: "bg-indigo-100 text-indigo-700",
    CANCELADO: "bg-red-100 text-red-700",
  };

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-indigo-600" /></div>;
  }

  if (!experiment) {
    return <div className="text-center py-12 text-gray-500">Sesión experimental no encontrada</div>;
  }

  return (
    <div className="space-y-6">
      <button onClick={() => router.push("/research/experiments")} className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver a experimentos
      </button>

      <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FlaskConical className="w-8 h-8 text-indigo-600" />
            {experiment.nombre}
          </h1>
          <p className="mt-2 text-gray-600">{experiment.descripcion || "Sin descripción"}</p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información de la Sesión</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <InfoField label="Estado" value={<span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${estadoStyles[experiment.estado] || estadoStyles.PLANIFICADO}`}>{experiment.estado}</span>} />
          <InfoField label="Fecha de Inicio" value={new Date(experiment.fecha_inicio).toLocaleDateString()} />
          <InfoField label="Fecha de Fin" value={experiment.fecha_fin ? new Date(experiment.fecha_fin).toLocaleDateString() : "En curso"} />
          <InfoField label="ID" value={`${experiment.id.slice(0, 8)}...`} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ActionCard
          title="Cuestionario SUS"
          description="Registrar evaluación de usabilidad"
          icon={<ClipboardList className="w-5 h-5" />}
          href={`/research/experiments/${experimentId}/sus`}
          color="indigo"
        />
        <ActionCard
          title="Reporte PDF"
          description="Exportar sesión experimental"
          icon={<FileDown className="w-5 h-5" />}
          href={`/api/backend/reports/research/experiments/${experimentId}/export?format_type=PDF`}
          external
          color="emerald"
        />
      </div>

      <div className={`rounded-2xl p-5 border ${
        experiment.estado === "PLANIFICADO" ? "bg-blue-50 border-blue-100" :
        experiment.estado === "ACTIVO" || experiment.estado === "EN_CURSO" ? "bg-emerald-50 border-emerald-100" :
        experiment.estado === "COMPLETADO" ? "bg-indigo-50 border-indigo-100" :
        "bg-gray-50 border-gray-200"
      }`}>
        <p className={`text-sm ${
          experiment.estado === "PLANIFICADO" ? "text-blue-800" :
          experiment.estado === "ACTIVO" || experiment.estado === "EN_CURSO" ? "text-emerald-800" :
          experiment.estado === "COMPLETADO" ? "text-indigo-800" :
          "text-gray-600"
        }`}>
          {experiment.estado === "PLANIFICADO" && "Sesión planificada. Prepárate para iniciar la recolección de datos."}
          {experiment.estado === "ACTIVO" || experiment.estado === "EN_CURSO" ? "Sesión activa. Puedes registrar respuestas SUS y mediciones." : null}
          {experiment.estado === "COMPLETADO" && "Sesión completada. Revisa el reporte y análisis asociados."}
          {experiment.estado === "CANCELADO" && "Sesión cancelada."}
        </p>
      </div>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs text-gray-400 mb-0.5">{label}</p>
      <div className="font-medium text-gray-900 text-sm">{value}</div>
    </div>
  );
}

function ActionCard({ title, description, icon, href, external, color }: {
  title: string; description: string; icon: React.ReactNode; href: string; external?: boolean; color: string;
}) {
  const colors: Record<string, string> = {
    indigo: "hover:border-indigo-300 hover:bg-indigo-50/50",
    emerald: "hover:border-emerald-300 hover:bg-emerald-50/50",
  };

  return (
    <a href={href} target={external ? "_blank" : undefined} rel={external ? "noopener noreferrer" : undefined}
      className={`flex items-center gap-4 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm transition-all ${colors[color] || ""}`}>
      <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${color === "emerald" ? "bg-emerald-50 text-emerald-600" : "bg-indigo-50 text-indigo-600"}`}>
        {icon}
      </div>
      <div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
    </a>
  );
}
