import { split } from '../../countdown';

// One page per possible remaining day, 0 .. today's count. The client only ever
// links to its own live count, which can never exceed the count at build time,
// so every link the site hands out is guaranteed to have been generated.
// The list shrinks by one a day.
export function generateStaticParams() {
  const max = split().days;
  return Array.from({ length: max + 1 }, (_, i) => ({ days: String(i) }));
}

// A path segment that isn't a plain count would 404 at export time anyway; this
// keeps the parse in one place.
export function parseDays(value: string): number {
  const n = Number(value);
  return Number.isInteger(n) && n >= 0 ? n : 0;
}
