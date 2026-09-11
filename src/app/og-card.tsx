import { ImageResponse } from 'next/og';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { milestone } from './countdown';

export const alt = 'Countdown to MYKONOS 2027';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

const STONE = '#f5f1ea';
const NIGHT = '#00142f';
// satori has no oklch() support — this is oklch(0.78 0.12 220) as sRGB hex
const ACCENT = '#4ac9ec';

// One card is rendered per remaining day, so the seal and the fonts are fetched
// once per build and reused — not once per card.
let sealOnce: Promise<string> | undefined;
function seal() {
  sealOnce ??= readFile(join(process.cwd(), 'public', 'seal.png')).then(
    (buf) => `data:image/png;base64,${buf.toString('base64')}`
  );
  return sealOnce;
}

async function fetchCinzel(weight: number) {
  const css = await fetch(
    `https://fonts.googleapis.com/css2?family=Cinzel:wght@${weight}`,
    { headers: { 'User-Agent': 'Mozilla/5.0' } }
  ).then((r) => r.text());
  const url = css.match(/src: url\((.+?)\) format/)?.[1];
  if (!url) throw new Error('Cinzel not found');
  return fetch(url).then((r) => r.arrayBuffer());
}

async function buildFonts() {
  try {
    const [bold, semi] = await Promise.all([fetchCinzel(700), fetchCinzel(600)]);
    return [
      { name: 'Cinzel', data: bold, weight: 700 as const, style: 'normal' as const },
      { name: 'Cinzel', data: semi, weight: 600 as const, style: 'normal' as const },
    ];
  } catch {
    return undefined; // fall back to the built-in face rather than failing the build
  }
}

let fontsOnce: ReturnType<typeof buildFonts> | undefined;
function fonts() {
  fontsOnce ??= buildFonts();
  return fontsOnce;
}

export async function card(days: number) {
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', gap: 48, padding: '58px 66px', background: NIGHT, color: STONE }}>
        <div style={{ display: 'flex', position: 'relative', width: 344, height: 344, flexShrink: 0 }}>
          <div style={{ position: 'absolute', top: 5, left: 5, width: 334, height: 334, borderRadius: 999, background: STONE }} />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={await seal()} alt="" width={344} height={344} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 18, flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontFamily: 'Cinzel', fontWeight: 700, fontSize: 27, letterSpacing: 6 }}>MYKONOS 2027</span>
            <div style={{ display: 'flex', height: 1, flex: 1, background: 'rgba(245,241,234,0.3)' }} />
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: 22 }}>
            <span style={{ fontFamily: 'Cinzel', fontWeight: 700, fontSize: 192, lineHeight: 0.8, letterSpacing: -8 }}>{days}</span>
            <span style={{ fontFamily: 'Cinzel', fontWeight: 600, fontSize: 34, letterSpacing: 7, color: ACCENT }}>DAYS</span>
          </div>

          <div style={{ display: 'flex', height: 1, background: 'rgba(245,241,234,0.22)' }} />

          <div style={{ display: 'flex', fontSize: 20, letterSpacing: 3, textTransform: 'uppercase', color: STONE }}>
            {milestone(days)}
          </div>

          <div style={{ display: 'flex', fontSize: 17, letterSpacing: 4, color: 'rgba(245,241,234,0.74)' }}>
            8 JULY 2027 · 06:00
          </div>
        </div>

        <div style={{ position: 'absolute', bottom: 28, right: 70, display: 'flex', fontSize: 15, letterSpacing: 3, color: 'rgba(245,241,234,0.5)' }}>
          COUNTDOWN.IBLITZA.COM
        </div>
      </div>
    ),
    { ...size, fonts: await fonts() }
  );
}
