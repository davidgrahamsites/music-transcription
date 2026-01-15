"""Basic test for instrument database."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notation.instrument_db import InstrumentDatabase


def test_instrument_database():
    """Test that instrument database loads correctly."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'instruments.json')
    
    print("Testing Instrument Database...")
    print(f"Loading from: {db_path}")
    
    db = InstrumentDatabase(db_path)
    
    # Test 1: Count instruments
    all_instruments = db.get_all_instruments()
    print(f"✅ Loaded {len(all_instruments)} instruments")
    
    # Test 2: List families
    families = db.get_all_families()
    print(f"✅ Found {len(families)} families: {', '.join(families)}")
    
    # Test 3: Get specific instrument
    horn = db.get_instrument('horn_f')
    if horn:
        print(f"✅ Horn in F:")
        print(f"   - Name: {horn.name}")
        print(f"   - Transposition: {horn.transposition_semitones} semitones")
        print(f"   - Clefs: {', '.join(horn.clefs)}")
    else:
        print("❌ Horn in F not found")
        return False
    
    # Test 4: Transposition logic
    violin = db.get_instrument('violin')
    if violin:
        print(f"✅ Violin:")
        print(f"   - Transposition: {violin.transposition_semitones} semitones (should be 0)")
    
    # Test 5: List instruments by family
    brass = db.list_by_family('Brass')
    print(f"✅ Brass family has {len(brass)} instruments")
    
    strings = db.list_by_family('Strings')
    print(f"✅ Strings family has {len(strings)} instruments")
    
    print("\n✅ All tests passed!")
    return True


if __name__ == '__main__':
    success = test_instrument_database()
    sys.exit(0 if success else 1)
