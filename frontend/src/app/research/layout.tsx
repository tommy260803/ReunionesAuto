"use client";

import { ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";

export default function ResearchLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  // Temporalmente deshabilitado para pruebas del sistema
  // Verificar que el usuario tenga rol de investigador o admin
  // if (user?.rol !== "INVESTIGADOR" && user?.rol !== "ADMIN") {
  //   return (
  //     <div className="flex items-center justify-center min-h-screen">
  //       <div className="text-center">
  //         <h1 className="text-2xl font-bold mb-4">Acceso Restringido</h1>
  //         <p className="text-gray-600">
  //           Esta sección es solo para investigadores y administradores.
  //         </p>
  //       </div>
  //     </div>
  //   );
  // }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <a href="/research" className="flex items-center px-4 border-b-2 border-indigo-500 text-indigo-600">
                Dashboard
              </a>
              <a href="/research/analyses" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Análisis
              </a>
              <a href="/research/experiments" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Experimentos
              </a>
              <a href="/research/evaluations" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Evaluaciones
              </a>
              <a href="/research/prompts" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Prompts
              </a>
              <a href="/research/gold-standard" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Gold Standard
              </a>
              <a href="/research/reports" className="flex items-center px-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
                Reportes
              </a>
            </div>
            <div className="flex items-center">
              <a href="/dashboard" className="text-gray-500 hover:text-gray-700">
                Volver al Dashboard Principal
              </a>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
