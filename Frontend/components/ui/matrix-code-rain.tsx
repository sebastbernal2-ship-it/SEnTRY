// components/ui/matrix-code-rain.tsx
"use client";
import React, { useRef, useEffect, useCallback } from 'react';

interface Character {
  char: string;
  opacity: number;
}

interface Strand {
  x: number;
  y: number;
  speed: number;
  length: number;
  characters: Character[];
  showCursor: boolean;
  layer: number;
  scale: number;
}

interface MatrixCodeRainProps {
  textColor?: string;
  fontSize?: number;
  speed?: number;
  density?: number;
}

export const MatrixCodeRain = ({
  textColor = '#22d3ee',
  fontSize = 14,
  speed = 0.4,
  density = 0.8,
}: MatrixCodeRainProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameId = useRef<number | null>(null);
  const strands = useRef<Strand[]>([]);
  const lastTime = useRef<number>(0);
  const cursorBlinkTime = useRef<number>(0);

  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:,./<>?';

  const getRandomChar = useCallback(() => {
    return characters.charAt(Math.floor(Math.random() * characters.length));
  }, []);

  const createStrand = useCallback((x: number) => {
    const layer = Math.floor(Math.random() * 3);
    const scale = layer === 0 ? 0.8 : layer === 1 ? 1 : 1.2;
    const length = Math.floor(Math.random() * 15) + 15;
    const chars: Character[] = Array(length).fill(null).map(() => ({
      char: getRandomChar(),
      opacity: 1,
    }));
    return {
      x,
      y: -length * (fontSize * scale),
      speed: (Math.random() * 0.3 + 0.7) * speed * fontSize * (layer === 2 ? 1.2 : layer === 1 ? 1 : 0.8),
      length,
      characters: chars,
      showCursor: true,
      layer,
      scale,
    };
  }, [fontSize, getRandomChar, speed]);

  const updateStrands = useCallback((
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    deltaTime: number
  ) => {
    const spacing = fontSize * 1.5;
    const maxStrands = Math.floor(width / spacing) * density * 1.5;

    if (strands.current.length < maxStrands) {
      const availableSlots = Array.from({ length: Math.floor(width / spacing) })
        .map((_, i) => i * spacing)
        .filter(x => !strands.current.some(strand => strand.x === x));

      if (availableSlots.length > 0 && Math.random() < 0.1 * density) {
        const x = availableSlots[Math.floor(Math.random() * availableSlots.length)];
        strands.current.push(createStrand(x));
      }
    }

    cursorBlinkTime.current += deltaTime;
    if (cursorBlinkTime.current >= 500) {
      strands.current.forEach(strand => { strand.showCursor = !strand.showCursor; });
      cursorBlinkTime.current = 0;
    }

    // Clear with dark background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    strands.current.sort((a, b) => a.layer - b.layer);

    strands.current = strands.current.filter(strand => {
      strand.y += strand.speed * deltaTime * 0.05;

      const baseOpacity = strand.layer === 0 ? 0.4 : strand.layer === 1 ? 0.6 : 0.8;
      const scaledFontSize = fontSize * strand.scale;

      ctx.font = `${scaledFontSize}px monospace`;
      ctx.shadowBlur = strand.layer + 1;
      ctx.shadowColor = textColor;

      strand.characters.forEach((char, i) => {
        const y = strand.y + (i * scaledFontSize);
        if (y > -scaledFontSize && y < height + scaledFontSize) {
          ctx.fillStyle = textColor;
          ctx.globalAlpha = baseOpacity;
          ctx.fillText(char.char, strand.x, y);
        }
      });

      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;

      if (Math.random() < 0.02) {
        const randomIndex = Math.floor(Math.random() * strand.characters.length);
        strand.characters[randomIndex].char = getRandomChar();
      }

      return strand.y - (strand.length * (fontSize * strand.scale)) < height;
    });
  }, [density, fontSize, getRandomChar, textColor, createStrand]);

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const container = canvas.parentElement;
    if (!container) return;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
  }, []);

  const animate = useCallback((time: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const deltaTime = time - lastTime.current;
    lastTime.current = time;
    if (
      canvas.width !== canvas.parentElement?.clientWidth ||
      canvas.height !== canvas.parentElement?.clientHeight
    ) {
      resizeCanvas();
    }
    updateStrands(ctx, canvas.width, canvas.height, deltaTime);
    animationFrameId.current = requestAnimationFrame(animate);
  }, [resizeCanvas, updateStrands]);

  useEffect(() => {
    resizeCanvas();
    lastTime.current = performance.now();
    cursorBlinkTime.current = 0;
    animationFrameId.current = requestAnimationFrame(animate);
    window.addEventListener('resize', resizeCanvas);
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
        animationFrameId.current = null;
      }
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [animate, resizeCanvas]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        zIndex: 0,
      }}
    />
  );
};