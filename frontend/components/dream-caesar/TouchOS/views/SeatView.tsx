'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Triangle, Cpu } from 'lucide-react';
import { SEAT_BY_COLOR, type SeatColor, type SeatConfig } from '../constants';
import { useSeatMail, type MailMessage } from '@/lib/hooks/useSeatMail';

interface SeatViewProps {
  color: SeatColor;
  onEnterTribunal: () => void;
  onEnterDashboard: () => void;
}

const TABS = ['Identity', 'State', 'Mail'] as const;
type Tab = typeof TABS[number];

export default function SeatView({ color, onEnterTribunal, onEnterDashboard }: SeatViewProps) {
  const [tab, setTab] = useState<Tab>('Identity');
  const [gemSpin, setGemSpin] = useState(0);
  const [mailCount, setMailCount] = useState(0);
  const gemLongPressRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const seat = SEAT_BY_COLOR[color];

  const handleGemPointerDown = () => {
    gemLongPressRef.current = setTimeout(() => setGemSpin((n) => n + 1), 350);
  };
  const handleGemPointerUp = () => {
    if (gemLongPressRef.current) clearTimeout(gemLongPressRef.current);
  };

  return (
    <div className="relative w-full h-full flex flex-col items-center overflow-y-auto select-none px-4 pt-16 pb-28">
      {/* Hero */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col items-center mb-6"
      >
        {/* Hexagonal node */}
        <div
          className="flex items-center justify-center rounded-full mb-4"
          style={{
            width: 100, height: 100,
            background: `radial-gradient(circle, ${seat.hex}55 0%, ${seat.hex}11 100%)`,
            border: `2px solid ${seat.hex}66`,
            boxShadow: `0 0 32px ${seat.hex}44`,
          }}
        >
          <span style={{ fontSize: 48 }}>{seat.emoji}</span>
        </div>
        <h2 className="text-white text-2xl font-bold">{seat.name}</h2>
        <p className="text-sm mt-1" style={{ color: seat.hex }}>{seat.role}</p>
        <p className="text-white/40 text-xs mt-1 italic">"{seat.totemName}"</p>
      </motion.div>

      {/* Tab bar */}
      <div className="flex gap-1 rounded-xl p-1 mb-5 w-full max-w-xs" style={{ background: 'rgba(255,255,255,0.06)' }}>
        {TABS.map((t) => (
          <button
            key={t}
            onPointerDown={() => setTab(t)}
            className="flex-1 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: tab === t ? `${seat.hex}33` : 'transparent',
              color: tab === t ? seat.hex : 'rgba(255,255,255,0.4)',
              border: tab === t ? `1px solid ${seat.hex}44` : '1px solid transparent',
              touchAction: 'manipulation',
            }}
          >
            {t === 'Mail' && mailCount > 0 ? (
              <span className="inline-flex items-center gap-1">
                Mail
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: seat.hex }} />
              </span>
            ) : t}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -8 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-xs"
        >
          {tab === 'Identity' && (
            <IdentityTab
              seat={seat}
              gemSpin={gemSpin}
              onGemPointerDown={handleGemPointerDown}
              onGemPointerUp={handleGemPointerUp}
            />
          )}
          {tab === 'State' && <StateTab seat={seat} />}
          {tab === 'Mail' && (
            <MailTab color={color} seat={seat} onLoad={setMailCount} />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Action buttons — fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 flex gap-3 p-4 z-20" style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.9), transparent)' }}>
        <ActionButton
          icon={<Triangle className="w-4 h-4" />}
          label="Sentry Tribunal"
          color={seat.hex}
          onTap={onEnterTribunal}
          flex={2}
        />
        <ActionButton
          icon={<Cpu className="w-4 h-4" />}
          label="Dashboard"
          color="rgba(255,255,255,0.15)"
          onTap={onEnterDashboard}
          flex={1}
        />
      </div>
    </div>
  );
}

// ============================================================================
// IDENTITY TAB — Cinematic Persona Card
// ============================================================================

interface IdentityTabProps {
  seat: SeatConfig;
  gemSpin: number;
  onGemPointerDown: () => void;
  onGemPointerUp: () => void;
}

function IdentityTab({ seat, gemSpin, onGemPointerDown, onGemPointerUp }: IdentityTabProps) {
  const identityFields = [
    { label: 'Gemstone',  value: seat.gemstone },
    { label: 'Chakra',    value: seat.chakra },
    { label: 'Quantum',   value: seat.quantum },
    { label: 'Theme',    value: seat.themeVariant },
    { label: 'Role',      value: seat.role },
    { label: 'Animal',    value: seat.animal },
  ];

  return (
    <div className="pb-4">
      {/* Gem hero with chakra radiance — long-press to respin */}
      <div
        className="relative flex justify-center items-center rounded-2xl mb-1 py-2"
        style={{
          background: `radial-gradient(ellipse 70% 55% at 50% 50%, ${seat.hex}18 0%, transparent 70%)`,
        }}
        onPointerDown={onGemPointerDown}
        onPointerUp={onGemPointerUp}
        onPointerLeave={onGemPointerUp}
      >
        <GemHero seat={seat} spinKey={gemSpin} />
        <p className="absolute bottom-1 right-3 text-white/15 text-xs">hold to spin</p>
      </div>

      {/* Mantra headline */}
      <motion.p
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="text-center font-semibold text-sm leading-snug px-2 mb-4 mt-1"
        style={{ color: seat.hex }}
      >
        "{seat.mantra}"
      </motion.p>

      {/* Identity grid — 2×3 */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        {identityFields.map(({ label, value }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="rounded-xl p-3"
            style={{
              background: `${seat.hex}0d`,
              border: `1px solid ${seat.hex}22`,
            }}
          >
            <p className="text-white/30 text-xs uppercase tracking-wide mb-0.5">{label}</p>
            <p className="text-white/85 text-xs font-medium leading-snug">{value}</p>
          </motion.div>
        ))}
      </div>

      {/* Quantum principle banner */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="rounded-2xl p-4 mb-3"
        style={{
          background: `${seat.hex}10`,
          border: `1px solid ${seat.hex}25`,
        }}
      >
        <p className="text-white/30 text-xs uppercase tracking-wider mb-1">Quantum Principle</p>
        <p className="font-bold text-sm mb-1" style={{ color: seat.glowHex }}>{seat.quantum}</p>
        <p className="text-white/55 text-xs leading-relaxed">{seat.quantumMeaning}</p>
      </motion.div>

      {/* Guiding question footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="pt-3"
        style={{ borderTop: `1px solid ${seat.hex}20` }}
      >
        <p className="text-white/20 text-xs uppercase tracking-wider mb-1.5">Guiding Question</p>
        <p className="text-white/65 text-sm italic leading-relaxed">"{seat.guidingQuestion}"</p>
      </motion.div>
    </div>
  );
}

// ============================================================================
// GEM HERO — CSS 3D spin, auto-spins on mount, re-spins on long-press
// ============================================================================

function GemHero({ seat, spinKey }: { seat: SeatConfig; spinKey: number }) {
  return (
    <div style={{ perspective: 600 }} className="flex justify-center items-center py-3">
      <motion.div
        key={spinKey}
        animate={{ rotateY: [0, 360] }}
        transition={{ duration: 1.1, ease: [0.4, 0, 0.2, 1] }}
        style={{
          width: 88,
          height: 88,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transformStyle: 'preserve-3d',
          filter: `drop-shadow(0 0 22px ${seat.glowHex}99)`,
        }}
      >
        <span style={{ fontSize: 56, lineHeight: 1 }}>{seat.emoji}</span>
      </motion.div>
    </div>
  );
}

// ============================================================================
// STATE TAB
// ============================================================================

function StateTab({ seat }: { seat: SeatConfig }) {
  return (
    <div className="space-y-3 pb-4">
      <StatusRow label="Agent Status"   value="Idle"               dot="green"  seat={seat} />
      <StatusRow label="Current Task"   value="Awaiting ring input" dot="gray"   seat={seat} />
      <StatusRow label="DreamFS Queue"  value="0 pending"           dot="gray"   seat={seat} />
      <StatusRow label="Last Crystal"   value="None"                dot="gray"   seat={seat} />
      <StatusRow label="Sentry Badge"   value="Not checked"         dot="yellow" seat={seat} />
    </div>
  );
}

// ============================================================================
// MAIL TAB
// ============================================================================

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function MailTab({ color, seat, onLoad }: { color: SeatColor; seat: SeatConfig; onLoad?: (n: number) => void }) {
  const { messages, loading, error } = useSeatMail(color);
  const [selected, setSelected] = useState<MailMessage | null>(null);

  // Notify parent of count once loaded
  React.useEffect(() => {
    if (!loading) onLoad?.(messages.length);
  }, [loading, messages.length, onLoad]);

  if (loading) return (
    <div className="flex justify-center py-12">
      <motion.div
        className="w-5 h-5 rounded-full border-2"
        style={{ borderColor: `${seat.hex}33`, borderTopColor: seat.hex }}
        animate={{ rotate: 360 }}
        transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );

  if (error) return (
    <div className="text-center py-8">
      <p className="text-white/25 text-sm">{error}</p>
    </div>
  );

  if (messages.length === 0) return (
    <div className="text-center py-8 pb-4">
      <p className="text-white/25 text-sm">No mail in inbox</p>
      <p className="text-white/15 text-xs mt-1">Mail arrives clockwise from prior seat</p>
    </div>
  );

  return (
    <div className="pb-4">
      <div className="space-y-2">
        {messages.map((msg, i) => {
          const senderSeat = SEAT_BY_COLOR[msg.sender as SeatColor];
          return (
            <motion.button
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              whileTap={{ scale: 0.98 }}
              onPointerDown={() => setSelected(msg)}
              className="w-full rounded-2xl p-3.5 text-left"
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: `1px solid ${seat.hex}18`,
                touchAction: 'manipulation',
              }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-lg"
                  style={{ background: senderSeat ? `${senderSeat.hex}22` : 'rgba(255,255,255,0.08)' }}
                >
                  {senderSeat?.emoji ?? '📨'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-white/85 text-xs font-semibold truncate">{msg.subject}</p>
                    <p className="text-white/25 text-xs shrink-0">{timeAgo(msg.timestamp)}</p>
                  </div>
                  <p className="text-white/40 text-xs mt-0.5 truncate">{msg.body}</p>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Message detail bottom sheet */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-end"
            style={{ background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(6px)' }}
            onPointerDown={() => setSelected(null)}
          >
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              onPointerDown={(e) => e.stopPropagation()}
              className="w-full rounded-t-3xl p-6 pb-10 space-y-4 max-h-[72vh] overflow-y-auto"
              style={{ background: '#0d0a1e', border: `1px solid ${seat.hex}30` }}
            >
              <div className="w-10 h-1 rounded-full mx-auto mb-1" style={{ background: 'rgba(255,255,255,0.15)' }} />
              {(() => {
                const s = SEAT_BY_COLOR[selected.sender as SeatColor];
                return (
                  <div className="flex items-start gap-3">
                    <div
                      className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                      style={{ background: s ? `${s.hex}22` : 'rgba(255,255,255,0.08)' }}
                    >
                      {s?.emoji ?? '📨'}
                    </div>
                    <div>
                      <p className="text-white font-semibold text-sm">{selected.subject}</p>
                      <p className="text-white/30 text-xs mt-0.5">
                        {s?.name ?? selected.sender} · {timeAgo(selected.timestamp)}
                      </p>
                    </div>
                  </div>
                );
              })()}
              <p className="text-white/70 text-sm leading-relaxed">{selected.body}</p>
              <button
                onPointerDown={() => setSelected(null)}
                className="w-full py-3 rounded-2xl text-white/50 text-sm"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', touchAction: 'manipulation' }}
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// SHARED SUB-COMPONENTS
// ============================================================================

function StatusRow({ label, value, dot, seat }: {
  label: string; value: string;
  dot: 'green' | 'yellow' | 'gray' | 'red';
  seat: SeatConfig;
}) {
  const dotColors = { green: '#22C55E', yellow: '#EAB308', gray: 'rgba(255,255,255,0.2)', red: '#EF4444' };
  return (
    <div className="rounded-xl p-3 flex items-center justify-between" style={{ background: 'rgba(255,255,255,0.04)', border: `1px solid ${seat.hex}15` }}>
      <p className="text-white/50 text-xs">{label}</p>
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full" style={{ background: dotColors[dot] }} />
        <p className="text-white/80 text-xs font-medium">{value}</p>
      </div>
    </div>
  );
}

function ActionButton({ icon, label, color, onTap, flex }: {
  icon: React.ReactNode; label: string; color: string; onTap: () => void; flex: number;
}) {
  return (
    <motion.button
      onPointerDown={onTap}
      whileTap={{ scale: 0.96 }}
      className="flex items-center justify-center gap-2 py-3.5 rounded-2xl font-medium text-sm text-white"
      style={{
        flex,
        background: color.startsWith('#') ? `${color}22` : color,
        border: `1px solid ${color.startsWith('#') ? `${color}44` : 'rgba(255,255,255,0.12)'}`,
        touchAction: 'manipulation',
      }}
    >
      {icon}
      {label}
    </motion.button>
  );
}
