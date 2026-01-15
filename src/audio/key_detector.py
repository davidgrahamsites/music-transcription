"""Key detection using music21."""

import music21
import numpy as np
from typing import Tuple, Optional

from utils.config import KEY_CONFIDENCE_THRESHOLD


class KeyDetector:
    """Detects musical key using Krumhansl-Schmuckler algorithm."""
    
    def detect(self, midi_notes: np.ndarray) -> Tuple[str, float]:
        """
        Detect key from MIDI note numbers.
        
        Args:
            midi_notes: Array of MIDI note numbers
        
        Returns:
            Tuple of (key_name, confidence)
            e.g., ("C major", 0.85) or ("A minor", 0.72)
        """
        if len(midi_notes) == 0:
            return ("C major", 0.0)
        
        # Round to nearest semitone and convert to integers
        midi_notes = np.round(midi_notes).astype(int)
        
        # Create a music21 stream with the notes
        stream = music21.stream.Stream()
        for midi_note in midi_notes:
            n = music21.note.Note(midi=midi_note)
            n.quarterLength = 1.0  # Arbitrary duration
            stream.append(n)
        
        # Analyze key
        try:
            key = stream.analyze('key')
            
            # Get key name
            key_name = f"{key.tonic.name} {key.mode}"
            
            # music21's key.correlationCoefficient gives confidence
            confidence = key.correlationCoefficient
            
            return (key_name, float(confidence))
        except Exception as e:
            print(f"Key detection error: {e}")
            return ("C major", 0.0)
    
    @staticmethod
    def parse_key_name(key_name: str) -> Tuple[str, str]:
        """
        Parse key name into tonic and mode.
        
        Args:
            key_name: e.g., "C major", "A minor", "F# major"
        
        Returns:
            Tuple of (tonic, mode)
        """
        parts = key_name.strip().split()
        if len(parts) >= 2:
            tonic = parts[0]
            mode = parts[1].lower()
            return (tonic, mode)
        else:
            return ("C", "major")
    
    @staticmethod
    def key_to_music21(key_name: str) -> music21.key.Key:
        """Convert key name string to music21 Key object."""
        tonic, mode = KeyDetector.parse_key_name(key_name)
        return music21.key.Key(tonic, mode)
