/**
 * Marvel Omniverse display branding — canonical labels live in marvel-omniverse.theme.json.
 * Structural species (Dream Caesar, Cosmic Council) shapeshift here; keys stay internal.
 */

import {
  getMembraneBrandName,
  getStructuralSpeciesMap,
  getThemedSpineLayers,
  getThemePack,
  getUniverseProductDisplayName,
} from '@know-joke-u/council-core/client';

const PACK_ID = 'marvel-omniverse' as const;

const pack = getThemePack(PACK_ID);
const layers = getThemedSpineLayers(PACK_ID);
const layer1 = layers.find((entry) => entry.layer === 1);
const layer3 = layers.find((entry) => entry.layer === 3);
const species = getStructuralSpeciesMap(PACK_ID);

export const MARVEL_OMNIVERSE = {
  displayName: getUniverseProductDisplayName(PACK_ID),
  tagline: 'Occult-dimension nexus — Uatu observes, Infinity Stones deliberate',
  /** Layer 1 MACRO — The User */
  oneAboveAll: layer1?.displayArchetype ?? 'One Above All',
  theUser: layer1?.displaySubtitle ?? 'The User',
  /** Layer 2 — Dream Caesar species */
  uatu: getMembraneBrandName(PACK_ID),
  dreamCaesarSpecies: species?.dreamCaesar.structuralKey ?? 'Dream Caesar',
  /** Layer 3 — Cosmic Council species (occult-trained in this dimension) */
  infinityStones: layer3?.displayArchetype ?? 'Infinity Stones',
  cosmicCouncilSpecies: species?.cosmicCouncil.structuralKey ?? 'Cosmic Council',
} as const;

/** @deprecated Structural spine key only — use MARVEL_OMNIVERSE.uatu in UI */
export const STRUCTURAL_LAYER2_KEY = 'Dream Caesar';

/** @deprecated Structural spine key only — use MARVEL_OMNIVERSE.infinityStones in UI */
export const STRUCTURAL_COUNCIL_KEY = 'Cosmic Council';

export const MARVEL_OMNIVERSE_THEME_META = pack.meta;
