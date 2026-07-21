"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

interface StatisticalAnalysis {
  id: string;
  nombre: string;
  objetivo: string | null;
  variable_resultado: string;
  diseno: string;
  prueba_ejecutada: string;
  estado: string;
  fecha_creacion: string;
  fecha_ejecucion: string | null;
}

export default function AnalysesPage() {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<StatisticalAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        const response = await api.get("/research/analyses");
        setAnalyses(response.data || []);
      } catch (error) {
        console.error("Error fetching analyses:", error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchAnalyses();
    }
  }, [user]);

  const filteredAnalyses = filter === "all" 
    ? analyses 
    : analyses.filter(a => a.estado === filter);

  const estadoColors = {
    PLANIFICADO: "bg-gray-100 text-gray-800",
    VALIDADO: "bg-blue-100 text-blue-800",
    EJECUTANDO: "bg-yellow-100 text-yellow-800",
    COMPLETADO: "bg-green-100 text-green-800",
    ERROR: "bg-red-100 text-red-800",
    CANCELADO: "bg-gray-100 text-gray-800",
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Análisis Estadísticos</h1>
          <p className="mt-2 text-gray-600">Gestiona tus análisis estadísticos de investigación.</p>
        </div>
        <a
          href="/research/analyses/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          Nuevo Análisis
        </a>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        <FilterButton active={filter === "all"} onClick={() => setFilter("all")}>
          Todos
        </FilterButton>
        <FilterButton active={filter === "PLANIFICADO"} onClick={() => setFilter("PLANIFICADO")}>
          Planificados
        </FilterButton>
        <FilterButton active={filter === "EJECUTANDO"} onClick={() => setFilter("EJECUTANDO")}>
          Ejecutando
        </FilterButton>
        <FilterButton active={filter === "COMPLETADO"} onClick={() => setFilter("COMPLETADO")}>
          Completados
        </FilterButton>
      </div>

      {/* Analyses List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {filteredAnalyses.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <p className="text-lg">No hay análisis estadísticos</p>
            <p className="mt-2">Crea tu primer análisis para comenzar.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Variable
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Diseño
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Prueba
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAnalyses.map((analysis) => (
                <tr key={analysis.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{analysis.nombre}</div>
                    {analysis.objetivo && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">{analysis.objetivo}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {analysis.variable_resultado}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {analysis.diseno}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {analysis.prueba_ejecutada}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColors[analysis.estado as keyof typeof estadoColors]}`}>
                      {analysis.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(analysis.fecha_creacion).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <a
                      href={`/research/analyses/${analysis.id}`}
                      className="text-indigo-600 hover:text-indigo-900 mr-3"
                    >
                      Ver
                    </a>
                    {analysis.estado === "COMPLETADO" && (
                      <a
                        href={`/research/analyses/${analysis.id}/results`}
                        className="text-green-600 hover:text-green-900"
                      >
                        Resultados
                      </a>
                    )}
                    {analysis.estado !== "EJECUTANDO" && (
                      <button
                        onClick={() => handleRerun(analysis.id)}
                        className="text-blue-600 hover:text-blue-900 ml-3"
                      >
                        Reejecutar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );

  async function handleRerun(analysisId: string) {
    try {
      await api.post(`/research/analyses/${analysisId}/rerun`, { force: false });
      // Refresh the list
      const response = await api.get("/research/analyses");
      setAnalyses(response.data || []);
    } catch (error) {
      console.error("Error rerunning analysis:", error);
      alert("Error al reejecutar el análisis");
    }
  }
}

function FilterButton({ 
  active, 
  onClick, 
  children 
}: { 
  active: boolean; 
  onClick: () => void; 
  children: React.ReactNode 
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        active
          ? "bg-indigo-600 text-white"
          : "bg-white text-gray-700 hover:bg-gray-100"
      }`}
    >
      {children}
    </button>
  );
}
