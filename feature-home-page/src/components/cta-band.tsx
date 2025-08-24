import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function CTABand() {
  return (
    <section className="bg-gradient-to-r from-primary/90 to-primary/80 text-primary-foreground py-16 md:py-20">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to outplay your league?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-primary-foreground/90">
            Join thousands of fantasy managers gaining an edge with data-driven insights.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button asChild size="lg" className="bg-background text-foreground hover:bg-background/90 text-base font-semibold">
              <Link href="/register">
                Get Started Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="bg-transparent border-background text-background hover:bg-background/10 text-base font-semibold">
              <Link href="#features">
                Learn More
              </Link>
            </Button>
          </div>
          <p className="mt-4 text-sm text-primary-foreground/80">
            No credit card required • Cancel anytime
          </p>
        </div>
      </div>
    </section>
  )
}
