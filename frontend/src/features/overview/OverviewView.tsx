import { ChevronRight } from "lucide-react";

import { MetricCard } from "../../components/MetricCard";
import { Button } from "../../components/ui/Button";
import type { View } from "../../app/navigation";

export function OverviewView({ setView }: { setView: (view: View) => void }) {
  return (
    <div className="overview-grid">
      <section className="panel overview-hero">
        <p className="eyebrow-dark">Policy-gated operations</p>
        <h2>Move from incoming message to a reviewable support decision.</h2>
        <p>
          Classify intent and urgency, review similar past cases as untrusted context, and inspect
          the policy gate. No approved policy source is configured, so the demo abstains and routes
          every case to human review.
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
