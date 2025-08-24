import { CheckCircle, UserPlus, User, Sliders } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function HowItWorks() {
  const steps = [
    {
      icon: UserPlus,
      title: "Connect or Create",
      description: "Sign in and link your fantasy rosters or start with a free account to track players manually.",
    },
    {
      icon: User,
      title: "Select Players",
      description: "Choose which players to track. We'll aggregate all the data you need in one place.",
    },
    {
      icon: Sliders,
      title: "Tune Your Weights",
      description: "Customize how much weight to give to injuries, social buzz, and betting insights in your AI summaries.",
    },
  ]

  return (
    <section id="how-it-works" className="py-16 md:py-24 lg:py-32">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Get started in minutes and transform how you manage your fantasy team.
          </p>
        </div>

        <div className="mt-16">
          <div className="relative">
            {/* Progress line */}
            <div className="absolute left-1/2 top-0 hidden h-full w-1 -translate-x-1/2 bg-primary/20 md:block" />
            
            <div className="space-y-12 md:space-y-16">
              {steps.map((step, index) => (
                <div 
                  key={index}
                  className="relative flex flex-col items-center md:flex-row md:justify-between md:even:flex-row-reverse"
                >
                  {/* Left side - for even steps on desktop */}
                  <div className="md:w-5/12 md:px-6">
                    {index % 2 === 0 && (
                      <StepCard 
                        icon={step.icon}
                        title={step.title}
                        description={step.description}
                        step={index + 1}
                      />
                    )}
                  </div>
                  
                  {/* Center dot */}
                  <div className="my-4 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-4 border-background bg-primary text-primary-foreground z-10 md:my-0">
                    <CheckCircle className="h-5 w-5" />
                  </div>
                  
                  {/* Right side - for odd steps on desktop */}
                  <div className="md:w-5/12 md:px-6">
                    {index % 2 !== 0 && (
                      <StepCard 
                        icon={step.icon}
                        title={step.title}
                        description={step.description}
                        step={index + 1}
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function StepCard({ icon: Icon, title, description, step }: { 
  icon: React.ComponentType<{ className?: string }>,
  title: string,
  description: string,
  step: number
}) {
  return (
    <Card className="h-full transition-all hover:shadow-md">
      <CardHeader>
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <span className="text-sm font-medium text-muted-foreground">Step {step}</span>
            <CardTitle className="text-xl">{title}</CardTitle>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-base">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  )
}
