# The Abyssal Planes

A text-based MUD built with [Evennia](https://www.evennia.com). Currently in development and playable over telnet.

**Live:** telnet `theabyssalplane.duckdns.org:4000` — website/webclient `http://theabyssalplane.duckdns.org` (web on port 80). A custom UI package installs automatically in Mudlet, and the browser webclient ships with matching custom panes.
**Local:** telnet `localhost:4000` — website/webclient `http://localhost`.

Every soul is born into one of nine species on the planes. Characters have no
levels or XP grind — growth comes purely from **using skills**, and the world is
split across the **physical** realm and the **visarial** (the realm of Vim),
which only some can perceive.

Below is an overview of the systems we've built on top of the stock Evennia
feature set. For the full technical reference (commands, modules, gotchas),
see [`DEVELOPMENT.md`](DEVELOPMENT.md); the living build-order and design
doc is [`GAMEPLAN.md`](GAMEPLAN.md).

---

## Definitions & Lore

**Abyss:** The darkness between the stars. The place where the Planes dance around Mundus, never drifting far from their Sol. A desolate and lifeless place that requires some sort of protective medium to travel through for most life. There are however, exceptions. Eldritch, unspeakable horrors do sometimes call the vast empty of the Abyss home.

**Mundus:** The known Universe, and all the realms within it. It was once thought that the edge of it was a solid mass of stars, meant to contain all of the Realms. Since scholars have started to explore and study the Abyss, this sentiment has shifted towards one that posits that it could be endless, limited only by our perception of the realms.

**Planes:** Planetary bodies that orbit around a central star. There are several known within Mundus. Some of them support life, while others do not. There are even some that do not exist within the Physical Realm, and are only seen by those that can perceive the Visarial Realm.

**Vim:** The energy force that binds all things together, whether they display any connection to it, or not. It's the stuff that pours out of whatever is beyond existence to give life to it, and then flows out into all living and non-living entities.

**Vis:** Force, power, and natural energy. This is the expression, the very actions one takes that are fueled by pure Vim. Vis can take endless forms. Whether it's coming from the hands of a direct wielder of Vim, or Vim-fueled contraptions and devices of all shapes and sizes. There are many schools of thought dedicated to the study of manipulating Vim into Vis.

**Visarial Realm:** The realm of Vim. This is the first realm that's known of where Vim pours in from beyond existence. It seems to be layered on top of the Physical Realm, sharing landscapes and even structures in some places, but does not follow all of the rules of physics that have been discovered so far within the Physical Realm. The first of the sentient species within existence were born within this realm, and a great number of entities call it home. Some can interact with the Physical Realm under certain circumstances, while others are bound to it entirely.

**Physical Realm:** The known Planes of existence. This is where most life that is not pure-Vim lives out its time within Mundus. Everything here is subject to the discovered laws of physics and entropy, although any of these forces can be manipulated through Vis.

**Vistronics:** The branch of technology and engineering dealing with the control, manipulation, and utilization of Vim flow through circuits, nodes, and conductive mediums.
- *Visographer:* One that creates Vistronic circuit boards and components that are made by etching or engraving copper, glass, or stone channels for the magic to flow through.
  - *Visography:* The practice of writing, etching, or coding spell-arrays into Vistronic components. (Real-world equivalent: Programming / Cryptography).

**Vismechanics:** Mechanical systems driven by physical Vim pressure, gears, and kinetic energy.
- *Viswright:* One that designs and engineers mechanical contraptions that are powered by Vim. Basic contraptions may not require a skilled Visographer to create vistronic components for them, though most advanced ones may require several devices.

**Viskinetics:** The study and application of Vim to generate heavy physical force, torque, and motion. This school of thought is what creates the devices that power most Vistronics and Vismechanical devices and contraptions.
- *Visicist:* A scholar that has dedicated themselves to the study of the flow of Vim and processing it into practical physical application, or, Vis.

---

## Systems Overview

### Visarial Planes & Vim Connection

Every object and character has a `visarial_nature` that sets both its **plane**
and its **connection to Vim**:

| Nature        | Plane        | Of Vim | Description             | Seen via |
|---------------|--------------|--------|-------------------------|----------|
| **physical**  | physical     | no     | Physical desc only      | physical only |
| **visarial**  | visarial     | yes    | Visarial desc / Magenta aura | visarial |
| **dual-natured** | physical (default) | both | Physical *and* visarial desc | both, by state |

Creatures also carry a `visarial_state` — `normal` (present in your native
realm), `perceiving` (aware of the other realm while staying put) or
`manifested` (fully present in the opposite realm). `perceive` (yellow) toggles
the middle state; `manifest` (cyan) toggles the last. Silex can do neither.

- Visibility is per-entity and split into *see* vs *touch* (`can_phys_see`,
  `can_vis_see`, `can_phys_touch`, `can_vis_touch`), so what you can perceive and
  what you can reach are independently controlled.
- Speech follows the same rule. Voice (`can_speak_phys` / `can_speak_vis`) only
  lands in the realm you occupy, and hearing (`can_hear_phys` / `can_hear_vis`)
  mirrors sight — you hear a realm if you can see it. Words spoken in the
  physical are heard only by those who can see the physical; words from the
  visarial only by those who can see it. Whispering to a named target bypasses
  the realms.
- Vim-connected things radiate a magenta aura; physical things read as
  "absolutely disconnected from Vim."
- Builders set a prop's nature with `setnature`. Staff can `force` anyone, in
  any room, on any plane, whether or not they can see them.

### The 5D Room Grid

Rooms are stamped with a two-tier coordinate grid (planet-level and subzone-level)
so `dig` and `setorigin` place them in a world automatically, and `look` renders
nearby neighbors in clockwise order with grammatical exit grouping.

### Tactical Grid & Movement

Inside each room, characters and objects occupy a tactical tile grid (2×2 to 51×51,
set via `setroomsize`). Characters store `pos_x`/`pos_y`/`pos_z` coordinates
and navigate autonomously via the `move` command. Flying characters can traverse
the z-axis (`fly`/`land`); ground-bound characters walk compass directions or
type `move <x> <y>`. A 6-second round system caps movement at 6 grids per round.

### Species, Appearance & Pose

- **9 playable species** with their own visarial nature, a persistent stat bonus,
  locked stat columns (remapped to an alternate main), hidden pools, and
  perception rules.
- Characters are described by a **three-word appearance phrase** ("A tall and
  lean, refracting Visarii standing here.") instead of a name, with builder
  helpers to set height / build / adjective / skin / eyes / eye colour / hair / hair colour.
- A whitelisted **pose system** replaces the stock `pose`. Players use
  `sit`/`rest`/`sleep`/`wake`/`lay`/`stand`/`rotate` (furniture-aware);
  builders set pose directly via `setpose`.

### Stats, Skills & Growth

- **9 sub-stats** (Corpus / Genius / Animus × Potestas / Reflexus / Obsistis)
  driving derived mains (Corpus / Genius / Animus) and pools (Vigor / Vim / Mens).
- **Skills 0-1000 across 10 tiers**, learned from trainers and gated by
  prerequisites; using a skill feeds it and its linked stats, with diminishing
  returns to push branching.
- **Level-less, nothing to bank** — you grow purely by using what you know.
- **19 skills** across 3 categories: combat (brawling tree: punch, kick, headbutt, knee, axehandle, haymaker + defense: melee_evasion/parry/block/feint/counterattack + bash), utility (lockpick, awareness), spirit (meditate, focused_meditation, pray, devoted_prayer).

### Doors & Locks

Exits can be doors with open/close/lock/unlock states, key-based access,
lockpick difficulty classes, breakable walls (bash DC), and hidden exits
(detect DC). Sibling doors sync open state. The `digmenu` builder tool
guides door creation interactively.

### Furniture & Items

Furniture objects sit on the tactical grid with facing, dimensions (1×1 to 2×2),
seat counts, and allowed pose states. Dropping furniture auto-places and auto-sits
characters on it. Furniture `quality` multiplies rest/sleep regen. The item
system supports multi-material Truecolor descriptions via `createitem`.

### Combat

A tick-based combat loop runs inside rooms (`CombatLoop` script). Players
`attack` a target (or use skill aliases: `punch`, `kick`, `haymaker`, etc.),
queuing up to 3 actions per 6-second round. Each action resolves accuracy
(attack vs best defense roll), base damage (skill category + highest sub-stat),
armor subtraction, and pool damage (Vigor/Vim/Mens). Knockout occurs at pool
depletion. Combat runs alongside grid movement, rest, and regeneration in the
same loop.

### Cosmic Time

A universal 23-hour / 28-day / 13-month calendar anchored to the cradle world
Auridon, with 13 ruling signs and 3 orbiting planets. `time` shows universal and
local dates resolved from the room's planetary body tag.

### Live Prompt

A colorful command-refresh prompt with `numbers` / `percent` / `bars` modes,
showing your pools and current plane/fold state. Refreshes after every command.

### Changelog

An in-game changelog (`changes` command) tracks all major updates. 44 entries
and counting. Unread entries alert on login. Builders add entries with
`addchange`; admins remove with `removechange`. Server start/reload broadcasts
the newest entry to connected players.

### Discord Integration

A Discord bridge relays in-game OOC chat to a Discord channel and sends
server lifecycle announcements (connections, disconnections, reloads) to an
announcements channel. A bot listens in the background.

### Custom Client UI (Mudlet & Webclient)

Both major clients get a matching custom interface out of the box:

- **Mudlet** auto-installs our package on login (`Client.GUI`). It adds a
  docked **Map** window fed by `autowhere`, a tabbed **Communication** window
  (Local / OOC / MudInfo), and a bottom **prompt bar** — all rendering full
  truecolor. Player-facing commands:
  - `TAP help` — command reference for the package
  - `TAP reset` — rebuild all windows after screen resizes
  - `TAP fontsize map|communication|status <size>` — per-window font size
  - `TAP font map|communication|status <name>` — per-window font
  - `TAP map|communication|status on|off` — show/hide windows
  - `TAP update` — download/install the latest package, then reload
- **Webclient** (browser) loads a custom plugin adding the same panes: a
  **TAP Map** that captures every map frame exactly as drawn (full ANSI,
  xterm-256 and truecolor support), and a **TAP Comm** pane whose Local/OOC/
  MudInfo tabs mirror the main-window lines — colors included. Font choices,
  active tabs, and window layouts persist between sessions.
- Say/emote/OOC/MudInfo lines and permission-colored names look identical in
  both clients and the main game window.

---

## Commands

**Player:** `skills` · `train` · `score` · `perceive` · `manifest` · `where` · `autowhere` · `mapsize` · `time` · `promptmode` · `emote` · `drop` · `get` · `grid` · `wherekey` · `approach` · `move` · `shove` · `attack` · `fly` · `land` · `sit` · `rest` · `sleep` · `wake` · `lay` · `stand` · `rotate` · `open` · `close` · `lock` · `unlock` · `autoopen` · `changes`

**Account:** `charcreate` · `mychars`

**Builder:** `dig` · `digmenu` · `setorigin` · `attset` · `setskill` · `settrainer` · `setnature` · `setspecies` · `setpose` · `setheight` · `setbuild` · `setadjective` · `setskin` · `seteyes` · `seteyecolor` · `sethair` · `sethaircolor` · `setgender` · `setcanfly` · `setroomsize` · `createfurniture` · `createitem` · `teleport` · `force` · `addchange` · `removechange` · `reload`

---

## Status

- **Phase 1 — Skills, Growth, Rankings:** done
- **Phase 2 — Regen, Rest, Time:** done
- **Phase 3 — Combat:** in progress (attack/damage/accuracy, movement, grid, knockouts; missing armor/equipment, ranged, injuries, knockout state)
- **Phase 4 — Items & Equipment:** in progress (furniture/items typeclass, multi-material descriptions; missing worn gear, stat modifiers, containers, shops)
- **Phase 5 — Custom Character Creation:** in progress (EvMenu chargen done; missing starting skills, sign selection)
- **Phase 6 — World, NPCs, Content & Polish:** planned
- **Client UI — Mudlet package + webclient plugin:** done (map/comm windows, truecolor, TAP commands, persistence, auto-update)

See [`GAMEPLAN.md`](GAMEPLAN.md) for the full build plan and [`DEVELOPMENT.md`](DEVELOPMENT.md)
for the technical reference.
