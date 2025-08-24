"use client"

import { useState, useEffect } from "react"
import { ArrowUp, ArrowDown, AlertTriangle, TrendingUp, Newspaper } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

// Mock data - in a real app, this would come from an API
const mockData = {
  risersFallers: {
    risers: 12,
    fallers: 8,
    trend: [2, 5, 3, 8, 6, 10, 8, 12, 8, 6, 7, 5]
  },
  injuries: {
    questionable: 5,
    out: 2,
    lastUpdated: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  },
  bettingValue: {
    score: 78,
    direction: 'up' as 'up' | 'down',
    change: 5
  },
  news: {
    headline: "Top RB's workload could increase in week 3",
    source: "NFL Insider",
    time: "2h ago"
  }
}

export function PeekTiles() {
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState<typeof mockData | null>(null)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData(mockData)
      setIsLoading(false)
    }, 800)
    
    return () => clearTimeout(timer)
  }, [])

  if (isLoading || !data) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-40 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {/* Risers & Fallers */}
      <Card className="relative overflow-hidden">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Risers & Fallers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between">
            <div>
              <div className="flex items-center text-2xl font-bold">
                <ArrowUp className="mr-1 h-5 w-5 text-green-500" />
                {data.risersFallers.risers}
                <ArrowDown className="ml-4 mr-1 h-5 w-5 text-red-500" />
                {data.risersFallers.fallers}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Last 24h</p>
            </div>
            <div className="h-12 w-20">
              <Sparkline data={data.risersFallers.trend} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Injury Watch */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Injury Watch</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center">
            <div className="mr-4 rounded-full bg-destructive/10 p-3">
              <AlertTriangle className="h-6 w-6 text-destructive" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {data.injuries.questionable + data.injuries.out} <span className="text-sm font-normal text-muted-foreground">total</span>
              </div>
              <div className="text-sm text-muted-foreground">
                {data.injuries.questionable} Q • {data.injuries.out} Out
              </div>
              <p className="text-xs text-muted-foreground mt-1">Updated {data.injuries.lastUpdated}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Betting Value */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Betting Value</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center">
            <div className="mr-4 rounded-full bg-primary/10 p-3">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div>
              <div className="text-2xl font-bold flex items-center">
                {data.bettingValue.score}/100
                {data.bettingValue.direction === 'up' ? (
                  <ArrowUp className="ml-2 h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDown className="ml-2 h-4 w-4 text-red-500" />
                )}
                <span className="ml-1 text-sm text-green-500">+{data.bettingValue.change}%</span>
              </div>
              <p className="text-sm text-muted-foreground">Value Score</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* News & Buzz */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">News & Buzz</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-start">
            <div className="mr-3 mt-1 rounded-full bg-secondary p-2">
              <Newspaper className="h-4 w-4" />
            </div>
            <div>
              <p className="line-clamp-2 text-sm font-medium">{data.news.headline}</p>
              <div className="mt-1 flex items-center text-xs text-muted-foreground">
                <span>{data.news.source}</span>
                <span className="mx-2">•</span>
                <span>{data.news.time}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Simple sparkline component for the trend visualization
function Sparkline({ data }: { data: number[] }) {
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1 // Avoid division by zero
  
  return (
    <div className="flex h-full w-full items-end gap-0.5">
      {data.map((value, i) => {
        const height = ((value - min) / range) * 100
        return (
          <div 
            key={i}
            className="w-1.5 rounded-t-full bg-primary/30"
            style={{ height: `${height}%` }}
            aria-hidden="true"
          />
        )
      })}
    </div>
  )
}
