# Data Directory

## Downloaded Data Files

### From d4lf (Diablo 4 Loot Filter)
Source: https://github.com/d4lfteam/d4lf

#### `raw/d4lf_affixes.json` (73KB, 1,188 lines)
**Format:** Key-value mapping of internal affix IDs to human-readable names

```json
{
  "all_stats": "all stats",
  "attack_speed": "attack speed",
  "critical_strike_damage": "critical strike damage",
  "maximum_life": "maximum life",
  ...
}
```

**Use:** Name normalization, OCR text matching, affix lookup

---

#### `raw/d4lf_aspects.json` (9.6KB)
**Format:** Array of aspect names (internal IDs)

```json
[
  "accelerating",
  "apostles",
  "balanced",
  "bladedancers",
  ...
]
```

**Use:** Aspect name validation, OCR matching

---

#### `raw/d4lf_item_types.json` (877B)
**Format:** Key-value mapping of internal type IDs to readable names

```json
{
  "Amulet": "amulet",
  "Axe": "axe",
  "Axe2H": "two-handed axe",
  "Helm": "helm",
  "Ring": "ring",
  ...
}
```

**Use:** Item type classification, slot determination

---

## Data Gaps

These files provide **name mappings only**. We still need:

### Critical Missing Data:
1. **Affix ranges** - [min, max] values for each affix
2. **Slot restrictions** - Which items can have which affixes
3. **Class restrictions** - Affix availability per class
4. **Item details** - Complete item database with base stats
5. **Aspect descriptions** - Full text and scaling values
6. **Unique Powers** - Complex conditional effect descriptions

### Potential Solutions:
1. **Manual curation** - Enter data for most important affixes/items
2. **OCR self-population** - Extract from user's own scanned items
3. **DiabloTools/d4data** - Parse game files (needs investigation)
4. **Wowhead scraping** - Requires Selenium setup
5. **Community databases** - Explore Diablo4Companion data exports

---

## Next Steps

See `/docs/data_sources_analysis.md` for full investigation results and recommendations.
