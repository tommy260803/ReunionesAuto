"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

interface BlindEvaluation {
  summary_id: string;
  prompt_version_id: string | null;
  quality_score: number;
  accuracy_score: number;
  completeness_score: number;
  clarity_score: number;
  comments: string;
}

export default function BlindEvaluationPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [summaryId, setSummaryId] = useState("");
  const [summaryText, setSummaryText] = useState("");
  const [evaluation, setEvaluation] = useState<BlindEvaluation>({
    summary_id: "",
    prompt_version_id: null,
    quality_score: 5,
    accuracy_score: 5,
    completeness_score: 5,
    clarity_score: 5,
    comments: "",
  });

  const handleLoadSummary = async () => {
    try {
      const response = await api.get(`/summaries/${summaryId}`);
      setSummaryText(response.data.contenido);
      setEvaluation((prev) => ({ ...prev, summary_id: summaryId }));
    } catch (error) {
      console.error("Error loading summary:", error);
      alert("Error al cargar el resumen");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post("/evaluations/blind", {
        ...evaluation,
        evaluador_id: user?.id,
      });
      alert("Evaluación guardada exitosamente");
      router.push("/research/evaluations");
    } catch (error) {
      console.error("Error submitting evaluation:", error);
      alert("Error al guardar la evaluación");
    } finally {
      setLoading(false);
    }
  };

  const handleScoreChange = (field: keyof BlindEvaluation, value: number) => {
    setEvaluation((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Evaluación Ciega de Resumen</h1>
        <p className="mt-2 text-gray-600">Evalúa un resumen sin conocer el prompt que lo generó.</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6 space-y-6">
        <div>
          <label htmlFor="summaryId" className="block text-sm font-medium text-gray-700 mb-2">
            ID del Resumen a evaluar *
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              id="summaryId"
              value={summaryId}
              onChange={(e) => setSummaryId(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ingresa el ID del resumen"
            />
            <button
              type="button"
              onClick={handleLoadSummary}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Cargar
            </button>
          </div>
        </div>

        {summaryText && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Resumen</h3>
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{summaryText}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Calidad General (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={evaluation.quality_score}
                onChange={(e) => handleScoreChange("quality_score", parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center font-semibold">{evaluation.quality_score}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Precisión (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={evaluation.accuracy_score}
                onChange={(e) => handleScoreChange("accuracy_score", parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center font-semibold">{evaluation.accuracy_score}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Completitud (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={evaluation.completeness_score}
                onChange={(e) => handleScoreChange("completeness_score", parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center font-semibold">{evaluation.completeness_score}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Claridad (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={evaluation.clarity_score}
                onChange={(e) => handleScoreChange("clarity_score", parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center font-semibold">{evaluation.clarity_score}</div>
            </div>
          </div>

          <div>
            <label htmlFor="comments" className="block text-sm font-medium text-gray-700 mb-2">
              Comentarios adicionales
            </label>
            <textarea
              id="comments"
              value={evaluation.comments}
              onChange={(e) => setEvaluation((prev) => ({ ...prev, comments: e.target.value }))}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Agrega comentarios sobre la evaluación..."
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || !summaryText}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {loading ? "Guardando..." : "Guardar Evaluación"}
            </button>
          </div>
        </form>
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Instrucciones de Evaluación Ciega</h3>
        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
          <li>Evalúa el resumen basándote únicamente en su calidad y contenido</li>
          <li>No intentes identificar qué prompt generó el resumen</li>
          <li>Usa la escala 1-10 para cada criterio (1 = muy pobre, 10 = excelente)</li>
          <li>Sé objetivo y consistente en tus evaluaciones</li>
        </ul>
      </div>
    </div>
  );
}
