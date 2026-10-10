import type { FactualVerdict } from '../lib/labels'

export interface SystemLimits {
  max_answer_chars: number
  max_source_chars: number
  max_files: number
  max_file_bytes: number
  max_claims: number
}

export interface HealthResponse {
  status: string
  version: string
  verifier_mode: string
  model_loaded: boolean
  model_id: string
  supported_file_types: string[]
  limits: SystemLimits
}

export interface SourceDocument {
  source_id: string
  filename: string
  media_type: string
  sha256: string
  character_count: number
  page_count?: number | null
  extraction_status: string
  warnings: string[]
}

export interface EvidenceReference {
  evidence_id: string
  source_id: string
  source_name: string
  quote: string
  page_number?: number | null
  section?: string | null
  start_char: number
  end_char: number
  relation: string
  retrieval_rank: number
}

export interface ClaimFinding {
  claim_id: string
  claim_text: string
  start_char: number
  end_char: number
  verdict: FactualVerdict
  explanation: string
  evidence: EvidenceReference[]
  logic_concerns: string[]
  safety_concerns: string[]
  review_priority: 'low' | 'medium' | 'high'
  evidence_strength: number
  model_details?: Record<string, unknown> | null
  warnings: string[]
}

export interface AuditSummary {
  assessment: string
  review_recommendation: string
  total_claims: number
  supported_claims: number
  contradicted_claims: number
  not_established_claims: number
  ambiguous_claims: number
  logic_concerns_count: number
  safety_concerns_count: number
  summary_text: string
}

export interface AuditResponse {
  audit_id: string
  status: string
  source_mode: string
  original_answer: string
  sources: SourceDocument[]
  findings: ClaimFinding[]
  summary: AuditSummary
  warnings: string[]
  engine_metadata: Record<string, unknown>
  created_at: string
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch('/api/health')
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail?.message || `Health check failed with status ${res.status}`)
  }
  return res.json()
}

export async function submitAudit(
  answer: string,
  sourceText?: string,
  files?: File[]
): Promise<AuditResponse> {
  const formData = new FormData()
  formData.append('answer', answer)

  if (sourceText && sourceText.trim()) {
    formData.append('source_text', sourceText.trim())
  }

  if (files && files.length > 0) {
    for (const file of files) {
      formData.append('files', file)
    }
  }

  const res = await fetch('/api/audits', {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail?.message || `Audit failed with HTTP status ${res.status}`)
  }

  return res.json()
}

export function downloadJsonReport(audit: AuditResponse): void {
  const blob = new Blob([JSON.stringify(audit, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `second_opinion_audit_${audit.audit_id}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export async function downloadMarkdownReport(audit: AuditResponse): Promise<void> {
  const res = await fetch('/api/audits/export/markdown', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(audit),
  })

  if (!res.ok) {
    throw new Error('Failed to generate Markdown report export.')
  }

  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `second_opinion_audit_${audit.audit_id}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
