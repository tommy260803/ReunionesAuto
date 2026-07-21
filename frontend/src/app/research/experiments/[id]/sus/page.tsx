"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

const SUS_QUESTIONS = [
  "1. Creo que usaría este sistema con frecuencia.",
  "2. Encontré el sistema innecesariamente complejo.",
  "3. Creo que el sistema fue fácil de usar.",
  "4. Necesité el apoyo de una persona técnica para usar el sistema.",
  "5. Encontré las varias funciones en el sistema bien integradas.",
  "6. Hubo mucha inconsistencia en el sistema.",
  "7. Imagino que la mayoría de la gente aprendería a usar este sistema muy rápidamente.",
  "8. Encontré el sistema muy torpe de usar.",
  "9. Me sentí muy seguro usando el sistema.",
  "10. Necesité aprender muchas cosas antes de poder usar el sistema.",
];

interface SUSResponse {
  experiment_id: string;
  responses: number[];
  comments: string;
}

export default function SUSQuestionnairePage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const experimentId = params.id as string;
  
  const [loading, setLoading] = useState(false);
  const [responses, setResponses] = useState<number[]>(new Array(10).fill(3));
  const [comments, setComments] = useState("");

  const handleResponseChange = (index: number, value: number) => {
    const newResponses = [...responses];
    newResponses[index] = value;
    setResponses(newResponses);
  };

  const calculateScore = () => {
    // Preguntas impares (1,3,5,7,9): valor - 1
    // Preguntas pares (2,4,6,8,10): 5 - valor
    let score = 0;
    for (let i = 0; i < 10; i++) {
      if (i % 2 === 0) { // Impar (índice 0, 2, 4, 6, 8)
        score += responses[i] - 1;
      } else { // Par (índice 1, 3, 5, 7, 9)
        score += 5 - responses[i];
      }
    }
    return score * 2.5; // Escalar a 0-100
  };

  const getInterpretation = (score: number) => {
    if (score >= 85) return "Excelente";
    if (score >= 70) return "Bueno";
    if (score >= 50) return "Aceptable";
    if (score >= 35) return "Pobre";
    return "Muy pobre";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const score = calculateScore();
      await api.post("/experiments/sus", {
        experiment_id: experimentId,
        responses: responses,
        score: score,
        comments: comments,
        evaluador_id: user?.id,
      });
      alert(`Cuestionario SUS completado. Puntuación: ${score.toFixed(1)}/100 (${getInterpretation(score)})`);
      router.push(`/research/experiments/${experimentId}`);
    } catch (error) {
      console.error("Error submitting SUS:", error);
      alert("Error al guardar el cuestionario");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Cuestionario SUS</h1>
        <p className="mt-2 text-gray-600">System Usability Scale - Evalúa la usabilidad del sistema.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">Instrucciones</h3>
          <p className="text-sm text-blue-800">
            Por favor, responde a cada pregunta usando la escala de 1 a 5, donde:
          </p>
          <ul className="list-disc list-inside text-sm text-blue-800 mt-2 space-y-1">
            <li>1 = Totalmente en desacuerdo</li>
            <li>2 = En desacuerdo</li>
            <li>3 = Neutral</li>
            <li>4 = De acuerdo</li>
            <li>5 = Totalmente de acuerdo</li>
          </ul>
        </div>

        {SUS_QUESTIONS.map((question, index) => (
          <div key={index} className="border-b border-gray-200 pb-4 last:border-0">
            <p className="text-sm text-gray-700 mb-3">{question}</p>
            <div className="flex items-center space-x-4">
              {[1, 2, 3, 4, 5].map((value) => (
                <label key={value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name={`question_${index}`}
                    value={value}
                    checked={responses[index] === value}
                    onChange={() => handleResponseChange(index, value)}
                    className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-600">{value}</span>
                </label>
              ))}
            </div>
          </div>
        ))}

        <div>
          <label htmlFor="comments" className="block text-sm font-medium text-gray-700 mb-2">
            Comentarios adicionales
          </label>
          <textarea
            id="comments"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Agrega comentarios sobre tu experiencia con el sistema..."
          />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Puntuación Preliminar</h3>
          <div className="text-2xl font-bold text-indigo-600">
            {calculateScore().toFixed(1)}/100
          </div>
          <div className="text-sm text-gray-600 mt-1">
            Interpretación: {getInterpretation(calculateScore())}
          </div>
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
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {loading ? "Enviando..." : "Enviar Cuestionario"}
          </button>
        </div>
      </form>
    </div>
  );
}
