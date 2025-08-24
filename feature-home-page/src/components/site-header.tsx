"use client"

import Link from "next/link"
import dynamic from "next/dynamic"
import { Menu, X } from "lucide-react"
import { useState, useEffect } from "react"

import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

// Dynamically import useSession to handle cases when auth isn't configured
const useSession = () => {
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { useSession: useAuthSession } = require("next-auth/react")
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return useAuthSession()
  } catch (error) {
    // Return a mock session when auth isn't configured
    return { data: { user: null } }
  }
}

export function SiteHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { data: session } = useSession()
  const isAuthenticated = !!session?.user

  // Close mobile menu when route changes
  useEffect(() => {
    const handleRouteChange = () => setIsMenuOpen(false)
    window.addEventListener('popstate', handleRouteChange)
    return () => window.removeEventListener('popstate', handleRouteChange)
  }, [])

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            <span className="inline-block font-bold text-xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Fantasy Football Codex
            </span>
          </Link>
          
          <nav className="hidden gap-6 md:flex">
            <Link
              href="#features"
              className="flex items-center text-sm font-medium text-muted-foreground transition-colors hover:text-foreground/80"
            >
              Features
            </Link>
            <Link
              href="#how-it-works"
              className="flex items-center text-sm font-medium text-muted-foreground transition-colors hover:text-foreground/80"
            >
              How It Works
            </Link>
            <Link
              href="#faq"
              className="flex items-center text-sm font-medium text-muted-foreground transition-colors hover:text-foreground/80"
            >
              FAQ
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden md:block">
            <ThemeToggle />
          </div>
          
          <div className="hidden md:flex items-center gap-2">
            {isAuthenticated ? (
              <Button asChild variant="outline" size="sm">
                <Link href="/dashboard">Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild size="sm">
                  <Link href="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          >
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t">
          <div className="container py-4 space-y-4">
            <nav className="flex flex-col space-y-2">
              <Link
                href="#features"
                className="px-4 py-2 text-sm font-medium hover:bg-accent/50 rounded-md transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Features
              </Link>
              <Link
                href="#how-it-works"
                className="px-4 py-2 text-sm font-medium hover:bg-accent/50 rounded-md transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                How It Works
              </Link>
              <Link
                href="#faq"
                className="px-4 py-2 text-sm font-medium hover:bg-accent/50 rounded-md transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                FAQ
              </Link>
            </nav>
            
            <div className="pt-4 border-t">
              <div className="flex items-center justify-between px-4 py-2">
                <span className="text-sm font-medium">Theme</span>
                <ThemeToggle />
              </div>
              
              <div className="mt-4 space-y-2">
                {isAuthenticated ? (
                  <Button asChild className="w-full" size="sm">
                    <Link href="/dashboard">Go to Dashboard</Link>
                  </Button>
                ) : (
                  <>
                    <Button asChild variant="outline" className="w-full" size="sm">
                      <Link href="/login">Sign In</Link>
                    </Button>
                    <Button asChild className="w-full" size="sm">
                      <Link href="/register">Get Started</Link>
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
