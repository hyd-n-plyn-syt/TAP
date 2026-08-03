# The Abyssal Planes

A text-based MUD built with [Evennia](https://www.evennia.com). Currently in development
and playable over telnet.

**Live:** telnet `theabyssalplane.duckdns.org:4000` — website/webclient
`http://theabyssalplane.duckdns.org` (web on port 80).
**Local:** telnet `localhost:4000` — website/webclient `http://localhost`.

Every soul is born into one of nine species on the planes. Characters have no
levels or XP grind — growth comes purely from **using skills**, and the world is
split across the **physical** realm and the **visarial** (the realm of Vim),
which only some can perceive.

Below is an overview of the systems we've built on top of the stock Evennia
feature set. For the full technical reference (commands, modules, gotchas),
see [`DEVELOPMENT.md`](DEVELOPMENT.md); the living build-order and design
doc is [`GAMEPLAN.md`](GAMEPLAN.md).

## Systems Overview

### Visarial Planes & Vim Connection
Every object and character has a `visarial_nature` that sets both its **plane**
and its **connection to Vim**:

| Nature        | Plane        | Of Vim | Description             | Seen via |
|---------------|--------------|--------|-------------------------|----------|
| **physical**  | physical     | no     | Physical desc only      | physical only |
| **visarial**  | visarial     | yes    | Visarial desc / Magenta aura | visarial |
| **dual-natured** | physical (default) | both | Physical *and* visarial desc | both, by state |

- `perceive` (yellow) to be aware of the other plane while staying put; `manifest`
  (cyan) to cross into it. Silex can do neither.
- Visibility is per-entity and split into *see* vs *touch* (`can_phys_see`,
  `can_vis_see`, `can_phys_touch`, `can_vis_touch`), so what you can perceive and
  what you can reach are independently controlled.
- Vim-connected things radiate a magenta aura; physical things read as
  "absolutely disconnected from Vim."
- Builders set a prop's nature with `setnature`.

### The 5D Room Grid
Rooms are stamped with a two-tier coordinate grid (planet-level and subzone-level)
so `dig` and `setorigin` place them in a world automatically, and `look` renders
nearby neighbors in clockwise order with grammatical exit grouping.

### Species, Appearance & Pose
- **9 playable species** with their own visarial nature, a persistent stat bonus,
  some locked stat columns (remapped to an alternate main), hidden pools, and
  perception rules.
- Characters are described by a **three-word appearance phrase** ("A tall and
  lean, refracting Visarii standing here.") instead of a name, with builder
  helpers to set height / build / adjective / skin.
- A whitelisted **pose system** replaces the stock `pose`, used to group room
  occupants and later feed combat/action.

### Stats, Skills & Growth
- **9 sub-stats** (Corpus / Genius / Animus × Potestas / Reflexus / Obsistis)
  driving derived mains (Vigor / Vim / Mens) and rank ladders.
- **Skills 0-1000 across 10 tiers**, learned from trainers and gated by
  prerequisites; using a skill feeds it and its linked stats, with diminishing
  returns to push branching.
- **Level-less, nothing to bank** — you grow purely by using what you know.

### Cosmic Time
A universal 23-hour / 28-day / 13-month calendar anchored to the cradle world
Auridon, with 13 ruling signs and 3 orbiting planets. `time` shows universal and
local dates resolved from the rooms a map.

### Live Prompt
A colorful command-refresh prompt with `numbers` / `percent` / `bars` modes,
showing your pools and current plane/fold state.

---

## Commands

**Player:** `skills` · `train` · `score` · `perceive` · `manifest` · `setpose` ·
`setheight` · `setbuild` · `setadjective` · `setskin` · `time` · `promptmode`
(player `pmode`)

**Builder:** `dig` · `setorigin` · `attset` · `setskill` · `settrainer` ·
`setnature` · `setspecies`

---

## Status

- **Phase 1 — Skills, Growth, Rankings:** done
- **Phase 2 — Regen, Rest, Time:** in progress
- **Phase 3 — Combat; Phase 4 — Items; Phase 5 — Custom creation; Phase 6 — World & polish:** planned

See [`GAMEPLAN.md`](GAMEPLAN.md) for the full build plan and [`DEVELOPMENT.md`](DEVELOPMENT.md)
for the technical reference.