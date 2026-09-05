import { Activity, Bot, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Button, Menu, MenuItem, MenuTrigger, Popover } from "react-aria-components";
import { getNavItems, primaryIds, secondaryIds, type View } from "../navigation";

const primary = getNavItems(primaryIds);
const secondary = getNavItems(secondaryIds);

export function ResponsiveNavigation({ view, setView, apiStatus }: { view: View; setView: (view: View) => void; apiStatus: "checking" | "connected" | "unavailable" }) {
  const secondaryCurrent = secondary.some((item) => item.id === view);
  const [open, setOpen] = useState(false);
  return <div className="responsive-shell">
    <header className="responsive-header"><span className="responsive-brand"><Bot size={18} /> ResolveOps</span><span className="responsive-status"><Activity size={13} /> {apiStatus === "connected" ? "API Ready" : apiStatus === "unavailable" ? "API Unavailable" : "Checking API"}</span></header>
    <nav aria-label="Primary workflow navigation" className="responsive-primary">
      {primary.map((item) => <button key={item.id} aria-current={view === item.id ? "page" : undefined} className={view === item.id ? "active" : ""} onClick={() => setView(item.id)}>{item.id === "triage" ? "Triage" : item.id === "trace" ? "Trace" : item.label}</button>)}
      <MenuTrigger isOpen={open} onOpenChange={setOpen}>
        <Button className={`more-trigger ${open || secondaryCurrent ? "active" : ""}`} data-current-secondary={secondaryCurrent ? "true" : undefined} aria-label="More">More <ChevronDown size={14} /></Button>
        <Popover placement="bottom end" className="more-menu"><Menu aria-label="Secondary tools" onAction={(key) => setView(key as View)}>{secondary.map((item) => <MenuItem id={item.id} key={item.id} data-current={view === item.id ? "true" : undefined}><span aria-current={view === item.id ? "page" : undefined}>{item.label}</span></MenuItem>)}</Menu></Popover>
      </MenuTrigger>
    </nav>
  </div>;
}
