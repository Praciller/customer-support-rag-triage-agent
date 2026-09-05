import { Bot, CircleDot } from "lucide-react";

import { getNavItems, primaryIds, secondaryIds, type View } from "../navigation";

export function Sidebar({
  view,
  setView,
}: {
  view: View;
  setView: (view: View) => void;
}) {
  return (
    <aside>
      <div className="brand"><Bot size={22} /><span>ResolveOps</span></div>
      <p className="eyebrow">Support intelligence</p>
      <nav aria-label="Main navigation">
        <p className="nav-group-label">Workflow</p>
        {getNavItems(primaryIds).map((item) => (
          <button
            aria-current={view === item.id ? "page" : undefined}
            className={view === item.id ? "active" : ""}
            key={item.id}
            onClick={() => setView(item.id)}
          >
            <item.icon size={18} />{item.label}
          </button>
        ))}
        <p className="nav-group-label nav-group-tools">Tools</p>
        {getNavItems(secondaryIds).map((item) => (
          <button aria-current={view === item.id ? "page" : undefined} className={view === item.id ? "active" : ""} key={item.id} onClick={() => setView(item.id)}><item.icon size={18} />{item.label}</button>
        ))}
      </nav>
      <div className="system-card">
        <span><CircleDot size={14} />Deterministic demo</span>
        <strong>No API key required</strong>
        <small>Mock provider and bounded local index</small>
      </div>
    </aside>
  );
}
