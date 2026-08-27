"""
In-game changelog data.

Every major change to the game is recorded here as a numbered entry. The
'changes' command reads from this module: bare 'changes' lists what you
haven't read yet, 'changes all' shows everything, and 'changes <number>'
shows one entry in full.

To add a new change simply append a dict with the next number; the on-login
alert and the live server-start broadcast pick it up automatically. The
builder 'addchange' command appends entries for you (numbering and dating
them) and writes them back to this file.
"""

import ast
import datetime

CHANGES_FILE = __file__

CHANGES = [
    {
        "number": 1,
        "date": "2026-07-29",
        "title": "The 5-D world grid",
        "body": (
            "Rooms were stamped with a two-tier coordinate grid: a planetary tier "
            "(planet_x / y / z) and a local subzone tier (site_x / y / z), keyed by "
            "planetary body and site. Each new room knows exactly where it sits in the "
            "world, which lets look, travel and future (weather, astronomy) features "
            "read positions off a room instead of tracking them by hand."
        ),
    },
    {
        "number": 2,
        "date": "2026-07-29",
        "title": "Exit descriptions & a clockwise direction matrix",
        "body": (
            "Exits now carry descriptions so players and staff know where a passage "
            "leads before stepping through. Room exits render in a strict clockwise "
            "order (n, ne, e, se, s, sw, w, nw, up, down, enter, leave) with multiple "
            "entrances grouped grammatically. The cardinal-direction coordinate "
            "stepping behind 'dig' was fixed so x, y, z map to the grid correctly."
        ),
    },
    {
        "number": 3,
        "date": "2026-07-30",
        "title": "Visarial meta-states, perception & manifestation",
        "body": (
            "Objects and characters gained visarial meta-states so they can exist in "
            "the physical world, the visarial world, or both at once. Characters gained "
            "'perceive' to be aware of the other plane from where they stand, and "
            "'manifest' to step fully across. When you halve similar names in a room, "
            "look now only shows the ones on planes you can actually see. A "
            "long-standing bug that stripped color codes while re-capitalizing room "
            "listings was also fixed."
        ),
    },
    {
        "number": 4,
        "date": "2026-08-01",
        "title": "Attributes, derived pools & the live prompt",
        "body": (
            "Nine sub-attributes (Corpus / Genius / Animus across Power, Speed and "
            "Resist) replaced a single stat line, feeding three main attributes whose "
            "derived pools (Vigor, Vim, Mens) and regen rates are computed on the fly "
            "and tracked per character. A new live prompt shows your pools in numbers, "
            "percentages or graphical bars, colored by how damaged the pools are, and "
            "toggles with 'promptmode'. New 'stats' and builder 'attset' commands were "
            "added for viewing and testing them."
        ),
    },
    {
        "number": 5,
        "date": "2026-08-02",
        "title": "Species, appearance phrases, poses & cosmic time",
        "body": (
            "Nine playable species were added, each with its own visarial nature, a "
            "persistent stat bonus, some permanently locked stat columns and hidden "
            "pools. Characters are now described by a three-word appearance phrase ('A "
            "tall and lean, refracting Visarii standing here.') tunable with setheight "
            "/ setbuild / setadjective / setskin. A whitelisted pose system replaced "
            "the stock pose, and a universal 23-hour day / 28-day month / 13-month year "
            "calendar with 13 ruling signs and 3 orbiting planets brought the 'time' "
            "command alive."
        ),
    },
    {
        "number": 6,
        "date": "2026-08-02",
        "title": "Skills, stat growth & rankings",
        "body": (
            "A full progression layer arrived: thirteen skills spanning categories, "
            "each tied to weighted sub-stats, with 0-1000 values across ten tiers "
            "(Novice to Grandmaster). Skills grow through 'use' with diminishing "
            "returns that reward branching, and the stats they feed also grow, capped "
            "by a 14-rank ladder from 'no rank' up to 'ungodly'. The 'skills' command "
            "shows what you know; builders learn or set skills with 'setskill'."
        ),
    },
    {
        "number": 7,
        "date": "2026-08-02",
        "title": "Trainers, alternate stat mains, colored tiers & a spawning area",
        "body": (
            "Trainer NPCs teach skills via the builder 'settrainer', and players learn "
            "them with 'train' once prerequisites are met. Species that lock out a main "
            "stat pivot that column to an alternate (Visarii corpus→animus, Silex "
            "animus→corpus) so no skill is wasted. Rank and tier names gained per-entry "
            "colors, and new characters now home to the Center of Creation, where a "
            "Keeper offers the fundamentals and sets the advanced skills as goals."
        ),
    },
    {
        "number": 8,
        "date": "2026-08-02",
        "title": "Visarial plane & Vim-connection model",
        "body": (
            "The engine for how things sit in the world was unified under a single "
            "'visarial nature' on every object, controlling both the plane it occupies "
            "and its connection to Vim. Physical nature (Silex, plain stones) is "
            "'absolutely disconnected from Vim'; visarial nature (Visarii) glows with a "
            "magenta Vim aura; dual-natured beings carry both descriptions. Perception "
            "is now per-entity and split between see and touch, so what you can "
            "perceive and what you can reach are independent. Builders can override a "
            "prop's nature with 'setnature'."
        ),
    },
    {
        "number": 9,
        "date": "2026-08-03",
        "title": "Realm-aware speech, unified states & staff tools",
        "body": (
            "Speech now follows the planes: your words only land in the realm you "
            "occupy, and a room's characters only hear you if they can see that realm. "
            "Whispering to a named target still crosses the fold. The internal state "
            "naming was unified so every creature's home realm is represented "
            "consistently, and staff gained a global 'force' that can command anyone on "
            "any plane, in any room, whether or not they can see them."
        ),
    },
    {
        "number": 10,
        "date": "2026-08-03",
        "title": "The 'changes' command",
        "body": (
            "This command was added. 'changes' lists the changes you haven't read yet; "
            "'changes all' shows the full history; 'changes <number>' (or 'changes "
            "latest') reads one entry and marks everything up to it as read. When new "
            "changes land, they announce themselves here and at login so nothing is "
            "missed. This is change #10, the one you are reading now."
        ),
    },
    {
        "number": 11,
        "date": "2026-08-03",
        "title": "Added the 'addchange' command",
        "body": (
            "The 'addchange' command was added. This command adds a new change to the "
            "list, applying time, date, and the newest number on the list before "
            "announcing it to the entire server. This is of course restricted to "
            "builder and above, and meant for significant changes only."
        ),
    },
    {
        "number": 12,
        "date": "2026-08-04",
        "title": "Added a builder setgender command",
        "body": (
            "There's now a setgender command for builders. The choices for now are "
            "male, female, and neuter. The first two are obvious. The third describes "
            "something without gender. Using SETGENDER CHOICE, where choice is one of "
            "the three options will set your gender. SETGENDER CHOICE = NAME, will set "
            "a character's gender."
        ),
    },
    {
        "number": 13,
        "date": "2026-08-04",
        "title": "Added an EMOTE command",
        "body": (
            "There is now a fully functional, fairly robust emote command in place. You "
            "can target others and yourself with @target, speak by utilizing quotation "
            "marks, and even declare possessive nouns for yourself with @my. There are "
            "many more examples, and much more thorough directions in HELP EMOTE."
        ),
    },
    {
        "number": 14,
        "date": "2026-08-04",
        "title": "Expanded character appearance system",
        "body": (
            "Looking at a character now shows a detailed, multi-sentence paragraph "
            "describing their appearance instead of a short phrase. The paragraph is "
            "auto-generated from stored attributes: height, build, species, gender, "
            "adjective, eyes, eye colour, hair, hair colour, and skin tone. Each "
            "attribute contributes a sentence; unset attributes are silently omitted. "
            "Pose determines the opening line (e.g. 'Before you stands...' vs 'Before "
            "you sits...'). Four new builder commands were added: seteyes, seteyecolor, "
            "sethair, and sethaircolor. The manual 'desc' is still appended after the "
            "generated paragraph for extra player-written flair."
        ),
    },
    {
        "number": 15,
        "date": "2026-08-04",
        "title": "Guided character creation system",
        "body": (
            "New characters are now created through a step-by-step menu: choose gender, "
            "species, then each appearance option (height, build, adjective, skin "
            "colour, eyes, eye colour, hair, hair colour). Finally, you order the three "
            "main attributes by priority and distribute bonus points (6/4/2) across "
            "their sub-stats. The 'charcreate' command replaces the stock Evennia flow, "
            "and a new 'mychars' command lists all characters on your account."
        ),
    },
    {
        "number": 16,
        "date": "2026-08-05",
        "title": "Builder teleport & custom messages",
        "body": (
            "The teleport command was lowered to Builder permission. Characters now "
            "have teleport locks that control who can teleport to or from them, "
            "defaulting to Admin and above. A new builder 'teleport' command delivers "
            "custom source, destination, and self messages when moving characters "
            "between rooms."
        ),
    },
    {
        "number": 17,
        "date": "2026-08-05",
        "title": "Doors, locks, hidden exits & the build menu",
        "body": (
            "Exits gained a full door system: open, close, lock, unlock, and an "
            "autoopen toggle. Locked doors require a matching key; each locked door "
            "creates one key shared between its two sides. Hidden exits are invisible "
            "until spotted, gated by the new 'awareness' skill. Doors can be breakable, "
            "gated by the new 'bash' skill. The new 'digm' (digmenu) command launches "
            "an interactive build menu for creating rooms and exits with all these "
            "options step by step."
        ),
    },
    {
        "number": 18,
        "date": "2026-08-05",
        "title": "Direction fallbacks",
        "body": (
            "Typing a cardinal direction where no exit exists now attempts to find and "
            "use an exit in that direction, rather than just saying 'no exit'. Exits "
            "named 'north', 'south', etc. (or their aliases 'n', 's', etc.) are "
            "detected dynamically and offered to the player."
        ),
    },
    {
        "number": 19,
        "date": "2026-08-05",
        "title": "Discord ↔ game OOC integration",
        "body": (
            "The OOC channel is now two-way with Discord. In-game OOC messages appear "
            "in the Discord #OOC channel, and messages sent in Discord appear in-game "
            "with a [Discord] tag. Sender names are coloured by permission level both "
            "ways: orange for developers, dark orange for builders, teal for players. "
            "The OOC command was removed; use 'ooc <message>' or the channel alias "
            "instead."
        ),
    },
    {
        "number": 20,
        "date": "2026-08-05",
        "title": "New skills: lockpick, bash, awareness",
        "body": (
            "Three new skills were added to support the door system. 'lockpick' lets "
            "you try to pick a locked door. 'bash' lets you force a door open by brute "
            "strength. 'awareness' lets you detect hidden exits in a room. All three "
            "gate their respective door interactions."
        ),
    },
    {
        "number": 21,
        "date": "2026-08-05",
        "title": "Appearance-based targeting",
        "body": (
            "Any word from a character's appearance description can now be used to "
            "target them. When multiple characters share the same description, Evennia "
            "shows numbered labels like [virentes-1] and [virentes-2] so you can select "
            "a specific one. The search checks name, aliases, then appearance paragraph "
            "words in order."
        ),
    },
    {
        "number": 22,
        "date": "2026-08-05",
        "title": "Character creation improvements",
        "body": (
            "The chargen menu now shows a welcome screen with 'Press ENTER to "
            "continue...' before starting. Skin, eye, and hair colour options are "
            "displayed in their actual colour so you can see what you're choosing. "
            "Species help entries can be browsed with the '?N' command at any species "
            "prompt, showing a full description, nature, stat bonus, and locked traits."
        ),
    },
    {
        "number": 23,
        "date": "2026-08-05",
        "title": "Account and permission fixes",
        "body": (
            "Character slots were overridden: players get 3, builders and above get 4. "
            "The 'mychars' command was fixed to work with the account system. The "
            "'charcreate' command now defers character creation until the final step. "
            "Permission checks now use lowercase strings and account-level lookups. The "
            "OOC channel name is displayed in white, and sender names are coloured by "
            "permission level in-game."
        ),
    },
    {
        "number": 24,
        "date": "2026-08-06",
        "title": "Added REMOVECHANGE and added to Discord Bot",
        "body": (
            "Successfully added the CHANGES command to the Discord announce bot. They "
            "will now dump into the 'system' channel on the official Discord server. "
            "Also added in a REMOVECHANGES command, and elevated both to admin level "
            "permissions."
        ),
    },
    {
        "number": 25,
        "date": "2026-08-06",
        "title": "SKILLS ALL added to the SKILLS command",
        "body": (
            "The new SKILLS ALL option of the SKILLS command will list all skills that "
            "are coded, or at the very least defined in the game. Not all of them have "
            "function yet, and there are still an absolute ton to come."
        ),
    },
    {
        "number": 26,
        "date": "2026-08-07",
        "title": "Skill categories & strict weighting rules",
        "body": (
            "Skills were fully reorganized into three main categories: Corpus, "
            "Genius, and Animus, determined by the major contributing sub-statistic. "
            "Strict weighting rules were established: single-stat skills take 100%, "
            "two-stat skills require a 55/45 minimum split favoring the major stat, "
            "and three-stat skills require a 40%+ major stat that strictly outranks "
            "minor and extra contributors, all summing to 100%."
        ),
    },
    {
        "number": 27,
        "date": "2026-08-07",
        "title": "Teleport fixes, MudInfo auto-subscriptions & custom reload",
        "body": (
            "Teleporting no longer triggers double announcement readouts. All "
            "existing and newly created player accounts are now automatically "
            "subscribed to the MudInfo channel by default so everyone receives "
            "system announcements. A custom @reload/@restart command was added "
            "to broadcast restart warnings immediately in real time."
        ),
    },
    {
        "number": 28,
        "date": "2026-08-09",
        "title": "MapSize command update",
        "body": (
            "Modified the MAPSIZE command to accept numeric input from 3 to 25, instead "
            "of toggling between small, medium, and large."
        ),
    },
    {
        "number": 29,
        "date": "2026-08-09",
        "title": "Combat System: Movement & Rendering",
        "body": (
            "The combat foundation is in place. Movement and map rendering are fully "
            "functional. Combat loops, grouping, targeting, and tactical systems remain "
            "in development."
        ),
    },
    {
        "number": 30,
        "date": "2026-08-09",
        "title": "Group System: Foundation",
        "body": (
            "Foundation for group and party management systems has been added. This "
            "system is currently under active development and not yet functional."
        ),
    },
    {
        "number": 31,
        "date": "2026-08-09",
        "title": "Grid movement, navigation & map rendering",
        "body": (
            "Characters now move on a per-room grid with x, y, z coordinates. "
            "The 'move' command navigates across the grid at a paced rate (6 grids "
            "per round), and a combat loop drains the movement queue each tick. "
            "The 'approach' command lets you track a moving target, recalculating "
            "their position every tick. A minimap renders around you showing "
            "exits, other characters, hostile targets, and your own position. "
            "Custom room sizes are supported via the builder 'setroomsize' command."
        ),
    },
    {
        "number": 32,
        "date": "2026-08-09",
        "title": "Door mechanics, proximity checks & doorway blocking",
        "body": (
            "Door commands (open, close, lock, unlock) now require you to be "
            "standing at the door's grid coordinate before operating it. If the "
            "other side of a door is occupied, traversal is blocked with a message "
            "showing who is in the way. Looking at a door shows who is standing "
            "just on the other side. The 'autoopen' toggle works with navigation "
            "to open unlocked doors without stopping."
        ),
    },
    {
        "number": 33,
        "date": "2026-08-09",
        "title": "SHOVE command & through-exit mechanics",
        "body": (
            "The 'shove' command pushes a character or object in the opposite "
            "direction from you. Diagonal pushes are supported. If the target is "
            "standing on an exit and you are pushing them toward it (aligned "
            "direction), they are shoved through to the other room. Shoving into "
            "a closed door bounces them into it. You can target characters on the "
            "other side of an exit by name, species, or appearance, and shove them "
            "away from the doorway. The 'door' keyword works with open, close, "
            "lock, and unlock to target the nearest door automatically."
        ),
    },
    {
        "number": 34,
        "date": "2026-08-09",
        "title": "Map coordinates display",
        "body": (
            "The minimap now shows your x, y, and z coordinates on the right "
            "side of the bottom rows, using colored labels for easy reading."
        ),
    },
    {
        "number": 35,
        "date": "2026-08-11",
        "title": "Combat system: attack, actions, accuracy & damage",
        "body": (
            "The combat engine is now functional. The 'attack' command (and "
            "aliases punch, kick, headbutt, knee, axehandle, haymaker) queues "
            "up to 3 actions per round. Each action costs time from a 6-second "
            "round and pool points (Mens for brawling). Hit resolution rolls "
            "attack vs defense using skill values, with critical hit chance. "
            "Damage is calculated from skill, stat weights, and damage type, "
            "then reduced by the target's armor. Health bars (Vigor, Vim, Mens) "
            "take damage and a knock-out threshold exists. The combat loop "
            "drains the action queue each tick and resolves attacks in order."
        ),
    },
    {
        "number": 36,
        "date": "2026-08-11",
        "title": "Skill overhaul: brawling tree, precursor chains & combat stats",
        "body": (
            "The skill system was restructured with a precursor chain model. "
            "Brawling is the foundation governing all unarmed combat. Offense "
            "skills form a tree: punch and kick lead to headbutt and knee, "
            "which lead to axehandle, which leads to haymaker. A new defense "
            "tree covers melee evasion, parry, block, feint and counterattack. "
            "Every skill now carries combat properties: reach (grid distance), "
            "damage type (physical/psychic/magical), health bar target, base "
            "time cost, and pool cost per use. Time cost decreases with skill "
            "level. Old generic skills (dodge, parry, attack, block, "
            "power_strike) were replaced by the new trees."
        ),
    },
    {
        "number": 37,
        "date": "2026-08-11",
        "title": "Pool regeneration, furniture healing & species pool routing",
        "body": (
            "A 1-minute regeneration tick now runs in the combat loop for every "
            "character in an active room. Regeneration rate scales with pose: "
            "sleeping grants 2x, resting/laying/sitting grant 1.5x. Furniture "
            "quality adds a multiplier on top (e.g. quality 1.0 doubles regen). "
            "Zeroed pools for species are routed through locked alternates via "
            "the new resolve_pool function, so Silex and Visarii regeneration "
            "respects their stat locks."
        ),
    },
    {
        "number": 38,
        "date": "2026-08-11",
        "title": "Furniture system & createfurniture command",
        "body": (
            "A new Furniture typeclass supports multi-tile objects with grid "
            "footprints, configurable dimensions (1x1, 1x2, 1x3, 2x2), "
            "facing, rotation, seat counts, quality ratings, and allowed "
            "states (sit, rest, lay, sleep). Furniture automatically seats "
            "occupants when dropped, placing them on free tiles. The builder "
            "createfurniture command walks through all options interactively: "
            "name, blocks-movement, seats, dimensions, states, and quality. "
            "Furniture is searchable by material description in room listings."
        ),
    },
    {
        "number": 39,
        "date": "2026-08-11",
        "title": "Item system: multi-material truecolor descriptions",
        "body": (
            "A new Item typeclass extends Furniture with truecolor material "
            "descriptions. Items carry one or two materials (each with a color), "
            "an adjective, and a base name. The display name is auto-generated: "
            "'a brown leather, sturdy couch' with each material rendered in its "
            "actual hex color. The builder createitem command walks through type, "
            "base name, materials, colors, adjectives, and furniture options. "
            "Item descriptions show in room listings, action messages, and "
            "anywhere the item is referenced."
        ),
    },
    {
        "number": 40,
        "date": "2026-08-11",
        "title": "Furniture-aware pose commands & plane-aware drop",
        "body": (
            "New player commands: sit, rest, sleep, lay, stand, and rotate. "
            "Each detects nearby furniture, validates allowed states, finds a "
            "free seat, and moves the character onto it. Standing finds an "
            "adjacent free spot. Wake now detects if you are on furniture and "
            "keeps you there instead of saying 'lie on the ground'. Drop is "
            "now a custom command: dropping furniture auto-seats you and sends "
            "a single combined message. All drop messages are plane-aware: "
            "observers who cannot see the item see nothing; those who see the "
            "item but not the dropper see the item appear without naming them."
        ),
    },
    {
        "number": 41,
        "date": "2026-08-11",
        "title": "Sleep mechanics: blocked commands & perception",
        "body": (
            "Sleeping now has real consequences. While sleeping, all commands "
            "are blocked except wake, score, stats, quit and help. Sleeping "
            "characters cannot perceive either the physical or visarial plane "
            "and cannot hear anything. The combat loop stays active while "
            "someone in the room is sleeping to support regeneration."
        ),
    },
    {
        "number": 42,
        "date": "2026-08-11",
        "title": "Coordinate teleport & movement improvements",
        "body": (
            "The builder teleport command now supports grid coordinates: "
            "'teleport 5 3' or 'teleport 5 3 2' for z-level, and "
            "'teleport target = 5 3' to teleport another character. Finding "
            "the nearest unoccupied coordinate is automatic. Movement now "
            "requires a standing pose; you must stand before walking. "
            "Multi-tile objects (furniture) use footprint collision instead "
            "of a single tile, so a 1x3 couch blocks three tiles properly."
        ),
    },
    {
        "number": 43,
        "date": "2026-08-11",
        "title": "Autowhere gating & map renderer updates",
        "body": (
            "The autowhere minimap now only updates when your position "
            "actually changes, not on every pose or state change. A new "
            "check_autowhere method compares location and coordinates before "
            "and after any action, firing only on real movement. The map "
            "renderer now displays items and furniture on the grid using "
            "their material colors. Characters sitting on furniture are shown "
            "on the furniture's tile. The minimap respects multi-tile "
            "footprints for proper collision display."
        ),
    },
    {
        "number": 44,
        "date": "2026-08-11",
        "title": "Room furniture display & skill storage migration",
        "body": (
            "Room descriptions now show characters 'on' furniture by name "
            "rather than listing furniture as a separate object. Occupied "
            "furniture is hidden from the things list; unoccupied furniture "
            "shows with its full material description. Skills have been "
            "migrated from attribute properties to a persistent db.skills "
            "dict for reliability. The skill value floor is now 1 (Novice) "
            "instead of 0. The train command no longer displays '0%' for "
            "newly learned skills."
        ),
    },
    {
        "number": 45,
        "date": "2026-08-19",
        "title": "Realm-shove contests on manifest",
        "body": (
            "Manifesting or withdrawing across realms onto a spot already held "
            "by someone in that realm now triggers a contest. Both parties roll "
            "their realm's stat (Corpus in the physical, Animus in the "
            "visarial) plus a d10: a 1 is a fumble and subtracts 10, a 10 "
            "explodes and rolls again. The loser is shoved off the seat when a "
            "seat is claimed underfoot, or shoved a random step back on open "
            "ground, keeping zeroed-stat species in the running. The crossing "
            "itself is announced: you blink into existence folding outward "
            "from a point, or blink out of existence folding inward before "
            "vanishing, and on a contested crossing onlookers see the loser "
            "shoved a compass direction. Roll totals are never shown. Pose "
            "changes (sit, rest, sleep, lay, stand) now also follow "
            "observational rules - only creatures that share your realm or "
            "perceive it see them. The manifest help file covers the contest "
            "rules."
        ),
    },
    {
        "number": 46,
        "date": "2026-08-19",
        "title": "Movement speed, pathfinding, and echo rework",
        "body": (
            "Movement now has three speed tiers: walk (3s/tile), jog (2s/tile), "
            "and run (1s/tile). Use the WALK, JOG, and RUN commands to switch "
            "speeds. Flight speeds scale accordingly: slowly, briskly, recklessly.\n\n"
            "Two new opt-in toggles:\n"
            "  AUTONAVIGATE - enables BFS pathfinding to route around furniture "
            "and obstacles. When blocked, your character automatically finds the "
            "shortest path around. Detours are announced to observers.\n"
            "  AUTOFLY - when grounded and blocked, automatically takes off, "
            "flies over the obstacle, and lands on the other side.\n\n"
            "Both are off by default. Movement echoes have been reworked: "
            "observers now see directional messages (\"walks to his east, "
            "toward you\") instead of destination-revealing ones. Arrival "
            "messages list only adjacent creatures and objects in a room-"
            "objects-style list. One-step navigation (move n, approach) "
            "remains greedy and unaffected by autonavigate.\n\n"
            "ETA now reflects your actual speed tier (walk = 3x base, "
            "jog = 2x, run = 1x). Arrival lists show what's at your "
            "actual landing position, not the navigation target. Occupied "
            "destinations now correctly arrive beside the occupant instead "
            "of blocking.\n\n"
            "The |D color-wrap bug on furniture names (visible in arrival "
            "and detour messages) has been fixed by removing the "
            "narrative_name/furniture_name wrappers and using "
            "appearance_name directly, matching the pattern used by "
            "APPROACH and SIT/STAND."
        ),
    },
    {
        "number": 47,
        "date": "2026-08-21",
        "title": "Custom client UI for Mudlet & webclient",
        "body": (
            "Mudlet auto-installs an updated package: Map and Communication "
            "windows, a bottom prompt bar, TAP help/reset/fontsize/font/on|off/"
            "update commands, saved fonts and layouts, and a self-updater. The "
            "browser webclient gains matching TAP Map/Comm panes with full "
            "truecolor rendering. All autowhere paths now push map updates to "
            "every client, and say/emote/OOC/MudInfo lines - including "
            "permission-colored names - render identically everywhere."
        ),
    },
    {
        "number": 48,
        "date": "2026-08-26",
        "title": "Eastern server time, Discord daily logs and time display overhaul",
        "body": (
            "Real server time is now Eastern (America/New_York, DST-aware) instead of "
            "fixed UTC-5. Added ZoneInfo handling in world/data/calendar.py "
            "(eastern_now, eastern_today_str, format_eastern) and a new Server Time "
            "section in the time command showing Eastern date/time without signs or "
            "notes, while cosmic and local clocks remain. Discord OOC/MudInfo now share "
            "per-channel daily ansi code blocks on Eastern date headers (yellow Eastern "
            "(UTC-5) with cont. part handling), constant blueish-black background, and "
            "8-color ANSI fallback (bold stripped, 30 gray vs 37 white distinct, 90-97 "
            "mapped). Channel tags use white brackets with red MudInfo and cyan OOC "
            "names in-game and on Discord. All game-to-Discord webhook posts use TAP as "
            "sender with sender name colored inside the block. Discord user OOC "
            "messages are immediately deleted (Manage Messages) and mirrored into the "
            "same daily code block with Eastern magenta HH white colon magenta MM "
            "timestamp and [Discord] tag, text-only. Fixed ServerConfig _SaverDict "
            "handling that caused new block per message. MudInfo system channel was "
            "cloned to clear history and webhook recreated; OOC was manually cleared; "
            "ServerConfig daily log keys reset for a fresh Eastern start."
        ),
    },
    {
        "number": 49,
        "date": "2026-08-26",
        "title": "Account main menu, OOC lounge and wisp system",
        "body": (
            "Login now lands in an account-level main menu - the first and last screen "
            "you see. Options: 0 Exit (disconnect), 1 Choose character (shows count, "
            "handles 0), 2 Create character (shows used/total slots from "
            "get_character_slots, blocks when full), 3 Delete character (wisp excluded, "
            "confirm yes), 4 Go to the lounge (OOC as wisp). "
            "AUTO_CREATE_CHARACTER_WITH_ACCOUNT and AUTO_PUPPET_ON_LOGIN are disabled; "
            "the menu is shown via Account.at_post_login with a short delay and "
            "auto_quit disabled. Wisp is a pseudo-species wisp (locked "
            "corpus/genius/animus, zeroed vigor/vim/mens) sharing the account name, "
            "living only in Limbo #2 flagged OOC_Room (is_ooc_room + ooc_room tag), not "
            "deletable (delete:false) and not counted toward slots. A new Light block "
            "in world/data/colors.py (white-light, gold-light, azure-light, "
            "violet-light, ember-light, cyan-light, rose-light, silver-light, "
            "ice-light, clear-light, amber-light, crimson-light) backs it, and "
            "world/data/appearance.py gains WISP_SIZES "
            "small/modest/middling/large/immense (person-relative, not tiny), 15 wisp "
            "adjectives (flickering, pulsing, steady, wavering, brilliant, dim, "
            "humming, cold, warm, prismatic, soft, sharp, echoing, hazy, lambent) with "
            "descriptions and Light skin tones, plus hovering pose. typeclasses/wisp.py "
            "(Wisp) overrides plane visibility to see/hear/touch everything in the OOC "
            "lounge and hides pools/prompt. world/systems/wisp.py provides get_wisp, "
            "get_or_create_wisp, non_wisp_characters, is_ooc_room and wisp_needs_setup "
            "(now strict valid_skin/valid_adjective/valid_wisp_size) so converted "
            "legacy characters correctly prompt for wisp setup. Legacy same-named "
            "characters are migrated on login via Account._migrate_legacy_wisp "
            "(swap_typeclass to Wisp, move to #2) and stale int refs like 102 are "
            "cleaned. Single-puppet rule enforced (MULTISESSION_MODE 0); quit/ooc/exit "
            "while puppeted now unpuppet to the main menu via "
            "commands/account/menu_commands.py (only menu 0 disconnects), ic removed "
            "from AccountCmdSet and CharacterCmdSet, OOC remains a channel. Puppeting "
            "via the menu now fires prompt (get_prompt) and is_autowhere map "
            "(send_autowhere) once at menu exit, and DefaultCharacter.at_post_puppet "
            "already does You become + look so no double look. Choose/delete lists now "
            "show a single b/back Back and no quit/exit/q grid entries. Discord MudInfo "
            "daily ansi codeblock overflow now correctly creates cont. part 2 when the "
            "2000-char block is full (was truncating), and the live new-change "
            "broadcast no longer includes Type changes to read whats new in the MudInfo "
            "codeblock - that hint stays in-game via changes.alert_text and the MudInfo "
            "channel display only, since Discord users cannot run the command."
        ),
    },
]


def all_changes():
    """All changelog entries, oldest first."""
    return list(CHANGES)


def latest_number():
    """The highest change number recorded."""
    return CHANGES[-1]["number"] if CHANGES else 0


def get_change(number):
    """Return the entry with this number, or None."""
    for change in CHANGES:
        if change["number"] == number:
            return change
    return None


def unread(last_read):
    """Entries the account has not read yet (number > last_read)."""
    return [c for c in CHANGES if c["number"] > last_read]


def alert_text(last_read):
    """The login/announce alert for an account with 'last_read' changes, or
    None if it is fully caught up."""
    pending = unread(last_read)
    if not pending:
        return None
    newest = pending[-1]
    rest = len(pending) - 1
    count = f" (+{rest} more)" if rest else ""
    return (
        f"|y*** New change: #{newest['number']} |w{newest['title']}|n{count}|n\n"
        f"Type |wchanges|n to read what's new."
    )


_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def _split_date(date_str):
    year, month, day = (int(p) for p in date_str.split("-"))
    return year, month, day


def short_date(date_str):
    """Short form date for list rows, e.g. 'Aug 3'."""
    year, month, day = _split_date(date_str)
    return f"{_MONTHS[month - 1][:3]} {day}"


def full_date(date_str):
    """Long form date for a detail view, e.g. 'August 3, 2026'."""
    year, month, day = _split_date(date_str)
    return f"{_MONTHS[month - 1]} {day}, {year}"


def _q(text):
    """A double-quoted Python string literal with quotes/backslashes escaped."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _wrap_string(text, width=74):
    """Split a body into lines of roughly 'width' characters on word bounds."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        candidate = f"{cur} {word}".strip()
        if len(candidate) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    return lines


def _serialize(entry):
    """Render one entry as Python source in the style of CHANGES."""
    chunks = _wrap_string(entry["body"])
    if len(chunks) == 1:
        body_block = [f'        "body": {_q(chunks[0])},']
    else:
        body_block = ['        "body": (']
        for chunk in chunks[:-1]:
            body_block.append(f"            {_q(chunk + ' ')}")
        body_block.append(f"            {_q(chunks[-1])}")
        body_block.append("        ),")
    block = [
        "    {",
        f'        "number": {entry["number"]},',
        f'        "date": {_q(entry["date"])},',
        f'        "title": {_q(entry["title"])},',
    ] + body_block + ["    },"]
    return "\n".join(block)


def _insert(entry_block, source):
    """Insert a serialized entry before the closing bracket of CHANGES."""
    tree = ast.parse(source)
    end = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CHANGES" for t in node.targets
        ):
            end = node.value.end_lineno
            break
    if end is None:
        raise ValueError("Could not locate the CHANGES list.")
    lines = source.splitlines()
    lines[end - 1:end - 1] = [entry_block]
    return "\n".join(lines) + "\n"


def append_entry(title, body, filepath=None):
    """Append a new, auto-numbered change dated today, persisting it to the
    changelog file and to the in-memory list. Returns the new entry. Pass a
    custom 'filepath' (tests) to avoid touching the real file."""
    title = " ".join(str(title).strip().split())
    body = " ".join(str(body).strip().split())
    if not title:
        raise ValueError("A title is required.")
    if not body:
        raise ValueError("A body is required.")
    entry = {
        "number": latest_number() + 1,
        "date": datetime.date.today().isoformat(),
        "title": title,
        "body": body,
    }
    path = filepath or CHANGES_FILE
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(_insert(_serialize(entry), source))
    CHANGES.append(entry)
    return entry


def remove_entry(number, filepath=None):
    """Remove change #number, renumber remaining entries sequentially from 1,
    and persist changes to the changelog file and in-memory list.
    Returns the removed entry."""
    found = None
    for entry in CHANGES:
        if entry["number"] == number:
            found = entry
            break
    if not found:
        raise ValueError(f"There is no change #{number}.")

    CHANGES.remove(found)
    for i, entry in enumerate(CHANGES, start=1):
        entry["number"] = i

    path = filepath or CHANGES_FILE
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    assign_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CHANGES" for t in node.targets
        ):
            assign_node = node
            break
    if assign_node is None:
        raise ValueError("Could not locate the CHANGES list.")

    entries_code = "\n".join([_serialize(e) for e in CHANGES])
    new_changes_block = f"CHANGES = [\n{entries_code}\n]"

    lines = source.splitlines()
    start_line = assign_node.lineno - 1
    end_line = assign_node.end_lineno
    lines[start_line:end_line] = [new_changes_block]

    new_source = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_source)

    return found

