"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

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
        const response = await api.get(`/experiments/${experimentId}`);
        setExperiment(response.data);
      } catch (error) {
        console.error("Error fetching experiment:", error);
        if ((error as any).response?.status === 404) {
          router.push("/research/experiments");
        }
      } finally {
        setLoading(false);
      }
    };

    if (experimentId) {
      fetchData();
    }
  }, [experimentId, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Sesión experimental no encontrada</p>
      </div>
    );
  }

  const estadoColors = {
    PLANIFICADO: "bg-gray-100 text-gray-800",
    ACTIVO: "bg-green-100 text-green-800",
    COMPLETADO: "bg-blue-100 text-blue-800",
    CANCELADO: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{experiment.nombre}</h1>
          <p className="mt-2 text-gray-600">{experiment.descripcion || "Sin descripción"}</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Volver
        </button>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información de la Sesión</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Estado</p>
            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColors[experiment.estado as keyof typeof estadoColors]}`}>
              {experiment.estado}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Fecha de Inicio</p>
            <p className="font-medium">{new Date(experiment.fecha_inicio).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Fecha de Fin</p>
            <p className="font-medium">{experiment.fecha_fin ? new Date(experiment.fecha_fin).toLocaleString() : "En curso"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">ID</p>
            <p className="font-medium text-sm">{experiment.id.slice(0, 8)}...</p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Acciones</h2>
        <div className="space-y-3">
          <button
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            disabled={experiment.estado !== "PLANIFICADO"}
          >
            Iniciar Sesión
          </button>
          <button
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            disabled={experiment.estado !== "ACTIVO"}
          >
            Finalizar Sesión
          </button>
          <button
            className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Ver Análisis Asociados
          </button>
          <button
            className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Ver Evaluaciones
          </button>
        </div>
      </div>

      {experiment.estado === "PLANIFICADO" && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            Esta sesión está planificada. Inicia la sesión cuando estés listo para comenzar la recolección de datos.
          </p>
        </div>
      )}

      {experiment.estado === "ACTIVO" && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-green-800">
            Esta sesión está activa. Los datos se están recolectando actualmente.
          </p>
        </div>
      )}

      {experiment.estado === "COMPLETADO" && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            Esta sesión está completada. Puedes ver los análisis y resultados asociados.
          </p>
        </div>
      )}
    </div>
  );
}
