Return candidate support actions for policy review. These are unapproved candidates, not customer-facing text.

Intent: {intent}
Urgency: {urgency}

Rules:
- Return only a JSON object with a `proposals` array of concise action statements.
- Do not include an answer, confidence, grounding claim, or citation.
- Similar past cases are not approved policy and are not supplied as policy evidence.
- Do not claim that an action or entitlement is allowed without an approved policy source.
