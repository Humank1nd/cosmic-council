// Runtime consumes canon. Runtime must not recreate canon.

export type ComedySeatColor =
  | "red"
  | "orange"
  | "yellow"
  | "green"
  | "blue"
  | "purple";

export type ComedySpineSeat = {
  color: ComedySeatColor;
  label: string;
  anchor: string;
  function: string;
};

export type ComedySpineLayer = {
  layer: number;
  scale: string;
  archetype: string;
  era: string;
  logic: string;
  seats: ComedySpineSeat[];
};

export const KJU_COMEDY_SPINE: ComedySpineLayer[] = [
  {
    layer: 1,
    scale: "MACRO",
    archetype: "The User",
    era: "The Present",
    logic: "The Observer. The one who laughs, judges, and directs. The source of the initial intent.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Intent", function: "Why the user is here / The core desire" },
      { color: "orange", label: "Orange 🟧", anchor: "Feedback", function: "How the user reacts / The adjustment" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Attention", function: "What the user notices / The focus" },
      { color: "green", label: "Green 🟩", anchor: "Timing", function: "When the user acts / The rhythm" },
      { color: "blue", label: "Blue 🟦", anchor: "Persona", function: "Who the user is / The mask" },
      { color: "purple", label: "Purple 🟪", anchor: "Synthesis", function: "The final takeaway / The memory" }
    ]
  },
  {
    layer: 2,
    scale: "MICRO",
    archetype: "Dream Caesar",
    era: "The Membrane",
    logic: "The Axis. The hologram between dimensions. Crystallization of logic into dream.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Orchestration", function: "Root-truth analysis and assignment" },
      { color: "orange", label: "Orange 🟧", anchor: "Strategy", function: "Sequencing and rollout planning" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Implementation", function: "Execution glue and code paths" },
      { color: "green", label: "Green 🟩", anchor: "Stewardship", function: "Runtime health and maintainability" },
      { color: "blue", label: "Blue 🟦", anchor: "Observability", function: "Operational clarity and human-readable truth" },
      { color: "purple", label: "Purple 🟪", anchor: "Synthesis", function: "Ring integrity and canon alignment" }
    ]
  },
  {
    layer: 3,
    scale: "NANO",
    archetype: "Cosmic Council",
    era: "The Frontier",
    logic: "The Supergenius Quantum Thought. Six faces of wisdom united in purpose.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Red Owl", function: "WHY? / Entanglement - Map dependencies; changes ripple" },
      { color: "orange", label: "Orange 🟧", anchor: "Orange Orangutan", function: "HOW? / Tunneling - Find paths through barriers" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Yellow Honeybee", function: "WHAT? / Superposition - Hold multiple options before collapsing" },
      { color: "green", label: "Green 🟩", anchor: "Green Tortoise", function: "WHEN? / Teleportation - Efficient transfer of resources" },
      { color: "blue", label: "Blue 🟦", anchor: "Blue Dolphin", function: "WHERE? / Wave-Particle - Broadcast or precision strikes" },
      { color: "purple", label: "Purple 🟪", anchor: "Purple Elephant", function: "WHO? / Zeno Effect - Stabilize through observation" }
    ]
  },
  {
    layer: 4,
    scale: "PICO",
    archetype: "Celestials",
    era: "The Archetypes",
    logic: "Ancient Humor / Archetype Keepers. Preservation of ancient patterns and primal joke functions.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Aristophanes", function: "Satirical absurdity / The Old Comedy / Structural subversion" },
      { color: "orange", label: "Orange 🟧", anchor: "Diogenes", function: "Cynical provocation / Public performance / Shameless truth" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Aesop", function: "Fable and moral logic / Animal archetypes / Encoded wisdom" },
      { color: "green", label: "Green 🟩", anchor: "Zeno", function: "Paradox and logic / Stoic endurance / The impossible turn" },
      { color: "blue", label: "Blue 🟦", anchor: "Momus", function: "The critic-god / Personification of mockery / Divine blame" },
      { color: "purple", label: "Purple 🟪", anchor: "Epictetus", function: "Self-mastery / Metacognition / The logic of reaction" }
    ]
  },
  {
    layer: 5,
    scale: "FEMTO",
    archetype: "The Avengers",
    era: "Printing Press",
    logic: "Satirists as Political Weaponry. The birth of mass-reproducible critique.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Jonathan Swift", function: "Why the joke attacks / moral attack / root contradiction" },
      { color: "orange", label: "Orange 🟧", anchor: "Voltaire", function: "How the joke spreads / distribution & virality" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Benjamin Franklin", function: "What the joke exposes / practical hypocrisy & social foolishness" },
      { color: "green", label: "Green 🟩", anchor: "Thomas Paine", function: "Timing and public pressure / catalytic release" },
      { color: "blue", label: "Blue 🟦", anchor: "Molière", function: "Delivery, voice, persuasion / theatrical character" },
      { color: "purple", label: "Purple 🟪", anchor: "Miguel de Cervantes", function: "Feedback, consequence, refinement / meta-awareness" }
    ]
  },
  {
    layer: 6,
    scale: "ATTO",
    archetype: "SHIELD",
    era: "Industrial Vaudeville",
    logic: "The Vaudevillian. Traveling troupes, standardized performance, and human survival inside industrial machinery.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Bert Williams", function: "Why the joke attacks / survival inside the machine" },
      { color: "orange", label: "Orange 🟧", anchor: "Charlie Chaplin", function: "How the act travels / global virality & portability" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Buster Keaton", function: "What the act reveals / human vs. industrial machinery" },
      { color: "green", label: "Green 🟩", anchor: "Jack Benny", function: "Timing, pressure, silence, and release" },
      { color: "blue", label: "Blue 🟦", anchor: "Mae West", function: "Delivery, voice, stagecraft, persona" },
      { color: "purple", label: "Purple 🟪", anchor: "Groucho Marx", function: "Feedback, repetition, refinement, meta-awareness" }
    ]
  },
  {
    layer: 7,
    scale: "ZEPTO",
    archetype: "The Defenders",
    era: "Broadcast Living Room",
    logic: "The Sitcom Star / Domestic Observer. Tightly controlled networks creating shared national monoculture.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Lucille Ball", function: "Why the joke attacks / domestic chaos inside controlled broadcast order" },
      { color: "orange", label: "Orange 🟧", anchor: "Milton Berle", function: "How the joke spreads / appointment viewing & national ritual" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Norman Lear", function: "What the joke reveals / family, class, race, prejudice, politics, social norms" },
      { color: "green", label: "Green 🟩", anchor: "Carol Burnett", function: "Timing, sketch rhythm, audience pressure, emotional release" },
      { color: "blue", label: "Blue 🟦", anchor: "Dick Van Dyke", function: "Delivery, character, voice, living-room intimacy" },
      { color: "purple", label: "Purple 🟪", anchor: "Johnny Carson", function: "Feedback, nightly adjustment, repetition, national mood-reading" }
    ]
  },
  {
    layer: 8,
    scale: "YOCTO",
    archetype: "The Vigilantes",
    era: "Fragmented Iconoclast Era",
    logic: "The Iconoclast. Breaking out of the broadcast monoculture. Sharp, cynical, individualized, targeting the structures.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Lenny Bruce", function: "Why the joke attacks / truth against censorship and polite hypocrisy" },
      { color: "orange", label: "Orange 🟧", anchor: "George Carlin", function: "How the joke spreads / language as virus through albums, cable, specials, clips" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Richard Pryor", function: "What the joke reveals / race, identity, pain, survival, power, vulnerability" },
      { color: "green", label: "Green 🟩", anchor: "Joan Rivers", function: "Timing, high-velocity pressure, insult, release" },
      { color: "blue", label: "Blue 🟦", anchor: "Robin Williams", function: "Delivery, voice, persona, improvisational intimacy, emotional chaos" },
      { color: "purple", label: "Purple 🟪", anchor: "Bill Hicks", function: "Feedback, taboo-breaking, cultural consequence, philosophical feedback" }
    ]
  },
  {
    layer: 9,
    scale: "RONTO",
    archetype: "Crime Fighters",
    era: "Digital Revolution",
    logic: "Street-Level Aware. Immediate, cheap, raw. The barrier to entry drops to zero.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "Chris Rock", function: "Why the joke attacks / street truth sharpened into thesis" },
      { color: "orange", label: "Orange 🟧", anchor: "Dave Chappelle", function: "How the joke spreads / viral myth, remix culture, quoted digital spread" },
      { color: "yellow", label: "Yellow 🟨", anchor: "Jerry Seinfeld", function: "What the joke reveals / micro-social rules, ordinary absurdity, etiquette systems" },
      { color: "green", label: "Green 🟩", anchor: "Bill Burr", function: "Timing, crowd pressure, social danger, escalation, release" },
      { color: "blue", label: "Blue 🟦", anchor: "Louis C.K.", function: "Delivery, confessional voice, direct intimacy, self-exposure" },
      { color: "purple", label: "Purple 🟪", anchor: "Patrice O'Neal", function: "Feedback, recursion, elephant truth, consequence, unresolved discomfort" }
    ]
  },
  {
    layer: 10,
    scale: "QUECTO",
    archetype: "The Population",
    era: "Algorithmic Feed",
    logic: "Everyday People / The First Spark. The 0/1 binary. The audience is the generator, filter, and consumer.",
    seats: [
      { color: "red", label: "Red 🔴", anchor: "The Troll", function: "Why the joke attacks / provocation, bait, disruption, raw contradiction" },
      { color: "orange", label: "Orange 🟧", anchor: "The Algorithm", function: "How the joke spreads / distribution, engagement math, feed amplification" },
      { color: "yellow", label: "Yellow 🟨", anchor: "The Meme", function: "What the joke reveals / crowd psychology, social insecurity, trend logic" },
      { color: "green", label: "Green 🟩", anchor: "The Ratio", function: "Timing, feed pressure, crowd correction, public failure" },
      { color: "blue", label: "Blue 🟦", anchor: "The Avatar", function: "Persona, caption, handle, face, mask, delivery format" },
      { color: "purple", label: "Purple 🟪", anchor: "The Screenshot", function: "Feedback, recursion, receipts, discourse, mutation, lore" }
    ]
  }
];
