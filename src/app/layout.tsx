import './globals.css';
import type { Metadata, Viewport } from 'next';
import { Cinzel, Archivo, JetBrains_Mono } from 'next/font/google';
import { split } from './countdown';

const cinzel = Cinzel({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-cinzel' });
const archivo = Archivo({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-archivo' });
const mono = JetBrains_Mono({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-mono' });

// Baked at build; the daily rebuild keeps the shared-link caption on today's count.
const days = split().days;
const caption = days === 0 ? 'Today. 06:00. Go.' : `${days} ${days === 1 ? 'day' : 'days'} to go`;

export const metadata: Metadata = {
  metadataBase: new URL('https://countdown.iblitza.com'),
  title: 'Mykonos 2027 — IBLITZA Countdown',
  description: caption,
  openGraph: {
    title: 'Countdown to MYKONOS 2027',
    description: caption,
    url: 'https://countdown.iblitza.com',
    siteName: 'IBLITZA',
    locale: 'en_US',
    type: 'website',
  },
  twitter: { card: 'summary_large_image', title: 'Countdown to MYKONOS 2027', description: caption },
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon-32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [{ url: '/favicon-180.png', sizes: '180x180' }],
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  viewportFit: 'cover',
  themeColor: '#f5f1ea',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${cinzel.variable} ${archivo.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
