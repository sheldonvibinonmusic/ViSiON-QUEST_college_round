import React, { useRef } from 'react'
import { UploadCloud, File, X, AlertCircle } from 'lucide-react'

interface FileDropzoneProps {
  files: File[]
  onFilesChange: (files: File[]) => void
  maxFiles?: number
  maxBytesPerFile?: number
}

export function FileDropzone({
  files,
  onFilesChange,
  maxFiles = 5,
  maxBytesPerFile = 10 * 1024 * 1024,
}: FileDropzoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const allowedExtensions = ['.txt', '.pdf', '.docx']

  const handleFiles = (incoming: FileList | null) => {
    if (!incoming) return
    setError(null)
    const newFiles: File[] = [...files]

    for (let i = 0; i < incoming.length; i++) {
      const file = incoming[i]
      const ext = '.' + file.name.split('.').pop()?.toLowerCase()

      if (!allowedExtensions.includes(ext)) {
        setError(`File '${file.name}' has an unsupported extension. Allowed: TXT, PDF, DOCX.`)
        return
      }

      if (file.size > maxBytesPerFile) {
        setError(`File '${file.name}' exceeds the 10MB limit.`)
        return
      }

      if (newFiles.length >= maxFiles) {
        setError(`Maximum of ${maxFiles} files allowed.`)
        return
      }

      // Check duplicates
      if (!newFiles.some((f) => f.name === file.name && f.size === file.size)) {
        newFiles.push(file)
      }
    }

    onFilesChange(newFiles)
  }

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index)
    onFilesChange(updated)
  }

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragActive(false)
          handleFiles(e.dataTransfer.files)
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
          dragActive
            ? 'border-indigo-500 bg-indigo-50/50'
            : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.pdf,.docx"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <p className="text-sm font-semibold text-slate-700">
          Click to upload or drag & drop reference files
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Supports PDF, DOCX, and TXT • Max {maxFiles} files • Up to 10MB per file
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Selected Files ({files.length}/{maxFiles})
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 bg-white border border-slate-200 rounded-lg text-xs shadow-2xs"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <File className="w-4 h-4 text-indigo-600 shrink-0" />
                  <span className="truncate font-medium text-slate-800" title={file.name}>
                    {file.name}
                  </span>
                  <span className="text-slate-400 text-[10px] shrink-0">
                    ({Math.round(file.size / 1024)} KB)
                  </span>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(idx)
                  }}
                  className="text-slate-400 hover:text-rose-600 p-1 rounded transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
