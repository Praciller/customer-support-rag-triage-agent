import { useEffect, useRef, useState } from "react";
import { Activity, Bot, ChevronDown } from "lucide-react";
import { nav, type View } from "../navigation";

const primary = nav.filter((item) => ["triage", "evaluation", "trace"].includes(item.id));
const secondary = nav.filter((item) => ["overview", "search", "dataset", "providers"].includes(item.id));

export function ResponsiveNavigation({ view, setView, apiStatus }: { view: View; setView: (view: View) => void; apiStatus: "checking" | "connected" | "unavailable" }) {
  const [open, setOpen] = useState(false);
  const moreRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { if (!open) return; const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") { setOpen(false); queueMicrotask(() => moreRef.current?.focus()); } }; window.addEventListener("keydown", onKeyDown); return () => window.removeEventListener("keydown", onKeyDown); }, [open]);
  const choose = (next: View) => { setView(next); setOpen(false); queueMicrotask(() => moreRef.current?.focus()); };
  return <div className="responsive-shell">
    <header className="responsive-header"><span className="responsive-brand"><Bot size={18} /> ResolveOps</span><span className="responsive-status"><Activity size={13} /> {apiStatus === "connected" ? "API Ready" : apiStatus === "unavailable" ? "API Unavailable" : "Checking API"}</span></header>
    <nav aria-label="Primary workflow navigation" className="responsive-primary">
      {primary.map((item) => <button key={item.id} aria-current={view === item.id ? "page" : undefined} className={view === item.id ? "active" : ""} onClick={() => choose(item.id)}>{item.id === "triage" ? "Triage" : item.id === "trace" ? "Trace" : item.label}</button>)}
      <button ref={moreRef} aria-expanded={open} aria-haspopup="menu" className={open ? "active" : ""} onClick={() => setOpen((value) => !value)}>More <ChevronDown size={14} /></button>
      {open && <div role="menu" aria-label="Secondary tools" className="more-menu">{secondary.map((item) => <button role="menuitem" key={item.id} aria-current={view === item.id ? "page" : undefined} onClick={() => choose(item.id)}>{item.label}</button>)}</div>}
    </nav>
  </div>;
}
