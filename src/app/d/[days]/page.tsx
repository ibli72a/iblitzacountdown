import type { Metadata } from 'next';
import Home from '../../page';
import { caption } from '../../countdown';
import { generateStaticParams, parseDays } from './params';

export { generateStaticParams };

export const dynamic = 'force-static';

// The day count is in the URL, so the preview a share renders is fixed by the
// link itself — not by whenever CI last rebuilt the site.
export async function generateMetadata({
  params,
}: {
  params: Promise<{ days: string }>;
}): Promise<Metadata> {
  const text = caption(parseDays((await params).days));
  return {
    description: text,
    openGraph: {
      title: 'Countdown to MYKONOS 2027',
      description: text,
      url: 'https://countdown.iblitza.com',
      siteName: 'IBLITZA',
      locale: 'en_US',
      type: 'website',
    },
    twitter: { card: 'summary_large_image', title: 'Countdown to MYKONOS 2027', description: text },
  };
}

// Same page as the root: the countdown itself is computed in the browser.
export default function SharedDay() {
  return <Home />;
}
