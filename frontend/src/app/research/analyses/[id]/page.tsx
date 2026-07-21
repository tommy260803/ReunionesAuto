"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Loader2, ArrowLeft, RotateCw, BarChart3 } from "lucide-react";
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

  const fetchData = async () => {
    try {
      const [analysisRes, resultsRes] = await Promise.all([
        api.get(`/api/v1/research/analyses/${analysisId}`),
        api.get(`/api/v1/research/analyses/${analysisId}/results`).catch(() => ({ data: null })),
      ]);
      setAnalysis(analysisRes.data);
      setResults(resultsRes.data || null);
    } catch (error: any) {
      if (error?.response?.status === 404) router.push("/research/analyses");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (analysisId) fetchData(); }, [analysisId]);

  const handleRerun = async () => {
    setRerunning(true);
    try {
      await api.post(`/api/v1/research/analyses/${analysisId}/rerun`, { force: false });
      const [analysisRes, resultsRes] = await Promise.all([
        api.get(`/api/v1/research/analyses/${analysisId}`),
        api.get(`/api/v1/research/analyses/${analysisId}/results`).catch(() => ({ data: null })),
      ]);
      setAnalysis(analysisRes.data);
      setResults(resultsRes.data || null);
    } catch (error) {
      alert("Error al reejecutar el análisis");
    } finally {
      setRerunning(false);
    }
  };

  const estadoStyles: Record<string, string> = {
    PLANIFICADO: "bg-gray-100 text-gray-700",
    VALIDADO: "bg-blue-100 text-blue-700",
    EJECUTANDO: "bg-yellow-100 text-yellow-700",
    COMPLETADO: "bg-emerald-100 text-emerald-700",
    ERROR: "bg-red-100 text-red-700",
    CANCELADO: "bg-gray-100 text-gray-700",
  };

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-indigo-600" /></div>;
  }

  if (!analysis) {
    return <div className="text-center py-12 text-gray-500">Análisis no encontrado</div>;
  }

  return (
    <div className="space-y-6">
      <button onClick={() => router.push("/research/analyses")} className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver a análisis
      </button>

      <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-indigo-600" />
            {analysis.nombre}
          </h1>
          <p className="mt-2 text-gray-600">{analysis.objetivo || "Sin objetivo definido"}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleRerun} disabled={rerunning || analysis.estado === "EJECUTANDO"}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
            <RotateCw className={`w-4 h-4 ${rerunning ? "animate-spin" : ""}`} />
            {rerunning ? "Reejecutando..." : "Reejecutar"}
          </button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información del Análisis</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <InfoField label="Estado" value={<span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${estadoStyles[analysis.estado] || ""}`}>{analysis.estado}</span>} />
          <InfoField label="Variable de Resultado" value={analysis.variable_resultado} />
          <InfoField label="Variable de Agrupación" value={analysis.variable_grupo || "N/A"} />
          <InfoField label="Diseño" value={analysis.diseno} />
          <InfoField label="Prueba Solicitada" value={analysis.prueba_solicitada || "Selector automático"} />
          <InfoField label="Prueba Ejecutada" value={analysis.prueba_ejecutada || "N/A"} />
          <InfoField label="Nivel α" value={String(analysis.alpha)} />
          <InfoField label="Corrección" value={analysis.correccion_multiple} />
          <InfoField label="Creado" value={new Date(analysis.fecha_creacion).toLocaleDateString()} />
          <InfoField label="Ejecutado" value={analysis.fecha_ejecucion ? new Date(analysis.fecha_ejecucion).toLocaleDateString() : "N/A"} />
        </div>
      </div>

      {results && (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resultados</h2>

          {results.interpretacion && (
            <div className="mb-4 p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
              <p className="text-sm font-semibold text-indigo-900">Interpretación</p>
              <p className="text-sm text-indigo-800 mt-1">{results.interpretacion}</p>
            </div>
          )}

          {results.advertencias && results.advertencias.length > 0 && (
            <div className="mb-4 p-4 bg-amber-50 border border-amber-100 rounded-xl">
              <p className="text-sm font-semibold text-amber-900">Advertencias</p>
              <ul className="list-disc list-inside text-sm text-amber-800 mt-1">
                {results.advertencias.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          )}

          <div className="space-y-4">
            {results.resultado && <ResultSection title="Resultado Principal" data={results.resultado} />}
            {results.descriptivos && <ResultSection title="Estadísticos Descriptivos" data={results.descriptivos} />}
            {results.efecto && <ResultSection title="Tamaño del Efecto" data={results.efecto} />}
            {results.intervalos && <ResultSection title="Intervalos de Confianza" data={results.intervalos} />}
          </div>
        </div>
      )}

      {results?.descriptivos && (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Visualizaciones</h2>
          {results.descriptivos.group_a && results.descriptivos.group_b && (
            <div className="mb-6">
              <BoxPlot title="Distribución por Grupo" data={[
                { group: "Grupo A", min: results.descriptivos.group_a.min || 0, q1: results.descriptivos.group_a.q1 || 0, median: results.descriptivos.group_a.median || 0, q3: results.descriptivos.group_a.q3 || 0, max: results.descriptivos.group_a.max || 0, mean: results.descriptivos.group_a.mean },
                { group: "Grupo B", min: results.descriptivos.group_b.min || 0, q1: results.descriptivos.group_b.q1 || 0, median: results.descriptivos.group_b.median || 0, q3: results.descriptivos.group_b.q3 || 0, max: results.descriptivos.group_b.max || 0, mean: results.descriptivos.group_b.mean },
              ]} height={300} />
            </div>
          )}
          {results.resultado?.contingency_table && (
            <ConfusionMatrix title="Matriz de Confusión" matrix={results.resultado.contingency_table} labels={["Éxito", "Fallo"]} />
          )}
        </div>
      )}

      {!results && (
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-6 text-center">
          <p className="text-gray-500">
            {analysis.estado === "PLANIFICADO" && "El análisis aún no ha sido ejecutado. Usa el botón Reejecutar para comenzar."}
            {analysis.estado === "EJECUTANDO" && "El análisis está siendo ejecutado. Espera unos momentos..."}
            {analysis.estado === "ERROR" && "El análisis falló durante la ejecución. Intenta reejecutar."}
          </p>
        </div>
      )}
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

function ResultSection({ title, data }: { title: string; data: any }) {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">{title}</h3>
      <pre className="bg-gray-50 border border-gray-100 p-4 rounded-xl overflow-x-auto text-sm text-gray-700">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
