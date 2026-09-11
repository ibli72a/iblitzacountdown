export const TARGET = new Date('2027-07-08T06:00:00+02:00');

// Long haul: a new line every 30 days, indexed by Math.floor(days / 30).
export const BY_30: (string | null)[] = [
  null,
  'The next stretch is the last one. Start the playlist.',
  'Two months of pretending to be patient.',
  'Villa, boat, table. In that order.',
  'Book the flights before the flights book you.',
  'Close enough to talk about it seriously.',
  'Halfway is closer than it was.',
  'Somebody should start a spreadsheet.',
  'The number is going down. Slowly, but down.',
  'Long enough that nobody has booked anything.',
  'Still measured in seasons, not weeks.',
  'Too early to pack. Not too early to count.',
];

// Last 30 days: the day matters more than the month.
export const FINAL_30: [number, string][] = [
  [21, 'The suitcase is out and it is watching you.'],
  [14, 'Two weeks. Lay it all on the bed, decide nothing.'],
  [7, 'One week. Six shirts in, four come back out.'],
  [3, 'Charger, sunglasses, one shirt too many. Pack.'],
  [1, 'Zipped. Tomorrow, six in the morning.'],
  [0, 'Today. 06:00. Go.'],
];

export function milestone(days: number): string {
  if (days <= 30) {
    const hit = FINAL_30.find(([t]) => days >= t);
    return (hit ?? FINAL_30[FINAL_30.length - 1])[1];
  }
  const i = Math.min(Math.floor(days / 30), BY_30.length - 1);
  return BY_30[i] ?? (BY_30[BY_30.length - 1] as string);
}

// The share caption: count on the first line, milestone on the second.
// On the day itself the two collapse into the single milestone line.
export function caption(days: number): string {
  const line = milestone(days);
  if (days === 0) return line;
  return `${days} ${days === 1 ? 'day' : 'days'} to go\n${line}`;
}

export function split(now: number = Date.now()) {
  const diff = Math.max(TARGET.getTime() - now, 0);
  return {
    days: Math.floor(diff / 86400000),
    hours: Math.floor((diff / 3600000) % 24),
    minutes: Math.floor((diff / 60000) % 60),
    seconds: Math.floor((diff / 1000) % 60),
  };
}

export const pad = (n: number) => String(n).padStart(2, '0');
