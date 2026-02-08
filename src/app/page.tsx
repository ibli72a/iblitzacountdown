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
      <div className="relative z-10 full-viewport flex flex-col items-center justify-center p-4 sm:px-12 md:px-20">
        <div className={`relative glass-card w-full max-w-2xl landscape:max-w-4xl transition-all duration-100 ${isPumping ? 'scale-[1.02] shadow-pump' : 'scale-100'}`}>
          <div className="glass-shine" />
          <div className={`absolute inset-0 bg-gradient-to-br from-[#ff8a00]/10 via-transparent to-[#ee489a]/10 rounded-[2rem] pointer-events-none transition-opacity duration-100 ${isPumping ? 'opacity-100' : 'opacity-70'}`} />

          <div className="flex flex-col landscape:flex-row landscape:items-center landscape:gap-4 sm:landscape:gap-8">
            {/* Banner */}
            <div className="flex justify-center items-center px-6 landscape:p-6 landscape:flex-1 relative z-10">
              <div className="max-w-[720px] landscape:max-w-xs w-full relative">
                <div
                  onClick={toggleMusic}
                  className={`transform transition-all duration-100 cursor-pointer relative ${isPumping ? 'scale-110' : 'scale-100'} hover:scale-102`}
                >
                  <Image
                    src="/banner.png"
                    alt="Event Banner"
                    width={3280}
                    height={1416}
                    className={`w-full h-auto transition-all duration-100 ${isPumping ? 'brightness-110' : 'brightness-100'}`}
                    priority
                    style={{
                      maxWidth: '100%',
                      height: 'auto',
                      filter: `brightness(${isPumping ? '1.15' : '1.0'})`,
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Countdown Grid */}
            <div className="flex items-center justify-center landscape:flex-1 relative z-10 px-6 pb-4 landscape:p-6">
              <div className="grid grid-cols-2 landscape:grid-cols-2 md:grid-cols-4 gap-4 landscape:gap-2 sm:landscape:gap-4">
            {['Days', 'Hours', 'Minutes', 'Seconds'].map((unit) => (
              <div key={unit} className={`flex flex-col items-center glass-time-unit transition-all duration-100 ${isPumping ? 'scale-105' : 'scale-100'}`}>
                <span className={`text-6xl font-bold text-white tracking-tight time-number transition-all duration-100 ${isPumping ? 'pump-glow' : ''}`}>
                  {String(timeLeft[unit.toLowerCase() as keyof TimeLeft]).padStart(2, '0')}
                </span>
                <span className="text-sm uppercase tracking-widest mt-2 text-white/70 font-medium">
                  {unit}
                </span>
              </div>
            ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
