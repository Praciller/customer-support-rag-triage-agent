import type { ComponentProps, ReactNode } from "react";

import { Button as AriaButton } from "@/components/aria-ui/button";

type ButtonVariant = "primary" | "secondary";

export function Button({
  variant = "primary",
  disabled = false,
  loading = false,
  children,
  className = "",
  ...props
}: Omit<ComponentProps<typeof AriaButton>, "children" | "isDisabled" | "className" | "variant"> & {
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <AriaButton
      {...props}
      variant={variant === "primary" ? "default" : "outline"}
      isDisabled={disabled || loading}
      aria-busy={loading || undefined}
      className={`button button-${variant} ${className}`.trim()}
    >
      {children}
    </AriaButton>
  );
}
