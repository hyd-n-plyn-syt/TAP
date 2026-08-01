"""
File-based help entries for the attribute and derived-pool system.

Loaded automatically via the default setting
``FILE_HELP_ENTRY_MODULES = ["world.help_entries"]``.
"""

HELP_ENTRY_DICTS = [
    {
        "key": "prompt",
        "category": "General",
        "aliases": ["promptmode", "pmode"],
        "text": """
|wPrompt|n

Your client prompt shows your three pools (Vigor, Vim, Mens) along with
your current visarial state. It refreshes after every command and whenever
your pools or state change.

|wPrompt Styles|n
  numbers - Vigor: 16/16  Vim: 16/16  Mens: 16/16  [physical]
  percent - Vigor: 100%   Vim: 100%   Mens: 100%   [physical]
  bars    - Vigor: [##########]  Vim: [##########]  Mens: [##########]

Use |wpromptmode|n to switch styles (no argument cycles through them).

See also: |wstats|n, |wattributes|n.
""".strip(),
    },
    {
        "key": "attributes",
        "category": "General",
        "aliases": ["attribute", "stats"],
        "text": """
|wThe Abyssal Planes - Attributes|n

Every character is defined by nine |wsub-attributes|n gathered into three
|wmain attributes|n. Together they drive your derived pools: Vigor
(physical durability), Vim (magical containment) and Mens (mental
capacity).

|wThe Three Main Attributes|n
  |wCorpus|n   - the body
  |wGenius|n   - the mind
  |wAnimus|n   - the spirit

Each main attribute is the |wsum|n of the three sub-attributes beneath it.
Every sub-attribute is one of three |waspects|n:

  |wPotestas|n (Power)  - raw output and capability; builds big pools
  |wReflexus|n (Speed)  - agility and recovery; speeds regeneration
  |wObsistis|n (Resist) - toughness and endurance; the backbone of every pool

|wThe Nine Sub-Attributes|n
  Corpus Potestas   - raw physical power
  Corpus Reflexus   - physical agility and coordination
  Corpus Obsistis   - physical toughness and durability

  Genius Potestas   - analytical power and intellect
  Genius Reflexus   - reaction speed and quick thinking
  Genius Obsistis   - mental resilience and focus

  Animus Potestas   - spiritual power output
  Animus Reflexus   - rapid visualization and channeling
  Animus Obsistis   - spiritual fortitude

Use |wstats|n to view your attributes. See also help on |wcorpus|n,
|wgenius|n, |wanimus|n, |wpotestas|n, |wreflexus|n, |wobsistis|n, |wvigor|n,
|wvim|n and |wmens|n.
""".strip(),
    },
    {
        "key": "corpus",
        "category": "General",
        "aliases": ["body"],
        "text": """
|wCorpus - The Body|n

Corpus is your physical being. It is the |wsum|n of three sub-attributes:

  |wCorpus Potestas|n - raw physical power
  |wCorpus Reflexus|n - agility and coordination
  |wCorpus Obsistis|n - toughness and durability

A high Corpus makes you physically imposing: harder to hurt, slower to tire.
It feeds your physical durability (|wVigor|n).

See also: |wgenius|n, |wanimus|n, |wvigor|n, |wattributes|n.
""".strip(),
    },
    {
        "key": "genius",
        "category": "General",
        "aliases": ["mind"],
        "text": """
|wGenius - The Mind|n

Genius is your intellect. It is the |wsum|n of three sub-attributes:

  |wGenius Potestas|n - analytical power
  |wGenius Reflexus|n - reaction speed
  |wGenius Obsistis|n - mental resilience and focus

A high Genius keeps you sharp and quick-witted. Its resilience bolsters your
mental capacity (|wMens|n) and stabilizes your other pools.

See also: |wcorpus|n, |wanimus|n, |wmens|n, |wattributes|n.
""".strip(),
    },
    {
        "key": "animus",
        "category": "General",
        "aliases": ["spirit"],
        "text": """
|wAnimus - The Spirit|n

Animus is your spiritual presence. It is the |wsum|n of three sub-attributes:

  |wAnimus Potestas|n - spiritual power output
  |wAnimus Reflexus|n - rapid visualization and channeling
  |wAnimus Obsistis|n - spiritual fortitude

A high Animus strengthens your connection to supernatural forces and
determines how much magic you can contain (|wVim|n).

See also: |wcorpus|n, |wgenius|n, |wvim|n, |wattributes|n.
""".strip(),
    },
    {
        "key": "potestas",
        "category": "General",
        "aliases": ["power"],
        "text": """
|wPotestas - Power|n

Potestas governs raw output - the power you can project in a given realm.
It does not speed recovery; instead it adds direct capacity to your pools:

  Corpus Potestas - raw physical power; adds capacity to |wVigor|n
  Genius Potestas - analytical power; adds capacity to |wMens|n
  Animus Potestas - spiritual power output; adds capacity to |wVim|n

A Potestas-heavy character has a |wgrowing|n pool but recovers slowly.
See |wreflexus|n for the opposite trade-off.
""".strip(),
    },
    {
        "key": "reflexus",
        "category": "General",
        "aliases": ["speed"],
        "text": """
|wReflexus - Speed|n

Reflexus governs agility and recovery. It does not grow your pools;
instead it accelerates your regeneration:

  Corpus Reflexus - physical coordination; speeds |wVigor|n recovery
  Genius Reflexus - reaction speed; speeds |wMens|n recovery
  Animus Reflexus - channeling speed; speeds |wVim|n recovery

A Reflexus-heavy character has a smaller pool but recovers far faster.
See |wpotestas|n for the opposite trade-off.
""".strip(),
    },
    {
        "key": "obsistis",
        "category": "General",
        "aliases": ["resist"],
        "text": """
|wObsistis - Resist|n

Obsistis governs toughness and endurance - how much you can take. It forms
the engine of your pools and fuels your regeneration:

  Corpus Obsistis - physical durability
  Genius Obsistis - mental resilience (and stabilizer of Vigor and Vim)
  Animus Obsistis - spiritual fortitude

Obsistis is the backbone of every pool formula. See |wvigor|n, |wvim|n
and |wmens|n.
""".strip(),
    },
    {
        "key": "vigor",
        "category": "General",
        "aliases": ["hp", "health"],
        "text": """
|wVigor - Physical Durability|n

Vigor is your physical pool - your health. When it is exhausted, you fall.
It is |wderived|n from your attributes and is never stored directly.

|wDerivation|n
  Vigor = ((Corpus + Corpus Obsistis) * 3)
          + ((Corpus Potestas + Genius Obsistis) * 2)

Your whole physical being (|wCorpus|n) and your physical toughness
(|wCorpus Obsistis|n) form the baseline engine of your physical durability,
which is tripled. Your raw physical power (|wCorpus Potestas|n) and your
sheer mental focus to endure pain (|wGenius Obsistis|n) are added as flat,
doubled capacity bonuses.

|wRegeneration|n
  Vigor regen = 1 + (Corpus + Corpus Obsistis) / 6
                + Corpus Reflexus / 4 + Genius Obsistis / 8

Your whole physical being (|wCorpus|n) and your physical toughness
(|wCorpus Obsistis|n) form your passive recovery engine, scaled down by a
sixth. Your physical coordination and agility (|wCorpus Reflexus|n) along
with your mental discipline to push through fatigue (|wGenius Obsistis|n)
actively accelerate how quickly your body heals. You always recover at
least 1 point per tick.

|wNote|n: all divisions round down (integer division).

See also: |wvim|n, |wmens|n, |wcorpus|n.
""".strip(),
    },
    {
        "key": "vim",
        "category": "General",
        "aliases": ["mana", "magic"],
        "text": """
|wVim - Magical Containment|n

Vim is your spiritual pool - your capacity to hold and channel supernatural
energy. Spellcraft draws on it. It is |wderived|n from your attributes and
is never stored directly.

|wDerivation|n
  Vim = ((Animus + Animus Obsistis) * 3)
        + ((Animus Potestas + Genius Obsistis) * 2)

Your core spiritual presence (|wAnimus|n) and your spiritual fortitude
(|wAnimus Obsistis|n) form the baseline engine of your magical containment,
which is tripled. Your raw spiritual power output (|wAnimus Potestas|n) and
your mental focus to stabilize supernatural energy (|wGenius Obsistis|n)
are added as flat, doubled capacity bonuses.

|wRegeneration|n
  Vim regen = 1 + (Animus + Animus Obsistis) / 6
              + Animus Reflexus / 4 + Genius Obsistis / 8

Your magical recovery engine scales heavily off your baseline spiritual
presence (|wAnimus|n) and your spiritual fortitude (|wAnimus Obsistis|n) to
cleanly channel energy back in. Your rapid visualization speed
(|wAnimus Reflexus|n) combined with your mental stability
(|wGenius Obsistis|n) safely ground incoming magical forces at a finer
modifier. You always recover at least 1 point per tick.

|wNote|n: all divisions round down (integer division).

See also: |wvigor|n, |wmens|n, |wanimus|n.
""".strip(),
    },
    {
        "key": "mens",
        "category": "General",
        "aliases": ["mental", "focus"],
        "text": """
|wMens - Mental Capacity|n

Mens is your mental pool - cognitive stamina for deep focus, long rituals
and resisting mental strain. It is |wderived|n from your attributes and is
never stored directly.

|wDerivation|n
  Mens = ((Genius + Genius Obsistis) * 3)
         + ((Genius Potestas + Corpus Obsistis) * 2)

Your baseline intellect (|wGenius|n) and your native mental resilience
(|wGenius Obsistis|n) form the core engine of your brain capacity, which is
tripled. Your active analytical power (|wGenius Potestas|n) and your body's
physical endurance against exhaustion (|wCorpus Obsistis|n) are added as
flat, doubled capacity bonuses to keep your mind sharp.

|wRegeneration|n
  Mens regen = 1 + (Genius + Genius Obsistis) / 6
               + Genius Reflexus / 4 + Corpus Obsistis / 8

Your brain clears cognitive fatigue based on your baseline intellect
(|wGenius|n) and your native mental resilience (|wGenius Obsistis|n). Your
raw reaction speed (|wGenius Reflexus|n) is then added alongside your body's
physical endurance (|wCorpus Obsistis|n), a healthy physical body directly
fueling your active mental recovery at a finer modifier. You always recover
at least 1 point per tick.

|wNote|n: all divisions round down (integer division).

See also: |wvigor|n, |wvim|n, |wgenius|n.
""".strip(),
    },
]
