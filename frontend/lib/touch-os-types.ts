export type SeatColor = "purple" | "red" | "orange" | "yellow" | "green" | "blue";

export interface SeatConfig {
  color: SeatColor;
  hex: string;
  glowHex: string;
  name: string;
  emoji: string;
  role: string;
  animal: string;
  gemstone: string;
  chakra: string;
  chakraMeaning: string;
  quantum: string;
  quantumMeaning: string;
  totemName: string;
  mantra: string;
  guidingQuestion: string;
  /** Universe theme persona label (from theme pack) */
  themeVariant: string;
  /** Clock angle in degrees: 0° = right, -90° = top */
  angle: number;
}
