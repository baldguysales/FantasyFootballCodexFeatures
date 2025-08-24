// Mock data for the home page components
export const mockPlayers = [
  {
    id: 1,
    name: "Patrick Mahomes",
    position: "QB",
    team: "KC",
    change: 5.2,
    trend: [65, 70, 68, 72, 75, 80, 78, 82, 85, 90, 92, 95],
  },
  {
    id: 2,
    name: "Christian McCaffrey",
    position: "RB",
    team: "SF",
    change: -2.1,
    trend: [95, 94, 96, 93, 92, 90, 91, 89, 90, 88, 90, 92],
  },
  {
    id: 3,
    name: "Justin Jefferson",
    position: "WR",
    team: "MIN",
    change: 3.8,
    trend: [85, 88, 86, 89, 91, 90, 92, 94, 95, 96, 97, 98],
  },
];

export const mockInjuries = [
  {
    id: 101,
    name: "Cooper Kupp",
    position: "WR",
    team: "LAR",
    status: "Questionable",
    injury: "Hamstring",
    practiceStatus: "Limited",
  },
  {
    id: 102,
    name: "Saquon Barkley",
    position: "RB",
    team: "NYG",
    status: "Out",
    injury: "Ankle",
    practiceStatus: "Did Not Practice",
  },
];

export const mockNews = [
  {
    id: 201,
    title: "Top RB's workload could increase in week 3",
    source: "NFL Insider",
    timestamp: "2h ago",
    category: "News",
  },
  {
    id: 202,
    title: "Injury Update: WR expected to play through minor injury",
    source: "Team Reporter",
    timestamp: "5h ago",
    category: "Injury",
  },
];

export const mockBettingValues = [
  {
    id: 301,
    name: "Travis Kelce",
    position: "TE",
    team: "KC",
    valueScore: 87,
    trend: "up",
    change: 3.2,
  },
  {
    id: 302,
    name: "Ja'Marr Chase",
    position: "WR",
    team: "CIN",
    valueScore: 92,
    trend: "up",
    change: 5.7,
  },
];

export const mockTestimonials = [
  {
    id: 1,
    quote:
      "The injury alerts alone have saved my season. I knew about key players being out before my league mates even caught wind.",
    author: "Alex T.",
    role: "3x League Champion",
    rating: 5,
  },
  {
    id: 2,
    quote:
      "I've tried every fantasy app out there. Codex is the first one that actually gives me an edge with its AI-powered insights.",
    author: "Jamie R.",
    role: "Fantasy Enthusiast",
    rating: 5,
  },
  {
    id: 3,
    quote:
      "The betting value scores have been a game-changer for my DFS lineups. I'm consistently cashing in more tournaments.",
    author: "Morgan K.",
    role: "DFS Player",
    rating: 5,
  },
];

export const mockFAQs = [
  {
    question: "Which data sources are used?",
    answer:
      "We aggregate data from multiple trusted sources including ESPN, NFL Data, MySportsFeeds, The Odds API, and curated social media feeds to provide comprehensive player insights.",
  },
  {
    question: "How fresh is the data?",
    answer:
      "Our data is updated in real-time with the following cadence: player stats (live during games, every 5-15 minutes otherwise), injury reports (immediate updates), betting odds (every 1-5 minutes), and news/social (every 15-30 minutes).",
  },
  {
    question: "Can I customize AI weights?",
    answer:
      "Yes! You can adjust the importance of different factors in your AI summaries. For example, you might weight Injuries at 50%, Social Buzz at 30%, and Betting Insights at 20%, or create your own custom weighting scheme.",
  },
  {
    question: "Do I need to link a league?",
    answer:
      "No, league linking is optional. You can manually select players to track if you prefer not to connect your fantasy platform.",
  },
  {
    question: "Is there a mobile app?",
    answer:
      "Our web app is fully responsive and works great on mobile browsers. We're currently developing native mobile apps for iOS and Android, coming soon!",
  },
  {
    question: "What's included in the free tier?",
    answer:
      "The free tier includes basic player stats, injury reports, and limited access to betting insights. Premium features like advanced analytics, custom alerts, and full betting value scores require a subscription.",
  },
];
