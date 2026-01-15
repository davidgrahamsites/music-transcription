"""Instrument database loader and query interface."""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Instrument:
    """Represents a musical instrument with all metadata."""
    id: str
    name: str
    family: str
    transposition_type: str
    transposition_semitones: int
    clefs: List[str]
    sounding_range: Tuple[str, str]
    written_range: Tuple[str, str]
    preferred_range: Tuple[str, str]
    octave_displacement: int
    midi_program: int
    lyrics_support: bool = False


class InstrumentDatabase:
    """Loads and queries instrument metadata."""
    
    def __init__(self, db_path: str):
        """Load instrument database from JSON file."""
        self.instruments: Dict[str, Instrument] = {}
        self._load_database(db_path)
    
    def _load_database(self, db_path: str):
        """Load instruments from JSON file."""
        # Handle both absolute and relative paths
        if not os.path.isabs(db_path):
            # For PyInstaller, check if we're in a bundle
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_path, db_path)
        
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        for inst_data in data['instruments']:
            inst = Instrument(
                id=inst_data['id'],
                name=inst_data['name'],
                family=inst_data['family'],
                transposition_type=inst_data['transposition']['type'],
                transposition_semitones=inst_data['transposition']['semitones'],
                clefs=inst_data['clefs'],
                sounding_range=(
                    inst_data['sounding_range']['lowest'],
                    inst_data['sounding_range']['highest']
                ),
                written_range=(
                    inst_data['written_range']['lowest'],
                    inst_data['written_range']['highest']
                ),
                preferred_range=(
                    inst_data['preferred_range']['lowest'],
                    inst_data['preferred_range']['highest']
                ),
                octave_displacement=inst_data['octave_displacement'],
                midi_program=inst_data['midi_program'],
                lyrics_support=inst_data.get('lyrics_support', False)
            )
            self.instruments[inst.id] = inst
    
    def get_instrument(self, instrument_id: str) -> Optional[Instrument]:
        """Get instrument by ID."""
        return self.instruments.get(instrument_id)
    
    def list_by_family(self, family: str) -> List[Instrument]:
        """Get all instruments in a family."""
        return [inst for inst in self.instruments.values() 
                if inst.family == family]
    
    def get_all_families(self) -> List[str]:
        """Get list of all instrument families."""
        families = set(inst.family for inst in self.instruments.values())
        return sorted(families)
    
    def get_all_instruments(self) -> List[Instrument]:
        """Get all instruments sorted by family then name."""
        instruments = list(self.instruments.values())
        instruments.sort(key=lambda x: (x.family, x.name))
        return instruments
    
    def get_transposition_semitones(self, instrument_id: str) -> int:
        """Get transposition in semitones (concert to written)."""
        inst = self.get_instrument(instrument_id)
        if inst:
            return inst.transposition_semitones
        return 0
    
    def get_preferred_clef(self, instrument_id: str, avg_pitch_midi: Optional[int] = None) -> str:
        """Get preferred clef for instrument, optionally based on pitch range."""
        inst = self.get_instrument(instrument_id)
        if not inst or not inst.clefs:
            return 'treble'
        
        # If only one clef, return it
        if len(inst.clefs) == 1:
            return inst.clefs[0]
        
        # If no pitch info, return first clef
        if avg_pitch_midi is None:
            return inst.clefs[0]
        
        # Select clef based on average pitch
        # This is a simplified heuristic
        if 'treble' in inst.clefs and avg_pitch_midi >= 60:  # Middle C and above
            return 'treble'
        elif 'bass' in inst.clefs and avg_pitch_midi < 60:
            return 'bass'
        elif 'alto' in inst.clefs and 48 <= avg_pitch_midi < 67:
            return 'alto'
        elif 'tenor' in inst.clefs and 50 <= avg_pitch_midi < 64:
            return 'tenor'
        
        return inst.clefs[0]


import sys
