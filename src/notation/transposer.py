"""Transposition between concert and written pitch."""

import music21
from typing import List
import numpy as np

from notation.instrument_db import Instrument


class Transposer:
    """Handles transposition between concert and written pitch."""
    
    @staticmethod
    def concert_to_written(
        concert_pitches: List[int],
        instrument: Instrument
    ) -> List[int]:
        """
        Convert concert pitch to written pitch for an instrument.
        
        Args:
            concert_pitches: List of MIDI note numbers in concert pitch
            instrument: Instrument object with transposition info
        
        Returns:
            List of MIDI note numbers in written pitch
        """
        # For transposing instruments, written pitch is HIGHER than concert
        # For example, Horn in F sounds a P5 lower (-7 semitones)
        # So written pitch = concert pitch - transposition_semitones
        # If transposition_semitones = -7, written = concert - (-7) = concert + 7
        
        written_pitches = []
        for concert_pitch in concert_pitches:
            written_pitch = concert_pitch - instrument.transposition_semitones
            written_pitches.append(written_pitch)
        
        return written_pitches
    
    @staticmethod
    def written_to_concert(
        written_pitches: List[int],
        instrument: Instrument
    ) -> List[int]:
        """
        Convert written pitch to concert pitch for an instrument.
        
        Args:
            written_pitches: List of MIDI note numbers in written pitch
            instrument: Instrument object with transposition info
        
        Returns:
            List of MIDI note numbers in concert pitch
        """
        concert_pitches = []
        for written_pitch in written_pitches:
            concert_pitch = written_pitch + instrument.transposition_semitones
            concert_pitches.append(concert_pitch)
        
        return concert_pitches
    
    @staticmethod
    def transpose_stream(
        stream: music21.stream.Stream,
        semitones: int
    ) -> music21.stream.Stream:
        """
        Transpose a music21 stream by semitones.
        
        Args:
            stream: music21 Stream object
            semitones: Number of semitones to transpose (positive = up, negative = down)
        
        Returns:
            Transposed stream
        """
        if semitones == 0:
            return stream
        
        interval = music21.interval.Interval(semitones)
        transposed_stream = stream.transpose(interval)
        return transposed_stream
