import { useEffect, useState } from "react";

import { api } from "../../lib/api";
import { Badge } from "../../components/ui/Badge";

export function DatasetView() {
  const [data, setData] = useState<Record<string, unknown>>({});
  useEffect(() => { api.dataset().then(setData).catch(() => setData({ status: "unavailable" })); }, []);
  const intents = (data.intents ?? {}) as Record<string, number>;
  const records = Number(data.records || 0);
  return (
    <section className="panel page-panel">
      <div className="section-title">
        <div><p>Public source</p><h2>Banking77 dataset explorer</h2></div>
        <Badge>{records} records</Badge>
      </div>
      <div className="dataset-summary">
        <div><span>Dataset</span><strong>{String(data.name ?? "Not loaded")}</strong></div>
        <div><span>License</span><strong>{String(data.license ?? "Unknown")}</strong></div>
        <div><span>Split</span><strong>{String(data.split ?? "Unknown")}</strong></div>
        <div><span>Source</span><strong>{String(data.upstream_dataset ?? data.name ?? "Unknown")}</strong></div>
      </div>
      <h3 className="subheading">Mapped intent distribution</h3>
      <div className="intent-bars">
        {Object.entries(intents).map(([intent, count]) => (
          <div key={intent}>
            <span>{intent.replaceAll("_", " ")}</span>
            <div><i style={{ width: `${Math.max(4, (count / Math.max(records, 1)) * 100)}%` }} /></div>
            <strong>{count}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
