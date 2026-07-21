"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { ArrowLeft, FlaskConical } from "lucide-react";

export default function NewExperimentPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre: "",
    descripcion: "",
    condicion: "manual",
    prompt_version_id: "",
    modelo: "",
    estado: "PLANIFICADO",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/experiments/sessions", {
        ...formData,
        investigador_id: user?.id,
      });
      router.push("/research/experiments");
    } catch (error) {
      alert("Error al crear la sesión experimental");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="max-w-3xl mx-auto">
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <FlaskConical className="w-8 h-8 text-indigo-600" />
          Nueva Sesión Experimental
        </h1>
        <p className="mt-2 text-gray-600">Configura una nueva sesión experimental de investigación</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-6">
        <div>
          <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">Nombre *</label>
          <input type="text" id="nombre" name="nombre" required value={formData.nombre} onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Nombre del experimento" />
        </div>

        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
          <textarea id="descripcion" name="descripcion" value={formData.descripcion} onChange={handleChange} rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Descripción detallada del experimento..." />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="condicion" className="block text-sm font-medium text-gray-700 mb-2">Condición *</label>
            <select id="condicion" name="condicion" required value={formData.condicion} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="manual">Manual</option>
              <option value="zoom2_base">Zoom2 Base</option>
              <option value="zoom2_mejorado">Zoom2 Mejorado</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div>
            <label htmlFor="estado" className="block text-sm font-medium text-gray-700 mb-2">Estado Inicial</label>
            <select id="estado" name="estado" value={formData.estado} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="PLANIFICADO">Planificado</option>
              <option value="EN_CURSO">En Curso</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="prompt_version_id" className="block text-sm font-medium text-gray-700 mb-2">ID Versión Prompt</label>
            <input type="text" id="prompt_version_id" name="prompt_version_id" value={formData.prompt_version_id} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="UUID del prompt" />
          </div>
          <div>
            <label htmlFor="modelo" className="block text-sm font-medium text-gray-700 mb-2">Modelo</label>
            <input type="text" id="modelo" name="modelo" value={formData.modelo} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="ej: gpt-4" />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button type="button" onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
            {loading ? "Creando..." : "Crear Experimento"}
          </button>
        </div>
      </form>
    </div>
  );
}
