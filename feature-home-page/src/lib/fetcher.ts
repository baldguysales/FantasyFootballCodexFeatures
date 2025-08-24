import { mockPlayers, mockInjuries, mockNews, mockBettingValues, mockTestimonials, mockFAQs } from "@/data/mocks/home"

// Types for our data
type Player = {
  id: number
  name: string
  position: string
  team: string
  change: number
  trend: number[]
}

type Injury = {
  id: number
  name: string
  position: string
  team: string
  status: string
  injury: string
  practiceStatus: string
}

type NewsItem = {
  id: number
  title: string
  source: string
  timestamp: string
  category: string
}

type BettingValue = {
  id: number
  name: string
  position: string
  team: string
  valueScore: number
  trend: string
  change: number
}

type Testimonial = {
  id: number
  quote: string
  author: string
  role: string
  rating: number
}

type FAQ = {
  question: string
  answer: string
}

// Configuration type
type FetcherConfig = {
  useMock: boolean
}

const defaultConfig: FetcherConfig = {
  useMock: process.env.NODE_ENV === 'development',
}

// Helper to simulate network delay
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Mock API client that can be replaced with real API calls
export const fetcher = {
  // Get player data
  async getPlayers(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(500) // Simulate network delay
      return {
        data: mockPlayers,
        error: null,
      }
    }
    
    // In a real app, this would be an actual API call
    // return fetch('/api/players').then(res => res.json())
    return {
      data: mockPlayers,
      error: null,
    }
  },
  
  // Get injury data
  async getInjuries(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(500)
      return {
        data: mockInjuries,
        error: null,
      }
    }
    
    // Real API call would go here
    return {
      data: mockInjuries,
      error: null,
    }
  },
  
  // Get news data
  async getNews(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(500)
      return {
        data: mockNews,
        error: null,
      }
    }
    
    // Real API call would go here
    return {
      data: mockNews,
      error: null,
    }
  },
  
  // Get betting values
  async getBettingValues(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(500)
      return {
        data: mockBettingValues,
        error: null,
      }
    }
    
    // Real API call would go here
    return {
      data: mockBettingValues,
      error: null,
    }
  },
  
  // Get testimonials
  async getTestimonials(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(500)
      return {
        data: mockTestimonials,
        error: null,
      }
    }
    
    // Real API call would go here
    return {
      data: mockTestimonials,
      error: null,
    }
  },
  
  // Get FAQs
  async getFAQs(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(300)
      return {
        data: mockFAQs,
        error: null,
      }
    }
    
    // Real API call would go here
    return {
      data: mockFAQs,
      error: null,
    }
  },
  
  // Get all data for the home page
  async getHomePageData(config: Partial<FetcherConfig> = {}) {
    const { useMock } = { ...defaultConfig, ...config }
    
    if (useMock) {
      await sleep(800)
      return {
        players: mockPlayers,
        injuries: mockInjuries,
        news: mockNews,
        bettingValues: mockBettingValues,
        testimonials: mockTestimonials,
        faqs: mockFAQs,
        error: null,
      }
    }
    
    // In a real app, this would be parallel API calls
    // const [players, injuries, news, bettingValues, testimonials, faqs] = await Promise.all([
    //   this.getPlayers({ useMock }),
    //   this.getInjuries({ useMock }),
    //   this.getNews({ useMock }),
    //   this.getBettingValues({ useMock }),
    //   this.getTestimonials({ useMock }),
    //   this.getFAQs({ useMock }),
    // ])
    
    return {
      players: mockPlayers,
      injuries: mockInjuries,
      news: mockNews,
      bettingValues: mockBettingValues,
      testimonials: mockTestimonials,
      faqs: mockFAQs,
      error: null,
    }
  },
}

export type { Player, Injury, NewsItem, BettingValue, Testimonial, FAQ }
