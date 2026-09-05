import {
  BarChart3,
  Database,
  GitBranch,
  LayoutDashboard,
  Search,
  ServerCog,
} from "lucide-react";

export type View =
  | "overview"
  | "triage"
  | "search"
  | "trace"
  | "evaluation"
  | "dataset"
  | "providers";

export const nav: { id: View; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "triage", label: "Ticket triage", icon: LayoutDashboard },
  { id: "search", label: "Semantic search", icon: Search },
  { id: "trace", label: "Agent trace", icon: GitBranch },
  { id: "evaluation", label: "Evaluation", icon: BarChart3 },
  { id: "dataset", label: "Dataset explorer", icon: Database },
  { id: "providers", label: "Provider status", icon: ServerCog },
];

export const primaryIds: View[] = ["triage", "evaluation", "trace"];
export const secondaryIds: View[] = ["overview", "search", "dataset", "providers"];
export const getNavItems = (ids: View[]) => ids.map((id) => nav.find((item) => item.id === id)!).filter(Boolean);
