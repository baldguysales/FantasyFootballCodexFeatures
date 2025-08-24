import { Star, Quote } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const testimonials = [
  {
    quote: "The injury alerts alone have saved my season. I knew about key players being out before my league mates even caught wind.",
    author: "Alex T.",
    role: "3x League Champion",
    rating: 5
  },
  {
    quote: "I've tried every fantasy app out there. Codex is the first one that actually gives me an edge with its AI-powered insights.",
    author: "Jamie R.",
    role: "Fantasy Enthusiast",
    rating: 5
  },
  {
    quote: "The betting value scores have been a game-changer for my DFS lineups. I'm consistently cashing in more tournaments.",
    author: "Morgan K.",
    role: "DFS Player",
    rating: 5
  }
]

export function Testimonials() {
  return (
    <section className="py-16 md:py-24 bg-muted/50">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Trusted by Fantasy Football Enthusiasts
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join thousands of managers who are dominating their leagues with data-driven insights.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="h-full transition-all hover:shadow-lg">
              <CardContent className="p-6 flex flex-col h-full">
                <div className="mb-4 text-muted-foreground">
                  <Quote className="h-6 w-6 opacity-20" />
                </div>
                
                <p className="mb-6 flex-grow text-lg font-medium">"{testimonial.quote}"</p>
                
                <div className="mt-auto">
                  <div className="flex items-center justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star 
                        key={i} 
                        className={`h-4 w-4 ${i < testimonial.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30'}`} 
                      />
                    ))}
                  </div>
                  
                  <div className="text-center">
                    <p className="font-medium">{testimonial.author}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="mt-12 flex flex-wrap items-center justify-center gap-6 opacity-70">
          {['ESPN', 'Yahoo', 'Sleeper', 'NFL', 'DraftKings', 'FanDuel'].map((logo, i) => (
            <div key={i} className="text-lg font-medium text-muted-foreground">
              {logo}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
