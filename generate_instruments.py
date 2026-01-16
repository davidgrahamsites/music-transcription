"""Generate comprehensive instruments.json from the user's exhaustive list.

This includes:
- Western orchestral (strings, woodwinds, brass, percussion, keyboards, voices)
- Chinese orchestra instruments
- Japanese traditional instruments
- Korean traditional instruments
- Indian classical instruments  
- Middle Eastern instruments
- European folk/early instruments
"""
import json

# MIDI program numbers (General MIDI + extended)
MIDI_PROGRAMS = {
    # Strings (0-7 + 24-31 + 40-47)
    'violin': 40, 'viola': 41, 'cello': 42, 'contrabass': 43, 'double bass': 43,
    'harp': 46, 'timpani': 47,
    'guitar': 24, 'acoustic guitar': 24, 'classical guitar': 25,
    'mandolin': 26, 'lute': 24, 'banjo': 105,
    
    # Piano/Keyboards (0-7)
    'piano': 0, 'harpsichord': 6, 'clavichord': 7, 'celesta': 8,
    
    # Organ (16-23)
    'organ': 19, 'church organ': 19, 'reed organ': 20,
    
    # Accordion (21-23)
    'accordion': 21,
    
    # Woodwinds (64-79)
    'flute': 73, 'piccolo': 72, 'recorder': 74, 
    'oboe': 68, 'english horn': 69, 'cor anglais': 69,
    'clarinet': 71, 'bassoon': 70,
    
    # Saxophone (64-67)
    'soprano sax': 64, 'alto sax': 65, 'tenor sax': 66, 'baritone sax': 67,
    'saxophone': 65, 'sax': 65,
    
    # Brass (56-63)
    'trumpet': 56, 'trombone': 57, 'tuba': 58, 'muted trumpet': 59,
    'french horn': 60, 'horn': 60, 'brass': 61, 'synth brass': 62,
    'euphonium': 58, 'cornet': 56, 'flugelhorn': 56,
    
    # Regional & Ethnic (104-111)
    'sitar': 104, 'banjo': 105, 'shamisen': 106, 'koto': 107,
    'kalimba': 108, 'bagpipe': 109, 'fiddle': 110, 'shanai': 111,
    'erhu': 110, 'pipa': 105, 'guzheng': 107,
    
    # Percussion
    'xylophone': 13, 'marimba': 12, 'vibraphone': 11, 'glockenspiel': 9,
    'tubular bells': 14, 'dulcimer': 15, 'crotales': 9,
    
    # Voices (52-55)
    'voice': 52, 'choir': 52, 'soprano': 52, 'alto': 52, 'tenor': 53, 'bass': 54,
}

def get_midi_program(name):
    """Get MIDI program number for instrument."""
    name_lower = name.lower()
    # Try exact matches first
    for key, prog in MIDI_PROGRAMS.items():
        if key == name_lower:
            return prog
    # Try partial matches
    for key, prog in MIDI_PROGRAMS.items():
        if key in name_lower:
            return prog
    return 0  # Default to piano

def parse_transposition(key_str, name):
    """Parse transposition from key string and handle octave displacements."""
    semitones = 0
    
    # Handle octave displacements
    if '8va' in key_str and '8vb' not in key_str:
        semitones = 12  # Sounds octave higher
    elif '8vb' in key_str:
        semitones = -12  # Sounds octave lower
    elif '15ma' in key_str:
        semitones = 24  # Sounds 2 octaves higher
    elif '15vb' in key_str or '16vb' in key_str:
        semitones = -24  # Sounds 2 octaves lower
    elif '22vb' in key_str:
        semitones = -36  # Sounds 3 octaves lower
    
    # Add transposition from key
    if 'Bb' in key_str or 'B♭' in key_str:
        semitones += -2
    elif 'Eb' in key_str or 'E♭' in key_str:
        if 'alto' in name.lower() or 'soprano' in name.lower():
            semitones += 3
        else:
            semitones += -3
    elif key_str.strip().startswith('A') and not key_str.startswith('Ab'):
        semitones += -3
    elif key_str.strip().startswith('F'):
        semitones += -5
    elif key_str.strip().startswith('G'):
        semitones += -2
    elif key_str.strip().startswith('D'):
        if 'contrabass' not in name.lower():
            semitones += 2
    elif key_str.strip().startswith('Ab'):
        semitones += -4
    
    return semitones

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
        clefs = ['treble', 'bass']  # Grand staff
    if 'perc' in clef_str:
        clefs.append('percussion')
    
    return clefs if clefs else ['treble']

# Parse the comprehensive instrument list
instruments_data = []

# Format: Name | Key/Trans | Clef | Family
comprehensive_list = """
Violin | C | tr | Strings
Viola | C | al | Strings
Viola d'amore | C | al/tr | Strings
Cello | C | bs | Strings
Cello piccolo | C | bs | Strings
Violoncello da spalla | C | bs | Strings
Double Bass | C (8vb) | bs | Strings
5-string Double Bass | C (8vb) | bs | Strings
Octobass | C (16vb) | bs | Strings
Treble Viol | C | tr | Strings
Tenor Viol | C | al/tn | Strings
Bass Viol | C | bs | Strings
Viola da gamba | C | bs | Strings
Violone | C | bs | Strings
Pedal Harp | C | gr | Strings
Lever Harp | C | gr | Strings
Classical Guitar | C (8vb) | tr | Strings
Mandolin | C | tr | Strings
Lute | C (8vb) | tr | Strings
Theorbo | C (8vb) | tr | Strings
Archlute | C (8vb) | tr | Strings
Piano | C | gr | Keyboards
Organ | C | gr | Keyboards
Harpsichord | C | gr | Keyboards
Clavichord | C | gr | Keyboards
Celesta | C (8va) | tr | Keyboards
Accordion | C | tr/bs | Keyboards
Piccolo | C (8va) | tr | Woodwinds
Flute | C | tr | Woodwinds
Alto Flute | G | tr | Woodwinds
Bass Flute | C (8vb) | tr | Woodwinds
Contrabass Flute | C (15vb) | tr | Woodwinds
Sopranino Recorder | F | tr | Woodwinds
Soprano Recorder | C | tr | Woodwinds
Alto Recorder | F | tr | Woodwinds  
Tenor Recorder | C | tr | Woodwinds
Bass Recorder | F | bs | Woodwinds
Great Bass Recorder | C | bs | Woodwinds
Oboe | C | tr | Woodwinds
Oboe d'amore | A | tr | Woodwinds
English Horn | F | tr | Woodwinds
Bass Oboe | C (8vb) | tr | Woodwinds
Heckelphone | C (8vb) | tr | Woodwinds
Piccolo Clarinet in Eb | Eb | tr | Woodwinds
Clarinet in Eb | Eb | tr | Woodwinds
Clarinet in D | D | tr | Woodwinds
Clarinet in C | C | tr | Woodwinds
Clarinet in Bb | Bb | tr | Woodwinds
Clarinet in A | A | tr | Woodwinds
Basset Clarinet | A | tr | Woodwinds
Basset Horn | F | tr | Woodwinds
Alto Clarinet | Eb | tr | Woodwinds
Bass Clarinet | Bb | tr | Woodwinds
Contra-alto Clarinet | Eb | tr | Woodwinds
Contrabass Clarinet | Bb | tr | Woodwinds
Bassoon | C | bs | Woodwinds
Tenoroon | F | bs | Woodwinds
Contrabassoon | C (8vb) | bs | Woodwinds
Sopranino Sax | Eb | tr | Woodwinds
Soprano Sax | Bb | tr | Woodwinds
Alto Sax | Eb | tr | Woodwinds
Tenor Sax | Bb | tr | Woodwinds
Baritone Sax | Eb | tr | Woodwinds
Bass Sax | Bb | tr | Woodwinds
Contrabass Sax | Eb | tr | Woodwinds
Trumpet in Bb | Bb | tr | Brass
Trumpet in C | C | tr | Brass
Trumpet in D | D | tr | Brass
Trumpet in Eb | Eb | tr | Brass
Piccolo Trumpet | Bb | tr | Brass
Cornet in Bb | Bb | tr | Brass
Cornet in Eb | Eb | tr | Brass
Flugelhorn | Bb | tr | Brass
Horn in F | F | tr | Brass
Horn in Bb alto | Bb | tr | Brass
Horn in Bb basso | Bb | bs | Brass
Horn in Eb | Eb | tr | Brass
Alto Trombone | Eb | al | Brass
Tenor Trombone | C | bs | Brass
Bass Trombone | C | bs | Brass
Contrabass Trombone | F | bs | Brass
Euphonium | Bb | tr/bs | Brass
Tuba in F | F | bs | Brass
Tuba in Eb | Eb | bs | Brass
Tuba in C | C | bs | Brass
Tuba in Bb | Bb | bs | Brass
Wagner Tuba | F | tr/bs | Brass
Timpani | variable | bs | Percussion
Glockenspiel | C (15ma) | tr | Percussion
Xylophone | C (8va) | tr | Percussion
Marimba | C | gr | Percussion
Vibraphone | C (8va) | tr | Percussion
Tubular Bells | C | tr | Percussion
Crotales | C (15ma) | tr | Percussion
Snare Drum | — | perc | Percussion
Bass Drum | — | perc | Percussion
Cymbals | — | perc | Percussion
Triangle | — | perc | Percussion
Tambourine | — | perc | Percussion
Erhu | D/A | tr | Regional
Zhonghu | G/D | al/tr | Regional
Gaohu | C/G | tr | Regional
Pipa | C | tr | Regional
Guzheng | C | gr | Regional
Yangqin | C | gr | Regional
Dizi | D | tr | Regional
Suona | C | tr | Regional
Sheng | C | tr | Regional
Shakuhachi | D | tr | Regional
Koto | C | gr | Regional
Shamisen | C | tr | Regional
Gayageum | C | gr | Regional
Sitar | C | tr | Regional
Veena | C | tr | Regional
Bansuri | C | tr | Regional
Oud | C | tr | Regional
Qanun | C | gr | Regional
Ney | C | tr | Regional
Soprano Voice | C | tr | Voices
Mezzo-soprano Voice | C | tr | Voices
Alto Voice | C | tr | Voices
Tenor Voice | C | tr | Voices
Baritone Voice | C | bs | Voices
Bass Voice | C | bs | Voices
"""

for line in comprehensive_list.strip().split('\n'):
    if not line.strip() or '|' not in line:
        continue
    
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 4:
        continue
    
    name, key, clef, family = parts
    
    # Create instrument ID
    inst_id = name.lower()
    inst_id = inst_id.replace(' ', '_').replace("'", '').replace('-', '_')
    inst_id = inst_id.replace('♭', 'b').replace('in_', '').replace('__', '_')
    
    instrument = {
        "id": inst_id,
        "name": name,
        "family": family,
        "transposition": {
            "type": "interval",
            "semitones": parse_transposition(key, name)
        },
        "clefs": parse_clefs(clef),
        "sounding_range": {
            "lowest": "C2",
            "highest": "C6"
        },
        "midi_program": get_midi_program(name)
    }
    
    instruments_data.append(instrument)

# Create final JSON structure
instruments_json = {"instruments": instruments_data}

# Write to file
with open('src/data/instruments.json', 'w') as f:
    json.dump(instruments_json, f, indent=2)

print(f"✅ Generated {len(instruments_data)} instruments")
print(f"   Families: {len(set(i['family'] for i in instruments_data))}")
for family in sorted(set(i['family'] for i in instruments_data)):
    count = len([i for i in instruments_data if i['family'] == family])
    print(f"   - {family}: {count}")
