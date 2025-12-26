# Data Uploader - Frontend

Modern Next.js 15 web application with authentication and real-time upload tracking.

## Features

- 🔐 **NextAuth.js Authentication** - Secure login with JWT tokens
- 🏢 **Multi-Tenant UI** - Company-scoped data access
- 👥 **Role-Based Interface** - Admin and user views
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎨 **Modern UI** - Built with Tailwind CSS and shadcn/ui
- ⚡ **Real-Time Updates** - Live upload progress tracking
- 🔄 **TanStack Query** - Efficient data fetching and caching

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your settings
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Login with default credentials: `admin` / `admin123`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                        # Next.js 15 App Router
│   ├── layout.tsx             # Root layout with providers
│   ├── page.tsx               # Landing page
│   ├── globals.css            # Global styles
│   ├── login/
│   │   └── page.tsx           # Login page
│   ├── dashboard/
│   │   ├── layout.tsx         # Dashboard layout with nav
│   │   ├── page.tsx           # Dashboard home
│   │   ├── projects/          # Projects pages (TODO)
│   │   ├── upload/            # Upload form (TODO)
│   │   ├── sessions/          # Sessions list (TODO)
│   │   └── admin/             # Admin pages (TODO)
│   └── api/
│       └── auth/
│           └── [...nextauth]/ # NextAuth.js API route
├── components/
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── label.tsx
│   ├── providers.tsx          # React Query + NextAuth providers
│   └── dashboard-nav.tsx      # Dashboard navigation sidebar
├── lib/
│   ├── api-client.ts          # API client (Axios)
│   ├── auth.ts                # NextAuth configuration
│   └── utils.ts               # Utility functions
├── types/
│   ├── api.ts                 # API type definitions
│   └── next-auth.d.ts         # NextAuth type extensions
├── next.config.ts             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── .env.local                 # Environment variables
└── package.json               # Dependencies

```

## Technology Stack

### Core Framework
- **Next.js** 15.1 - React framework with App Router
- **React** 19.0 - UI library
- **TypeScript** 5.7 - Type safety

### Authentication
- **NextAuth.js** 5.0 - Authentication for Next.js
- **Credentials Provider** - Username/password auth

### UI & Styling
- **Tailwind CSS** 3.4 - Utility-first CSS
- **shadcn/ui** - Re-usable components
- **Lucide React** - Icon library
- **CVA** - Class variance authority for component variants

### Data Fetching
- **TanStack Query** 5.62 - Data synchronization
- **Axios** 1.7 - HTTP client

### Forms & Validation
- **React Hook Form** 7.54 - Form state management
- **Zod** 3.24 - Schema validation

## Environment Variables

Create `.env.local` file:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth.js configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secret-key-change-in-production-min-32-chars
```

**Important:**
- Change `NEXTAUTH_SECRET` to a random 32+ character string in production
- Use `openssl rand -base64 32` to generate a secure secret

## Authentication Flow

1. User visits `/login`
2. Enters username and password
3. NextAuth.js calls FastAPI `/api/auth/login`
4. Backend returns JWT tokens + user info
5. Tokens stored in NextAuth.js session
6. Session accessible via `useSession()` hook
7. Protected routes redirect to `/login` if not authenticated

## API Integration

The frontend communicates with the FastAPI backend via the API client:

```typescript
import { apiClient } from '@/lib/api-client'

// Login (handled by NextAuth)
const response = await apiClient.login({ username, password })

// Get projects (authenticated)
const projects = await apiClient.getProjects()

// Create session
const session = await apiClient.createSession({
  project_id: 1,
  cycle_id: 2,
  local_directory: '/path/to/files',
  s3_prefix: 'uploads/'
})
```

### Using TanStack Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// Fetch data
const { data, isLoading } = useQuery({
  queryKey: ['projects'],
  queryFn: () => apiClient.getProjects()
})

// Mutate data
const mutation = useMutation({
  mutationFn: (data) => apiClient.createProject(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['projects'] })
  }
})
```

## Components

### UI Components (shadcn/ui)

Located in `components/ui/`:
- **Button** - Customizable buttons with variants
- **Input** - Form input fields
- **Card** - Container components
- **Label** - Form labels

### Page Components

**Login Page** (`app/login/page.tsx`):
- Username/password form
- Error handling
- Redirects to dashboard on success

**Dashboard Layout** (`app/dashboard/layout.tsx`):
- Sidebar navigation
- User profile display
- Sign out button
- Admin navigation (conditional)

**Dashboard Home** (`app/dashboard/page.tsx`):
- Statistics cards (placeholder)
- Quick start guide
- Overview metrics

## Protected Routes

Routes under `/dashboard/*` require authentication via middleware:

```typescript
// middleware.ts
export { auth as middleware } from "./auth"

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

Unauthenticated users are redirected to `/login`.

## Development

### Adding a New Page

1. Create file in `app/` directory
2. Use TypeScript and React Server Components by default
3. Use `"use client"` directive for client components
4. Access session with `useSession()` hook

Example:
```typescript
// app/dashboard/projects/page.tsx
"use client"

import { useSession } from "next-auth/react"

export default function ProjectsPage() {
  const { data: session } = useSession()

  return (
    <div>
      <h1>Projects for {session?.user?.name}</h1>
    </div>
  )
}
```

### Adding a New shadcn/ui Component

1. Copy component from shadcn/ui documentation
2. Place in `components/ui/`
3. Ensure it uses `cn()` utility from `lib/utils.ts`

## Deployment

### Production Build

```bash
npm run build
npm start
```

### Docker Deployment

See main project `docker-compose.yml` for full stack deployment.

## Security Considerations

### Authentication
- ✅ JWT tokens stored in secure HTTP-only cookies (NextAuth.js)
- ✅ CSRF protection enabled
- ✅ Session expiration handled

### Production Checklist
- [ ] Change NEXTAUTH_SECRET to random value
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set secure cookie settings
- [ ] Use environment variables for all secrets

## Troubleshooting

### "Module not found" errors

Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

### Authentication not working

1. Check backend is running on http://localhost:8000
2. Verify credentials: `admin` / `admin123`
3. Check browser console for errors
4. Ensure NEXTAUTH_SECRET is set in `.env.local`

### Styles not loading

1. Check Tailwind config is correct
2. Verify `globals.css` is imported in `layout.tsx`
3. Clear browser cache

## Next Steps (Week 6)

- [ ] Build projects list page
- [ ] Build cycles management page
- [ ] Create upload form component
- [ ] Build session progress page with real-time updates
- [ ] Build sessions history page
- [ ] Create user profile page
- [ ] Build admin pages (user management)

## License

[Your License Here]
