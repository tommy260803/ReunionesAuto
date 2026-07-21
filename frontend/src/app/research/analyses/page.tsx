"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Loader2, BarChart3, Plus, RotateCw, Eye, FileText } from "lucide-react";

interface StatisticalAnalysis {
  id: string;
  nombre: string;
  objetivo: string | null;
  variable_resultado: string;
  diseno: string;
  prueba_ejecutada: string | null;
  estado: string;
  fecha_creacion: string;
  fecha_ejecucion: string | null;
}

export default function AnalysesPage() {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<StatisticalAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<string>("all");

  const fetchAnalyses = async () => {
    try {
      const response = await api.get("/api/v1/research/analyses");
      setAnalyses(response.data || []);
      setError("");
    } catch (err) {
      setError("Error al cargar análisis");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) fetchAnalyses();
  }, [user]);

  const handleRerun = async (analysisId: string) => {
    try {
      await api.post(`/api/v1/research/analyses/${analysisId}/rerun`, { force: false });
      fetchAnalyses();
    } catch (err) {
      alert("Error al reejecutar el análisis");
    }
  };

  const filteredAnalyses = filter === "all"
    ? analyses
    : analyses.filter(a => a.estado === filter);

  const estadoStyles: Record<string, string> = {
    PLANIFICADO: "bg-gray-100 text-gray-700",
    VALIDADO: "bg-blue-100 text-blue-700",
    EJECUTANDO: "bg-yellow-100 text-yellow-700",
    COMPLETADO: "bg-emerald-100 text-emerald-700",
    ERROR: "bg-red-100 text-red-700",
    CANCELADO: "bg-gray-100 text-gray-700",
  };

  const filters = [
    { key: "all", label: "Todos" },
    { key: "PLANIFICADO", label: "Planificados" },
    { key: "EJECUTANDO", label: "Ejecutando" },
    { key: "COMPLETADO", label: "Completados" },
  ];

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-indigo-600" />
            Análisis Estadísticos
          </h1>
          <p className="text-gray-600">Gestiona tus análisis estadísticos de investigación</p>
        </div>
        <a
          href="/research/analyses/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors inline-flex items-center gap-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          Nuevo Análisis
        </a>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">{error}</div>
      )}

      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === f.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 font-medium">Nombre</th>
                <th className="px-6 py-4 font-medium">Variable</th>
                <th className="px-6 py-4 font-medium">Diseño</th>
                <th className="px-6 py-4 font-medium">Prueba</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Fecha</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredAnalyses.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{a.nombre}</div>
                    {a.objetivo && (
                      <div className="text-xs text-gray-400 truncate max-w-[200px]">{a.objetivo}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{a.variable_resultado}</td>
                  <td className="px-6 py-4 text-gray-500">{a.diseno}</td>
                  <td className="px-6 py-4 text-gray-500">{a.prueba_ejecutada || "—"}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${estadoStyles[a.estado] || estadoStyles.PLANIFICADO}`}>
                      {a.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-xs">
                    {a.fecha_ejecucion
                      ? new Date(a.fecha_ejecucion).toLocaleDateString()
                      : new Date(a.fecha_creacion).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <a
                        href={`/research/analyses/${a.id}`}
                        className="p-2 rounded-lg text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                        title="Ver detalles"
                      >
                        <Eye className="w-4 h-4" />
                      </a>
                      {a.estado !== "EJECUTANDO" && (
                        <button
                          onClick={() => handleRerun(a.id)}
                          className="p-2 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                          title="Reejecutar"
                        >
                          <RotateCw className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {filteredAnalyses.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center">
                    <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500 font-medium">No hay análisis estadísticos</p>
                    <p className="text-gray-400 text-sm mt-1">Crea tu primer análisis para comenzar</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
