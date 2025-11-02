'use client';

import React, { useState, useEffect, useRef } from 'react';
import Image from 'next/image';

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

const TARGET_DATE = new Date('2026-07-09T11:15:00');

export default function Home() {
  const [timeLeft, setTimeLeft] = useState<TimeLeft>({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPumping, setIsPumping] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const beatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const toggleMusic = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        if (audioRef.current.currentTime === 0) {
          audioRef.current.currentTime = 23.5;
        }
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  // Beat animation - only when music is playing
  useEffect(() => {
    if (isPlaying) {
      const beatInterval = 60000/128; // 128 BPM
      beatIntervalRef.current = setInterval(() => {
        setIsPumping(true);
        setTimeout(() => setIsPumping(false), 100);
      }, beatInterval);
    }

    return () => {
      if (beatIntervalRef.current) {
        clearInterval(beatIntervalRef.current);
        beatIntervalRef.current = null;
      }
      setIsPumping(false); // Ensure pumping stops when music stops
    };
  }, [isPlaying]);

  // Countdown timer
  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const difference = TARGET_DATE.getTime() - now.getTime();
      const clampedDifference = Math.max(difference, 0);

      setTimeLeft({
        days: Math.floor(clampedDifference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((clampedDifference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((clampedDifference / 1000 / 60) % 60),
        seconds: Math.floor((clampedDifference / 1000) % 60)
      });
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <main className="relative full-viewport overflow-hidden">
      <audio ref={audioRef} loop playsInline>
        <source src="/music.mp3" type="audio/mpeg" />
      </audio>

      {/* Content Container */}
      <div
        className="relative z-10 full-viewport flex flex-col items-center justify-center px-6 sm:px-12 md:px-20 py-12"
        style={{
          paddingTop: 'max(3rem, calc(env(safe-area-inset-top, 0px) + 2rem))',
          paddingBottom: 'max(3rem, calc(env(safe-area-inset-bottom, 0px) + 2rem))',
          paddingLeft: 'max(1.5rem, calc(env(safe-area-inset-left, 0px) + 1.5rem))',
          paddingRight: 'max(1.5rem, calc(env(safe-area-inset-right, 0px) + 1.5rem))',
        }}
      >
        <div className="relative bg-black/35 rounded-3xl w-full max-w-4xl border border-white/10">
          <div className="absolute inset-0 bg-gradient-to-br from-[#ff8a00] to-[#ee489a] opacity-5 rounded-3xl pointer-events-none" />
          
          {/* Banner */}
          <div className="flex justify-center pt-8 px-8">
            <div className="max-w-[700px] w-full relative">
              <div 
                onClick={toggleMusic}
                className={`transform transition-transform duration-100 cursor-pointer relative ${isPumping ? 'scale-105' : ''}`}
              >
                <Image
                  src="/banner.png"
                  alt="Event Banner"
                  width={3280}
                  height={1416}
                  className="w-full h-auto [filter:drop-shadow(2px_0_0_white)_drop-shadow(-2px_0_0_white)_drop-shadow(0_2px_0_white)_drop-shadow(0_-2px_0_white)]"
                  priority
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    filter: 'grayscale(50%) brightness(0.7)',
                  }}
                />
                {/* COMING SOON Overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="transform -rotate-12">
                    <h1 className="text-6xl md:text-[8rem] font-black text-white tracking-wider uppercase text-center drop-shadow-lg">
                      Coming Soon
                    </h1>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Countdown Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 p-8">
            {['Days', 'Hours', 'Minutes', 'Seconds'].map((unit) => (
              <div key={unit} className="flex flex-col items-center">
                <span className="text-5xl md:text-7xl font-bold text-white tracking-tight">
                  {String(timeLeft[unit.toLowerCase() as keyof TimeLeft]).padStart(2, '0')}
                </span>
                <span className="text-xs md:text-sm uppercase tracking-widest mt-2 text-gray-200">
                  {unit}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
