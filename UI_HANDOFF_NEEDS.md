# UI Handoff Needs — Backend Upgrade Capabilities

This document tracks upcoming UI/UX capabilities required by backend engine upgrades.
Per Rule 1 of the Backend Upgrade Master Prompt, frontend code remains untouched during the backend logic upgrade.
The specifications below record the API fields, expected behaviors, and suggested UI placements for later implementation.

---

## 1. Source Fit Indicator
* **Backend API Field:** `AuditResponse.source_fit` (type: `SourceFitSummary`)
  * `source_fit.overall_fit`: `"RELEVANT" | "PARTIALLY_RELEVANT" | "OFF_TOPIC"`
  * `source_fit.score`: `float` (0.0 to 1.0)
  * `source_fit.reason`: `string` explanation
  * `source_fit.all_sources_off_topic`: `boolean`
  * `source_fit.documents`: List of per-source fit ratings with salient/missing terms
* **Suggested UI Placement:**
  * In `AuditSummary`, directly below the overall assessment headline.
  * If `all_sources_off_topic === true`: Render a prominent Amber advisory banner stating:
    `"Domain Mismatch: Provided sources do not cover the topic of this answer. Claims are unverified, not false."`
  * Add a pill badge in the source documents list indicating `Relevant`, `Partial`, or `Off-Topic`.

---

## 2. Direct Web URL Input
* **Backend API Parameter:** `urls` (string on `POST /api/audits`, comma- or newline-separated)
* **Backend Response Field:** `SourceDocument.media_type === "text/html"` and `SourceDocument.source_id`
* **Suggested UI Placement:**
  * In `AuditForm.tsx`, add a 3rd tab to the source input toggle: `[ Paste Text | Upload Files | Web URLs ]`.
  * Textarea accepting HTTP/HTTPS links (e.g., textbook links, open access papers, Wikipedia articles).
  * Display a security advisory note: "Private, loopback, and cloud metadata URLs are blocked by SSRF defense."

---

## 3. Automatic Web Evidence Fallback Toggle
* **Backend API Parameter:** `enable_web_search` (boolean on `POST /api/audits`, default `false`)
* **Suggested UI Placement:**
  * In `AuditForm.tsx`, add a checkbox below the source inputs:
    `[ ] Enable free web fallback (arXiv, Crossref, Wikipedia) if sources are missing or off-topic.`
  * Allows users to audit answers even when no local reference documents are available.

---

## 4. Evidence Origin Badges & Provenance Inspector
* **Backend API Field:** `EvidenceReference.origin_type`
  * Values: `"user_document" | "user_url" | "wikipedia" | "scholarly_arxiv" | "scholarly_crossref" | "web_search"`
  * `EvidenceReference.source_url`: URL of origin (if web)
  * `EvidenceReference.citation_verified`: boolean indicating substantive coverage
* **Suggested UI Placement:**
  * In `EvidencePanel.tsx`, add a provenance badge to each evidence card:
    * `User File` (Zinc)
    * `Web URL` (Sky)
    * `Wikipedia` (Slate)
    * `arXiv / Crossref` (Emerald)
  * If `source_url` exists, render a clean external link icon opening the reference in a new tab.

---

## 5. Independent Source Corroboration Counter
* **Backend API Field:** `ClaimFinding.independent_sources_agreeing` (integer)
* **Suggested UI Placement:**
  * In `ClaimList.tsx`, render a subtle indicator chip next to the verdict badge:
    `"2 independent sources agree"`
  * Prevents treating a single web passage as absolute truth.
