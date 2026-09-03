import { Activity, ChevronRight } from "lucide-react";

import { StatusIndicator } from "../../components/ui/StatusIndicator";
import { nav, type View } from "../navigation";

export type ApiStatus = "checking" | "connected" | "unavailable";

export function Topbar({ view, apiStatus }: { view: View; apiStatus: ApiStatus }) {
  const currentLabel = nav.find((item) => item.id === view)?.label;

  return (
    <header className="topbar">
      <div>
        <p className="breadcrumb">Workspace <ChevronRight size={13} /> {currentLabel}</p>
        <h1>{currentLabel}</h1>
      </div>
      <StatusIndicator
        icon={<Activity size={13} />}
        label={apiStatus === "connected" ? "API connected" : apiStatus === "unavailable" ? "API unavailable" : "Checking API"}
        tone={apiStatus === "connected" ? "success" : apiStatus === "unavailable" ? "danger" : "neutral"}
      />
    </header>
  );
}
