import type { ReactElement, ReactNode } from "react";

import { type View } from "../navigation";
import { Sidebar } from "./Sidebar";
import { type ApiStatus, Topbar } from "./Topbar";
import { ResponsiveNavigation } from "./ResponsiveNavigation";

export function AppShell(props: {
  view: View;
  setView: (view: View) => void;
  apiStatus: ApiStatus;
  children: ReactNode;
}): ReactElement {
  return (
    <div className="app-shell antialiased">
      <Sidebar view={props.view} setView={props.setView} />
      <ResponsiveNavigation view={props.view} setView={props.setView} apiStatus={props.apiStatus} />
      <main>
        <Topbar view={props.view} apiStatus={props.apiStatus} />
        {props.children}
      </main>
    </div>
  );
}
