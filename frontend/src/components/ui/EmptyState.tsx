import type { ReactNode } from "react";

export function EmptyState({
  description,
  title,
  icon,
  action,
}: {
  description: string;
  title?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      {icon && <span aria-hidden="true">{icon}</span>}
      {title && <strong>{title}</strong>}
      <p>{description}</p>
      {action}
    </div>
  );
}
