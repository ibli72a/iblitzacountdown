import './globals.css';
import type { Metadata, Viewport } from 'next';
import localFont from 'next/font/local';
import { caption, split } from './countdown';

// Fonts ship in the repo (latin subset, from Fontsource) rather than via next/font/google:
// fetching them from Google at build time made the scheduled deploys fail intermittently.
const cinzel = localFont({
  src: [
    { path: './fonts/cinzel-latin-400-normal.woff2', weight: '400', style: 'normal' },
    { path: './fonts/cinzel-latin-500-normal.woff2', weight: '500', style: 'normal' },
    { path: './fonts/cinzel-latin-600-normal.woff2', weight: '600', style: 'normal' },
    { path: './fonts/cinzel-latin-700-normal.woff2', weight: '700', style: 'normal' },
  ],
  variable: '--font-cinzel',
  display: 'swap',
  fallback: ['serif'],
});
const archivo = localFont({
  src: [
    { path: './fonts/archivo-latin-400-normal.woff2', weight: '400', style: 'normal' },
    { path: './fonts/archivo-latin-500-normal.woff2', weight: '500', style: 'normal' },
  ],
  variable: '--font-archivo',
  display: 'swap',
  fallback: ['system-ui', 'sans-serif'],
});
const mono = localFont({
  src: [
    { path: './fonts/jetbrains-mono-latin-400-normal.woff2', weight: '400', style: 'normal' },
    { path: './fonts/jetbrains-mono-latin-500-normal.woff2', weight: '500', style: 'normal' },
  ],
  variable: '--font-mono',
  display: 'swap',
  fallback: ['monospace'],
});

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
