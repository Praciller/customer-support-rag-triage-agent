import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary";

export function Button({
  variant = "primary",
  disabled = false,
  loading = false,
  children,
  className = "",
  ...props
}: Omit<ButtonHTMLAttributes<HTMLButtonElement>, "disabled"> & {
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <button
      {...props}
      aria-busy={loading || undefined}
      className={`button button-${variant} ${className}`.trim()}
      disabled={disabled || loading}
    >
      {children}
    </button>
  );
}
