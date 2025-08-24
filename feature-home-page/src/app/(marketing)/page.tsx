import { Suspense } from "react"
import { SiteHeader } from "@/components/site-header"
import { Hero } from "@/components/hero"
import { Benefits } from "@/components/benefits"
import { PeekTiles } from "@/components/peek-tiles"
import { HowItWorks } from "@/components/how-it-works"
import { Testimonials } from "@/components/testimonials"
import { FAQ } from "@/components/faq"
import { CTABand } from "@/components/cta-band"
import { SiteFooter } from "@/components/site-footer"

export const metadata = {
  title: "Fantasy Football Codex — Game-Day Intelligence",
  description: "Conquer your fantasy football league with data-driven insights, real-time stats, injury intelligence, and betting edges.",
  keywords: ["fantasy football", "NFL", "fantasy sports", "betting insights", "injury reports", "player stats"],
  authors: [{ name: "Fantasy Football Codex Team" }],
  creator: "Fantasy Football Codex",
  publisher: "Fantasy Football Codex",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ffcodex.com",
    title: "Fantasy Football Codex — Game-Day Intelligence",
    description: "Conquer your fantasy football league with data-driven insights, real-time stats, injury intelligence, and betting edges.",
    siteName: "Fantasy Football Codex",
    images: [
      {
        url: "https://ffcodex.com/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Fantasy Football Codex - Game-Day Intelligence",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Fantasy Football Codex — Game-Day Intelligence",
    description: "Conquer your fantasy football league with data-driven insights, real-time stats, injury intelligence, and betting edges.",
    images: ["https://ffcodex.com/og-image.jpg"],
    creator: "@ffcodex",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
  manifest: "/site.webmanifest",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
}

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      
      <main className="flex-1">
        <Hero />
        <Benefits />
        
        <section className="py-16 md:py-24">
          <div className="container">
            <div className="mx-auto max-w-4xl text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Real-time Insights at a Glance
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Get the latest updates on player performance, injuries, and betting value in one place.
              </p>
            </div>
            
            <Suspense fallback={
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-40 rounded-xl bg-muted animate-pulse" />
                ))}
              </div>
            }>
              <PeekTiles />
            </Suspense>
          </div>
        </section>
        
        <HowItWorks />
        <Testimonials />
        <FAQ />
        <CTABand />
      </main>
      
      <SiteFooter />
    </div>
  )
}
