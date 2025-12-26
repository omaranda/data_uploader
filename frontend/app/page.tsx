import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white">
      <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
        <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 sm:text-[5rem]">
          Data <span className="text-blue-600">Uploader</span>
        </h1>
        <p className="text-xl text-gray-600 text-center max-w-2xl">
          Multi-tenant data upload management system with real-time progress tracking
        </p>
        <div className="flex gap-4">
          <Link href="/login">
            <Button size="lg" className="text-lg">
              Sign In
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline" className="text-lg">
              Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
