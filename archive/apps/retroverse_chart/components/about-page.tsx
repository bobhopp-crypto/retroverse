'use client'

import { ArrowLeft, Music, BarChart3, Users, Calendar } from 'lucide-react'

interface AboutPageProps {
  onBack: () => void
}

export function AboutPage({ onBack }: AboutPageProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="p-2 -ml-2 rounded-xl hover:bg-muted active:scale-95 transition-all"
          aria-label="Go back"
        >
          <ArrowLeft className="w-6 h-6 text-foreground" />
        </button>
        <h2 className="text-xl font-bold text-foreground">About</h2>
      </div>

      <div className="space-y-4">
        {/* App Info Card */}
        <div className="bg-card rounded-2xl p-5 shadow-md border border-border/50">
          <h1 className="text-2xl font-black text-card-foreground mb-2 text-balance">
            RetroVerse Charts
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Explore decades of music history through the Billboard Hot 100. 
            Browse songs, discover artists, and relive the hits that defined generations.
          </p>
        </div>

        {/* Features */}
        <div className="bg-card rounded-2xl p-5 shadow-md border border-border/50">
          <h3 className="font-bold text-card-foreground mb-4 text-sm uppercase tracking-wide">
            Features
          </h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-retro-teal/20 flex items-center justify-center flex-shrink-0">
                <Music className="w-5 h-5 text-retro-teal" />
              </div>
              <div>
                <p className="font-semibold text-sm text-foreground">Browse Songs</p>
                <p className="text-xs text-muted-foreground">
                  Search and filter through thousands of chart hits
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-retro-coral/20 flex items-center justify-center flex-shrink-0">
                <Calendar className="w-5 h-5 text-retro-coral" />
              </div>
              <div>
                <p className="font-semibold text-sm text-foreground">Weekly Charts</p>
                <p className="text-xs text-muted-foreground">
                  View any week from 1958 to present like a classic Billboard magazine
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-retro-mustard/20 flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5 text-retro-mustard" />
              </div>
              <div>
                <p className="font-semibold text-sm text-foreground">Artist Profiles</p>
                <p className="text-xs text-muted-foreground">
                  Explore artist stats, decade breakdowns, and chart history
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-retro-mint/20 flex items-center justify-center flex-shrink-0">
                <BarChart3 className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-sm text-foreground">Chart Records</p>
                <p className="text-xs text-muted-foreground">
                  Discover all-time records and chart statistics
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Data Info */}
        <div className="bg-card rounded-2xl p-5 shadow-md border border-border/50">
          <h3 className="font-bold text-card-foreground mb-3 text-sm uppercase tracking-wide">
            Data
          </h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Chart data spans from 1958 to 2024, covering the entire history of 
            the Billboard Hot 100. All chart positions, peak rankings, and 
            weekly runs are based on historical Billboard data.
          </p>
        </div>

        {/* Credits */}
        <div className="bg-muted/30 rounded-2xl p-4 text-center">
          <p className="text-xs text-muted-foreground">
            Built with the RetroVerse pastel design system
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Version 1.0
          </p>
        </div>
      </div>
    </div>
  )
}
