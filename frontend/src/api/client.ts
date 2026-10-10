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
  origin_type?: 'user_document' | 'user_url' | 'wikipedia' | 'scholarly_arxiv' | 'scholarly_crossref' | 'web_search' | string
  source_url?: string | null
  retrieved_at?: string | null
  citation_verified?: boolean
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
  independent_sources_agreeing?: number
}

export interface SourceFitDocument {
  source_id: string
  filename: string
  fit_level: 'RELEVANT' | 'PARTIALLY_RELEVANT' | 'OFF_TOPIC'
  fit_score: number
  matched_terms: string[]
  missing_topics: string[]
  reason: string
}

export interface SourceFitSummary {
  overall_fit: 'RELEVANT' | 'PARTIALLY_RELEVANT' | 'OFF_TOPIC'
  average_fit_score: number
  all_sources_off_topic: boolean
  documents: SourceFitDocument[]
  explanation: string
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
  source_fit?: SourceFitSummary | null
}

function extractErrorMessage(errorData: any, defaultMsg: string): string {
  if (typeof errorData?.detail?.message === 'string') {
    return errorData.detail.message
  }
  if (typeof errorData?.detail === 'string') {
    return errorData.detail
  }
  if (Array.isArray(errorData?.detail) && errorData.detail.length > 0) {
    const first = errorData.detail[0]
    return first?.msg || first?.message || JSON.stringify(first)
  }
  if (typeof errorData?.message === 'string') {
    return errorData.message
  }
  return defaultMsg
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch('/api/health')
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(extractErrorMessage(errorData, `Health check failed with status ${res.status}`))
  }
  return res.json()
}

export async function submitAudit(
  answer: string,
  sourceText?: string,
  files?: File[],
  urls?: string[],
  enableWebSearch?: boolean
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

  if (urls && urls.length > 0) {
    formData.append('urls', urls.join('\n'))
  }

  if (enableWebSearch !== undefined) {
    formData.append('enable_web_search', enableWebSearch ? 'true' : 'false')
  }

  const res = await fetch('/api/audits', {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(extractErrorMessage(errorData, `Audit failed with HTTP status ${res.status}`))
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
