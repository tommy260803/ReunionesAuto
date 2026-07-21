"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Loader2, Star, MessageSquare, CheckCircle, XCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/context/LanguageContext";

interface SummaryEvaluation {
  id: string;
  reunion_id: string;
  summary_version_id: string;
  evaluador_id: string;
  fidelidad: number | null;
  cobertura: number | null;
  claridad: number | null;
  coherencia: number | null;
  concision: number | null;
  utilidad: number | null;
  acuerdos_correctos: number | null;
  responsables_correctos: number | null;
  fechas_correctas: number | null;
  omisiones: number;
  afirmaciones_no_respaldadas: number;
  contradicciones: number;
  aprobado_sin_cambios: boolean | null;
  fecha_evaluacion: string;
}

export default function EvaluationsPage() {
  const { user, loading: authLoading } = useAuth();
  const { language, t } = useLanguage();
  const router = useRouter();
  const [evaluations, setEvaluations] = useState<SummaryEvaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading) {
      if (!user?.is_admin) {
        router.push("/dashboard");
      } else {
        fetchEvaluations();
      }
    }
  }, [user, authLoading, router]);

  const fetchEvaluations = async () => {
    try {
      const { data } = await api.get<SummaryEvaluation[]>("/evaluations/summaries?limit=50");
      setEvaluations(data);
    } catch (err) {
      setError("Error al cargar evaluaciones");
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (value: number | null) => {
    if (value === null) return <span className="text-slate-400">—</span>;
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= value ? "fill-yellow-400 text-yellow-400" : "text-slate-300"
            }`}
          />
        ))}
        <span className="ml-1 text-xs text-slate-600">{value}</span>
      </div>
    );
  };

  const calculateAverage = (evaluations: SummaryEvaluation[]) => {
    if (evaluations.length === 0) return null;
    const criteria = [
      "fidelidad", "cobertura", "claridad", "coherencia", "concision", "utilidad",
      "acuerdos_correctos", "responsables_correctos", "fechas_correctas"
    ] as const;
    
    let total = 0;
    let count = 0;
    
    evaluations.forEach(ev => {
      criteria.forEach(criterion => {
        if (ev[criterion] !== null) {
          total += ev[criterion];
          count++;
        }
      });
    });
    
    return count > 0 ? (total / count).toFixed(2) : null;
  };

  if (authLoading || loading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
      </div>
    );
  }

  if (!user?.is_admin) {
    return null;
  }

  const averageScore = calculateAverage(evaluations);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <MessageSquare className="w-8 h-8 text-brand-500" />
          Evaluaciones de Resúmenes
        </h1>
        <p className="text-slate-500">Calidad de resúmenes generados por IA</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      {averageScore && (
        <div className="bg-gradient-to-r from-brand-50 to-blue-50 dark:from-brand-900/20 dark:to-blue-900/20 border border-brand-200 dark:border-brand-800 rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Puntaje Promedio Global</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Basado en {evaluations.length} evaluaciones</p>
            </div>
            <div className="text-4xl font-bold text-brand-600 dark:text-brand-400">
              {averageScore} <span className="text-lg text-slate-500">/ 5</span>
            </div>
          </div>
        </div>
      )}

      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 border-b border-border">
              <tr>
                <th className="px-4 py-4 font-medium">Fidelidad</th>
                <th className="px-4 py-4 font-medium">Cobertura</th>
                <th className="px-4 py-4 font-medium">Claridad</th>
                <th className="px-4 py-4 font-medium">Coherencia</th>
                <th className="px-4 py-4 font-medium">Concisión</th>
                <th className="px-4 py-4 font-medium">Utilidad</th>
                <th className="px-4 py-4 font-medium">Acuerdos</th>
                <th className="px-4 py-4 font-medium">Resp.</th>
                <th className="px-4 py-4 font-medium">Fechas</th>
                <th className="px-4 py-4 font-medium">Omis.</th>
                <th className="px-4 py-4 font-medium">No Resp.</th>
                <th className="px-4 py-4 font-medium">Contrad.</th>
                <th className="px-4 py-4 font-medium">Aprobado</th>
                <th className="px-4 py-4 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {evaluations.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-4">{renderStars(ev.fidelidad)}</td>
                  <td className="px-4 py-4">{renderStars(ev.cobertura)}</td>
                  <td className="px-4 py-4">{renderStars(ev.claridad)}</td>
                  <td className="px-4 py-4">{renderStars(ev.coherencia)}</td>
                  <td className="px-4 py-4">{renderStars(ev.concision)}</td>
                  <td className="px-4 py-4">{renderStars(ev.utilidad)}</td>
                  <td className="px-4 py-4">{renderStars(ev.acuerdos_correctos)}</td>
                  <td className="px-4 py-4">{renderStars(ev.responsables_correctos)}</td>
                  <td className="px-4 py-4">{renderStars(ev.fechas_correctas)}</td>
                  <td className="px-4 py-4 text-slate-500">{ev.omisiones}</td>
                  <td className="px-4 py-4 text-slate-500">{ev.afirmaciones_no_respaldadas}</td>
                  <td className="px-4 py-4 text-slate-500">{ev.contradicciones}</td>
                  <td className="px-4 py-4">
                    {ev.aprobado_sin_cambios === true ? (
                      <CheckCircle className="w-5 h-5 text-emerald-500" />
                    ) : ev.aprobado_sin_cambios === false ? (
                      <XCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-slate-500 text-xs">
                    {format(parseISO(ev.fecha_evaluacion), "dd MMM yyyy", { locale: language === "es" ? es : enUS })}
                  </td>
                </tr>
              ))}
              {evaluations.length === 0 && (
                <tr>
                  <td colSpan={14} className="px-6 py-8 text-center text-slate-400">
                    No hay evaluaciones registradas
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
