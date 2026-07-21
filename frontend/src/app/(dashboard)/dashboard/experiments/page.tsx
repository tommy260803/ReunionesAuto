"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Loader2, FlaskConical, Plus, Play, Pause, Check } from "lucide-react";
import { useRouter } from "next/navigation";

interface ExperimentSession {
  id: string;
  nombre: string;
  descripcion: string | null;
  investigador_id: string;
  condicion: string;
  prompt_version_id: string | null;
  modelo: string | null;
  estado: string;
  fecha_inicio: string;
  fecha_fin: string | null;
}

export default function ExperimentsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [experiments, setExperiments] = useState<ExperimentSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    nombre: "",
    descripcion: "",
    condicion: "manual",
    prompt_version_id: "",
    modelo: "",
    estado: "PLANIFICADO",
  });

  useEffect(() => {
    if (!authLoading) {
      if (!user?.is_admin) {
        router.push("/dashboard");
      } else {
        fetchExperiments();
      }
    }
  }, [user, authLoading, router]);

  const fetchExperiments = async () => {
    try {
      const { data } = await api.get<ExperimentSession[]>("/experiments/sessions?limit=50");
      setExperiments(data);
    } catch (err) {
      setError("Error al cargar experimentos");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/experiments/sessions", {
        ...formData,
        investigador_id: user?.id,
      });
      setShowCreateModal(false);
      setFormData({
        nombre: "",
        descripcion: "",
        condicion: "manual",
        prompt_version_id: "",
        modelo: "",
        estado: "PLANIFICADO",
      });
      fetchExperiments();
    } catch (err) {
      alert("Error al crear experimento");
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await api.patch(`/experiments/sessions/${id}`, { estado: newStatus });
      fetchExperiments();
    } catch (err) {
      alert("Error al actualizar estado");
    }
  };

  const getStatusBadge = (estado: string) => {
    const styles = {
      PLANIFICADO: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
      EN_CURSO: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
      COMPLETADO: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
      CANCELADO: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    };
    return styles[estado as keyof typeof styles] || styles.PLANIFICADO;
  };

  const getStatusIcon = (estado: string) => {
    switch (estado) {
      case "EN_CURSO":
        return <Play className="w-3 h-3" />;
      case "COMPLETADO":
        return <Check className="w-3 h-3" />;
      case "CANCELADO":
        return <Pause className="w-3 h-3" />;
      default:
        return null;
    }
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            <FlaskConical className="w-8 h-8 text-brand-500" />
            Sesiones Experimentales
          </h1>
          <p className="text-slate-500">Gestión de experimentos para evaluación científica</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary inline-flex items-center gap-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          Nuevo Experimento
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 border-b border-border">
              <tr>
                <th className="px-6 py-4 font-medium">Nombre</th>
                <th className="px-6 py-4 font-medium">Descripción</th>
                <th className="px-6 py-4 font-medium">Condición</th>
                <th className="px-6 py-4 font-medium">Modelo</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Inicio</th>
                <th className="px-6 py-4 font-medium">Fin</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {experiments.map((exp) => (
                <tr key={exp.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-foreground">{exp.nombre}</td>
                  <td className="px-6 py-4 text-slate-500 truncate max-w-xs">{exp.descripcion || "—"}</td>
                  <td className="px-6 py-4">
                    <span className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono uppercase">
                      {exp.condicion}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">{exp.modelo || "—"}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${getStatusBadge(exp.estado)}`}>
                      {getStatusIcon(exp.estado)}
                      {exp.estado.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 text-xs">
                    {format(parseISO(exp.fecha_inicio), "dd MMM yyyy", { locale: es })}
                  </td>
                  <td className="px-6 py-4 text-slate-500 text-xs">
                    {exp.fecha_fin ? format(parseISO(exp.fecha_fin), "dd MMM yyyy", { locale: es }) : "—"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <select
                      value={exp.estado}
                      onChange={(e) => handleStatusChange(exp.id, e.target.value)}
                      className="bg-slate-100 dark:bg-slate-800 border-none rounded-md px-2 py-1 outline-none text-xs cursor-pointer hover:bg-slate-200 transition-colors"
                    >
                      <option value="PLANIFICADO">Planificado</option>
                      <option value="EN_CURSO">En Curso</option>
                      <option value="COMPLETADO">Completado</option>
                      <option value="CANCELADO">Cancelado</option>
                    </select>
                  </td>
                </tr>
              ))}
              {experiments.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                    No hay experimentos registrados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-2xl shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Crear Nuevo Experimento</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nombre</label>
                  <input
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                    placeholder="Nombre del experimento"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Descripción</label>
                  <textarea
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background min-h-[100px]"
                    placeholder="Descripción detallada..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Condición</label>
                  <select
                    required
                    value={formData.condicion}
                    onChange={(e) => setFormData({ ...formData, condicion: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                  >
                    <option value="manual">Manual</option>
                    <option value="zoom2_base">Zoom2 Base</option>
                    <option value="zoom2_mejorado">Zoom2 Mejorado</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">ID Versión Prompt</label>
                    <input
                      type="text"
                      value={formData.prompt_version_id}
                      onChange={(e) => setFormData({ ...formData, prompt_version_id: e.target.value })}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                      placeholder="UUID del prompt"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Modelo</label>
                    <input
                      type="text"
                      value={formData.modelo}
                      onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                      placeholder="ej: gpt-4"
                    />
                  </div>
                </div>
                <div className="flex gap-3 justify-end pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800"
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="btn-primary px-4 py-2">
                    Crear Experimento
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
