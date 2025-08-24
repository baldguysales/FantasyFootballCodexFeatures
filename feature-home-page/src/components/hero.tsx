import Link from "next/link"
import { ArrowRight, BarChart2, Zap, Shield, Bell, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Hero() {
  return (
    <section className="relative overflow-hidden py-16 md:py-24 lg:py-32">
      <div className="absolute inset-0 -z-10 gridiron-bg" aria-hidden="true" />
      <div className="container relative z-10">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
            Conquer Your League with <span className="text-primary">Data-Driven</span> Insights
          </h1>
          
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Real-time stats, injury intelligence, betting edges, expert news, and social buzz—all unified to optimize your game-day calls.
          </p>
          
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button asChild size="lg" className="text-base font-semibold">
              <Link href="/register">
                Start Managing Smarter
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            
            <Button asChild variant="outline" size="lg" className="text-base font-semibold">
              <Link href="#how-it-works">
                See How It Works
              </Link>
            </Button>
          </div>
          
          <div className="mt-12">
            <div className="inline-flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <BarChart2 className="h-4 w-4 text-primary" />
                <span>Advanced Stats</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                <span>Injury Intel</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                <span>Betting Edges</span>
              </div>
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-primary" />
                <span>Expert News</span>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-primary" />
                <span>Social Buzz</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
