"use client"

import { useSession } from "next-auth/react"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { User, Building2, Mail, Shield, Calendar } from "lucide-react"
import { formatDate } from "@/lib/utils"

export default function ProfilePage() {
  const { data: session } = useSession()

  if (session?.user?.accessToken) {
    apiClient.setToken(session.user.accessToken)
  }

  // Fetch current user details
  const { data: currentUser } = useQuery({
    queryKey: ["current-user"],
    queryFn: () => apiClient.getCurrentUser(),
    enabled: !!session?.user?.accessToken,
  })

  // Fetch company details
  const { data: company } = useQuery({
    queryKey: ["company", currentUser?.company_id],
    queryFn: () => apiClient.getCompany(currentUser!.company_id),
    enabled: !!currentUser?.company_id,
  })

  return (
    <div className="flex flex-col gap-4 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground">
          Your account information and settings
        </p>
      </div>

      {/* User Information */}
      <Card>
        <CardHeader>
          <CardTitle>
            <User className="inline mr-2 h-5 w-5" />
            User Information
          </CardTitle>
          <CardDescription>Your personal details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Full Name</span>
              <div className="font-medium">{currentUser?.full_name || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Username</span>
              <div className="font-medium">{currentUser?.username || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Email</span>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{currentUser?.email || "Loading..."}</span>
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Role</span>
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <Badge variant={currentUser?.role === "admin" ? "default" : "secondary"}>
                  {currentUser?.role || "user"}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Status</span>
              <div>
                {currentUser?.is_active ? (
                  <Badge variant="success">Active</Badge>
                ) : (
                  <Badge variant="secondary">Inactive</Badge>
                )}
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Last Login</span>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{formatDate(currentUser?.last_login || null)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Company Information */}
      <Card>
        <CardHeader>
          <CardTitle>
            <Building2 className="inline mr-2 h-5 w-5" />
            Company Information
          </CardTitle>
          <CardDescription>Your organization details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Company Name</span>
              <div className="font-medium">{company?.company_name || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Company Code</span>
              <div className="font-mono text-sm">{company?.company_code || "Loading..."}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Contact Email</span>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{company?.contact_email || "N/A"}</span>
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Status</span>
              <div>
                {company?.is_active ? (
                  <Badge variant="success">Active</Badge>
                ) : (
                  <Badge variant="secondary">Inactive</Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Account Timeline</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Account Created</span>
            <div className="text-sm">{formatDate(currentUser?.created_at || null)}</div>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Last Updated</span>
            <div className="text-sm">{formatDate(currentUser?.updated_at || null)}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
