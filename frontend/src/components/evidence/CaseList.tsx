import { Database } from "lucide-react";

import type { SimilarCase } from "../../types/api";
import { EmptyState } from "../ui/EmptyState";

export function CaseList({ cases }: { cases: SimilarCase[] }) {
  if (!cases.length) {
    return <EmptyState icon={<Database size={20} />} description="No matching indexed cases yet." />;
  }
  return (
    <div className="case-list" role="list" aria-label="Retrieved evidence">
      {cases.map((item) => (
        <article className="case" role="listitem" key={item.ticket_id}>
          <div className="case-head">
            <strong>{item.ticket_id}</strong>
            <span className="score">{item.score.toFixed(2)} similarity</span>
          </div>
          <p className="case-intent">{item.intent.replaceAll("_", " ")}</p>
          <p>{item.message}</p>
          <small>Source: {item.source} · bounded demo evidence</small>
        </article>
      ))}
    </div>
  );
}
