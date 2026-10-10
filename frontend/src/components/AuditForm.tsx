import { useState } from 'react'
import { Sparkles, FileText, Send, AlertCircle, RefreshCw } from 'lucide-react'
import { FileDropzone } from './FileDropzone'

interface AuditFormProps {
  onSubmit: (answer: string, sourceText?: string, files?: File[]) => Promise<void>
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
  const [activeTab, setActiveTab] = useState<'paste' | 'upload'>('paste')
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleLoadSample = () => {
    setAnswer(SAMPLE_ANSWER)
    setSourceText(SAMPLE_SOURCE)
    setActiveTab('paste')
    setValidationError(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)

    if (!answer.trim()) {
      setValidationError('Please provide an AI-generated answer to audit.')
      return
    }

    const hasText = Boolean(sourceText.trim())
    const hasFiles = files.length > 0

    if (!hasText && !hasFiles) {
      setValidationError('Please provide at least one reference source (pasted text or uploaded files).')
      return
    }

    onSubmit(answer, sourceText || undefined, files)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 text-[var(--ink)]">
      {/* Sample Loader Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div>
          <h2 className="text-base font-medium text-white">Submit Answer for Evidence Audit</h2>
          <p className="text-xs text-[var(--muted)]">
            Compare an AI answer against your textbook, report, or source documents.
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
          <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-zinc-400" /> AI-Generated Answer to Audit
          </label>
          <span className="text-[11px] text-neutral-500 font-mono">
            {answer.length.toLocaleString()} / 40,000 characters
          </span>
        </div>
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Paste the AI-generated answer you want to verify against source evidence..."
          rows={5}
          disabled={loading}
          className="w-full p-3.5 rounded-xl border border-white/10 bg-[#0c0c0c] text-neutral-100 text-sm focus:border-white/30 focus:outline-none transition-all placeholder:text-neutral-600 font-sans"
        />
      </div>

      {/* Source Input Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-zinc-400" /> Reference Ground Truth Sources
          </label>
          {/* Source Tabs */}
          <div className="flex bg-[#141414] p-1 rounded-full text-xs font-medium border border-white/10">
            <button
              type="button"
              onClick={() => setActiveTab('paste')}
              className={`px-3.5 py-1 rounded-full transition-all cursor-pointer ${
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
              className={`px-3.5 py-1 rounded-full transition-all cursor-pointer ${
                activeTab === 'upload'
                  ? 'bg-white/15 text-white font-semibold'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              Upload Files {files.length > 0 && `(${files.length})`}
            </button>
          </div>
        </div>

        {activeTab === 'paste' ? (
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
        ) : (
          <FileDropzone files={files} onFilesChange={setFiles} />
        )}
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
