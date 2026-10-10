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
        className={`border border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-white/50 bg-white/10'
            : 'border-white/15 hover:border-white/30 bg-white/[0.02]'
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
        <UploadCloud className="w-7 h-7 text-neutral-400 mx-auto mb-2" />
        <p className="text-sm font-medium text-neutral-200">
          Click to upload or drag &amp; drop source documents
        </p>
        <p className="text-xs text-neutral-500 mt-1">
          Supports PDF, DOCX, and TXT • Up to {maxFiles} files • 10MB limit per file
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-950/40 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
            Selected Sources ({files.length}/{maxFiles})
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 bg-[#111111] border border-white/10 rounded-lg text-xs"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <File className="w-4 h-4 text-neutral-400 shrink-0" />
                  <span className="truncate font-medium text-neutral-200" title={file.name}>
                    {file.name}
                  </span>
                  <span className="text-neutral-500 text-[10px] shrink-0">
                    ({Math.round(file.size / 1024)} KB)
                  </span>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(idx)
                  }}
                  className="text-neutral-500 hover:text-rose-400 p-1 rounded transition-colors"
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
