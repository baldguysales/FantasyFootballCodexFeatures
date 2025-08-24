"use client"

import * as React from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

const faqs = [
  {
    question: "Which data sources are used?",
    answer: "We aggregate data from multiple trusted sources including ESPN, NFL Data, MySportsFeeds, The Odds API, and curated social media feeds to provide comprehensive player insights."
  },
  {
    question: "How fresh is the data?",
    answer: "Our data is updated in real-time with the following cadence: player stats (live during games, every 5-15 minutes otherwise), injury reports (immediate updates), betting odds (every 1-5 minutes), and news/social (every 15-30 minutes)."
  },
  {
    question: "Can I customize AI weights?",
    answer: "Yes! You can adjust the importance of different factors in your AI summaries. For example, you might weight Injuries at 50%, Social Buzz at 30%, and Betting Insights at 20%, or create your own custom weighting scheme."
  },
  {
    question: "Do I need to link a league?",
    answer: "No, league linking is optional. You can manually select players to track if you prefer not to connect your fantasy platform."
  },
  {
    question: "Is there a mobile app?",
    answer: "Our web app is fully responsive and works great on mobile browsers. We're currently developing native mobile apps for iOS and Android, coming soon!"
  },
  {
    question: "What's included in the free tier?",
    answer: "The free tier includes basic player stats, injury reports, and limited access to betting insights. Premium features like advanced analytics, custom alerts, and full betting value scores require a subscription."
  }
]

export function FAQ() {
  const [openIndex, setOpenIndex] = React.useState<number | null>(0)

  const toggleAccordion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section id="faq" className="py-16 md:py-24">
      <div className="container">
        <div className="mx-auto max-w-3xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Frequently Asked Questions
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to know about Fantasy Football Codex.
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="border rounded-lg overflow-hidden">
                <button
                  className={cn(
                    "flex w-full items-center justify-between p-6 text-left",
                    "hover:bg-muted/50 transition-colors",
                    "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  )}
                  onClick={() => toggleAccordion(index)}
                  aria-expanded={openIndex === index}
                  aria-controls={`faq-${index}`}
                >
                  <span className="font-medium">{faq.question}</span>
                  <ChevronDown 
                    className={cn(
                      "h-5 w-5 text-muted-foreground transition-transform",
                      openIndex === index && "rotate-180"
                    )} 
                  />
                </button>
                
                <div 
                  id={`faq-${index}`}
                  className={cn(
                    "px-6 overflow-hidden transition-all duration-300 ease-in-out",
                    openIndex === index ? "max-h-96 pb-6" : "max-h-0"
                  )}
                  aria-hidden={openIndex !== index}
                >
                  <p className="text-muted-foreground">
                    {faq.answer}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
