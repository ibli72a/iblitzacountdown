import { card } from '../../og-card';
import { generateStaticParams, parseDays } from './params';

export { generateStaticParams };
export { alt, size, contentType } from '../../og-card';

export const dynamic = 'force-static';

export default async function Image({ params }: { params: Promise<{ days: string }> }) {
  return card(parseDays((await params).days));
}
