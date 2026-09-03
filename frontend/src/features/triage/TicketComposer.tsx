import { Send } from "lucide-react";

import { ErrorNotice } from "../../components";

export const sampleTicketMessage = "My card has still not arrived and I need help before I travel tomorrow.";

const demoTickets = [
  {
    label: "Card not arrived",
    message: sampleTicketMessage,
  },
  {
    label: "Cash withdrawal",
    message: "My cash withdrawal is still pending and I need to understand why.",
  },
  {
    label: "Transfer pending",
    message: "My transfer has been pending since yesterday. What should I do?",
  },
  {
    label: "Card stolen",
    message: "My card was stolen and I need urgent help protecting my account.",
  },
  {
    label: "Account access",
    message: "I forgot my passcode and cannot sign in to the app.",
  },
  {
    label: "Suspicious transaction",
    message: "A cash withdrawal was made from my account, but I did not make it. This is urgent.",
  },
  {
    label: "Payment reversed",
    message: "My card payment was reversed even though I already received the item.",
  },
] as const;

export function TicketComposer({
  message,
  setMessage,
  run,
  loading,
  error,
}: {
  message: string;
  setMessage: (value: string) => void;
  run: () => void;
  loading: boolean;
  error: string;
}) {
  return (
    <section className="panel composer">
      <div className="section-title"><div><p>Incoming request</p><h2>Customer message</h2></div><code>{message.length}/2000</code></div>
      <textarea
        aria-label="Customer message"
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        maxLength={2000}
      />
      <div className="example-tickets" aria-label="Example tickets">
        {demoTickets.map((ticket) => (
          <button
            className="example-ticket"
            key={ticket.label}
            onClick={() => setMessage(ticket.message)}
            type="button"
          >
            {ticket.label}
          </button>
        ))}
      </div>
      <div className="actions">
        <button className="primary" onClick={run} disabled={loading || !message.trim()}>
          <Send size={16} />{loading ? "Running workflow..." : "Run triage"}
        </button>
      </div>
      {error && <ErrorNotice message={error} />}
    </section>
  );
}
