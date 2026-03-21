import type { Metadata } from 'next'
import Link from 'next/link'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || ''

export const metadata: Metadata = {
  title: 'RetroVerse Charts',
  description: 'Explore historical music chart data from the Billboard Hot 100',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: `${basePath}/icon-light-32x32.png`,
        media: '(prefers-color-scheme: light)',
      },
      {
        url: `${basePath}/icon-dark-32x32.png`,
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: `${basePath}/icon.svg`,
        type: 'image/svg+xml',
      },
    ],
    apple: `${basePath}/apple-icon.png`,
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <nav className="border-b border-border bg-card px-4 py-3">
          <div className="max-w-4xl mx-auto flex gap-4 text-sm font-medium">
            <Link href="/" className="text-foreground hover:text-primary">
              Charts
            </Link>
            <span className="text-muted-foreground">|</span>
            <Link href="/magazine" className="text-foreground hover:text-primary">
              Magazine
            </Link>
          </div>
        </nav>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
