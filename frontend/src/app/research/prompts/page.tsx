"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Loader2, Plus, Trash2, FileText, Check, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/context/LanguageContext";

interface PromptVersion {
  id: string;
  nombre: string;
  version: string;
  objetivo: string | null;
  proveedor: string | null;
  modelo_recomendado: string | null;
  activo: boolean;
  creado_por: string | null;
  fecha_creacion: string;
}

export default function PromptsPage() {
  const { user, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const router = useRouter();
  const [prompts, setPrompts] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    nombre: "",
    version: "",
    contenido: "",
    objetivo: "",
    proveedor: "",
    modelo_recomendado: "",
    activo: true,
  });

  useEffect(() => {
    if (!authLoading) {
      if (!user?.is_admin) {
        router.push("/dashboard");
      } else {
        fetchPrompts();
      }
    }
  }, [user, authLoading, router]);

  const fetchPrompts = async () => {
    try {
      const { data } = await api.get<PromptVersion[]>("/prompts");
      setPrompts(data);
    } catch (err) {
      setError("Error al cargar prompts");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/prompts", formData);
      setShowCreateModal(false);
      setFormData({
        nombre: "",
        version: "",
        contenido: "",
        objetivo: "",
        proveedor: "",
        modelo_recomendado: "",
        activo: true,
      });
      fetchPrompts();
    } catch (err) {
      alert("Error al crear prompt");
    }
  };

  const handleToggleActive = async (id: string, currentActive: boolean) => {
    try {
      await api.patch(`/prompts/${id}`, { activo: !currentActive });
      fetchPrompts();
    } catch (err) {
      alert("Error al actualizar prompt");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Desactivar este prompt?")) return;
    try {
      await api.delete(`/prompts/${id}`);
      fetchPrompts();
    } catch (err) {
      alert("Error al desactivar prompt");
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
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
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FileText className="w-8 h-8 text-indigo-600" />
            Gestión de Prompts
          </h1>
          <p className="text-gray-600">Versiones de prompts para ejecuciones de IA</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors inline-flex items-center gap-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          Nuevo Prompt
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 font-medium">Nombre</th>
                <th className="px-6 py-4 font-medium">Versión</th>
                <th className="px-6 py-4 font-medium">Objetivo</th>
                <th className="px-6 py-4 font-medium">Proveedor</th>
                <th className="px-6 py-4 font-medium">Modelo</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Creado</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {prompts.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{p.nombre}</td>
                  <td className="px-6 py-4 text-gray-500">{p.version}</td>
                  <td className="px-6 py-4 text-gray-500 truncate max-w-xs">{p.objetivo || "—"}</td>
                  <td className="px-6 py-4 text-gray-500">{p.proveedor || "—"}</td>
                  <td className="px-6 py-4 text-gray-500">{p.modelo_recomendado || "—"}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleToggleActive(p.id, p.activo)}
                      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
                        p.activo
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {p.activo ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                      {p.activo ? "Activo" : "Inactivo"}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-xs">
                    {format(parseISO(p.fecha_creacion), "dd MMM yyyy", { locale: language === "es" ? es : enUS })}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors inline-flex"
                      title="Desactivar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {prompts.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-gray-400">
                    No hay prompts registrados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Crear Nuevo Prompt</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nombre</label>
                  <input
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                    placeholder="ej: resumen_reunion"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Versión</label>
                  <input
                    type="text"
                    required
                    value={formData.version}
                    onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                    placeholder="ej: 1.0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Contenido</label>
                  <textarea
                    required
                    value={formData.contenido}
                    onChange={(e) => setFormData({ ...formData, contenido: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white min-h-[150px]"
                    placeholder="Contenido completo del prompt..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Objetivo</label>
                  <input
                    type="text"
                    value={formData.objetivo}
                    onChange={(e) => setFormData({ ...formData, objetivo: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                    placeholder="Descripción del propósito"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Proveedor</label>
                    <input
                      type="text"
                      value={formData.proveedor}
                      onChange={(e) => setFormData({ ...formData, proveedor: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                      placeholder="ej: openai"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Modelo Recomendado</label>
                    <input
                      type="text"
                      value={formData.modelo_recomendado}
                      onChange={(e) => setFormData({ ...formData, modelo_recomendado: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                      placeholder="ej: gpt-4"
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="activo"
                    checked={formData.activo}
                    onChange={(e) => setFormData({ ...formData, activo: e.target.checked })}
                    className="rounded"
                  />
                  <label htmlFor="activo" className="text-sm font-medium">Activo</label>
                </div>
                <div className="flex gap-3 justify-end pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    Crear Prompt
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
