import { card } from './og-card';
import { split } from './countdown';

export const dynamic = 'force-static';
export { alt, size, contentType } from './og-card';

// The bare domain has no day in its URL, so this card is only as fresh as the
// last build. Shares from the site use /d/<days>, which cannot go stale.
export default function Image() {
  return card(split().days);
}
