'use client';

/**
 * Fractal Hierarchy Visualizer
 *
 * An infinite zoom experience through the 10 tiers of the Cosmic Council.
 * Like Powers of Ten, users can dive from the User level down to 45 million agents.
 *
 * @module components/dream-caesar/FractalHierarchy
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, ChevronDown, Eye, Layers } from 'lucide-react';
import { ComputeTier, TIER_PROFILES } from '@/lib/cosmic-council/compute-tiers';
import { COSMIC_BIBLE, TotemId } from '@/lib/cosmic-council/cosmic-bible';
import { useAudioManager } from '@/lib/hooks/useAudio';
import { MARVEL_OMNIVERSE } from '@/lib/branding/marvel-omniverse';

// ============================================================================
// TYPES
// ============================================================================

interface TierConfig {
  tier: ComputeTier;
  name: string;
  prefix: string;
  description: string;
  agentCount: number;
  visualTheme: {
    background: string;
    primaryColor: string;
    accentColor: string;
  };
}

interface FractalHierarchyProps {
  initialTier?: ComputeTier;
  onTierChange?: (tier: ComputeTier) => void;
  onAgentClick?: (agentId: string) => void;
  className?: string;
}

// ============================================================================
// TIER CONFIGURATIONS
// ============================================================================

const TIER_CONFIGS: TierConfig[] = [
  {
    tier: 1,
    name: 'MACRO',
    prefix: MARVEL_OMNIVERSE.oneAboveAll,
    description: `${MARVEL_OMNIVERSE.theUser} — sovereign intent and final judgment`,
    agentCount: 1,
    visualTheme: {
      background: 'linear-gradient(180deg, #87CEEB 0%, #FFE4B5 50%, #FFA500 100%)',
      primaryColor: '#FFD700',
      accentColor: '#FFA500',
    },
  },
  {
    tier: 2,
    name: 'MICRO',
    prefix: MARVEL_OMNIVERSE.uatu,
    description: 'The Watcher at the nexus — observes all timelines',
    agentCount: 1,
    visualTheme: {
      background: 'linear-gradient(180deg, #2D2D2D 0%, #4A3728 50%, #C9A227 100%)',
      primaryColor: '#C9A227',
      accentColor: '#FFD700',
    },
  },
  {
    tier: 3,
    name: 'NANO',
    prefix: MARVEL_OMNIVERSE.infinityStones,
    description: 'Occult-trained six-seat ring — WHY through WHO',
    agentCount: 6,
    visualTheme: {
      background: 'linear-gradient(180deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%)',
      primaryColor: '#A78BFA',
      accentColor: '#7C3AED',
    },
  },
  {
    tier: 4,
    name: 'PICO',
    prefix: '108 Agents',
    description: 'The worker bees of the council',
    agentCount: 108,
    visualTheme: {
      background: 'linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 50%, #2D1B4E 100%)',
      primaryColor: '#60A5FA',
      accentColor: '#3B82F6',
    },
  },
  {
    tier: 5,
    name: 'FEMTO',
    prefix: 'Sub-Caesars',
    description: 'Each agent has its own guide',
    agentCount: 108,
    visualTheme: {
      background: 'linear-gradient(180deg, #0A0A14 0%, #14142A 50%, #1E1E3F 100%)',
      primaryColor: '#34D399',
      accentColor: '#10B981',
    },
  },
  {
    tier: 6,
    name: 'ATTO',
    prefix: 'Sub-Councils',
    description: 'Councils within councils',
    agentCount: 648,
    visualTheme: {
      background: 'linear-gradient(180deg, #050510 0%, #0A0A1F 50%, #10102E 100%)',
      primaryColor: '#F472B6',
      accentColor: '#EC4899',
    },
  },
  {
    tier: 7,
    name: 'ZEPTO',
    prefix: 'Sub-Agents',
    description: 'Pure energy flows',
    agentCount: 69984,
    visualTheme: {
      background: 'linear-gradient(180deg, #030308 0%, #05050F 50%, #0A0A1A 100%)',
      primaryColor: '#FBBF24',
      accentColor: '#F59E0B',
    },
  },
  {
    tier: 8,
    name: 'YOCTO',
    prefix: 'Deep Caesars',
    description: 'Quantum foam guides',
    agentCount: 69984,
    visualTheme: {
      background: 'linear-gradient(180deg, #020206 0%, #03030A 50%, #050510 100%)',
      primaryColor: '#F87171',
      accentColor: '#EF4444',
    },
  },
  {
    tier: 9,
    name: 'RONTO',
    prefix: 'Deep Councils',
    description: 'Nearly atomic deliberation',
    agentCount: 419904,
    visualTheme: {
      background: 'linear-gradient(180deg, #010103 0%, #020206 50%, #03030A 100%)',
      primaryColor: '#A3E635',
      accentColor: '#84CC16',
    },
  },
  {
    tier: 10,
    name: 'QUECTO',
    prefix: 'Gruntwork Agents',
    description: '45 million stars working in the void',
    agentCount: 45349632,
    visualTheme: {
      background: 'linear-gradient(180deg, #000000 0%, #010102 50%, #020204 100%)',
      primaryColor: '#E879F9',
      accentColor: '#D946EF',
    },
  },
];

// ============================================================================
// COMPONENT
// ============================================================================

export default function FractalHierarchy({
  initialTier = 3,
  onTierChange,
  onAgentClick,
  className = '',
}: FractalHierarchyProps) {
  const [currentTier, setCurrentTier] = useState<ComputeTier>(initialTier);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const { playUI } = useAudioManager();

  const tierConfig = TIER_CONFIGS[currentTier - 1];

  // Navigate to a tier
  const goToTier = useCallback(
    (tier: ComputeTier) => {
      if (tier < 1 || tier > 10 || tier === currentTier || isTransitioning) return;

      setIsTransitioning(true);
      const direction = tier > currentTier ? 'in' : 'out';
      playUI(direction === 'in' ? 'tier-zoom-in' : 'tier-zoom-out');

      setTimeout(() => {
        setCurrentTier(tier);
        onTierChange?.(tier);
        setIsTransitioning(false);
      }, 400);
    },
    [currentTier, isTransitioning, onTierChange, playUI]
  );

  const canZoomIn = currentTier < 10;
  const canZoomOut = currentTier > 1;

  // Generate nodes for current tier
  const nodes = useMemo(() => {
    const count = Math.min(tierConfig.agentCount, 20); // Limit for performance
    return Array.from({ length: count }, (_, i) => ({
      id: `${tierConfig.prefix}-${i}`,
      index: i,
    }));
  }, [tierConfig]);

  return (
    <div
      className={`relative w-full h-full min-h-[500px] overflow-hidden rounded-2xl ${className}`}
      style={{ background: tierConfig.visualTheme.background }}
    >
      {/* Tier indicator */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between">
        <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-black/40 backdrop-blur-sm">
          <Layers className="w-5 h-5" style={{ color: tierConfig.visualTheme.primaryColor }} />
          <div>
            <p className="text-white font-bold text-sm">
              Tier {currentTier}: {tierConfig.name}
            </p>
            <p className="text-white/60 text-xs">{tierConfig.prefix}</p>
          </div>
        </div>

        <div className="px-3 py-1.5 rounded-lg bg-black/40 backdrop-blur-sm">
          <p className="text-white/80 text-xs">
            {tierConfig.agentCount.toLocaleString()} agents
          </p>
        </div>
      </div>

      {/* Tier navigation */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-1">
        {TIER_CONFIGS.map((config) => (
          <button
            key={config.tier}
            onClick={() => goToTier(config.tier)}
            className={`w-8 h-2 rounded-full transition-all ${
              config.tier === currentTier
                ? 'w-12 bg-white'
                : 'bg-white/30 hover:bg-white/50'
            }`}
            title={`${config.name} - ${config.prefix}`}
          />
        ))}
      </div>

      {/* Main visualization area */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentTier}
          initial={{ scale: currentTier > (initialTier || 3) ? 0.5 : 2, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: currentTier > (initialTier || 3) ? 2 : 0.5, opacity: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {/* Tier-specific visualization */}
          {currentTier === 3 ? (
            <CouncilView onTotemClick={onAgentClick} />
          ) : (
            <NodeGrid
              nodes={nodes}
              tierConfig={tierConfig}
              onNodeClick={onAgentClick}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Description */}
      <div className="absolute bottom-16 left-4 right-4 z-20 text-center">
        <motion.p
          key={currentTier}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-white/70 text-sm italic"
        >
          "{tierConfig.description}"
        </motion.p>
      </div>

      {/* Zoom controls */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2">
        <button
          onClick={() => goToTier((currentTier - 1) as ComputeTier)}
          disabled={!canZoomOut || isTransitioning}
          className="flex items-center gap-1 px-3 py-2 rounded-lg bg-black/40 backdrop-blur-sm text-white/80 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <ChevronUp className="w-4 h-4" />
          <span className="text-xs">Zoom Out</span>
        </button>

        <div className="px-4 py-2 rounded-lg bg-black/60 backdrop-blur-sm">
          <p className="text-white font-mono text-sm">{currentTier} / 10</p>
        </div>

        <button
          onClick={() => goToTier((currentTier + 1) as ComputeTier)}
          disabled={!canZoomIn || isTransitioning}
          className="flex items-center gap-1 px-3 py-2 rounded-lg bg-black/40 backdrop-blur-sm text-white/80 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <span className="text-xs">Zoom In</span>
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

interface CouncilViewProps {
  onTotemClick?: (totemId: string) => void;
}

function CouncilView({ onTotemClick }: CouncilViewProps) {
  const totems: { id: TotemId; emoji: string; name: string; color: string }[] = [
    { id: 'purple', emoji: '🐘', name: 'Purple Elephant', color: '#7C3AED' },
    { id: 'red', emoji: '🦉', name: 'Red Owl', color: '#DC2626' },
    { id: 'orange', emoji: '🦧', name: 'Orange Orangutan', color: '#EA580C' },
    { id: 'yellow', emoji: '🐝', name: 'Yellow Honeybee', color: '#CA8A04' },
    { id: 'green', emoji: '🐢', name: 'Green Tortoise', color: '#16A34A' },
    { id: 'blue', emoji: '🐬', name: 'Blue Dolphin', color: '#2563EB' },
  ];

  return (
    <div className="relative w-80 h-80">
      {/* Hexagonal arrangement */}
      {totems.map((totem, i) => {
        const angle = (i * 60 - 90) * (Math.PI / 180);
        const radius = 100;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;

        return (
          <motion.button
            key={totem.id}
            className="absolute w-16 h-16 rounded-full flex items-center justify-center text-2xl"
            style={{
              left: `calc(50% + ${x}px - 32px)`,
              top: `calc(50% + ${y}px - 32px)`,
              background: `radial-gradient(circle, ${totem.color}40 0%, ${totem.color}20 100%)`,
              border: `2px solid ${totem.color}`,
              boxShadow: `0 0 20px ${totem.color}40`,
            }}
            whileHover={{ scale: 1.15, boxShadow: `0 0 30px ${totem.color}60` }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onTotemClick?.(totem.id)}
            animate={{
              y: [0, -5, 0],
            }}
            transition={{
              y: { duration: 2 + i * 0.3, repeat: Infinity, ease: 'easeInOut' },
            }}
          >
            {totem.emoji}
          </motion.button>
        );
      })}

      {/* Center indicator */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/10 border border-white/30 flex items-center justify-center">
        <Eye className="w-6 h-6 text-white/60" />
      </div>
    </div>
  );
}

interface NodeGridProps {
  nodes: Array<{ id: string; index: number }>;
  tierConfig: TierConfig;
  onNodeClick?: (nodeId: string) => void;
}

function NodeGrid({ nodes, tierConfig, onNodeClick }: NodeGridProps) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2 max-w-md p-4">
      {nodes.map((node) => (
        <motion.button
          key={node.id}
          className="w-8 h-8 rounded-full"
          style={{
            background: `radial-gradient(circle, ${tierConfig.visualTheme.primaryColor}60 0%, ${tierConfig.visualTheme.primaryColor}20 100%)`,
            border: `1px solid ${tierConfig.visualTheme.primaryColor}40`,
          }}
          whileHover={{
            scale: 1.2,
            boxShadow: `0 0 15px ${tierConfig.visualTheme.primaryColor}60`,
          }}
          whileTap={{ scale: 0.9 }}
          onClick={() => onNodeClick?.(node.id)}
          animate={{
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            opacity: {
              duration: 2 + Math.random(),
              repeat: Infinity,
              delay: Math.random(),
            },
          }}
        />
      ))}

      {tierConfig.agentCount > 20 && (
        <p className="w-full text-center text-white/50 text-xs mt-2">
          +{(tierConfig.agentCount - 20).toLocaleString()} more agents...
        </p>
      )}
    </div>
  );
}
