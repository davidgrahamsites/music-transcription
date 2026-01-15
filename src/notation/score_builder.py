"""Build music21 Score from analyzed audio."""

import music21
from typing import List, Tuple, Optional
import numpy as np

from audio.rhythm_quantizer import QuantizedNote
from audio.key_detector import KeyDetector
from notation.instrument_db import Instrument, InstrumentDatabase
from notation.transposer import Transposer
from utils.config import DEFAULT_TEMPO


class ScoreBuilder:
    """Builds music21 Score from quantized notes."""
    
    def __init__(self, instrument_db: InstrumentDatabase):
        self.instrument_db = instrument_db
    
    def build(
        self,
        notes: List[QuantizedNote],
        instrument: Instrument,
        key_name: str,
        time_signature: Tuple[int, int],
        tempo_bpm: int,
        use_written_pitch: bool = True
    ) -> music21.stream.Score:
        """
        Build a music21 Score from quantized notes.
        
        Args:
            notes: List of quantized notes
            instrument: Instrument object
            key_name: Key signature (e.g., "C major", "A minor")
            time_signature: Tuple of (numerator, denominator)
            tempo_bpm: Tempo in BPM
            use_written_pitch: If True, use written pitch; if False, use concert pitch
        
        Returns:
            music21 Score object
        """
        # Create score and part
        score = music21.stream.Score()
        part = music21.stream.Part()
        part.partName = instrument.name
        
        # Set instrument
        m21_instrument = self._get_music21_instrument(instrument)
        part.insert(0, m21_instrument)
        
        # Create first measure with key, time signature, and tempo
        measure = music21.stream.Measure(number=1)
        
        # Add key signature
        key = KeyDetector.key_to_music21(key_name)
        measure.insert(0, key)
        
        # Add time signature
        ts = music21.meter.TimeSignature(f'{time_signature[0]}/{time_signature[1]}')
        measure.insert(0, ts)
        
        # Add tempo
        tempo = music21.tempo.MetronomeMark(number=tempo_bpm)
        measure.insert(0, tempo)
        
        # Add clef
        avg_pitch = np.mean([n.midi_note for n in notes]) if notes else 60
        clef_name = self.instrument_db.get_preferred_clef(instrument.id, int(avg_pitch))
        clef = self._get_clef(clef_name)
        measure.insert(0, clef)
        
        # Convert notes to written pitch if needed
        if use_written_pitch:
            note_pitches = Transposer.concert_to_written(
                [n.midi_note for n in notes],
                instrument
            )
        else:
            note_pitches = [n.midi_note for n in notes]
        
        # Add notes to measures
        current_beat = 0.0
        beats_per_measure = time_signature[0] * (4.0 / time_signature[1])
        measure_number = 1
        
        for note, pitch in zip(notes, note_pitches):
            # Check if we need a new measure
            while current_beat >= beats_per_measure:
                part.append(measure)
                measure_number += 1
                measure = music21.stream.Measure(number=measure_number)
                current_beat -= beats_per_measure
            
            # Create note
            m21_note = music21.note.Note(midi=pitch)
            m21_note.quarterLength = note.duration_beats
            
            # Add to measure
            measure.insert(current_beat, m21_note)
            current_beat += note.duration_beats
        
        # Append final measure
        if len(measure.notesAndRests) > 0:
            part.append(measure)
        
        # Add part to score
        score.append(part)
        
        return score
    
    def _get_music21_instrument(self, instrument: Instrument) -> music21.instrument.Instrument:
        """Get appropriate music21 instrument object."""
        # Map instrument family to music21 instrument classes
        # This is a simplified mapping
        if instrument.family == 'Strings':
            if 'violin' in instrument.id.lower():
                return music21.instrument.Violin()
            elif 'viola' in instrument.id.lower():
                return music21.instrument.Viola()
            elif 'cello' in instrument.id.lower():
                return music21.instrument.Violoncello()
            elif 'bass' in instrument.id.lower():
                return music21.instrument.Contrabass()
            elif 'harp' in instrument.id.lower():
                return music21.instrument.Harp()
            elif 'guitar' in instrument.id.lower():
                return music21.instrument.Guitar()
        elif instrument.family == 'Brass':
            if 'horn' in instrument.id.lower():
                return music21.instrument.Horn()
            elif 'trumpet' in instrument.id.lower():
                return music21.instrument.Trumpet()
            elif 'trombone' in instrument.id.lower():
                return music21.instrument.Trombone()
            elif 'tuba' in instrument.id.lower():
                return music21.instrument.Tuba()
        elif instrument.family == 'Woodwinds':
            if 'flute' in instrument.id.lower():
                return music21.instrument.Flute()
            elif 'oboe' in instrument.id.lower():
                return music21.instrument.Oboe()
            elif 'clarinet' in instrument.id.lower():
                return music21.instrument.Clarinet()
            elif 'bassoon' in instrument.id.lower():
                return music21.instrument.Bassoon()
            elif 'saxophone' in instrument.id.lower():
                return music21.instrument.Saxophone()
        elif instrument.family == 'Keyboard':
            if 'piano' in instrument.id.lower():
                return music21.instrument.Piano()
            elif 'organ' in instrument.id.lower():
                return music21.instrument.Organ()
            elif 'harpsichord' in instrument.id.lower():
                return music21.instrument.Harpsichord()
        elif instrument.family == 'Vocal':
            return music21.instrument.Voice()
        
        # Default: generic instrument
        generic = music21.instrument.Instrument()
        generic.instrumentName = instrument.name
        generic.midiProgram = instrument.midi_program
        return generic
    
    @staticmethod
    def _get_clef(clef_name: str) -> music21.clef.Clef:
        """Get music21 clef object from name."""
        clef_map = {
            'treble': music21.clef.TrebleClef(),
            'bass': music21.clef.BassClef(),
            'alto': music21.clef.AltoClef(),
            'tenor': music21.clef.TenorClef()
        }
        return clef_map.get(clef_name.lower(), music21.clef.TrebleClef())
