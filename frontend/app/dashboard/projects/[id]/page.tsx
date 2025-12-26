// Copyright 2025 Omar Miranda
// SPDX-License-Identifier: Apache-2.0

"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ArrowLeft, Plus, Pencil, Trash2 } from "lucide-react"
import type { Cycle, CreateCycleRequest, UpdateCycleRequest } from "@/types/api"
import { formatDate } from "@/lib/utils"

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = parseInt(params.id as string)
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [editingCycle, setEditingCycle] = useState<Cycle | null>(null)
  const [formData, setFormData] = useState({
    cycle_name: "",
    cycle_number: 1,
    s3_prefix: "",
    description: "",
  })

  if (session?.user?.accessToken) {
    apiClient.setToken(session.user.accessToken)
  }

  // Fetch project
  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => apiClient.getProject(projectId),
    enabled: !!session?.user?.accessToken,
  })

  // Fetch cycles
  const { data: cycles, isLoading } = useQuery({
    queryKey: ["cycles", projectId],
    queryFn: () => apiClient.getCycles(projectId),
    enabled: !!session?.user?.accessToken,
  })

  // Create cycle mutation
  const createMutation = useMutation({
    mutationFn: (data: CreateCycleRequest) => apiClient.createCycle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cycles", projectId] })
      setIsCreateOpen(false)
      resetForm()
    },
  })

  // Update cycle mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Cycle> }) => {
      // Convert null to undefined for API compatibility
      const updateData: UpdateCycleRequest = {
        ...data,
        description: data.description ?? undefined,
      }
      return apiClient.updateCycle(id, updateData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cycles", projectId] })
      setEditingCycle(null)
      resetForm()
    },
  })

  // Delete cycle mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.deleteCycle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cycles", projectId] })
    },
  })

  const resetForm = () => {
    setFormData({
      cycle_name: "",
      cycle_number: 1,
      s3_prefix: "",
      description: "",
    })
  }

  const handleCreate = () => {
    setIsCreateOpen(true)
    setEditingCycle(null)
    // Auto-increment cycle number
    const maxCycleNumber = cycles?.reduce((max, c) => Math.max(max, c.cycle_number), 0) || 0
    setFormData({
      cycle_name: `C${maxCycleNumber + 1}`,
      cycle_number: maxCycleNumber + 1,
      s3_prefix: `cycle${maxCycleNumber + 1}/`,
      description: "",
    })
  }

  const handleEdit = (cycle: Cycle) => {
    setEditingCycle(cycle)
    setFormData({
      cycle_name: cycle.cycle_name,
      cycle_number: cycle.cycle_number,
      s3_prefix: cycle.s3_prefix,
      description: cycle.description || "",
    })
    setIsCreateOpen(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingCycle) {
      updateMutation.mutate({ id: editingCycle.id, data: formData })
    } else {
      createMutation.mutate({
        project_id: projectId,
        ...formData,
      })
    }
  }

  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this cycle?")) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="success">Completed</Badge>
      case "in_progress":
        return <Badge variant="warning">In Progress</Badge>
      case "incomplete":
        return <Badge variant="destructive">Incomplete</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            {project?.project_name || "Project"}
          </h1>
          <p className="text-muted-foreground">
            {project?.description || "Manage cycles for this project"}
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="mr-2 h-4 w-4" />
          New Cycle
        </Button>
      </div>

      {project && (
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">S3 Bucket:</span>
              <span className="font-mono text-sm">{project.bucket_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">AWS Region:</span>
              <span>{project.aws_region}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              {project.is_active ? (
                <Badge variant="success">Active</Badge>
              ) : (
                <Badge variant="secondary">Inactive</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Cycles</CardTitle>
          <CardDescription>
            {cycles?.length || 0} cycle(s) in this project
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading cycles...
            </div>
          ) : cycles?.length === 0 ? (
            <div className="text-center py-8">
              <h3 className="mt-4 text-lg font-semibold">No cycles yet</h3>
              <p className="text-muted-foreground">
                Create your first cycle to organize uploads
              </p>
              <Button onClick={handleCreate} className="mt-4">
                <Plus className="mr-2 h-4 w-4" />
                Create Cycle
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Number</TableHead>
                  <TableHead>S3 Prefix</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cycles?.map((cycle) => (
                  <TableRow key={cycle.id}>
                    <TableCell className="font-medium">
                      {cycle.cycle_name}
                      {cycle.description && (
                        <div className="text-xs text-muted-foreground">
                          {cycle.description}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>{cycle.cycle_number}</TableCell>
                    <TableCell className="font-mono text-sm">
                      {cycle.s3_prefix}
                    </TableCell>
                    <TableCell>{getStatusBadge(cycle.status)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(cycle.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(cycle)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(cycle.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent onClose={() => setIsCreateOpen(false)}>
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>
                {editingCycle ? "Edit Cycle" : "Create New Cycle"}
              </DialogTitle>
              <DialogDescription>
                Configure cycle details for organized uploads
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="cycle_name">Cycle Name</Label>
                <Input
                  id="cycle_name"
                  placeholder="C1"
                  value={formData.cycle_name}
                  onChange={(e) =>
                    setFormData({ ...formData, cycle_name: e.target.value })
                  }
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="cycle_number">Cycle Number</Label>
                <Input
                  id="cycle_number"
                  type="number"
                  min="1"
                  value={formData.cycle_number}
                  onChange={(e) =>
                    setFormData({ ...formData, cycle_number: parseInt(e.target.value) })
                  }
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="s3_prefix">S3 Prefix</Label>
                <Input
                  id="s3_prefix"
                  placeholder="cycle1/"
                  value={formData.s3_prefix}
                  onChange={(e) =>
                    setFormData({ ...formData, s3_prefix: e.target.value })
                  }
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  placeholder="Cycle description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {editingCycle ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
