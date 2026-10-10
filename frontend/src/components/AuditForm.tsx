import { useState } from 'react'
import { Sparkles, FileText, Send, AlertCircle, RefreshCw } from 'lucide-react'
import { FileDropzone } from './FileDropzone'

interface AuditFormProps {
  onSubmit: (answer: string, sourceText?: string, files?: File[]) => Promise<void>
  loading: boolean
}

const SAMPLE_ANSWER =
  'Acme Corp provides employees with a $500 home office equipment reimbursement. Employees can purchase their own laptops and request reimbursement. In addition, workers receive a $100 monthly internet stipend.'

const SAMPLE_SOURCE = `ACME CORP REMOTE WORK AND EQUIPMENT POLICY

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

export function AuditForm({ onSubmit, loading }: AuditFormProps) {
  const [answer, setAnswer] = useState('')
  const [sourceText, setSourceText] = useState('')
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
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Sample Loader Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h2 className="text-base font-bold text-slate-900">New Evidence Audit</h2>
          <p className="text-xs text-slate-500">
            Compare an AI answer against your textbook, report, or source documents.
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 transition-colors cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5" /> Load Sample Policy Audit
        </button>
      </div>

      {validationError && (
        <div className="flex items-center gap-2.5 p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Answer Input */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> AI-Generated Answer to Audit
          </label>
          <span className="text-[11px] text-slate-400 font-mono">
            {answer.length.toLocaleString()} / 40,000 characters
          </span>
        </div>
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Paste the AI-generated answer you want to verify..."
          rows={5}
          disabled={loading}
          className="w-full p-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-sans"
        />
      </div>

      {/* Source Input Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-indigo-600" /> Reference Ground Truth Sources
          </label>
          {/* Source Tabs */}
          <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium border border-slate-200">
            <button
              type="button"
              onClick={() => setActiveTab('paste')}
              className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                activeTab === 'paste'
                  ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Paste Text
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('upload')}
              className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                activeTab === 'upload'
                  ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
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
              className="w-full p-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-sans"
            />
            <p className="text-[11px] text-slate-400 mt-1">
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
          className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2 shadow-sm transition-all cursor-pointer ${
            loading
              ? 'bg-indigo-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99]'
          }`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Auditing Answer Against Evidence...
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
