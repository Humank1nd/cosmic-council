# @know-joke-u/council-core

Shared **structural** Cosmic Council engine for Know Joke and Marvel Omniverse:

- 10-layer comedy spine (`KJU_COMEDY_SPINE`)
- Bottom-up router (`comedy-spine-router.ts`)
- Agent registry, curriculum map, verification gates
- Universe theme packs (`theme-packs/*.json`)

## Packages

| Export | Use |
| --- | --- |
| `@know-joke-u/council-core` | Full structural + theme API |
| `@know-joke-u/council-core/client` | Browser-safe (Vite/React) |
| `@know-joke-u/council-core/theme-packs/know-joke.theme.json` | KJU public skin |
| `@know-joke-u/council-core/theme-packs/marvel-omniverse.theme.json` | Marvel/dev skin |

## Theme selection

```typescript
import { getThemedSpineLayers, resolveThemePackId } from "@know-joke-u/council-core/client";

const packId = resolveThemePackId(undefined, { publicSurface: true });
const layers = getThemedSpineLayers(packId);
```

Environment: `THEME_PACK`, `NEXT_PUBLIC_THEME_PACK`, or `VITE_THEME_PACK`.

### Deploy contract

| Surface | Variable | Required value |
| --- | --- | --- |
| KJU production (knowjoke.lol) | `THEME_PACK` or `NEXT_PUBLIC_THEME_PACK` | `know-joke` |
| KJU public API / browser | same | `know-joke` (enforced via `publicSurface: true` in loaders) |
| Dream Caesar / Marvel dev | `NEXT_PUBLIC_THEME_PACK` | `marvel-omniverse` (displays **Marvel Omniverse**, **Uatu the Watcher**, **Infinity Stones**) |
| Lineage pyramid UI | — | reads `know-joke.lineage.json` (no env override yet) |

Never set `marvel-omniverse` on KJU production hosting or student-facing builds.

## Lineage theme pack

Historical comedy descent (pyramid UI) lives separately from the system spine:

```typescript
import { getLineageLayersForPyramid } from "@know-joke-u/council-core/client";

const pyramid = getLineageLayersForPyramid("know-joke-lineage");
```

See `docs/architecture/kju-lineage-system-spine-mapping.md` — **lineage layer N ≠ system spine layer N**.

## Python runtime

`src/cosmic_council/canon/theme_pack.py` loads JSON from `packages/council-core/theme-packs/`.

## Marvel Omniverse / external repos

Add a git submodule or file dependency on this package path, or publish when ready:

```json
{
  "dependencies": {
    "@know-joke-u/council-core": "workspace:*"
  }
}
```

Structural keys **`Dream Caesar`** and **`Cosmic Council`** are shared **species** (replicate, shapeshift via theme packs). KJU skins: Thalia / Comedic Council. Marvel skins: Uatu / Infinity Stones (occult dimension — must not leak to KJU public paths).
