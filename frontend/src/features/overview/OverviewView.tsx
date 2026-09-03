import { ChevronRight } from "lucide-react";

import { MetricCard } from "../../components/MetricCard";
import { Button } from "../../components/ui/Button";
import type { View } from "../../app/navigation";

export function OverviewView({ setView }: { setView: (view: View) => void }) {
  return (
    <div className="overview-grid">
      <section className="panel overview-hero">
        <p className="eyebrow-dark">Retrieval-grounded operations</p>
        <h2>Move from incoming message to a reviewable support decision.</h2>
        <p>
          Classify intent, assess urgency, retrieve similar Banking77 cases, draft a response,
          verify grounding, and inspect all seven LangGraph steps.
        </p>
        <Button onClick={() => setView("triage")}>
          Open triage workspace <ChevronRight size={16} />
        </Button>
      </section>
      <MetricCard label="Workflow" value="7 nodes" detail="Typed and traceable" />
      <MetricCard label="Retrieval" value="Local BGE" detail="Qdrant semantic search" />
      <MetricCard label="Reliability" value="3 providers" detail="Cache, retry, fallback" />
    </div>
  );
}
