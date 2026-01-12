# In-Game Tooltip Structure Analysis

Based on the screenshots provided, here's the detailed structure of Diablo 4 item tooltips.

## Example 1: LOCRAN'S TALISMAN (Amulet)

```
Header:
├── Name: "LOCRAN'S TALISMAN ✦ ✦ ✦"
├── Rarity Stars: 3 stars (Unique)
├── Item Type: "Ancestral Unique Amulet"
├── Item Power: 800
├── Quality: 40 (✦+25) - Base 40, Tempering +25
├── Flags: Armory Loadout, Sanctified
└── Level Requirement: 60

Primary Stats:
└── "304 All Resist"

Affixes (Variable Roll):
├── "+72% All Stats"
├── "+30 Maximum Resource"
├── "+218.5% Critical Strike Damage"
├── "+91 Resistance to All Elements [56-70]" (shows range)
└── "+15 Item Quality [5-25]"

Unique Power:
└── "Your Skills gain 0.26%[+] [0.10 - 0.40]% Critical Strike Chance per point of
    Primary Resource you have when cast, up to 26%[×] [10 - 40]%. Each point of
    Primary Resource above 100 grants Skills 0.2%[×] Critical Strike Damage instead,
    up to 500 Resource."

Elemental Resistance:
└── "-1,750 Fire Resistance" (negative, shown in red)

Footer:
├── Flavor Text: "A single petal of the Mother's own blood, slowly wilting under glass."
├── Requires Level: 60
├── Binding: "Account Bound"
├── Status: "Unique Equipped"
└── "Unmodifiable"
```

---

## Example 2: SPEEDY AMULET (Magic Item - Comparison View)

```
Left Side - Currently Equipped:
Name: "LOCRAN'S TALISMAN ✦ ✦ ✦"
[Same as above]

Right Side - Candidate Item:
Header:
├── Name: "SPEEDY AMULET"
├── Item Type: "Magic Amulet"
├── Item Power: 712
└── Quality: 131

Primary Stat:
└── "131 All Resist (-15.2% Toughness)"
    ├── Base value: 131
    └── Comparison: Shows % change in Toughness stat

Affixes:
├── "+13.0% Movement Speed [11.5 - 19.0]% (+13.0%)"
└── "◇ Empty Socket"

Properties Lost When Equipped:
├── "+15 Item Quality" (red, negative)
├── "+30 Maximum Resource" (red)
├── "+218.5% Critical Strike Damage" (red)
├── "+72% All Stats" (red)
├── "+91 Resistance to All Elements" (red)
└── "Unique Power" (red)

Footer:
├── Requires Level: 60
└── Sell Value: 7,851 [gold coin icon]
```

**Color Coding:**
- White: Normal text
- Blue: Magic affixes, basic stats
- Orange: Unique/special effects
- Green: Positive values, ranges, increases
- Red: Negative values, properties lost, decreases
- Purple: Unique item name color

---

## Example 3: HERALD'S MORNINGSTAR (Weapon)

```
Header:
├── Name: "HERALD'S MORNINGSTAR ✦ ✦ ✦"
├── Item Type: "Ancestral Unique Mace"
├── Item Power: 800
├── Quality: 25 (✦+25)
└── Flags: Armory Loadout, Sanctified

Weapon Stats:
├── "357 Damage Per Second"
├── "⤷ [271 - 379] Damage per Hit"
├── "⤷ 1.10 Attacks per Second (Fast)"
└── "◆ +12.5% Lucky Hit Chance [10.0]%"

Affixes:
├── "✦ +212 Strength"
├── "✦ +799 Maximum Life"
├── "✦ +146.2% Chance for Blessed Hammer to Deal Double Damage"
├── "◆ +4 to Blessed Hammer [3 - 4]"
├── "☨ +14.4% Attack Speed [10.0 - 12.0]%"
└── "✦ Blessed Hammer deals 138%[×] [110 - 150]% increased damage."

Passive Effect:
└── "Lucky Hit: Up to a 20% chance to spawn a base Blessed Hammer on the target hit."

Unique Power:
└── "+72.0% Critical Strike Damage"

Flavor Text:
└── "First in the Swan, the Herald by name. This is the star of morning that shines
    brightest, which marshals the order of all other celestial bodies."

Footer:
├── Requires Level: 60
├── "Account Bound"
├── "☣ Only"
├── "Unique Equipped"
├── "Lord of Hatred Item ♆"
└── "Unmodifiable"
```

**Symbol Meanings:**
- ✦ - Tempering indicator
- ◆ - Implicit stat (diamond)
- ◇ - Empty socket (hollow diamond)
- ☨ - Tempering affix
- ☣ - Class-specific (Paladin only)
- ⤷ - Sub-stat (indented detail)
- [×] - Multiplicative scaling
- [+] - Additive scaling
- ♆ - Mythic/Special item category

---

## Example 4: RING OF STARLESS SKIES (Ring)

```
Header:
├── Name: "RING OF STARLESS SKIES ✦ ✦"
├── Item Type: "Ancestral Mythic Unique Ring"
├── Item Power: 800
├── Quality: 25 (✦+25)
└── Flags: Armory Loadout, Sanctified

Primary Stat:
└── "204 All Resist"

Affixes:
├── "◆ +21.9% Attack Speed [17.5]%"
├── "✦ +21.9% Critical Strike Chance [12.5]%"
├── "✦ +21.9% Lucky Hit Chance"
├── "✦ +4 to Core Skills"
└── "☨ 5.3% Maximum Life [4.0 - 5.0]%"

Unique Power:
└── "Spending your Primary Resource reduces the Resource cost of your Skills and
    increases your damage by 10%[×] for 3 seconds, up to 50%[×]."

Elemental Resistance:
└── "+1,750 Lightning Resistance"

Flavor Text:
└── "Yours is the power to pluck the stars from the heavens with the ease of a child
    gathering fruit from the bough."
└── "- Unknown"

Footer:
├── Requires Level: 35
├── "Account Bound"
├── "Unique Equipped"
└── "Unmodifiable"
```

---

## Data Extraction Challenges for OCR

### High Confidence Elements:
- Item name (large, distinct font)
- Item type (consistent position)
- Item Power number
- Primary stats (consistent format)
- Level requirements

### Medium Confidence Elements:
- Affix values (small numbers, varied positions)
- Stat ranges in brackets [min-max]
- Comparison percentages
- Symbols (✦, ◆, ☨, etc.)

### Low Confidence Elements:
- Unique Powers (long text, complex formatting)
- Flavor text (italics, may wrap)
- Conditional effects (nested logic)
- Color coding (need color detection, not just text)

### Critical OCR Considerations:
1. **Font variation**: Different sizes and styles
2. **Color-coded information**: Red/green comparisons, blue/orange text
3. **Symbols**: Many Unicode symbols that must be recognized
4. **Ranges**: Text like "[56-70]" needs parsing
5. **Multi-line effects**: Unique powers often span multiple lines
6. **Indentation**: Sub-stats use arrows (⤷)
7. **Percentage vs absolute values**: Mixed unit types

---

## Database Implications

### Must Support:
- Multi-line text fields (Unique Powers)
- Nullable fields (not all items have all affixes)
- Range storage (min, max, current roll)
- Complex conditional logic (Unique Powers with breakpoints)
- Metadata (tempering status, sanctified flag, modifiable status)
- Comparisons (properties lost/gained)
- Localization (flavor text, ability names)

### Relationships:
- Items → Affixes (many-to-many with roll values)
- Items → Aspects (one-to-many for legendaries)
- Items → Sockets (one-to-many)
- Affixes → AllowedSlots (many-to-many)
- Affixes → AllowedClasses (many-to-many)
