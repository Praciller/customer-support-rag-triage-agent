import { cloneElement, type ReactElement } from "react";

type ControlProps = {
  id?: string;
  "aria-describedby"?: string;
  "aria-invalid"?: boolean;
};

export function Field({
  id,
  label,
  helperText,
  error,
  children,
}: {
  id: string;
  label: string;
  helperText?: string;
  error?: string;
  children: ReactElement<ControlProps>;
}) {
  const helpId = helperText ? `${id}-help` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [children.props["aria-describedby"], helpId, errorId].filter(Boolean).join(" ") || undefined;
  const control = cloneElement(children, {
    id: children.props.id ?? id,
    "aria-describedby": describedBy,
    "aria-invalid": error ? true : children.props["aria-invalid"],
  });

  return (
    <div className={`field${error ? " field-invalid" : ""}`}>
      <label htmlFor={id}>{label}</label>
      {control}
      {helperText && <span className="field-help" id={helpId}>{helperText}</span>}
      {error && <span className="field-error" id={errorId}>{error}</span>}
    </div>
  );
}
