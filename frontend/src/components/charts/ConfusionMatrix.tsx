"use client";

interface ConfusionMatrixProps {
  matrix: number[][];
  labels?: string[];
  title?: string;
}

export default function ConfusionMatrix({ matrix, labels, title }: ConfusionMatrixProps) {
  const defaultLabels = labels || ["Positivo", "Negativo"];
  
  // Calcular totales
  const rowTotals = matrix.map((row) => row.reduce((a, b) => a + b, 0));
  const colTotals = matrix[0].map((_, colIndex) => 
    matrix.reduce((sum, row) => sum + row[colIndex], 0)
  );
  const total = rowTotals.reduce((a, b) => a + b, 0);

  // Calcular porcentajes
  const getPercentage = (value: number) => {
    if (total === 0) return 0;
    return ((value / total) * 100).toFixed(1);
  };

  // Calcular intensidad del color basado en valor
  const getColorIntensity = (value: number) => {
    const max = Math.max(...matrix.flat());
    if (max === 0) return "bg-gray-100";
    const intensity = value / max;
    if (intensity > 0.7) return "bg-indigo-600";
    if (intensity > 0.5) return "bg-indigo-500";
    if (intensity > 0.3) return "bg-indigo-400";
    if (intensity > 0.1) return "bg-indigo-300";
    return "bg-indigo-100";
  };

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      
      <div className="overflow-x-auto">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2 bg-gray-50"></th>
              {defaultLabels.map((label, i) => (
                <th key={i} className="border border-gray-300 px-4 py-2 bg-gray-50">
                  {label} (Predicho)
                </th>
              ))}
              <th className="border border-gray-300 px-4 py-2 bg-gray-50">Total</th>
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td className="border border-gray-300 px-4 py-2 bg-gray-50 font-medium">
                  {defaultLabels[rowIndex]} (Real)
                </td>
                {row.map((value, colIndex) => (
                  <td
                    key={colIndex}
                    className={`border border-gray-300 px-4 py-2 text-center ${getColorIntensity(value)} text-white`}
                  >
                    <div className="font-semibold">{value}</div>
                    <div className="text-xs opacity-75">{getPercentage(value)}%</div>
                  </td>
                ))}
                <td className="border border-gray-300 px-4 py-2 bg-gray-100 text-center font-semibold">
                  {rowTotals[rowIndex]}
                </td>
              </tr>
            ))}
            <tr>
              <td className="border border-gray-300 px-4 py-2 bg-gray-50 font-medium">
                Total
              </td>
              {colTotals.map((total, i) => (
                <td key={i} className="border border-gray-300 px-4 py-2 bg-gray-100 text-center font-semibold">
                  {total}
                </td>
              ))}
              <td className="border border-gray-300 px-4 py-2 bg-gray-200 text-center font-bold">
                {total}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Métricas calculadas */}
      {matrix.length === 2 && (
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="text-sm text-green-600 font-medium">Precisión</div>
            <div className="text-lg font-bold text-green-800">
              {((matrix[0][0] / (matrix[0][0] + matrix[0][1])) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="text-sm text-blue-600 font-medium">Recall</div>
            <div className="text-lg font-bold text-blue-800">
              {((matrix[0][0] / (matrix[0][0] + matrix[1][0])) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div className="text-sm text-purple-600 font-medium">F1-Score</div>
            <div className="text-lg font-bold text-purple-800">
              {(
                (2 * (matrix[0][0] / (matrix[0][0] + matrix[0][1])) * (matrix[0][0] / (matrix[0][0] + matrix[1][0]))) /
                ((matrix[0][0] / (matrix[0][0] + matrix[0][1])) + (matrix[0][0] / (matrix[0][0] + matrix[1][0]))) * 100
              ).toFixed(1)}%
            </div>
          </div>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div className="text-sm text-orange-600 font-medium">Accuracy</div>
            <div className="text-lg font-bold text-orange-800">
              {(((matrix[0][0] + matrix[1][1]) / total) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
