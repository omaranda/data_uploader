"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Upload, FolderOpen, AlertCircle, FileIcon, X, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"

export default function UploadPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [selectedCycleId, setSelectedCycleId] = useState<number | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [uploadingSessionId, setUploadingSessionId] = useState<number | null>(null)
  const [showAdvanced, setShowAdvanced] = useState(false)

  if (session?.user?.accessToken) {
    apiClient.setToken(session.user.accessToken)
  }

  // Fetch projects
  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => apiClient.getProjects(true), // Only active projects
    enabled: !!session?.user?.accessToken,
  })

  // Fetch cycles for selected project
  const { data: cycles } = useQuery({
    queryKey: ["cycles", selectedProjectId],
    queryFn: () => apiClient.getCycles(selectedProjectId!),
    enabled: !!session?.user?.accessToken && selectedProjectId !== null,
  })

  // Create session and upload files directly to S3
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selectedProjectId || !selectedCycleId) {
        throw new Error("Please select a project and cycle")
      }

      if (selectedFiles.length === 0) {
        throw new Error("Please select files to upload")
      }

      // Create session (with empty local_directory since we're uploading from browser)
      const uploadSession = await apiClient.createSession({
        project_id: selectedProjectId,
        cycle_id: selectedCycleId,
        local_directory: "browser-upload",
        s3_prefix: cycles?.find((c) => c.id === selectedCycleId)?.s3_prefix || "",
        aws_profile: "default",
        max_workers: 1, // Minimum value for browser uploads (not actually used)
        times_to_retry: 0,
        use_find: false,
      })

      setUploadingSessionId(uploadSession.id)

      // Upload each file directly to S3 using presigned URLs
      let uploadedCount = 0
      let failedCount = 0
      const totalBytes = selectedFiles.reduce((sum, f) => sum + f.size, 0)

      for (const file of selectedFiles) {
        try {
          // Use the file's webkitRelativePath (preserves folder structure) or fallback to name
          // webkitRelativePath includes the folder name and full path (e.g., "my-folder/subdir/file.txt")
          const relativePath = (file as any).webkitRelativePath || file.name

          // Strip the top-level folder name to get just the internal structure
          // Example: "C1/subfolder/file.txt" becomes "subfolder/file.txt"
          // Example: "C1/file.txt" becomes "file.txt"
          const pathParts = relativePath.split('/')
          const fileKey = pathParts.length > 1 ? pathParts.slice(1).join('/') : pathParts[0]

          // Get presigned URL for this file
          const { presigned_url } = await apiClient.getPresignedUrl({
            session_id: uploadSession.id,
            file_key: fileKey,
          })

          // Upload file directly to S3
          await apiClient.uploadFileToS3(presigned_url, file)

          // Update progress
          uploadedCount++
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: 100,
          }))
        } catch (error) {
          const relativePath = (file as any).webkitRelativePath || file.name
          const pathParts = relativePath.split('/')
          const fileKey = pathParts.length > 1 ? pathParts.slice(1).join('/') : pathParts[0]

          console.error(`Failed to upload ${fileKey}:`, error)
          failedCount++
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: -1, // -1 indicates failed
          }))
        }
      }

      // Update session with final statistics
      // Note: We can't update total_files, files_uploaded, etc. through the API
      // since those fields aren't in UpdateSessionRequest schema
      // Only status can be updated
      await apiClient.updateSession(uploadSession.id, {
        status: failedCount === selectedFiles.length ? "failed" : "completed",
      })

      return { session: uploadSession, uploadedCount, failedCount }
    },
    onSuccess: (data) => {
      // Redirect to session details page
      router.push(`/dashboard/sessions/${data.session.id}`)
    },
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files)
      setSelectedFiles((prev) => [...prev, ...filesArray])
      setUploadProgress({}) // Reset progress when new files are added
    }
  }

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    uploadMutation.mutate()
  }

  const selectedProject = projects?.find((p) => p.id === selectedProjectId)
  const selectedCycle = cycles?.find((c) => c.id === selectedCycleId)
  const availableCycles = cycles?.filter((c) => c.status !== "completed")

  const totalSize = selectedFiles.reduce((sum, file) => sum + file.size, 0)
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="flex flex-col gap-4 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Files</h1>
        <p className="text-muted-foreground">
          Start a new upload session to S3
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Project & Cycle</CardTitle>
            <CardDescription>
              Select the destination for your upload
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="project">Project *</Label>
              <Select
                id="project"
                value={selectedProjectId?.toString() || ""}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value ? parseInt(e.target.value) : null)
                  setSelectedCycleId(null) // Reset cycle when project changes
                }}
                required
              >
                <option value="">Select a project...</option>
                {projects?.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.project_name} ({project.bucket_name})
                  </option>
                ))}
              </Select>
            </div>

            {selectedProject && (
              <div className="p-3 bg-muted rounded-md text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">S3 Bucket:</span>
                  <span className="font-mono">{selectedProject.bucket_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Region:</span>
                  <span>{selectedProject.aws_region}</span>
                </div>
              </div>
            )}

            <div className="grid gap-2">
              <Label htmlFor="cycle">Cycle *</Label>
              <Select
                id="cycle"
                value={selectedCycleId?.toString() || ""}
                onChange={(e) =>
                  setSelectedCycleId(e.target.value ? parseInt(e.target.value) : null)
                }
                disabled={!selectedProjectId}
                required
              >
                <option value="">Select a cycle...</option>
                {availableCycles?.map((cycle) => (
                  <option
                    key={cycle.id}
                    value={cycle.id}
                    disabled={cycle.status === "completed"}
                  >
                    {cycle.cycle_name} - {cycle.s3_prefix}
                    {cycle.status === "completed" && " (Completed)"}
                  </option>
                ))}
              </Select>
              {selectedProjectId && availableCycles?.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No available cycles. All cycles are completed or none exist.
                </p>
              )}
            </div>

            {selectedCycle && (
              <div className="p-3 bg-muted rounded-md text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">S3 Prefix:</span>
                  <span className="font-mono">{selectedCycle.s3_prefix}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge
                    variant={
                      selectedCycle.status === "pending"
                        ? "secondary"
                        : selectedCycle.status === "in_progress"
                        ? "warning"
                        : "success"
                    }
                  >
                    {selectedCycle.status}
                  </Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              <FileIcon className="inline mr-2 h-5 w-5" />
              Select Files
            </CardTitle>
            <CardDescription>
              Choose files from your computer to upload to S3
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                {...({ webkitdirectory: "", directory: "" } as any)}
                onChange={handleFileSelect}
                className="hidden"
                disabled={uploadMutation.isPending}
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadMutation.isPending}
                className="w-full"
              >
                <FolderOpen className="mr-2 h-4 w-4" />
                Choose Folder
              </Button>
              <p className="text-sm text-muted-foreground">
                Select a folder to upload. All files within the folder (including subdirectories) will be uploaded to S3.
              </p>
            </div>

            {selectedFiles.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Selected Files ({selectedFiles.length})</Label>
                  <span className="text-sm text-muted-foreground">
                    Total: {formatBytes(totalSize)}
                  </span>
                </div>
                <div className="border rounded-md max-h-64 overflow-y-auto">
                  {selectedFiles.map((file, index) => {
                    const relativePath = (file as any).webkitRelativePath || file.name
                    // Strip the top-level folder name for display
                    const pathParts = relativePath.split('/')
                    const fileKey = pathParts.length > 1 ? pathParts.slice(1).join('/') : pathParts[0]

                    return (
                      <div
                        key={`${fileKey}-${index}`}
                        className="flex items-center justify-between p-3 border-b last:border-b-0 hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <FileIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{fileKey}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatBytes(file.size)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {uploadProgress[fileKey] === 100 && (
                            <Badge variant="success" className="text-xs">Uploaded</Badge>
                          )}
                          {uploadProgress[fileKey] === -1 && (
                            <Badge variant="destructive" className="text-xs">Failed</Badge>
                          )}
                          {uploadProgress[fileKey] !== undefined &&
                           uploadProgress[fileKey] !== 100 &&
                           uploadProgress[fileKey] !== -1 && (
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                          )}
                          {!uploadMutation.isPending && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveFile(index)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex gap-4">
          <Button
            type="submit"
            size="lg"
            disabled={
              !selectedProjectId ||
              !selectedCycleId ||
              selectedFiles.length === 0 ||
              uploadMutation.isPending
            }
            className="flex-1"
          >
            {uploadMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Uploading {selectedFiles.length} file(s)...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-5 w-5" />
                Upload {selectedFiles.length > 0 ? `${selectedFiles.length} file(s)` : 'Files'}
              </>
            )}
          </Button>
        </div>

        {uploadMutation.isError && (
          <div className="p-4 border border-red-200 bg-red-50 rounded-md text-sm text-red-900">
            <p className="font-medium">Error starting upload:</p>
            <p>{(uploadMutation.error as Error).message}</p>
          </div>
        )}
      </form>
    </div>
  )
}
