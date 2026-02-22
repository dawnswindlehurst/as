# Capivara Bet - Next.js + FastAPI Frontend

Modern frontend built with Next.js 14, TypeScript, and Tailwind CSS for the Capivara Bet esports betting system.

## 🎨 Features

- **Dark Theme** - Professional dark mode with slate-900 background
- **Responsive Design** - Mobile-first design with Tailwind CSS
- **Live Updates** - Real-time game updates with auto-refresh
- **Player Props Analysis** - Comprehensive player statistics and prop betting analysis
- **Game Cards** - Beautiful game cards with live badges and scores
- **TypeScript** - Full type safety across the application

## 📁 Structure

```
frontend/
├── app/                    # Next.js 14 app directory
│   ├── layout.tsx         # Root layout with navbar
│   ├── page.tsx           # Dashboard/home page
│   ├── games/             # Games listing page
│   ├── props/             # Player props analysis
│   └── players/[id]/      # Player detail pages
├── components/
│   ├── ui/                # Base UI components
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Button.tsx
│   │   ├── Table.tsx
│   │   └── Navbar.tsx
│   ├── GameCard.tsx       # Game display card
│   ├── PlayerProps.tsx    # Props table
│   ├── LiveBadge.tsx      # Live indicator
│   └── StatsChart.tsx     # Statistics visualization
├── lib/
│   ├── api.ts            # API client functions
│   └── utils.ts          # Utility functions
└── styles/
    └── globals.css        # Global styles with Tailwind

## 🚀 Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## 🎨 Design System

### Colors

- **Background**: `#0f172a` (slate-900)
- **Cards**: `#1e293b` (slate-800)
- **Primary**: `#3b82f6` (blue-500)
- **Success**: `#22c55e` (green-500)
- **Danger**: `#ef4444` (red-500)

### Components

All UI components follow a consistent dark theme design with:
- Border colors: `slate-700`
- Text colors: `slate-50` (primary), `slate-400` (secondary)
- Hover states with smooth transitions

## 📡 API Integration

The frontend connects to the FastAPI backend at the URL specified in `NEXT_PUBLIC_API_URL`.

Available endpoints:
- `GET /api/health` - Health check
- `GET /api/games` - List games
- `GET /api/games/live` - Live games
- `GET /api/players/search` - Search players
- `GET /api/props/{player_id}` - Player props

## 🐳 Docker

```bash
# Build Docker image
docker build -t capivara-bet-frontend .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 capivara-bet-frontend
```

## 📝 License

This project is for educational purposes.
