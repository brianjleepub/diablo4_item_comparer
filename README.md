#Diablo IV Item Comparator

A computer-vision–driven item comparison tool for Diablo IV that evaluates two in-game items and determines which is better for a specific build—based on extracted stats, affix weighting, and deterministic scoring logic.

This project exists to eliminate subjective loot decisions and manual spreadsheet work. The app captures item tooltips via camera input, extracts structured stat data, and scores each item against a build-defined priority model. The output is a reproducible comparison, not a vibe check.

What It Does

Captures Diablo IV item tooltips directly from the game screen using a camera feed

Performs OCR and post-processing tuned specifically for Diablo IV’s UI and typography

Normalizes affixes, ranges, implicit modifiers, and conditional bonuses

Scores items using a build-aware weighting system

Produces a clear, explainable winner between two items

The comparison logic is explicit and configurable. If two items score the same, they score the same for a reason.

Why Camera-Based?

This tool intentionally avoids memory reading, overlays, or game file inspection. Camera capture keeps the system platform-agnostic and resilient to game updates, anti-cheat changes, and patch-level UI shifts. The tradeoff is input quality, which is treated as a solvable engineering problem rather than a limitation.

Build Scoring Model

Each build defines:

Relevant stats and affixes

Priority weights and scaling behavior

Conditional modifiers (e.g. skill interactions, breakpoints, diminishing returns)

Scoring is deterministic and transparent. No black-box ML deciding your loot.

Design Constraints

No automation of gameplay

No interaction with game memory or network traffic

No hidden heuristics

This is a decision-support tool, not a bot.

Project Status

Active development. Expect breaking changes. Accuracy depends on camera quality, lighting, and tooltip clarity. Build definitions and affix mappings will evolve alongside Diablo IV patches.
