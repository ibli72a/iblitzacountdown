import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'IBLITZA Countdown',
  description: 'Countdown to IBLITZA 2026',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    viewportFit: 'cover',
  },
  themeColor: '#000000',
  openGraph: {
    title: 'IBLITZA Countdown',
    description: 'Countdown to IBLITZA 2026',
    url: 'https://countdown.iblitza.com',
    siteName: 'IBLITZA',
    images: [
      {
        url: '/banner.png',
        width: 3280,
        height: 1416,
        alt: 'IBLITZA Event Banner',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IBLITZA Countdown',
    description: 'Countdown to IBLITZA 2026',
    images: ['/banner.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
} 