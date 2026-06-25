import {
  getThemedTotemOverlays,
  resolveThemePackId,
  type ComedySeatColor,
} from "@know-joke-u/council-core/client";
import type { SeatColor, SeatConfig } from "./touch-os-types";

const DEFAULT_DREAM_CAESAR_PACK = "marvel-omniverse";

export function resolveDreamCaesarThemePackId(): string {
  return resolveThemePackId(
    (process.env.NEXT_PUBLIC_THEME_PACK as string | undefined) ?? DEFAULT_DREAM_CAESAR_PACK,
  );
}

export function applyThemePackToSeats(baseSeats: SeatConfig[]): SeatConfig[] {
  const packId = resolveDreamCaesarThemePackId();
  const overlays = getThemedTotemOverlays(packId);
  const overlayByColor = new Map(
    overlays.map((overlay) => [overlay.color as SeatColor, overlay]),
  );

  return baseSeats.map((seat) => {
    const overlay = overlayByColor.get(seat.color);
    const themeVariant = overlay?.displayVariant?.trim() || seat.themeVariant;
    return {
      ...seat,
      themeVariant,
    };
  });
}

export function getThemedTotemLabel(color: ComedySeatColor): string {
  const packId = resolveDreamCaesarThemePackId();
  const overlay = getThemedTotemOverlays(packId).find((entry) => entry.color === color);
  return overlay?.displayVariant || overlay?.optionalAlias || color;
}
