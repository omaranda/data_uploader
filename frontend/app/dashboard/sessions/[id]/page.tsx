"use client"

import { useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, CheckCircle2, XCircle, Clock, Upload, HardDrive } from "lucide-react"
import { formatBytes, formatDate, formatDuration } from "@/lib/utils"

export default function SessionProgressPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = parseInt(params.id as string)
  const { data: authSession } = useSession()

  if (authSession?.user?.accessToken) {
    apiClient.setToken(authSession.user.accessToken)
  }

  // Fetch session with polling for real-time updates
  const { data: session, refetch } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => apiClient.getSession(sessionId),
    enabled: !!authSession?.user?.accessToken,
    refetchInterval: (query) => {
      // Poll every 2 seconds if session is active
      const data = query.state.data
      if (data && (data.status === "pending" || data.status === "in_progress")) {
        return 2000
      }
      return false // Stop polling when completed or failed
    },
  })

  // Fetch project details
  const { data: project } = useQuery({
    queryKey: ["project", session?.project_id],
    queryFn: () => apiClient.getProject(session!.project_id),
    enabled: !!session?.project_id,
  })

  // Fetch cycle details
  const { data: cycle } = useQuery({
    queryKey: ["cycle", session?.cycle_id],
    queryFn: () => apiClient.getCycle(session!.cycle_id!),
    enabled: !!session?.cycle_id,
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="success">Completed</Badge>
      case "in_progress":
        return <Badge variant="warning">In Progress</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-12 w-12 text-green-500" />
      case "in_progress":
        return <Upload className="h-12 w-12 text-yellow-500 animate-pulse" />
      case "failed":
        return <XCircle className="h-12 w-12 text-red-500" />
      default:
        return <Clock className="h-12 w-12 text-gray-400" />
    }
  }

  const progress = session?.total_files
    ? Math.round((session.files_uploaded / session.total_files) * 100)
    : 0

  const isActive = session?.status === "pending" || session?.status === "in_progress"

  return (
    <div className="flex flex-col gap-4 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => router.push("/dashboard/sessions")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">Upload Session</h1>
          <p className="text-muted-foreground">
            Session ID: {sessionId}
          </p>
        </div>
        {getStatusBadge(session?.status || "pending")}
      </div>

      {/* Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Status</CardTitle>
          <CardDescription>
            {isActive ? "Upload in progress..." : "Upload session details"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            {getStatusIcon(session?.status || "pending")}
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Progress</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <Progress value={progress} />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{session?.total_files || 0}</div>
                <div className="text-sm text-muted-foreground">Total Files</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {session?.files_uploaded || 0}
                </div>
                <div className="text-sm text-muted-foreground">Uploaded</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {session?.files_failed || 0}
                </div>
                <div className="text-sm text-muted-foreground">Failed</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {session?.files_skipped || 0}
                </div>
                <div className="text-sm text-muted-foreground">Skipped</div>
              </div>
            </div>

            {isActive && (
              <div className="p-3 border border-blue-200 bg-blue-50 rounded-md text-sm text-blue-900 flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                <span>Live updates - refreshing every 2 seconds</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Session Details */}
      <Card>
        <CardHeader>
          <CardTitle>Session Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Project</span>
              <div className="font-medium">{project?.project_name || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Cycle</span>
              <div className="font-medium">{cycle?.cycle_name || "N/A"}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">S3 Bucket</span>
              <div className="font-mono text-sm">{project?.bucket_name || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">S3 Prefix</span>
              <div className="font-mono text-sm">{session?.s3_prefix || "N/A"}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Local Directory</span>
              <div className="font-mono text-sm break-all">
                {session?.local_directory || "N/A"}
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Total Size</span>
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-muted-foreground" />
                <span>{formatBytes(session?.total_size_bytes || 0)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">AWS Profile</span>
            <div className="font-medium">{session?.aws_profile || "default"}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Max Workers</span>
            <div className="font-medium">{session?.max_workers || 15}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Retry Count</span>
            <div className="font-medium">{session?.times_to_retry || 3}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Use Find</span>
            <div className="font-medium">{session?.use_find ? "Yes" : "No"}</div>
          </div>
        </CardContent>
      </Card>

      {/* Timing */}
      <Card>
        <CardHeader>
          <CardTitle>Timing</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Created</span>
            <div className="text-sm">{formatDate(session?.created_at || null)}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Started</span>
            <div className="text-sm">{formatDate(session?.started_at || null)}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Completed</span>
            <div className="text-sm">{formatDate(session?.completed_at || null)}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Duration</span>
            <div className="text-sm">
              {formatDuration(session?.started_at || null, session?.completed_at || null)}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
