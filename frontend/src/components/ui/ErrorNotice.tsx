import { ShieldAlert } from "lucide-react";

export function ErrorNotice({ message }: { message: string }) {
  return <div className="error" role="alert"><ShieldAlert size={18} />{message}</div>;
}
