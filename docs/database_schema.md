# Database Schema Design

## Overview

This schema supports:
- **Reference data** from Wowhead/community sources (items, affixes, aspects)
- **OCR'd item instances** from ShareX captures
- **Build definitions** with weighted affix priorities
- **Comparison history** for analysis

## Core Entities

### Items (Reference Data)
Base item templates from game data or community sources.

### Item Instances
Specific items scanned via OCR with actual roll values.

### Affixes
Stat modifiers with min/max ranges, restrictions, and metadata.

### Aspects
Legendary/Unique powers with descriptions and scaling values.

### Builds
User-defined character builds with affix priority weights.

---

## Schema Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         REFERENCE DATA                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   item_types     │       │     classes      │       │   affix_categories│
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id         SERIAL│       │ id         SERIAL│       │ id         SERIAL│
│ name       TEXT  │       │ name       TEXT  │       │ name       TEXT  │
│ internal_id TEXT │       │ internal_id TEXT │       │ description TEXT │
│ slot       TEXT  │       │ created_at       │       │ created_at       │
│ is_weapon  BOOL  │       └──────────────────┘       └──────────────────┘
│ is_armor   BOOL  │
│ created_at       │
└──────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                            affixes                               │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ internal_id           TEXT UNIQUE NOT NULL                       │
│ name                  TEXT NOT NULL                              │
│ description           TEXT                                       │
│ category_id           INTEGER → affix_categories.id             │
│ min_value             DECIMAL(10,2)                             │
│ max_value             DECIMAL(10,2)                             │
│ is_percentage         BOOLEAN DEFAULT false                     │
│ is_implicit           BOOLEAN DEFAULT false                     │
│ is_tempering          BOOLEAN DEFAULT false                     │
│ allowed_item_types    INTEGER[] → item_types.id                │
│ allowed_classes       INTEGER[] → classes.id                    │
│ magic_type            INTEGER (0=Affix,1=Legendary,2=Unique...)│
│ priority_tier         INTEGER (for default sorting)            │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
│ updated_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                           aspects                                │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ internal_id           TEXT UNIQUE NOT NULL                       │
│ name                  TEXT NOT NULL                              │
│ description           TEXT                                       │
│ category_id           INTEGER → affix_categories.id             │
│ min_value             DECIMAL(10,2)                             │
│ max_value             DECIMAL(10,2)                             │
│ scaling_formula       TEXT                                       │
│ allowed_classes       INTEGER[] → classes.id                    │
│ allowed_item_types    INTEGER[] → item_types.id                │
│ is_unique_power       BOOLEAN DEFAULT false                     │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
│ updated_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        USER DATA & OCR                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        item_instances                            │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ name                  TEXT NOT NULL                              │
│ item_type_id          INTEGER → item_types.id                   │
│ class_restriction_id  INTEGER → classes.id (nullable)           │
│ item_power            INTEGER                                    │
│ quality               INTEGER (0-8 rarity scale)                │
│ quality_bonus         INTEGER (tempering bonus)                 │
│ rarity_stars          INTEGER (1-4 for unique display)          │
│ is_ancestral          BOOLEAN DEFAULT false                     │
│ is_unique             BOOLEAN DEFAULT false                     │
│ is_mythic             BOOLEAN DEFAULT false                     │
│ is_sanctified         BOOLEAN DEFAULT false                     │
│ is_account_bound      BOOLEAN DEFAULT true                      │
│ is_modifiable         BOOLEAN DEFAULT true                      │
│ level_requirement     INTEGER                                    │
│ sell_value            INTEGER                                    │
│ unique_power_text     TEXT (long-form description)             │
│ flavor_text           TEXT                                       │
│ screenshot_path       TEXT (path to ShareX capture)            │
│ ocr_confidence        DECIMAL(3,2) (0.00-1.00)                 │
│ source                TEXT (ocr, manual, import)               │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
│ updated_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    item_instance_affixes                         │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ item_instance_id      INTEGER → item_instances.id              │
│ affix_id              INTEGER → affixes.id                      │
│ roll_value            DECIMAL(10,2) NOT NULL                    │
│ is_greater_affix      BOOLEAN DEFAULT false                     │
│ is_tempered           BOOLEAN DEFAULT false                     │
│ is_implicit           BOOLEAN DEFAULT false                     │
│ affix_order           INTEGER (display order on tooltip)       │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘
UNIQUE(item_instance_id, affix_id, affix_order)

┌──────────────────────────────────────────────────────────────────┐
│                    item_instance_aspects                         │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ item_instance_id      INTEGER → item_instances.id              │
│ aspect_id             INTEGER → aspects.id                      │
│ roll_value            DECIMAL(10,2) (if aspect has ranges)     │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘
UNIQUE(item_instance_id, aspect_id)

┌──────────────────────────────────────────────────────────────────┐
│                    item_instance_sockets                         │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ item_instance_id      INTEGER → item_instances.id              │
│ socket_index          INTEGER (0,1,2... for multiple sockets)  │
│ gem_type              TEXT (ruby, emerald, etc.)               │
│ is_empty              BOOLEAN DEFAULT true                      │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    BUILD MANAGEMENT                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                            builds                                │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ name                  TEXT NOT NULL                              │
│ class_id              INTEGER → classes.id                      │
│ description           TEXT                                       │
│ is_active             BOOLEAN DEFAULT true                      │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
│ updated_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        build_affix_weights                       │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ build_id              INTEGER → builds.id                       │
│ affix_id              INTEGER → affixes.id                      │
│ weight                DECIMAL(5,2) NOT NULL (0.00-100.00)      │
│ priority              INTEGER (1=highest priority)              │
│ is_required           BOOLEAN DEFAULT false                     │
│ notes                 TEXT                                       │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘
UNIQUE(build_id, affix_id)

┌─────────────────────────────────────────────────────────────────┐
│                    COMPARISON HISTORY                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       item_comparisons                           │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ build_id              INTEGER → builds.id                       │
│ item_a_id             INTEGER → item_instances.id              │
│ item_b_id             INTEGER → item_instances.id              │
│ winner                TEXT (item_a, item_b, tie)               │
│ score_a               DECIMAL(10,2)                             │
│ score_b               DECIMAL(10,2)                             │
│ score_delta           DECIMAL(10,2)                             │
│ comparison_details    JSONB (detailed breakdown)               │
│ screenshot_path       TEXT (comparison screenshot)             │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         ocr_cache                                │
├──────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                         │
│ image_hash            TEXT UNIQUE NOT NULL (SHA256)            │
│ image_path            TEXT                                       │
│ extracted_data        JSONB (raw OCR output)                   │
│ confidence_score      DECIMAL(3,2)                              │
│ processing_time_ms    INTEGER                                    │
│ ocr_engine_version    TEXT                                       │
│ created_at            TIMESTAMP DEFAULT NOW()                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Reference vs Instance Data
- **Reference tables** (`affixes`, `aspects`) = Game data (static, from Wowhead/d4lf)
- **Instance tables** (`item_instances`, `item_instance_affixes`) = Actual items from OCR

### 2. Flexible Roll Values
- `item_instance_affixes.roll_value` stores the specific roll (e.g., 72% for an affix that ranges 50-80%)
- `affixes.min_value` and `max_value` define possible ranges

### 3. Multiple Affixes of Same Type
- An item can have the same affix multiple times (e.g., two +Strength rolls)
- `affix_order` field preserves tooltip display order
- Composite unique constraint prevents exact duplicates

### 4. OCR Support
- `screenshot_path` links items to ShareX captures
- `ocr_confidence` tracks extraction quality
- `ocr_cache` table prevents re-processing same images
- `source` field tracks data provenance (ocr/manual/import)

### 5. Build Scoring System
- `build_affix_weights` defines what matters for each build
- `weight` = numerical importance (0-100)
- `priority` = ranking for tie-breaking
- `is_required` = must-have affixes

### 6. Array Fields for Many-to-Many
- `allowed_classes`, `allowed_item_types` use PostgreSQL arrays
- Simpler than junction tables for static, rarely-queried relationships
- Can switch to junction tables later if needed

### 7. JSONB for Complex Data
- `comparison_details` stores full scoring breakdown
- `extracted_data` preserves raw OCR output for debugging
- Flexible schema for evolving comparison logic

---

## Indexes

```sql
-- Performance indexes
CREATE INDEX idx_affixes_category ON affixes(category_id);
CREATE INDEX idx_affixes_internal_id ON affixes(internal_id);
CREATE INDEX idx_item_instances_type ON item_instances(item_type_id);
CREATE INDEX idx_item_instances_quality ON item_instances(quality);
CREATE INDEX idx_item_instance_affixes_item ON item_instance_affixes(item_instance_id);
CREATE INDEX idx_item_instance_affixes_affix ON item_instance_affixes(affix_id);
CREATE INDEX idx_build_weights_build ON build_affix_weights(build_id);
CREATE INDEX idx_comparisons_build ON item_comparisons(build_id);
CREATE INDEX idx_comparisons_created ON item_comparisons(created_at DESC);
CREATE INDEX idx_ocr_cache_hash ON ocr_cache(image_hash);

-- GIN index for array searches
CREATE INDEX idx_affixes_allowed_types ON affixes USING GIN(allowed_item_types);
CREATE INDEX idx_affixes_allowed_classes ON affixes USING GIN(allowed_classes);

-- JSONB indexes
CREATE INDEX idx_comparison_details ON item_comparisons USING GIN(comparison_details);
CREATE INDEX idx_ocr_extracted_data ON ocr_cache USING GIN(extracted_data);
```

---

## Example Queries

### Find Best Helm for a Build
```sql
SELECT
  ii.*,
  SUM(baw.weight * iia.roll_value) AS score
FROM item_instances ii
JOIN item_instance_affixes iia ON ii.id = iia.item_instance_id
JOIN build_affix_weights baw ON iia.affix_id = baw.affix_id
WHERE baw.build_id = $1
  AND ii.item_type_id = (SELECT id FROM item_types WHERE slot = 'Helm')
GROUP BY ii.id
ORDER BY score DESC
LIMIT 10;
```

### Compare Two Items
```sql
WITH
  item_a_score AS (
    SELECT SUM(baw.weight * iia.roll_value) AS score
    FROM item_instance_affixes iia
    JOIN build_affix_weights baw ON iia.affix_id = baw.affix_id
    WHERE iia.item_instance_id = $1 AND baw.build_id = $3
  ),
  item_b_score AS (
    SELECT SUM(baw.weight * iia.roll_value) AS score
    FROM item_instance_affixes iia
    JOIN build_affix_weights baw ON iia.affix_id = baw.affix_id
    WHERE iia.item_instance_id = $2 AND baw.build_id = $3
  )
SELECT
  (SELECT score FROM item_a_score) AS score_a,
  (SELECT score FROM item_b_score) AS score_b,
  CASE
    WHEN (SELECT score FROM item_a_score) > (SELECT score FROM item_b_score) THEN 'item_a'
    WHEN (SELECT score FROM item_a_score) < (SELECT score FROM item_b_score) THEN 'item_b'
    ELSE 'tie'
  END AS winner;
```

### Find Items Missing from OCR Cache
```sql
SELECT ii.*
FROM item_instances ii
LEFT JOIN ocr_cache oc ON ii.screenshot_path = oc.image_path
WHERE ii.source = 'ocr' AND oc.id IS NULL;
```

---

## Migration Strategy

1. **Phase 1:** Core reference tables (item_types, classes, affix_categories)
2. **Phase 2:** Affixes and aspects (seed with d4lf data)
3. **Phase 3:** Item instances and relationships
4. **Phase 4:** Build management
5. **Phase 5:** Comparison history and OCR cache

## Next Steps

1. Create SQLAlchemy models implementing this schema
2. Set up Alembic for migrations
3. Write seed data script using d4lf JSON files
4. Create database initialization utilities
