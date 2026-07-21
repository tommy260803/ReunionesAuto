"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { ArrowLeft, BarChart3 } from "lucide-react";

export default function NewAnalysisPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre: "",
    objetivo: "",
    variable_resultado: "",
    variable_grupo: "",
    diseno: "INDEPENDIENTE",
    prueba_solicitada: "",
    alpha: 0.05,
    correccion_multiple: "HOLM",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/api/v1/research/analyses", {
        ...formData,
        filtros: {},
        configuracion: {},
      });
      router.push(`/research/analyses/${response.data.id}`);
    } catch (error) {
      alert("Error al crear el análisis");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: name === "alpha" ? parseFloat(value) : value }));
  };

  return (
    <div className="max-w-3xl mx-auto">
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-indigo-600" />
          Nuevo Análisis Estadístico
        </h1>
        <p className="mt-2 text-gray-600">Configura y crea un nuevo análisis estadístico</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-6">
        <div>
          <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">Nombre del análisis *</label>
          <input type="text" id="nombre" name="nombre" required value={formData.nombre} onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Ej: Comparación de prompts v1.0 vs v1.1" />
        </div>

        <div>
          <label htmlFor="objetivo" className="block text-sm font-medium text-gray-700 mb-2">Objetivo</label>
          <textarea id="objetivo" name="objetivo" value={formData.objetivo} onChange={handleChange} rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Describe el objetivo del análisis..." />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="variable_resultado" className="block text-sm font-medium text-gray-700 mb-2">Variable de resultado *</label>
            <input type="text" id="variable_resultado" name="variable_resultado" required value={formData.variable_resultado} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ej: calidad_resumen" />
          </div>
          <div>
            <label htmlFor="variable_grupo" className="block text-sm font-medium text-gray-700 mb-2">Variable de agrupación</label>
            <input type="text" id="variable_grupo" name="variable_grupo" value={formData.variable_grupo} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ej: version_prompt" />
          </div>
        </div>

        <div>
          <label htmlFor="diseno" className="block text-sm font-medium text-gray-700 mb-2">Diseño del análisis *</label>
          <select id="diseno" name="diseno" required value={formData.diseno} onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="INDEPENDIENTE">Independiente</option>
            <option value="PAREADO">Pareado</option>
            <option value="MEDIDAS_REPETIDAS">Medidas Repetidas</option>
          </select>
        </div>

        <div>
          <label htmlFor="prueba_solicitada" className="block text-sm font-medium text-gray-700 mb-2">Prueba estadística</label>
          <select id="prueba_solicitada" name="prueba_solicitada" value={formData.prueba_solicitada} onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">Selector automático (recomendado)</option>
            <option value="welch_t_test">Welch t-test</option>
            <option value="mann_whitney_u">Mann-Whitney U</option>
            <option value="paired_t_test">Prueba t pareada</option>
            <option value="friedman">Friedman</option>
            <option value="mcnemar">McNemar</option>
            <option value="cochran_q">Q de Cochran</option>
            <option value="cronbach_alpha">Alfa de Cronbach</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="alpha" className="block text-sm font-medium text-gray-700 mb-2">Nivel de significancia (α)</label>
            <input type="number" id="alpha" name="alpha" step="0.001" min="0.001" max="0.999" value={formData.alpha} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label htmlFor="correccion_multiple" className="block text-sm font-medium text-gray-700 mb-2">Corrección múltiple</label>
            <select id="correccion_multiple" name="correccion_multiple" value={formData.correccion_multiple} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="HOLM">Holm (recomendado)</option>
              <option value="BONFERRONI">Bonferroni</option>
              <option value="NONE">Ninguna</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button type="button" onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
            {loading ? "Creando..." : "Crear Análisis"}
          </button>
        </div>
      </form>
    </div>
  );
}
