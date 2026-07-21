"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import BoxPlot from "@/components/charts/BoxPlot";
import ConfusionMatrix from "@/components/charts/ConfusionMatrix";

interface StatisticalAnalysis {
  id: string;
  nombre: string;
  objetivo: string | null;
  variable_resultado: string;
  variable_grupo: string | null;
  diseno: string;
  prueba_solicitada: string | null;
  prueba_ejecutada: string | null;
  alpha: number;
  correccion_multiple: string;
  estado: string;
  fecha_creacion: string;
  fecha_ejecucion: string | null;
}

interface AnalysisResult {
  id: string;
  analysis_id: string;
  resultado: any;
  descriptivos: any;
  supuestos: any;
  efecto: any;
  intervalos: any;
  advertencias: string[];
  interpretacion: string | null;
}

export default function AnalysisDetailPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;
  
  const [analysis, setAnalysis] = useState<StatisticalAnalysis | null>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [rerunning, setRerunning] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analysisRes, resultsRes] = await Promise.all([
          api.get(`/research/analyses/${analysisId}`),
          api.get(`/research/analyses/${analysisId}/results`),
        ]);
        
        setAnalysis(analysisRes.data);
        setResults(resultsRes.data || null);
      } catch (error) {
        console.error("Error fetching analysis:", error);
        if ((error as any).response?.status === 404) {
          router.push("/research/analyses");
        }
      } finally {
        setLoading(false);
      }
    };

    if (analysisId) {
      fetchData();
    }
  }, [analysisId, router]);

  const handleRerun = async () => {
    setRerunning(true);
    try {
      await api.post(`/research/analyses/${analysisId}/rerun`, { force: false });
      // Refetch data
      const [analysisRes, resultsRes] = await Promise.all([
        api.get(`/research/analyses/${analysisId}`),
        api.get(`/research/analyses/${analysisId}/results`),
      ]);
      setAnalysis(analysisRes.data);
      setResults(resultsRes.data || null);
    } catch (error) {
      console.error("Error rerunning analysis:", error);
      alert("Error al reejecutar el análisis");
    } finally {
      setRerunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Análisis no encontrado</p>
      </div>
    );
  }

  const estadoColors = {
    PLANIFICADO: "bg-gray-100 text-gray-800",
    VALIDADO: "bg-blue-100 text-blue-800",
    EJECUTANDO: "bg-yellow-100 text-yellow-800",
    COMPLETADO: "bg-green-100 text-green-800",
    ERROR: "bg-red-100 text-red-800",
    CANCELADO: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{analysis.nombre}</h1>
          <p className="mt-2 text-gray-600">{analysis.objetivo || "Sin objetivo definido"}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleRerun}
            disabled={rerunning || analysis.estado === "EJECUTANDO"}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {rerunning ? "Reejecutando..." : "Reejecutar"}
          </button>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Volver
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información del Análisis</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Estado</p>
            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColors[analysis.estado as keyof typeof estadoColors]}`}>
              {analysis.estado}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Variable de Resultado</p>
            <p className="font-medium">{analysis.variable_resultado}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Variable de Agrupación</p>
            <p className="font-medium">{analysis.variable_grupo || "N/A"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Diseño</p>
            <p className="font-medium">{analysis.diseno}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Prueba Solicitada</p>
            <p className="font-medium">{analysis.prueba_solicitada || "Selector automático"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Prueba Ejecutada</p>
            <p className="font-medium">{analysis.prueba_ejecutada || "N/A"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Nivel de Significancia</p>
            <p className="font-medium">{analysis.alpha}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Corrección Múltiple</p>
            <p className="font-medium">{analysis.correccion_multiple}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Fecha de Creación</p>
            <p className="font-medium">{new Date(analysis.fecha_creacion).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Fecha de Ejecución</p>
            <p className="font-medium">{analysis.fecha_ejecucion ? new Date(analysis.fecha_ejecucion).toLocaleString() : "N/A"}</p>
          </div>
        </div>
      </div>

      {results && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resultados</h2>
          
          {results.interpretacion && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium text-blue-900">Interpretación</p>
              <p className="text-sm text-blue-800">{results.interpretacion}</p>
            </div>
          )}

          {results.advertencias && results.advertencias.length > 0 && (
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm font-medium text-yellow-900">Advertencias</p>
              <ul className="list-disc list-inside text-sm text-yellow-800">
                {results.advertencias.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="space-y-4">
            {results.resultado && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Resultado Principal</h3>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(results.resultado, null, 2)}
                </pre>
              </div>
            )}

            {results.descriptivos && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Estadísticos Descriptivos</h3>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(results.descriptivos, null, 2)}
                </pre>
              </div>
            )}

            {results.efecto && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Tamaño del Efecto</h3>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(results.efecto, null, 2)}
                </pre>
              </div>
            )}

            {results.intervalos && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Intervalos de Confianza</h3>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(results.intervalos, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {results && results.descriptivos && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Visualizaciones</h2>
          
          {/* BoxPlot si hay datos descriptivos con grupos */}
          {results.descriptivos.group_a && results.descriptivos.group_b && (
            <div className="mb-6">
              <BoxPlot
                title="Distribución por Grupo"
                data={[
                  {
                    group: "Grupo A",
                    min: results.descriptivos.group_a.min || 0,
                    q1: results.descriptivos.group_a.q1 || 0,
                    median: results.descriptivos.group_a.median || 0,
                    q3: results.descriptivos.group_a.q3 || 0,
                    max: results.descriptivos.group_a.max || 0,
                    mean: results.descriptivos.group_a.mean,
                  },
                  {
                    group: "Grupo B",
                    min: results.descriptivos.group_b.min || 0,
                    q1: results.descriptivos.group_b.q1 || 0,
                    median: results.descriptivos.group_b.median || 0,
                    q3: results.descriptivos.group_b.q3 || 0,
                    max: results.descriptivos.group_b.max || 0,
                    mean: results.descriptivos.group_b.mean,
                  },
                ]}
                height={300}
              />
            </div>
          )}

          {/* Matriz de confusión si hay datos binarios */}
          {results.resultado && results.resultado.contingency_table && (
            <div>
              <ConfusionMatrix
                title="Matriz de Confusión"
                matrix={results.resultado.contingency_table}
                labels={["Éxito", "Fallo"]}
              />
            </div>
          )}
        </div>
      )}

      {!results && analysis.estado === "COMPLETADO" && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">No hay resultados disponibles para este análisis.</p>
        </div>
      )}

      {!results && analysis.estado !== "COMPLETADO" && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            {analysis.estado === "PLANIFICADO" && "El análisis aún no ha sido ejecutado."}
            {analysis.estado === "EJECUTANDO" && "El análisis está siendo ejecutado."}
            {analysis.estado === "ERROR" && "El análisis falló durante la ejecución."}
          </p>
        </div>
      )}
    </div>
  );
}
