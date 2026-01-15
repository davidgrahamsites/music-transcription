"""Script to update and sort the instruments database."""
import json
import sys

# Read current database
with open('src/data/instruments.json', 'r') as f:
    data = json.load(f)

# Add missing Horn in B-flat
horn_bb = {
    "id": "horn_bb",
    "name": "Horn in B♭",
    "family": "Brass",
    "transposition": {
        "type": "interval",
        "semitones": -2
    },
    "clefs": ["treble", "bass"],
    "sounding_range": {
        "lowest": "B1",
        "highest": "F5"
    },
    "written_range": {
        "lowest": "C#2",
        "highest": "G5"
    },
    "preferred_range": {
        "lowest": "D3",
        "highest": "A5"
    },
    "octave_displacement": 0,
    "midi_program": 60
}

# Check if it exists
exists = any(inst['id'] == 'horn_bb' for inst in data['instruments'])
if not exists:
    data['instruments'].append(horn_bb)
    print("✅ Added Horn in B♭")
else:
    print("ℹ️  Horn in B♭ already exists")

# Sort instruments alphabetically within each family
from collections import defaultdict

by_family = defaultdict(list)
for inst in data['instruments']:
    by_family[inst['family']].append(inst)

# Sort each family
for family in by_family:
    by_family[family].sort(key=lambda x: x['name'])

# Rebuild instrument list with sorted families
sorted_instruments = []
for family in sorted(by_family.keys()):
    sorted_instruments.extend(by_family[family])

data['instruments'] = sorted_instruments

# Write back
with open('src/data/instruments.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ Sorted {len(data['instruments'])} instruments across {len(by_family)} families")
print("Families:", ", ".join(sorted(by_family.keys())))
