import { Search } from "lucide-react";
import { useState } from "react";

import { api } from "../../lib/api";
import { CaseList } from "../../components/evidence/CaseList";
import { Button } from "../../components/ui/Button";
import { ErrorNotice } from "../../components/ui/ErrorNotice";
import { Field } from "../../components/ui/Field";
import type { SimilarCase } from "../../types/api";

export function SearchView() {
  const [query, setQuery] = useState("card delivery is late");
  const [intent, setIntent] = useState("");
  const [topK, setTopK] = useState(5);
  const [cases, setCases] = useState<SimilarCase[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function search() {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      setCases(await api.search(query, topK, intent));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <section className="panel page-panel">
      <div className="section-title"><div><p>Vector retrieval</p><h2>Search indexed support tickets</h2></div></div>
      <div className="search-row">
        <Field id="search-query" label="Search support tickets">
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </Field>
        <Field id="search-intent" label="Intent filter">
          <select value={intent} onChange={(event) => setIntent(event.target.value)}>
            <option value="">All intents</option>
            {["delivery_issue", "refund_request", "billing_issue", "technical_issue", "account_access", "product_question", "complaint", "cancellation", "other"].map((value) => <option key={value}>{value}</option>)}
          </select>
        </Field>
        <Field id="search-top-k" label="Top K">
          <select value={topK} onChange={(event) => setTopK(Number(event.target.value))}>
            {[3, 5, 8, 10].map((value) => (
              <option key={value} value={value}>Top {value}</option>
            ))}
          </select>
        </Field>
        <Button onClick={search} disabled={!query.trim()} loading={loading}>
          <Search size={16} />{loading ? "Searching..." : "Search"}
        </Button>
      </div>
      {error && <ErrorNotice message={error} />}
      <CaseList cases={cases} />
    </section>
  );
}
