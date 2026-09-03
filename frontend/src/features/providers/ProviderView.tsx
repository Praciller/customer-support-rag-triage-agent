import { useEffect, useState } from "react";

import { api } from "../../api";

export function ProviderView() {
  const [data, setData] = useState<Record<string, unknown>>({});
  useEffect(() => { api.providers().then(setData).catch(() => setData({ status: "unavailable" })); }, []);
  return (
    <section className="panel page-panel">
      <div className="section-title"><div><p>Runtime</p><h2>Provider and infrastructure status</h2></div></div>
      <div className="config-list">
        {Object.entries(data).map(([key, value]) => (
          <div key={key}><span>{key.replaceAll("_", " ")}</span><code>{typeof value === "object" ? JSON.stringify(value) : String(value)}</code></div>
        ))}
      </div>
    </section>
  );
}
