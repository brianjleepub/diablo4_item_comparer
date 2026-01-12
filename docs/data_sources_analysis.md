# Diablo 4 Data Sources Analysis

## Summary

After investigating Wowhead scraping and alternative data sources, I've identified multiple approaches for building our item database. Wowhead proved challenging due to heavy JavaScript rendering, but we found excellent community-maintained data sources.

## Data Sources Found

### 1. d4lf (Diablo 4 Loot Filter) ✅
**URL:** https://github.com/d4lfteam/d4lf

**Available Data:**
- `affixes.json` (73KB) - 1,188 affix name mappings
- `aspects.json` (9.6KB) - Aspect name mappings
- `item_types.json` (877B) - Item type classifications

**Format:** Simple key-value JSON (internal_id -> human_readable_name)

**Limitations:** Only name mappings, no stat ranges, slot restrictions, or detailed metadata

**Status:** ✅ Downloaded to `data/raw/`

---

### 2. Diablo4Companion
**URL:** https://github.com/josdemmers/Diablo4Companion

**Data Structure:** C# entity models defining complete data schema

**Key Entities Found:**
- `AffixInfo.cs` - Comprehensive affix data structure
  - `IdSno`, `IdName` - Identifiers
  - `AffixType`, `Category`, `Flags` - Classification
  - `MagicType` - Quality tier (0=Affix, 1=Legendary, 2=Unique, 3=Test, 4=Mythic)
  - `AllowedForPlayerClass` - Class restrictions (Sorc, Druid, Barb, Rogue, Necro, Spiritborn, Paladin)
  - `AllowedItemLabels` - Slot restrictions
  - `IsTemperingAvailable` - Tempering flag
  - `AffixAttributes` - Localization and formula values

- `ItemType.cs`, `ItemTypeInfo.cs` - Item classification
- `AspectInfo.cs` - Aspect data
- `UniqueInfo.cs` - Unique item data
- `ParagonBoardInfo.cs` - Paragon systems

**Value:** Excellent reference for database schema design

**Status:** Analyzed entity structure, data files not directly accessible

---

### 3. DiabloTools/d4data
**URL:** https://github.com/DiabloTools/d4data

**Description:** Game data extracted from CASC files and parsed to JSON

**Known Contents:**
- `json/` directory with parsed game data
- `definitions/` - Data structure definitions
- `names/` - Name mapping files

**Status:** Repository is large, attempted clone but timed out

**Recommendation:** Target specific files via raw GitHub URLs when we know what we need

---

### 4. d4-item-tooltip-ocr
**URL:** https://github.com/mxtsdev/d4-item-tooltip-ocr

**Description:** OCR project for Diablo 4 tooltips using PaddleOCR

**Technology:** Custom-trained model specifically for D4 tooltips

**Value:** Potential reference for OCR implementation phase

**Status:** Analyzed, similar to our end goal

---

### 5. Wowhead Diablo 4 Database
**URL:** https://www.wowhead.com/diablo-4/database

**Data Available:**
- 9,719 items
- 466 aspects (Offensive, Defensive, Utility, Mobility, Resource)
- 4,425 affixes with stat ranges

**Challenge:** Data is loaded dynamically via JavaScript, making scraping difficult

**Attempts Made:**
1. ❌ Static HTML scraping - data not in initial HTML
2. ❌ Embedded JSON extraction - variable names/patterns not found
3. ❌ Selenium browser automation - Chrome not available in environment
4. ❌ Individual item API endpoints - no accessible endpoints found

**Status:** Deferred - would require Selenium with Chrome or Playwright

---

## Recommendations

### Immediate Next Steps

**Option A: Hybrid Approach (RECOMMENDED)**
1. Use d4lf name mappings as a foundation
2. Manually curate critical data for MVP (50-100 most important affixes)
3. Structure based on Diablo4Companion entity models
4. Design schema to accommodate future bulk imports
5. Build OCR pipeline to extract data from user's own items (self-populating database)

**Option B: DiabloTools Deep Dive**
1. Clone DiabloTools/d4data successfully (or download specific files)
2. Parse their JSON format
3. Import into our PostgreSQL schema
4. May be most complete but needs investigation of their data structure

**Option C: Wowhead Revisited**
1. Set up proper browser automation (Selenium + Chrome in Docker)
2. Extract data from rendered pages
3. Most comprehensive web source
4. Higher implementation complexity

### Schema Design Priority

Based on your screenshots and Diablo4Companion models, our schema should support:

**Items:**
- Name, Type, Slot, Rarity (Quality 0-8)
- Item Power
- Class restrictions
- Unique Powers (long-form text)
- Sanctified/Armory Loadout flags
- Tempering indicators

**Affixes:**
- Internal ID + Human-readable name
- Category (Offensive, Defensive, Utility, Resource, Mobility)
- Stat ranges [min-max]
- Item slot restrictions
- Class restrictions
- Tempering availability

**Aspects:**
- Name, Description
- Category
- Class applicability
- Scaling values/ranges
- Slot compatibility

**Item Instances (from OCR):**
- All item fields above
- Specific roll values for each affix
- Tempering status
- Quality bonuses
- Screenshot reference

---

## Next Actions

What would you like to do?

1. **Design PostgreSQL schema** based on findings above
2. **Investigate DiabloTools/d4data** more thoroughly
3. **Build hybrid database** with d4lf mappings + manual curation
4. **Start with OCR integration** using ShareX captures to self-populate database

My recommendation: **#1 then #3** - Design the schema with all fields we'll need, start with a curated foundation, then let the OCR pipeline enrich the database as you scan items from your own game.
