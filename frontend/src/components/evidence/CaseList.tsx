import { Database } from "lucide-react";

import type { SimilarCase } from "../../types/api";
import { Badge } from "../ui/Badge";
import { EmptyState } from "../ui/EmptyState";

export function CaseList({ cases }: { cases: SimilarCase[] }) {
  if (!cases.length) {
    return <EmptyState icon={<Database size={20} />} description="No matching indexed cases yet." />;
  }
  return (
    <div className="case-list">
      {cases.map((item) => (
        <article className="case" key={item.ticket_id}>
          <div className="case-head">
            <Badge>{item.intent.replaceAll("_", " ")}</Badge>
            <span className="score">{Math.round(item.score * 100)}% match</span>
          </div>
          <p>{item.message}</p>
          <small>{item.source} / {item.ticket_id}</small>
        </article>
      ))}
    </div>
  );
}
