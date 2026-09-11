'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { milestone, pad, split } from './countdown';

const LAT = 37.4467;
const LON = 25.3289;
const BEAT_MS = 60000 / 123;

type Island = { temp: number | null; sky: string; key: string; sunrise: string | null; sunset: string | null };

function skyWord(code: number) {
  if (code === 0) return 'CLEAR';
  if (code <= 2) return 'SUN';
  if (code === 3) return 'CLOUD';
  if (code <= 48) return 'HAZE';
  if (code <= 67) return 'RAIN';
  if (code <= 77) return 'SNOW';
  if (code <= 82) return 'SHOWERS';
  if (code <= 86) return 'SNOW';
  return 'STORM';
}

function skyKey(code: number) {
  if (code <= 1) return 'clear';
  if (code === 2) return 'part';
  if (code === 3) return 'cloud';
  if (code <= 48) return 'haze';
  if (code <= 67) return 'rain';
  if (code <= 77) return 'snow';
  if (code <= 82) return 'rain';
  if (code <= 86) return 'snow';
  return 'storm';
}

function islandMinutes() {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Athens', hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(new Date());
  const get = (t: string) => Number(parts.find((p) => p.type === t)!.value);
  return get('hour') * 60 + get('minute');
}

const toMin = (hhmm: string | null) => {
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
};

function WeatherIcon({ name }: { name: string }) {
  const common = {
    width: 14, height: 14, viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', strokeWidth: 1.5, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const,
  };
  const cloud = <path d="M6.2 14.6h11a3.7 3.7 0 0 0 0-7.4A5.4 5.4 0 0 0 6.8 8.5a3.1 3.1 0 0 0-0.6 6.1z" />;
  switch (name) {
    case 'moon':  return <svg {...common}><path d="M20 14.6A8.6 8.6 0 0 1 9.4 4 8.6 8.6 0 1 0 20 14.6z" /></svg>;
    case 'part':  return <svg {...common}><circle cx="9" cy="7.5" r="3" /><path d="M6.5 20h10.6a3.6 3.6 0 0 0 0-7.2A5.2 5.2 0 0 0 7 14a3 3 0 0 0-0.5 6z" /></svg>;
    case 'cloud': return <svg {...common}><path d="M6.2 18.8h11a3.7 3.7 0 0 0 0-7.4A5.4 5.4 0 0 0 6.8 12.7a3.1 3.1 0 0 0-0.6 6.1z" /></svg>;
    case 'haze':  return <svg {...common}><path d="M3 8.5h18M5 12.5h14M7 16.5h10" /></svg>;
    case 'rain':  return <svg {...common}>{cloud}<path d="M9.5 17.6v2.6M13 17.6v2.6M16.5 17.6v2.6" /></svg>;
    case 'snow':  return <svg {...common}>{cloud}<path d="M9.5 18.6h0.01M13 18.6h0.01M16.5 18.6h0.01" /></svg>;
    case 'storm': return <svg {...common}>{cloud}<path d="M13.2 16.4l-2.7 4.2h3.1l-1.6 3" /></svg>;
    default:      return <svg {...common}><circle cx="12" cy="12" r="4" /><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4" /></svg>;
  }
}

export default function Home() {
  const [t, setT] = useState(() => split());
  // React leaves suppressHydrationWarning text as baked at build, and later ticks only
  // rewrite nodes whose value changed — so the days/hours figures can stay hours stale.
  // Flipping this key remounts the readout and rewrites every node from the client clock.
  const [hydrated, setHydrated] = useState(false);
  const [island, setIsland] = useState<Island>({ temp: null, sky: '···', key: 'clear', sunrise: null, sunset: null });
  const [night, setNight] = useState(false);
  const [playing, setPlaying] = useState(false);

  const audio = useRef<HTMLAudioElement | null>(null);
  const seal = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setHydrated(true);
    const id = setInterval(() => setT(split()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,weather_code&daily=sunrise,sunset&timezone=Europe%2FAthens`
        );
        const j = await r.json();
        setIsland({
          temp: Math.round(j.current.temperature_2m),
          sky: skyWord(j.current.weather_code),
          key: skyKey(j.current.weather_code),
          sunrise: j.daily.sunrise[0].slice(11, 16),
          sunset: j.daily.sunset[0].slice(11, 16),
        });
      } catch {
        /* offline: the clock-based fallback below still picks a theme */
      }
    };
    load();
    const id = setInterval(load, 900000);
    return () => clearInterval(id);
  }, []);

  // Theme follows the sun over Mykonos, so everyone sees the same one.
  useEffect(() => {
    const now = islandMinutes();
    const rise = toMin(island.sunrise);
    const set = toMin(island.sunset);
    const isNight = rise === null || set === null ? now < 390 || now >= 1250 : now < rise || now > set;
    setNight(isNight);
    document.documentElement.dataset.theme = isNight ? 'night' : 'day';
  }, [island, t.minutes]);

  useEffect(() => {
    if (!playing) return;
    const el = seal.current;
    const kick = () => {
      if (!el) return;
      el.style.transition = 'none';
      el.style.transform = 'scale(1.055)';
      setTimeout(() => {
        if (!el) return;
        el.style.transition = `transform ${Math.round(BEAT_MS * 0.62)}ms cubic-bezier(0.16,1,0.3,1)`;
        el.style.transform = 'scale(1)';
      }, 55);
    };
    kick();
    const id = setInterval(kick, BEAT_MS);
    return () => {
      clearInterval(id);
      if (el) { el.style.transform = 'scale(1)'; }
    };
  }, [playing]);

  const toggle = useCallback(() => {
    const el = audio.current;
    if (!el) return;
    if (playing) { el.pause(); setPlaying(false); }
    else { void el.play(); setPlaying(true); }
  }, [playing]);

  const line = milestone(t.days);
  // The day count is the path, so the preview WhatsApp scrapes is baked into the
  // link itself: it can't drift from the live number while a rebuild is pending,
  // and it doubles as the cache key, which changes exactly when the count does.
  // Bare link only: WhatsApp still renders the preview card, and the card itself is the tap target.
  const share = `https://wa.me/?text=${encodeURIComponent(
    `https://countdown.iblitza.com/d/${t.days}/`
  )}`;
  const icon = island.key === 'clear' ? (night ? 'moon' : 'sun') : island.key;
  const ringStyle = (i: number) => ({
    animationName: playing ? 'sonar' : 'none',
    animationDuration: `${((BEAT_MS * 3) / 1000).toFixed(3)}s`,
    animationTimingFunction: 'linear',
    animationIterationCount: 'infinite',
    animationDelay: `${((BEAT_MS * i) / 1000).toFixed(3)}s`,
  });

  return (
    <main className="screen">
      <audio ref={audio} loop playsInline src="/music.mp3" />

      <div className="photo" />
      <div className="veil" />
      <div className="veilX" />

      <header className="strip">
        <span>MYKONOS · 37.45°N 25.33°E</span>
        <span className="wx">
          <WeatherIcon name={icon} />
          {island.temp === null ? '—' : `${island.temp}°`} · {island.sky}
        </span>
      </header>

      <section className="stage">
        <div className="coinWrap" onClick={toggle} role="button" aria-label="Play the track" tabIndex={0}>
          <div className="disc" />
          <div className="sonarRing" style={ringStyle(0)} />
          <div className="sonarRing" style={ringStyle(1)} />
          <div className="sonarRing" style={ringStyle(2)} />
          <div ref={seal} className="coin">
            <Image src="/seal.png" alt="Mykonos by IBLITZA" width={1254} height={1254} priority />
          </div>
        </div>

        <div className="readout" key={hydrated ? 'live' : 'baked'}>
          <div className="date">8 JULY 2027 · 06:00</div>
          <div className="hair" />
          <div className="bigRow">
            <span className="big" suppressHydrationWarning>{t.days}</span>
            <span className="bigLabel">DAYS</span>
          </div>
          <div className="hms" suppressHydrationWarning>{pad(t.hours)}h {pad(t.minutes)}m {pad(t.seconds)}s</div>
          <p className="line" suppressHydrationWarning>{line}</p>
        </div>
      </section>

      <footer className="foot" key={hydrated ? 'live' : 'baked'}>
        <div className="stats">
          <div><span className="statN" suppressHydrationWarning>{Math.floor(t.days / 7)}</span><span className="statL">WEEKS</span></div>
          <div><span className="statN" suppressHydrationWarning>{Math.floor(t.days / 30.44)}</span><span className="statL">MONTHS</span></div>
          <div><span className="statN" suppressHydrationWarning>{t.days + 1}</span><span className="statL">SLEEPS</span></div>
        </div>
        <a className="share" href={share} target="_blank" rel="noreferrer" suppressHydrationWarning>SHARE</a>
      </footer>
    </main>
  );
}
