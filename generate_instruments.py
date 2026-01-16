"""Generate comprehensive instruments.json from the user's comprehensive list."""
import json

# MIDI program numbers (General MIDI)
MIDI_PROGRAMS = {
    # Strings
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'double bass': 43,
    'harp': 46,
    'guitar': 24,
    'mandolin': 26,
    'lute': 24,
    
    # Keyboards
    'piano': 0,
    'organ': 19,
    'harpsichord': 6,
    'celesta': 8,
    
    # Woodwinds
    'flute': 73,
    'piccolo': 72,
    'recorder': 74,
    'oboe': 68,
    'english horn': 69,
    'clarinet': 71,
    'bassoon': 70,
    'saxophone': 65,  # alto sax default
    
    # Brass
    'trumpet': 56,
    'horn': 60,
    'trombone': 57,
    'tuba': 58,
    'euphonium': 58,
    
    # Percussion
    'timpani': 47,
    'glockenspiel': 9,
    'xylophone': 13,
    'vibraphone': 11,
    'marimba': 12,
    'tubular bells': 14,
    
    # Regional
    'erhu': 110,
    'pipa': 105,
    'koto': 107,
    'shakuhachi': 77,
    'sitar': 104,
    'oud': 106,
}

def get_midi_program(name):
    """Get MIDI program number for instrument."""
    name_lower = name.lower()
    for key, prog in MIDI_PROGRAMS.items():
        if key in name_lower:
            return prog
    return 0  # Default to piano

def parse_transposition(key_str):
    """Parse transposition from key string."""
    if 'C' in key_str and '8vb' not in key_str and '8va' not in key_str:
        return 0
    elif 'Bb' in key_str or 'B♭' in key_str:
        return -2
    elif 'A' in key_str:
        return -3
    elif 'Eb' in key_str or 'E♭' in key_str:
        return 3
    elif 'F' in key_str:
        return -5
    elif 'G' in key_str:
        return -2
    elif 'D' in key_str:
        return 2
    return 0

def parse_clefs(clef_str):
    """Parse clef list from string."""
    clefs = []
    if 'tr' in clef_str:
        clefs.append('treble')
    if 'bs' in clef_str:
        clefs.append('bass')
    if 'al' in clef_str:
        clefs.append('alto')
    if 'tn' in clef_str:
        clefs.append('tenor')
    if 'gr' in clef_str:
        clefs = ['treble', 'bass']  # Grand staff = both
    if 'perc' in clef_str:
        clefs.append('percussion')
    
    return clefs if clefs else ['treble']

# Instrument families
instruments = {
    "instruments": []
}

# Parse the comprehensive list
instrument_data = """
Violin | C | tr
Viola | C | al (tr high)
Cello | C | bs (tn,tr high)
Double Bass | C (8vb) | bs
Pedal Harp | C | gr
Classical Guitar | C (8vb) | tr
Mandolin | C | tr
Piano | C | gr
Organ | C | gr
Harpsichord | C | gr
Celesta | C (8va) | tr
Piccolo | C (8va) | tr
Flute | C | tr
Alto Flute | G | tr
Soprano Recorder | C | tr
Alto Recorder | F | tr
Oboe | C | tr
Oboe d'amore | A | tr
English Horn | F | tr
Clarinet in Bb | Bb | tr
Clarinet in A | A | tr
Clarinet in Eb | Eb | tr
Bass Clarinet | Bb | tr
Bassoon | C | bs (tn)
Contrabassoon | C (8vb) | bs
Sopranino Sax | Eb | tr
Soprano Sax | Bb | tr
Alto Sax | Eb | tr
Tenor Sax | Bb | tr
Baritone Sax | Eb | tr
Bass Sax | Bb | tr
Trumpet in Bb | Bb | tr
Trumpet in C | C | tr
Piccolo Trumpet | Bb | tr
Cornet in Bb | Bb | tr
Flugelhorn | Bb | tr
Horn in F | F | tr/bs
Horn in Bb alto | Bb | tr
Tenor Trombone | C | bs/tn
Bass Trombone | C | bs
Euphonium | Bb | tr/bs
Tuba in F | F | bs
Tuba in Eb | Eb | bs
Tuba in C | C | bs
Timpani | variable | bs
Glockenspiel | C (15ma) | tr
Xylophone | C (8va) | tr
Marimba | C | gr
Vibraphone | C (8va) | tr
Tubular Bells | C | tr
Soprano Voice | C | tr
Alto Voice | C | tr
Tenor Voice | C | tr
Bass Voice | C | bs
"""

family_map = {
    'Violin': 'Strings', 'Viola': 'Strings', 'Cello': 'Strings', 'Double Bass': 'Strings',
    'Harp': 'Strings', 'Guitar': 'Strings', 'Mandolin': 'Strings',
    'Piano': 'Keyboards', 'Organ': 'Keyboards', 'Harpsichord': 'Keyboards', 'Celesta': 'Keyboards',
    'Piccolo': 'Woodwinds', 'Flute': 'Woodwinds', 'Alto Flute': 'Woodwinds',
    'Recorder': 'Woodwinds', 'Oboe': 'Woodwinds', 'English Horn': 'Woodwinds',
    'Clarinet': 'Woodwinds', 'Bass Clarinet': 'Woodwinds', 'Bassoon': 'Woodwinds', 'Contrabassoon': 'Woodwinds',
    'Sax': 'Woodwinds',
    'Trumpet': 'Brass', 'Cornet': 'Brass', 'Flugelhorn': 'Brass',
    'Horn': 'Brass', 'Trombone': 'Brass', 'Euphonium': 'Brass', 'Tuba': 'Brass',
    'Timpani': 'Percussion', 'Glockenspiel': 'Percussion', 'Xylophone': 'Percussion',
    'Marimba': 'Percussion', 'Vibraphone': 'Percussion', 'Bells': 'Percussion',
    'Voice': 'Voices'
}

def get_family(name):
    for key, family in family_map.items():
        if key in name:
            return family
    return 'Other'

# Parse instruments
for line in instrument_data.strip().split('\n'):
    if '|' not in line or not line.strip():
        continue
    
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 3:
        continue
    
    name, key, clef = parts[0], parts[1], parts[2]
    
    instrument_id = name.lower().replace(' ', '_').replace('in_', '').replace('♭', 'b')
    
    inst = {
        "id": instrument_id,
        "name": name,
        "family": get_family(name),
        "transposition": {
            "type": "interval",
            "semitones": parse_transposition(key)
        },
        "clefs": parse_clefs(clef),
        "sounding_range": {
            "lowest": "C2",
            "highest": "C6"
        },
        "midi_program": get_midi_program(name)
    }
    
    instruments["instruments"].append(inst)

# Write to file  
with open('src/data/instruments_comprehensive.json', 'w') as f:
    json.dump(instruments, f, indent=2)

print(f"Generated {len(instruments['instruments'])} instruments")
print("File: src/data/instruments_comprehensive.json")
