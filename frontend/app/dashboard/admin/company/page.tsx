// Copyright 2025 Omar Miranda
// SPDX-License-Identifier: Apache-2.0

"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Building2, Pencil, ShieldAlert, CheckCircle2, XCircle } from "lucide-react"
import type { Company } from "@/types/api"
import { formatDate } from "@/lib/utils"

export default function AdminCompanyPage() {
  const { data: authSession } = useSession()
  const queryClient = useQueryClient()
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [formData, setFormData] = useState({
    company_name: "",
    company_code: "",
    contact_email: "",
  })

  if (authSession?.user?.accessToken) {
    apiClient.setToken(authSession.user.accessToken)
  }

  // Redirect if not admin
  if (authSession?.user?.role !== "admin") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <ShieldAlert className="h-16 w-16 text-muted-foreground" />
        <h2 className="text-2xl font-bold">Access Denied</h2>
        <p className="text-muted-foreground">
          You need admin privileges to access this page
        </p>
      </div>
    )
  }

  // Fetch companies (will only return user's own company)
  const { data: companies, isLoading } = useQuery({
    queryKey: ["companies"],
    queryFn: () => apiClient.getCompanies(),
    enabled: !!authSession?.user?.accessToken,
  })

  const company = companies?.[0] // Admin can only see their own company

  // Update company mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Company> }) =>
      apiClient.updateCompany(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] })
      setIsEditOpen(false)
    },
  })

  const handleEdit = () => {
    if (company) {
      setFormData({
        company_name: company.company_name,
        company_code: company.company_code,
        contact_email: company.contact_email,
      })
      setIsEditOpen(true)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (company) {
      updateMutation.mutate({
        id: company.id,
        data: formData,
      })
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Company Settings</h1>
          <p className="text-muted-foreground">
            Manage your company information
          </p>
        </div>
        {company && (
          <Button onClick={handleEdit}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit Company
          </Button>
        )}
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-muted-foreground">
              Loading company information...
            </div>
          </CardContent>
        </Card>
      ) : !company ? (
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <Building2 className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No Company Found</h3>
              <p className="text-muted-foreground">
                Unable to load company information
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <CardDescription>
                Basic details about your company
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Company Name</p>
                  <p className="text-lg font-semibold">{company.company_name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Company Code</p>
                  <p className="text-lg font-mono">{company.company_code}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Status</p>
                  <div className="mt-1">
                    {company.is_active ? (
                      <Badge variant="success">
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        <XCircle className="mr-1 h-3 w-3" />
                        Inactive
                      </Badge>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid gap-2">
                <p className="text-sm font-medium text-muted-foreground">Contact Email</p>
                <p className="text-lg">{company.contact_email}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Created</p>
                  <p className="text-sm">{formatDate(company.created_at)}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                  <p className="text-sm">{formatDate(company.updated_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Company Statistics</CardTitle>
              <CardDescription>
                Overview of company activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-2xl font-bold text-primary">
                    {authSession?.user?.companyId || company.id}
                  </p>
                  <p className="text-sm text-muted-foreground">Company ID</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-2xl font-bold text-primary">Active</p>
                  <p className="text-sm text-muted-foreground">Account Status</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-2xl font-bold text-primary">Multi-tenant</p>
                  <p className="text-sm text-muted-foreground">Architecture</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Company</DialogTitle>
              <DialogDescription>
                Update your company information
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="company_name">Company Name</Label>
                <Input
                  id="company_name"
                  placeholder="My Company Inc."
                  value={formData.company_name}
                  onChange={(e) =>
                    setFormData({ ...formData, company_name: e.target.value })
                  }
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="company_code">Company Code</Label>
                <Input
                  id="company_code"
                  placeholder="MYCO"
                  value={formData.company_code}
                  onChange={(e) =>
                    setFormData({ ...formData, company_code: e.target.value.toUpperCase() })
                  }
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Unique identifier for your company (uppercase)
                </p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="contact_email">Contact Email</Label>
                <Input
                  id="contact_email"
                  type="email"
                  placeholder="contact@company.com"
                  value={formData.contact_email}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_email: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            {updateMutation.isError && (
              <div className="mb-4 p-3 border border-red-200 bg-red-50 rounded-md text-sm text-red-900">
                <p className="font-medium">Error updating company:</p>
                <p>{(updateMutation.error as Error).message}</p>
              </div>
            )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save Changes"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
