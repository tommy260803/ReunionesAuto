"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface BoxPlotData {
  group: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  mean?: number;
}

interface BoxPlotProps {
  data: BoxPlotData[];
  title?: string;
  height?: number;
}

export default function BoxPlot({ data, title, height = 400 }: BoxPlotProps) {
  const chartData = useMemo(() => {
    return data.map((item) => ({
      group: item.group,
      min: item.min,
      q1: item.q1,
      median: item.median,
      q3: item.q3,
      max: item.max,
      mean: item.mean || item.median,
    }));
  }, [data]);

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, "dataMax"]} />
          <YAxis dataKey="group" type="category" width={100} />
          <Tooltip />
          <Legend />
          <Bar dataKey="min" fill="#e0e7ff" name="Mínimo" />
          <Bar dataKey="q1" fill="#a5b4fc" name="Q1" />
          <Bar dataKey="median" fill="#6366f1" name="Mediana" />
          <Bar dataKey="q3" fill="#4338ca" name="Q3" />
          <Bar dataKey="max" fill="#312e81" name="Máximo" />
          {data.some((d) => d.mean !== undefined) && (
            <ReferenceLine x={0} stroke="#ef4444" strokeDasharray="3 3" label="Media" />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
