import './globals.css';
import type { Metadata, Viewport } from 'next';
import { Cinzel, Archivo, JetBrains_Mono } from 'next/font/google';
import { caption, split } from './countdown';

const cinzel = Cinzel({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-cinzel' });
const archivo = Archivo({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-archivo' });
const mono = JetBrains_Mono({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-mono' });

// Only the bare domain falls back to this build-time caption; /d/<days> overrides it
// with the count from the URL, which is what the site's own share button links to.
const line = caption(split().days);

export const metadata: Metadata = {
  metadataBase: new URL('https://countdown.iblitza.com'),
  title: 'Mykonos 2027 — IBLITZA Countdown',
  description: line,
  openGraph: {
    title: 'Countdown to MYKONOS 2027',
    description: line,
    url: 'https://countdown.iblitza.com',
    siteName: 'IBLITZA',
    locale: 'en_US',
    type: 'website',
  },
  twitter: { card: 'summary_large_image', title: 'Countdown to MYKONOS 2027', description: line },
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
