"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Loader2, FileDown, FileText } from "lucide-react";

interface Report {
  id: string;
  nombre: string;
  tipo: "ANALISIS" | "EXPERIMENTO";
  formato: string;
  fecha_generacion: string;
  estado: string;
}

export default function ReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await api.get("/reports");
        setReports(response.data || []);
      } catch (err) {
        console.error("Error fetching reports:", err);
      } finally {
        setLoading(false);
      }
    };
    if (user) fetchReports();
  }, [user]);

  const estadoStyles: Record<string, string> = {
    GENERANDO: "bg-yellow-100 text-yellow-700",
    COMPLETADO: "bg-emerald-100 text-emerald-700",
    ERROR: "bg-red-100 text-red-700",
    PLANIFICADO: "bg-gray-100 text-gray-700",
    EN_CURSO: "bg-blue-100 text-blue-700",
    CANCELADO: "bg-gray-100 text-gray-700",
    EJECUTANDO: "bg-yellow-100 text-yellow-700",
  };

  const tipoStyles: Record<string, string> = {
    ANALISIS: "bg-indigo-100 text-indigo-700",
    EXPERIMENTO: "bg-purple-100 text-purple-700",
    EVALUACION: "bg-blue-100 text-blue-700",
  };

  const downloadUrl = (report: Report) => {
    if (report.tipo === "ANALISIS") {
      return `/api/backend/reports/research/analyses/${report.id}/export?format_type=${report.formato}`;
    }
    return `/api/backend/reports/research/experiments/${report.id}/export?format_type=${report.formato}`;
  };

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
            <FileDown className="w-8 h-8 text-indigo-600" />
            Reportes
          </h1>
          <p className="text-gray-600">Exporta análisis y experimentos en PDF, Word o Excel</p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 font-medium">Nombre</th>
                <th className="px-6 py-4 font-medium">Tipo</th>
                <th className="px-6 py-4 font-medium">Formato</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Fecha</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {reports.map((report) => (
                <tr key={`${report.tipo}-${report.id}`} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{report.nombre}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${tipoStyles[report.tipo] || "bg-gray-100 text-gray-600"}`}>
                      {report.tipo}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 font-mono text-xs uppercase">{report.formato}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${estadoStyles[report.estado] || "bg-gray-100 text-gray-600"}`}>
                      {report.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-xs">
                    {new Date(report.fecha_generacion).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {report.estado === "COMPLETADO" || report.estado === "EN_CURSO" ? (
                      <a
                        href={downloadUrl(report)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                      >
                        <FileDown className="w-4 h-4" /> Descargar
                      </a>
                    ) : (
                      <span className="text-gray-400 text-sm">No disponible</span>
                    )}
                  </td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500 font-medium">No hay reportes generados</p>
                    <p className="text-gray-400 text-sm mt-1">Los reportes de análisis y experimentos aparecerán aquí</p>
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
