"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { ArrowLeft, EyeOff } from "lucide-react";

export default function BlindEvaluationPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [summaryId, setSummaryId] = useState("");
  const [summaryText, setSummaryText] = useState("");

  const [scores, setScores] = useState({
    fidelidad: 3, cobertura: 3, claridad: 3, coherencia: 3, concision: 3, utilidad: 3,
    acuerdos_correctos: 3, responsables_correctos: 3, fechas_correctas: 3,
    omisiones: 0, afirmaciones_no_respaldadas: 0, contradicciones: 0,
    aprobado_sin_cambios: undefined as boolean | undefined,
  });
  const [observaciones, setObservaciones] = useState("");

  const handleLoadSummary = async () => {
    try {
      const response = await api.get(`/summaries/${summaryId}`);
      setSummaryText(response.data.contenido || response.data.texto || "");
    } catch (error) {
      alert("Error al cargar el resumen");
    }
  };

  const setScore = (field: keyof typeof scores, value: any) => {
    setScores((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/evaluations/summaries", {
        reunion_id: "",
        summary_version_id: summaryId,
        evaluador_id: user?.id,
        fidelidad: scores.fidelidad,
        cobertura: scores.cobertura,
        claridad: scores.claridad,
        coherencia: scores.coherencia,
        concision: scores.concision,
        utilidad: scores.utilidad,
        acuerdos_correctos: scores.acuerdos_correctos,
        responsables_correctos: scores.responsables_correctos,
        fechas_correctas: scores.fechas_correctas,
        omisiones: scores.omisiones,
        afirmaciones_no_respaldadas: scores.afirmaciones_no_respaldadas,
        contradicciones: scores.contradicciones,
        aprobado_sin_cambios: scores.aprobado_sin_cambios ?? null,
        observaciones: observaciones || null,
      });
      alert("Evaluación guardada exitosamente");
      router.push("/research/evaluations");
    } catch (error) {
      alert("Error al guardar la evaluación");
    } finally {
      setLoading(false);
    }
  };

  const ScoreSlider = ({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label} (1-5)</label>
      <input type="range" min="1" max="5" value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600" />
      <div className="text-center font-bold text-indigo-600 text-lg mt-1">{value}</div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto">
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <EyeOff className="w-8 h-8 text-indigo-600" />
          Evaluación de Resumen
        </h1>
        <p className="mt-2 text-gray-600">Evalúa un resumen en los criterios de calidad definidos</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
          <label htmlFor="summaryId" className="block text-sm font-medium text-gray-700 mb-2">ID del Resumen a evaluar *</label>
          <div className="flex gap-2">
            <input type="text" id="summaryId" value={summaryId} onChange={(e) => setSummaryId(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ingresa el ID del resumen" />
            <button type="button" onClick={handleLoadSummary}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">Cargar</button>
          </div>

          {summaryText && (
            <div className="mt-4 bg-gray-50 border border-gray-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Resumen</h3>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">{summaryText}</p>
            </div>
          )}
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-6">
          <h3 className="font-semibold text-gray-900">Criterios de Calidad (1-5)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ScoreSlider label="Fidelidad" value={scores.fidelidad} onChange={(v) => setScore("fidelidad", v)} />
            <ScoreSlider label="Cobertura" value={scores.cobertura} onChange={(v) => setScore("cobertura", v)} />
            <ScoreSlider label="Claridad" value={scores.claridad} onChange={(v) => setScore("claridad", v)} />
            <ScoreSlider label="Coherencia" value={scores.coherencia} onChange={(v) => setScore("coherencia", v)} />
            <ScoreSlider label="Concisión" value={scores.concision} onChange={(v) => setScore("concision", v)} />
            <ScoreSlider label="Utilidad" value={scores.utilidad} onChange={(v) => setScore("utilidad", v)} />
            <ScoreSlider label="Acuerdos Correctos" value={scores.acuerdos_correctos} onChange={(v) => setScore("acuerdos_correctos", v)} />
            <ScoreSlider label="Responsables Correctos" value={scores.responsables_correctos} onChange={(v) => setScore("responsables_correctos", v)} />
            <ScoreSlider label="Fechas Correctas" value={scores.fechas_correctas} onChange={(v) => setScore("fechas_correctas", v)} />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-4">
          <h3 className="font-semibold text-gray-900">Errores Detectados</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Omisiones</label>
              <input type="number" min="0" value={scores.omisiones}
                onChange={(e) => setScore("omisiones", parseInt(e.target.value || "0"))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Afirmaciones no respaldadas</label>
              <input type="number" min="0" value={scores.afirmaciones_no_respaldadas}
                onChange={(e) => setScore("afirmaciones_no_respaldadas", parseInt(e.target.value || "0"))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contradicciones</label>
              <input type="number" min="0" value={scores.contradicciones}
                onChange={(e) => setScore("contradicciones", parseInt(e.target.value || "0"))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Aprobado sin cambios</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="aprobado" checked={scores.aprobado_sin_cambios === true}
                  onChange={() => setScore("aprobado_sin_cambios", true)}
                  className="w-4 h-4 text-indigo-600 focus:ring-indigo-500" />
                <span className="text-sm text-gray-700">Sí</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="aprobado" checked={scores.aprobado_sin_cambios === false}
                  onChange={() => setScore("aprobado_sin_cambios", false)}
                  className="w-4 h-4 text-indigo-600 focus:ring-indigo-500" />
                <span className="text-sm text-gray-700">No</span>
              </label>
            </div>
          </div>

          <div>
            <label htmlFor="observaciones" className="block text-sm font-medium text-gray-700 mb-2">Observaciones</label>
            <textarea id="observaciones" value={observaciones} onChange={(e) => setObservaciones(e.target.value)} rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Comentarios adicionales..." />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button type="button" onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">Cancelar</button>
          <button type="submit" disabled={loading || !summaryText}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
            {loading ? "Guardando..." : "Guardar Evaluación"}
          </button>
        </div>
      </form>
    </div>
  );
}
