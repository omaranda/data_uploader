// Copyright 2025 Omar Miranda
// SPDX-License-Identifier: Apache-2.0

// API Response Types

export interface User {
  id: number
  company_id: number
  username: string
  email: string
  full_name: string
  role: "admin" | "user"
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface Company {
  id: number
  company_name: string
  company_code: string
  contact_email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Project {
  id: number
  company_id: number
  project_name: string
  bucket_name: string
  aws_region: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Cycle {
  id: number
  project_id: number
  cycle_name: string
  cycle_number: number
  s3_prefix: string
  status: "pending" | "in_progress" | "completed" | "incomplete"
  description: string | null
  metadata: Record<string, any> | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface SyncSession {
  id: number
  project_id: number
  cycle_id: number | null
  user_id: number | null
  local_directory: string
  s3_prefix: string
  aws_profile: string
  max_workers: number
  times_to_retry: number
  use_find: boolean
  status: "pending" | "in_progress" | "completed" | "failed"
  total_files: number
  files_uploaded: number
  files_failed: number
  files_skipped: number
  total_size_bytes: number
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface SessionStats {
  total_sessions: number
  active_sessions: number
  completed_sessions: number
  failed_sessions: number
  total_files_uploaded: number
  total_size_bytes: number
}

// Auth Types

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RefreshRequest {
  refresh_token: string
}

export interface RefreshResponse {
  access_token: string
  token_type: string
}

// Upload Job Types

export interface UploadStartRequest {
  session_id: number
}

export interface UploadStartResponse {
  job_id: string
  session_id: number
  status: string
  message: string
}

export interface JobStatusResponse {
  job_id: string
  status: "queued" | "started" | "finished" | "failed"
  session_id: number | null
  created_at: string | null
  started_at: string | null
  ended_at: string | null
  result: Record<string, any> | null
  error: string | null
}

// Request Types

export interface CreateProjectRequest {
  project_name: string
  bucket_name: string
  aws_region: string
  description?: string
}

export interface UpdateProjectRequest {
  project_name?: string
  bucket_name?: string
  aws_region?: string
  description?: string
  is_active?: boolean
}

export interface CreateCycleRequest {
  project_id: number
  cycle_name: string
  cycle_number: number
  s3_prefix: string
  status?: "pending" | "in_progress" | "completed" | "incomplete"
  description?: string
}

export interface UpdateCycleRequest {
  cycle_name?: string
  s3_prefix?: string
  status?: "pending" | "in_progress" | "completed" | "incomplete"
  description?: string
}

export interface CreateSessionRequest {
  project_id: number
  cycle_id?: number
  local_directory: string
  s3_prefix: string
  aws_profile?: string
  max_workers?: number
  times_to_retry?: number
  use_find?: boolean
}

export interface UpdateSessionRequest {
  status?: "pending" | "in_progress" | "completed" | "failed"
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  full_name: string
  role: "admin" | "user"
}

export interface UpdateUserRequest {
  email?: string
  full_name?: string
  role?: "admin" | "user"
  is_active?: boolean
}

// Presigned URL Types

export interface PresignedUrlRequest {
  session_id: number
  file_key: string
}

export interface PresignedUrlResponse {
  presigned_url: string
  file_key: string
  full_s3_key: string
  expires_in: number
}

// API Error Response

export interface APIError {
  detail: string
}
