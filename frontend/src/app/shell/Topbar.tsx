import { Activity, ChevronRight } from "lucide-react";

import { Badge } from "../../components";
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
      <Badge tone={apiStatus === "connected" ? "success" : apiStatus === "unavailable" ? "danger" : "neutral"}>
        <Activity size={13} />
        {apiStatus === "connected"
          ? "API connected"
          : apiStatus === "unavailable"
            ? "API unavailable"
            : "Checking API"}
      </Badge>
    </header>
  );
}
