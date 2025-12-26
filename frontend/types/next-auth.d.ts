import { DefaultSession } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      accessToken: string
      role: string
      companyId: number
    } & DefaultSession["user"]
  }

  interface User {
    accessToken: string
    refreshToken: string
    role: string
    companyId: number
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken: string
    refreshToken: string
    role: string
    companyId: number
  }
}
