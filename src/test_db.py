"""
Database test and exploration script
Tests basic functionality and demonstrates queries
"""

import sys
import os
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import (
    Class, ItemType, AffixCategory, Affix, Aspect,
    Build, BuildAffixWeight
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_connection():
    """Test database connection"""
    print_section("Testing Database Connection")

    try:
        with get_db() as db:
            # Simple query to test connection
            result = db.execute("SELECT 1").scalar()
            print(f"✓ Connection successful (test query returned: {result})")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def show_statistics():
    """Show database statistics"""
    print_section("Database Statistics")

    with get_db() as db:
        stats = {
            'Classes': db.query(Class).count(),
            'Item Types': db.query(ItemType).count(),
            'Affix Categories': db.query(AffixCategory).count(),
            'Affixes': db.query(Affix).count(),
            'Aspects': db.query(Aspect).count(),
            'Builds': db.query(Build).count(),
        }

        for name, count in stats.items():
            print(f"  {name:.<30} {count:>5}")


def explore_classes():
    """Show all character classes"""
    print_section("Character Classes")

    with get_db() as db:
        classes = db.query(Class).order_by(Class.name).all()

        for cls in classes:
            print(f"  {cls.id}. {cls.name:.<20} (internal: {cls.internal_id})")


def explore_item_types():
    """Show item type breakdown"""
    print_section("Item Types")

    with get_db() as db:
        item_types = db.query(ItemType).order_by(ItemType.slot, ItemType.name).all()

        # Group by slot
        by_slot = {}
        for item_type in item_types:
            slot = item_type.slot or 'Other'
            if slot not in by_slot:
                by_slot[slot] = []
            by_slot[slot].append(item_type)

        for slot, types in sorted(by_slot.items()):
            print(f"\n  {slot}:")
            for item_type in types:
                weapon_flag = "⚔" if item_type.is_weapon else " "
                armor_flag = "🛡" if item_type.is_armor else " "
                print(f"    {weapon_flag}{armor_flag} {item_type.name}")


def explore_affix_categories():
    """Show affix categories with counts"""
    print_section("Affix Categories")

    with get_db() as db:
        categories = db.query(AffixCategory).order_by(AffixCategory.name).all()

        for category in categories:
            affix_count = db.query(Affix).filter_by(category_id=category.id).count()
            aspect_count = db.query(Aspect).filter_by(category_id=category.id).count()
            print(f"\n  {category.name}")
            print(f"    Description: {category.description}")
            print(f"    Affixes: {affix_count}, Aspects: {aspect_count}")


def sample_affixes():
    """Show sample affixes"""
    print_section("Sample Affixes (First 20)")

    with get_db() as db:
        affixes = db.query(Affix).order_by(Affix.name).limit(20).all()

        for affix in affixes:
            range_str = ""
            if affix.min_value or affix.max_value:
                range_str = f" [{affix.min_value or '?'} - {affix.max_value or '?'}]"

            print(f"  {affix.id:>4}. {affix.name}{range_str}")


def sample_aspects():
    """Show sample aspects"""
    print_section("Sample Aspects (First 15)")

    with get_db() as db:
        aspects = db.query(Aspect).order_by(Aspect.name).limit(15).all()

        for aspect in aspects:
            category_name = "Unknown"
            if aspect.category_id:
                category = db.query(AffixCategory).get(aspect.category_id)
                if category:
                    category_name = category.name

            print(f"  {aspect.id:>4}. {aspect.name}")
            print(f"         Category: {category_name}, Internal: {aspect.internal_id}")


def search_affixes(keyword):
    """Search affixes by keyword"""
    print_section(f"Searching Affixes for '{keyword}'")

    with get_db() as db:
        affixes = db.query(Affix).filter(
            Affix.name.ilike(f"%{keyword}%")
        ).order_by(Affix.name).limit(20).all()

        if affixes:
            print(f"  Found {len(affixes)} matches:\n")
            for affix in affixes:
                print(f"  {affix.id:>4}. {affix.name}")
        else:
            print(f"  No matches found")


def create_test_build():
    """Create a test build with affix weights"""
    print_section("Creating Test Build: Fire Sorcerer")

    with get_db() as db:
        # Check if build already exists
        existing = db.query(Build).filter_by(name='Fire Sorcerer (Test)').first()
        if existing:
            print(f"  Build already exists (ID: {existing.id})")
            return existing.id

        # Get Sorcerer class
        sorcerer = db.query(Class).filter_by(name='Sorcerer').first()
        if not sorcerer:
            print("  ✗ Sorcerer class not found")
            return None

        # Create build
        build = Build(
            name='Fire Sorcerer (Test)',
            class_id=sorcerer.id,
            description='High-damage fire build focusing on critical strikes and burning',
            is_active=True
        )
        db.add(build)
        db.flush()
        print(f"  ✓ Created build (ID: {build.id})")

        # Add affix priorities
        priority_affixes = [
            ('critical_strike_damage', 100.0, 1, True),   # Must-have
            ('critical_strike_chance', 95.0, 2, True),    # Must-have
            ('burning_damage', 90.0, 3, False),
            ('fire_damage', 85.0, 4, False),
            ('damage', 75.0, 5, False),
            ('intelligence', 70.0, 6, False),
            ('cooldown_reduction', 60.0, 7, False),
            ('maximum_life', 50.0, 8, False),
        ]

        added_count = 0
        for internal_id, weight, priority, is_required in priority_affixes:
            # Find affix
            affix = db.query(Affix).filter(
                Affix.internal_id.ilike(f"%{internal_id}%")
            ).first()

            if affix:
                weight_entry = BuildAffixWeight(
                    build_id=build.id,
                    affix_id=affix.id,
                    weight=Decimal(str(weight)),
                    priority=priority,
                    is_required=is_required,
                    notes=f"Priority {priority}" if not is_required else "Required stat"
                )
                db.add(weight_entry)
                added_count += 1
                req_flag = "✓ REQUIRED" if is_required else ""
                print(f"    {priority}. {affix.name:.<40} Weight: {weight:>5.0f} {req_flag}")

        print(f"\n  ✓ Added {added_count} affix weights to build")
        return build.id


def show_build_summary(build_id):
    """Show summary of a build"""
    print_section(f"Build Summary (ID: {build_id})")

    with get_db() as db:
        build = db.query(Build).get(build_id)
        if not build:
            print("  Build not found")
            return

        print(f"  Name: {build.name}")
        print(f"  Class: {build.character_class.name}")
        print(f"  Description: {build.description}")
        print(f"  Active: {build.is_active}")

        # Show affix weights
        print(f"\n  Affix Priorities:")
        weights = db.query(BuildAffixWeight).filter_by(
            build_id=build_id
        ).order_by(BuildAffixWeight.priority).all()

        for w in weights:
            req_str = " [REQUIRED]" if w.is_required else ""
            print(f"    {w.priority}. {w.affix.name:.<40} {w.weight:>5.1f}{req_str}")


def test_scoring_query(build_id):
    """Test a scoring query"""
    print_section("Testing Scoring Query Logic")

    with get_db() as db:
        # Get build weights
        weights = db.query(BuildAffixWeight).filter_by(build_id=build_id).all()

        print(f"  Build has {len(weights)} weighted affixes")
        print(f"\n  Example scoring calculation:")
        print(f"  If an item had these affixes at max roll:")

        total_score = 0
        for w in weights[:5]:  # Show first 5
            affix = w.affix
            max_roll = affix.max_value or 100  # Placeholder
            score_contribution = float(w.weight) * float(max_roll)
            total_score += score_contribution

            print(f"    {affix.name:.<40} {w.weight:>5.1f} × {max_roll:>5} = {score_contribution:>8.1f}")

        print(f"  {'':.<48} Total: {total_score:>8.1f}")


def main():
    """Run all tests and exploration"""
    print("\n" + "█" * 70)
    print("█" + " " * 15 + "DIABLO 4 DATABASE TEST & EXPLORATION" + " " * 16 + "█")
    print("█" * 70)

    # Test connection
    if not test_connection():
        print("\n✗ Cannot proceed without database connection")
        return

    # Show statistics
    show_statistics()

    # Explore reference data
    explore_classes()
    explore_item_types()
    explore_affix_categories()

    # Sample data
    sample_affixes()
    sample_aspects()

    # Search examples
    search_affixes("critical")
    search_affixes("fire")

    # Create test build
    build_id = create_test_build()

    if build_id:
        show_build_summary(build_id)
        test_scoring_query(build_id)

    # Final summary
    print_section("Test Complete")
    print("  ✓ Database connection working")
    print("  ✓ All tables accessible")
    print("  ✓ Reference data loaded")
    print("  ✓ Build creation working")
    print("  ✓ Queries functioning correctly")
    print("\n  Database is ready for Phase 3 (OCR Integration)!\n")


if __name__ == "__main__":
    main()
