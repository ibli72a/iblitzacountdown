import { split } from '../../countdown';

// Share links went out from this date, with the day count in the URL. A link stays in
// chats long after the count has moved on, so every count since then keeps its page:
// building only 0 .. today's count made each shared link 404 a day or so later.
const FIRST_SHARE = Date.parse('2026-09-11T00:00:00Z');

// One page per count a share link can carry, 0 .. the count on FIRST_SHARE.
export function generateStaticParams() {
  const max = Math.max(split(FIRST_SHARE).days, split().days);
  return Array.from({ length: max + 1 }, (_, i) => ({ days: String(i) }));
}

// A path segment that isn't a plain count would 404 at export time anyway; this
// keeps the parse in one place.
export function parseDays(value: string): number {
  const n = Number(value);
  return Number.isInteger(n) && n >= 0 ? n : 0;
}
