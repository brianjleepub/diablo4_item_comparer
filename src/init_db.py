"""
Database initialization and seed data loading script
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from sqlalchemy.exc import IntegrityError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, init_db
from models import (
    ItemType, Class, AffixCategory, Affix, Aspect
)


class DatabaseSeeder:
    """Seed database with initial reference data"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.stats = {
            'item_types': 0,
            'classes': 0,
            'affix_categories': 0,
            'affixes': 0,
            'aspects': 0,
        }

    def seed_all(self):
        """Run all seed operations"""
        print("=" * 60)
        print("DATABASE SEEDING")
        print("=" * 60)

        with get_db() as db:
            self.seed_classes(db)
            self.seed_item_types(db)
            self.seed_affix_categories(db)
            self.seed_affixes(db)
            self.seed_aspects(db)

        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)
        print(f"Item Types:        {self.stats['item_types']}")
        print(f"Classes:           {self.stats['classes']}")
        print(f"Affix Categories:  {self.stats['affix_categories']}")
        print(f"Affixes:           {self.stats['affixes']}")
        print(f"Aspects:           {self.stats['aspects']}")
        print("=" * 60)

    def seed_classes(self, db):
        """Seed character classes"""
        print("\nSeeding classes...")

        classes = [
            {'name': 'Barbarian', 'internal_id': 'barbarian'},
            {'name': 'Druid', 'internal_id': 'druid'},
            {'name': 'Necromancer', 'internal_id': 'necromancer'},
            {'name': 'Rogue', 'internal_id': 'rogue'},
            {'name': 'Sorcerer', 'internal_id': 'sorcerer'},
            {'name': 'Spiritborn', 'internal_id': 'spiritborn'},
            {'name': 'Paladin', 'internal_id': 'paladin'},
        ]

        for class_data in classes:
            try:
                char_class = Class(**class_data)
                db.add(char_class)
                db.flush()
                self.stats['classes'] += 1
                print(f"  ✓ {class_data['name']}")
            except IntegrityError:
                db.rollback()
                print(f"  - {class_data['name']} (already exists)")

    def seed_item_types(self, db):
        """Seed item types from d4lf data"""
        print("\nSeeding item types...")

        item_types_file = self.data_dir / 'raw' / 'd4lf_item_types.json'

        if not item_types_file.exists():
            print(f"  ✗ File not found: {item_types_file}")
            return

        with open(item_types_file, 'r', encoding='utf-8') as f:
            item_types_data = json.load(f)

        # Map to slots and classifications
        slot_mapping = {
            'Helm': 'Head',
            'ChestArmor': 'Torso',
            'Gloves': 'Hands',
            'Legs': 'Legs',
            'Boots': 'Feet',
            'Amulet': 'Neck',
            'Ring': 'Finger',
            'Shield': 'OffHand',
            'Focus': 'OffHand',
            'OffHandTotem': 'OffHand',
        }

        weapon_types = {
            'Axe', 'Axe2H', 'Sword', 'Sword2H', 'Mace', 'Mace2H',
            'Dagger', 'Bow', 'Crossbow2H', 'Staff', 'Wand', 'Polearm',
            'Quarterstaff', 'Glaive', 'Scythe', 'Scythe2H', 'Flail'
        }

        armor_types = {
            'Helm', 'ChestArmor', 'Gloves', 'Legs', 'Boots', 'Shield'
        }

        for internal_id, name in item_types_data.items():
            try:
                item_type = ItemType(
                    name=name,
                    internal_id=internal_id,
                    slot=slot_mapping.get(internal_id, 'MainHand' if internal_id in weapon_types else None),
                    is_weapon=internal_id in weapon_types,
                    is_armor=internal_id in armor_types,
                )
                db.add(item_type)
                db.flush()
                self.stats['item_types'] += 1
                print(f"  ✓ {name}")
            except IntegrityError:
                db.rollback()
                print(f"  - {name} (already exists)")

    def seed_affix_categories(self, db):
        """Seed affix categories"""
        print("\nSeeding affix categories...")

        categories = [
            {'name': 'Offensive', 'description': 'Damage and attack-related affixes'},
            {'name': 'Defensive', 'description': 'Survivability and damage reduction'},
            {'name': 'Utility', 'description': 'Cooldown reduction, duration, skill enhancements'},
            {'name': 'Resource', 'description': 'Resource generation and management'},
            {'name': 'Mobility', 'description': 'Movement speed and positioning'},
        ]

        for cat_data in categories:
            try:
                category = AffixCategory(**cat_data)
                db.add(category)
                db.flush()
                self.stats['affix_categories'] += 1
                print(f"  ✓ {cat_data['name']}")
            except IntegrityError:
                db.rollback()
                print(f"  - {cat_data['name']} (already exists)")

    def seed_affixes(self, db):
        """Seed affixes from d4lf data"""
        print("\nSeeding affixes...")

        affixes_file = self.data_dir / 'raw' / 'd4lf_affixes.json'

        if not affixes_file.exists():
            print(f"  ✗ File not found: {affixes_file}")
            return

        with open(affixes_file, 'r', encoding='utf-8') as f:
            affixes_data = json.load(f)

        # Get default category (Utility)
        default_category = db.query(AffixCategory).filter_by(name='Utility').first()

        for internal_id, name in affixes_data.items():
            try:
                affix = Affix(
                    internal_id=internal_id,
                    name=name,
                    category_id=default_category.id if default_category else None,
                    # Leave ranges empty for now - will be populated later
                    min_value=None,
                    max_value=None,
                    is_percentage=False,
                )
                db.add(affix)
                db.flush()
                self.stats['affixes'] += 1

                if self.stats['affixes'] % 100 == 0:
                    print(f"  ... {self.stats['affixes']} affixes loaded")

            except IntegrityError:
                db.rollback()

        print(f"  ✓ Loaded {self.stats['affixes']} affixes")

    def seed_aspects(self, db):
        """Seed aspects from d4lf data"""
        print("\nSeeding aspects...")

        aspects_file = self.data_dir / 'raw' / 'd4lf_aspects.json'

        if not aspects_file.exists():
            print(f"  ✗ File not found: {aspects_file}")
            return

        with open(aspects_file, 'r', encoding='utf-8') as f:
            aspects_data = json.load(f)

        for internal_id in aspects_data:
            try:
                # Convert internal_id to readable name
                name = internal_id.replace('_', ' ').title()

                aspect = Aspect(
                    internal_id=internal_id,
                    name=name,
                    category='Utility',  # Default, will be updated later
                    # Leave ranges and descriptions empty for now
                    min_value=None,
                    max_value=None,
                )
                db.add(aspect)
                db.flush()
                self.stats['aspects'] += 1

                if self.stats['aspects'] % 50 == 0:
                    print(f"  ... {self.stats['aspects']} aspects loaded")

            except IntegrityError:
                db.rollback()

        print(f"  ✓ Loaded {self.stats['aspects']} aspects")


def main():
    """Main initialization script"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize and seed Diablo 4 database')
    parser.add_argument('--create-tables', action='store_true', help='Create database tables')
    parser.add_argument('--seed', action='store_true', help='Seed reference data')
    parser.add_argument('--all', action='store_true', help='Create tables and seed data')
    parser.add_argument('--data-dir', type=str, default='../data', help='Path to data directory')

    args = parser.parse_args()

    # Resolve data directory path
    script_dir = Path(__file__).parent
    data_dir = (script_dir / args.data_dir).resolve()

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    # Execute operations
    if args.all or args.create_tables:
        print("\nCreating database tables...")
        init_db()

    if args.all or args.seed:
        print("\nLoading seed data...")
        seeder = DatabaseSeeder(data_dir)
        seeder.seed_all()

    if not (args.create_tables or args.seed or args.all):
        parser.print_help()
        print("\nExample usage:")
        print("  python init_db.py --all")
        print("  python init_db.py --create-tables")
        print("  python init_db.py --seed")


if __name__ == "__main__":
    main()
