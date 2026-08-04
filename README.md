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

### Definitions & Lore
Abyss: The darkness between the stars. The place where the Planes dance around Mundus, never drifting far from their Sol. A desolate and lifeless place that requires some sort of protective medium to travel through for most life. There are however, exceptions. Eldritch, unspeakable horrors do sometimes call the vast empty of the Abyss home.

Mundus: The known Universe, and all the realms within it. It's was once thought that the edge of it was a solid mass of stars, meant to contain all of the Realms. Since scholars have started to explore and study the Abyss, this sentiment has shifted towards one that posits that it could be endless, limited only by our perception of the realms.

Planes: Planetary bodies that orbit around a central star. There are several known within Mundus. Some of them support life, while others do not. There are even some that do not exist within the Physical Realm, and are only seen by those that can perceive the Visarial Realm.

Vim: This is the energy force that binds all things together, whether they display any connection to it, or not. It's the stuff that pours out of whatever is beyond existence to give life to it, and then flows out into all living and non-living entities.

Vis: Force, power, and natural energy. This is the expression, the very actions one takes that are fueled by pure Vim. Vis can take endless forms. Whether it's coming from the hands of a direct wielder of Vim, or Vim-fueled contraptions and devices of all shapes and sizes. There are many schools of thought dedicated to the study manipulating Vim into Vis.

Visarial Realm: The realm of Vim. This is the first realm that's known of where Vim pours in from beyond existence. It seems to be layered on top of the Physical Realm, sharing landscapes and even structures in some places, but does not follow all of the rules of physics that have been discovered so far within the Physical Realm. The first of the sentient species within existence were born within this realm, and a great number of entities call it home. Some can interact with the Physical Realm under certain circumstances, while others are bound to it entirely.

Physical Realm: The known Planes of existence. This is where most life that is not pure-Vim lives out it's time within Mundus. Everything here is subject to the discovered laws of physics and entropy, although any of these forces can be manipulated through Vis.

Vistronics: The branch of technology and engineering dealing with the control, manipulation, and utilization of Vim flow through circuits, nodes, and conductive mediums.
    * Visographer: One that creates Vistronic circuit boards and components that are made by etching or engraving copper, glass, or stone channels for the magic to flow through.
        * Visography: The practice of writing, etching, or coding spell-arrays into Vistronic components. (Real-world equivalent: Programming / Cryptography).

Vismechanics: Mechanical systems driven by physical Vim pressure, gears, and kinetic energy.
    * Viswright: One that designs and engineers mechanical contraptions that are powered by Vim. Basic contraptions may not require a skilled Visographer to create vistronic components for them, though most advanced ones may require several devices.

Viskinetics: The study and application of Vim to generate heavy physical force, torque, and motion. This school of thought is what creates the devices that power most Vistronics and Vismechanical devices and contraptions.
    * Visicist: A scholar that has dedicated themselves to the study of the flow of Vim and processing it into practical physical application, or, Vis.

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
`setnature` · `setspecies` · `force`

---

## Status

- **Phase 1 — Skills, Growth, Rankings:** done
- **Phase 2 — Regen, Rest, Time:** in progress
- **Phase 3 — Combat; Phase 4 — Items; Phase 5 — Custom creation; Phase 6 — World & polish:** planned

See [`GAMEPLAN.md`](GAMEPLAN.md) for the full build plan and [`DEVELOPMENT.md`](DEVELOPMENT.md)
for the technical reference.