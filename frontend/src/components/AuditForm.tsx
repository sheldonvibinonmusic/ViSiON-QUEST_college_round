import { useState } from 'react'
import { Sparkles, FileText, Send, AlertCircle, RefreshCw, Globe, Plus, X, Search } from 'lucide-react'
import { FileDropzone } from './FileDropzone'

interface AuditFormProps {
  onSubmit: (
    answer: string,
    sourceText?: string,
    files?: File[],
    urls?: string[],
    enableWebSearch?: boolean
  ) => Promise<void>
  loading: boolean
  initialAnswer?: string
  initialSource?: string
}

export const SAMPLE_ANSWER =
  'Acme Corp provides employees with a $500 home office equipment reimbursement. Employees can purchase their own laptops and request reimbursement. In addition, workers receive a $100 monthly internet stipend.'

export const SAMPLE_SOURCE = `ACME CORP REMOTE WORK AND EQUIPMENT POLICY

1. Equipment Reimbursement
Employees working remotely are eligible for a one-time home office equipment reimbursement of up to $500.
Eligible purchases include monitors, ergonomic chairs, and keyboards.
Laptops are provided directly by IT and cannot be purchased for reimbursement.

2. Expense Submission Deadline
All reimbursement requests must be submitted within 30 calendar days of purchase.
Requests submitted after 30 calendar days will be automatically rejected.

3. Ownership and Returns
All reimbursed items remain company property for the first 12 months of employment.
If an employee resigns within 12 months, the equipment must be returned or repaid at depreciated value.`

export function AuditForm({ onSubmit, loading, initialAnswer = '', initialSource = '' }: AuditFormProps) {
  const [answer, setAnswer] = useState(initialAnswer)
  const [sourceText, setSourceText] = useState(initialSource)
  const [files, setFiles] = useState<File[]>([])
  const [urls, setUrls] = useState<string[]>([])
  const [currentUrl, setCurrentUrl] = useState('')
  const [urlInputError, setUrlInputError] = useState<string | null>(null)
  const [enableWebSearch, setEnableWebSearch] = useState(false)
  const [activeTab, setActiveTab] = useState<'paste' | 'upload' | 'urls'>('paste')
  const [validationError, setValidationError] = useState<string | null>(null)

  const MAX_URLS = 5

  const handleLoadSample = () => {
    setAnswer(SAMPLE_ANSWER)
    setSourceText(SAMPLE_SOURCE)
    setFiles([])
    setUrls([])
    setEnableWebSearch(false)
    setActiveTab('paste')
    setValidationError(null)
    setUrlInputError(null)
  }

  const handleAddUrl = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setUrlInputError(null)

    const trimmed = currentUrl.trim()
    if (!trimmed) {
      setUrlInputError('Please enter a URL.')
      return
    }

    if (!/^https?:\/\//i.test(trimmed)) {
      setUrlInputError('URL must begin with http:// or https://')
      return
    }

    try {
      new URL(trimmed)
    } catch {
      setUrlInputError('Please enter a valid, well-formed URL.')
      return
    }

    if (urls.includes(trimmed)) {
      setUrlInputError('This URL has already been added.')
      return
    }

    if (urls.length >= MAX_URLS) {
      setUrlInputError(`Maximum of ${MAX_URLS} URLs allowed per audit.`)
      return
    }

    setUrls([...urls, trimmed])
    setCurrentUrl('')
    setUrlInputError(null)
  }

  const handleRemoveUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index))
  }

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setValidationError(null)

    if (!answer.trim()) {
      setValidationError('Please provide an AI-generated answer to audit.')
      return
    }

    const hasText = Boolean(sourceText.trim())
    const hasFiles = files.length > 0
    const hasUrls = urls.length > 0

    if (!hasText && !hasFiles && !hasUrls && !enableWebSearch) {
      setValidationError(
        'Please provide at least one reference source (pasted text, uploaded files, or web URLs), or enable web fallback mode.'
      )
      return
    }

    onSubmit(
      answer,
      hasText ? sourceText.trim() : undefined,
      hasFiles ? files : undefined,
      hasUrls ? urls : undefined,
      enableWebSearch
    )
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (!loading) {
        handleSubmit()
      }
    }
  }

  return (
    <form onSubmit={handleSubmit} onKeyDown={handleKeyDown} className="space-y-6 text-[var(--ink)]">
      {/* Sample Loader Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div>
          <h2 className="text-base font-medium text-white">Submit Answer for Evidence Audit</h2>
          <p className="text-xs text-[var(--muted)]">
            Compare an AI answer against your textbook, report, web pages, or source documents.
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white/90 bg-white/5 hover:bg-white/10 border border-white/15 hover:border-white/30 transition-all cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 text-zinc-300" /> Load Sample Policy
        </button>
      </div>

      {validationError && (
        <div className="flex items-center gap-2.5 p-3.5 bg-rose-950/40 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Answer Input */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label htmlFor="audit-answer-input" className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-zinc-400" /> AI-Generated Answer to Audit
          </label>
          <span className="text-[11px] text-neutral-500 font-mono">
            {answer.length.toLocaleString()} / 40,000 characters
          </span>
        </div>
        <textarea
          id="audit-answer-input"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Paste the AI-generated answer you want to verify against source evidence... (Press Ctrl+Enter to submit)"
          rows={5}
          disabled={loading}
          className="w-full p-3.5 rounded-xl border border-white/10 bg-[#0c0c0c] text-neutral-100 text-sm focus:border-white/30 focus:outline-none transition-all placeholder:text-neutral-600 font-sans"
        />
      </div>

      {/* Source Input Section */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-zinc-400" /> Reference Ground Truth Sources
          </label>
          {/* Source Tabs */}
          <div className="flex bg-[#141414] p-1 rounded-full text-xs font-medium border border-white/10 self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setActiveTab('paste')}
              className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                activeTab === 'paste'
                  ? 'bg-white/15 text-white font-semibold'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              Paste Text
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('upload')}
              className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                activeTab === 'upload'
                  ? 'bg-white/15 text-white font-semibold'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              Upload Files {files.length > 0 && `(${files.length})`}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('urls')}
              className={`px-3 py-1 rounded-full transition-all cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'urls'
                  ? 'bg-white/15 text-white font-semibold'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Globe className="w-3 h-3" /> Web URLs {urls.length > 0 && `(${urls.length})`}
            </button>
          </div>
        </div>

        {activeTab === 'paste' && (
          <div>
            <textarea
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="Paste raw textbook, policy, or reference documentation text..."
              rows={7}
              disabled={loading}
              className="w-full p-3.5 rounded-xl border border-white/10 bg-[#0c0c0c] text-neutral-100 text-sm focus:border-white/30 focus:outline-none transition-all placeholder:text-neutral-600 font-sans"
            />
            <p className="text-[11px] text-neutral-500 mt-1">
              Supports raw text inputs up to 150,000 characters.
            </p>
          </div>
        )}

        {activeTab === 'upload' && (
          <FileDropzone files={files} onFilesChange={setFiles} />
        )}

        {activeTab === 'urls' && (
          <div className="space-y-3">
            {/* URL Input Bar */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="url"
                  value={currentUrl}
                  onChange={(e) => {
                    setCurrentUrl(e.target.value)
                    if (urlInputError) setUrlInputError(null)
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAddUrl()
                    }
                  }}
                  placeholder="https://example.org/article or https://en.wikipedia.org/wiki/..."
                  disabled={loading || urls.length >= MAX_URLS}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-white/10 bg-[#0c0c0c] text-neutral-100 text-xs focus:border-white/30 focus:outline-none transition-all placeholder:text-neutral-600 disabled:opacity-50"
                />
              </div>
              <button
                type="button"
                onClick={() => handleAddUrl()}
                disabled={loading || urls.length >= MAX_URLS || !currentUrl.trim()}
                className="px-4 py-2.5 rounded-xl text-xs font-medium bg-white/10 hover:bg-white/20 text-white border border-white/15 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer flex items-center gap-1.5 shrink-0"
              >
                <Plus className="w-3.5 h-3.5" /> Add URL
              </button>
            </div>

            {urlInputError && (
              <div className="flex items-center gap-2 p-2.5 bg-rose-950/40 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
                <AlertCircle className="w-3.5 h-3.5 shrink-0 text-rose-400" />
                <span>{urlInputError}</span>
              </div>
            )}

            {/* URL Chips */}
            {urls.length === 0 ? (
              <div className="border border-dashed border-white/15 rounded-xl p-6 text-center bg-white/[0.02]">
                <Globe className="w-6 h-6 text-neutral-500 mx-auto mb-2" />
                <p className="text-xs font-medium text-neutral-300">No web URLs added yet</p>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  Paste a webpage URL above and click Add URL or press Enter. Up to {MAX_URLS} URLs.
                </p>
              </div>
            ) : (
              <div className="space-y-1.5">
                <p className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                  Added URLs ({urls.length}/{MAX_URLS})
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {urls.map((url, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 bg-[#111111] border border-white/10 rounded-lg text-xs"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <Globe className="w-4 h-4 text-sky-400 shrink-0" />
                        <span className="truncate font-mono text-[11px] text-neutral-200" title={url}>
                          {url}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveUrl(idx)}
                        disabled={loading}
                        className="text-neutral-500 hover:text-rose-400 p-1 rounded transition-colors ml-2 shrink-0 cursor-pointer disabled:opacity-50"
                        title="Remove URL"
                        aria-label={`Remove URL ${url}`}
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="text-[11px] text-neutral-500 leading-relaxed">
              Supports public HTTP/HTTPS pages. Server strictly blocks loopback, private ranges, and cloud metadata.
            </p>
          </div>
        )}
      </div>

      {/* Free Web Evidence Fallback Checkbox */}
      <div className="p-3 bg-white/[0.02] border border-white/10 rounded-xl flex items-start gap-3">
        <input
          type="checkbox"
          id="enable-web-search"
          checked={enableWebSearch}
          onChange={(e) => setEnableWebSearch(e.target.checked)}
          disabled={loading}
          className="mt-0.5 rounded border-white/20 bg-black/40 text-emerald-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
        />
        <label htmlFor="enable-web-search" className="text-xs text-neutral-300 cursor-pointer select-none">
          <span className="font-medium text-white flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5 text-neutral-400" />
            Enable free web evidence fallback (Wikipedia, arXiv, Crossref)
          </span>
          <span className="text-[11px] text-[var(--muted)] block mt-0.5 leading-relaxed">
            Automatically queries open knowledge sources if no documents are provided or if provided sources do not cover the topic.
          </span>
        </label>
      </div>

      {/* Submit Button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3.5 px-6 rounded-full font-medium text-sm flex items-center justify-center gap-2 transition-all cursor-pointer ${
            loading
              ? 'bg-neutral-700 text-neutral-300 cursor-not-allowed'
              : 'bg-white text-[#050505] hover:bg-[#ededed] active:scale-[0.99] shadow-lg shadow-white/5'
          }`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Auditing Answer Against Sources...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" /> Run Evidence Audit
            </>
          )}
        </button>
      </div>
    </form>
  )
}
