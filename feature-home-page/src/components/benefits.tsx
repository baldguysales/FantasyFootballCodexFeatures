import { BarChart2, Activity, TrendingUp, Zap } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function Benefits() {
  const features = [
    {
      icon: BarChart2,
      title: "Unified Player View",
      description: "Cross-source stats, news, and analysis in one comprehensive dashboard.",
    },
    {
      icon: Activity,
      title: "Injury Watch",
      description: "Real-time injury reports with severity indicators and estimated return timelines.",
    },
    {
      title: "Betting Insights",
      icon: TrendingUp,
      description: "Odds, props, and value indicators to find the best betting opportunities.",
    },
    {
      title: "AI Summaries",
      icon: Zap,
      description: "Customizable AI-powered insights based on your preferred data sources and weights.",
    },
  ]

  return (
    <section id="features" className="py-16 md:py-24 lg:py-32 bg-muted/50">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything You Need to Dominate Your League
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Get the competitive edge with our comprehensive suite of fantasy football tools.
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <Card key={index} className="h-full transition-all hover:shadow-lg">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <feature.icon className="h-6 w-6" />
                </div>
                <CardTitle className="mt-4">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
