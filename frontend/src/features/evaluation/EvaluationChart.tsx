import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type MetricDatum = {
  metric: string;
  value: number;
};

export default function EvaluationChart({ data }: { data: MetricDatum[] }) {
  return (
    <section className="panel evaluation-chart">
      <div className="section-title">
        <div><p>Quality profile</p><h2>Offline baseline metrics</h2></div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <XAxis dataKey="metric" tickLine={false} axisLine={false} />
          <YAxis domain={[0, 100]} tickLine={false} axisLine={false} />
          <Tooltip formatter={(value) => `${Number(value).toFixed(1)}%`} />
          <Bar dataKey="value" fill="var(--color-success)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
