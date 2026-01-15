"""MIDI export functionality."""

import music21
import os
from typing import Optional


class MIDIExporter:
    """Handles export to MIDI format."""
    
    @staticmethod
    def export(
        score: music21.stream.Score,
        output_path: str
    ) -> bool:
        """
        Export score to MIDI file.
        
        Args:
            score: music21 Score object
            output_path: Path to output .mid or .midi file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write to MIDI file
            score.write('midi', fp=output_path)
            return True
        
        except Exception as e:
            print(f"MIDI export error: {e}")
            return False
