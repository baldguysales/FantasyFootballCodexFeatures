import Link from "next/link"
import { Twitter, Github, Mail } from "lucide-react"

export function SiteFooter() {
  const currentYear = new Date().getFullYear()
  
  const footerLinks = [
    {
      title: "Product",
      items: [
        { label: "Features", href: "#features" },
        { label: "How It Works", href: "#how-it-works" },
        { label: "Pricing", href: "/pricing" },
        { label: "Testimonials", href: "#testimonials" },
      ],
    },
    {
      title: "Resources",
      items: [
        { label: "Documentation", href: "/docs" },
        { label: "Blog", href: "/blog" },
        { label: "Guides", href: "/guides" },
        { label: "API Status", href: "/status" },
      ],
    },
    {
      title: "Company",
      items: [
        { label: "About Us", href: "/about" },
        { label: "Careers", href: "/careers" },
        { label: "Contact", href: "/contact" },
        { label: "Press", href: "/press" },
      ],
    },
    {
      title: "Legal",
      items: [
        { label: "Privacy Policy", href: "/privacy" },
        { label: "Terms of Service", href: "/terms" },
        { label: "Cookie Policy", href: "/cookies" },
        { label: "GDPR", href: "/gdpr" },
      ],
    },
  ]

  return (
    <footer className="border-t bg-background/95">
      <div className="container py-12 md:py-16">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4 lg:grid-cols-5">
          <div className="col-span-2 lg:col-span-1">
            <div className="flex flex-col h-full">
              <Link href="/" className="inline-block">
                <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Fantasy Football Codex
                </span>
              </Link>
              <p className="mt-4 text-sm text-muted-foreground">
                Data-driven insights to help you dominate your fantasy football league.
              </p>
              <div className="mt-6 flex space-x-4">
                <a 
                  href="https://twitter.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter className="h-5 w-5" />
                </a>
                <a 
                  href="https://github.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="GitHub"
                >
                  <Github className="h-5 w-5" />
                </a>
                <a 
                  href="mailto:hello@ffcodex.com" 
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Email"
                >
                  <Mail className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
          
          {footerLinks.map((column, index) => (
            <div key={index} className="space-y-4">
              <h3 className="text-sm font-semibold">{column.title}</h3>
              <ul className="space-y-2">
                {column.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    <Link 
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        
        <div className="mt-12 pt-8 border-t border-border">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground text-center md:text-left">
              &copy; {currentYear} Fantasy Football Codex. All rights reserved.
            </p>
            <p className="text-xs text-muted-foreground text-center md:text-right max-w-xl">
              Fantasy Football Codex is not affiliated with the National Football League (NFL).
              All NFL team names, logos, and related marks are the property of the NFL and its teams.
              This service is intended for entertainment purposes only.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
