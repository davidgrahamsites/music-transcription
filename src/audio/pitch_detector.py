"""Pitch detection using CREPE."""

import numpy as np
import crepe
from scipy import signal
from typing import Tuple, List
from dataclasses import dataclass

from utils.config import (
    SAMPLE_RATE, PITCH_CONFIDENCE_THRESHOLD, PITCH_SMOOTH_WINDOW
)


@dataclass
class PitchAnalysis:
    """Results of pitch detection."""
    times: np.ndarray  # Time stamps in seconds
    frequencies: np.ndarray  # Fundamental frequencies in Hz
    confidences: np.ndarray  # Confidence scores (0-1)
    midi_notes: np.ndarray  # MIDI note numbers (can be float for microtones)


class PitchDetector:
    """Detects pitch from monophonic audio using CREPE."""
    
    def __init__(self, model_capacity='tiny'):
        """
        Initialize pitch detector.
        
        Args:
            model_capacity: CREPE model size ('tiny', 'small', 'medium', 'large', 'full')
                           'tiny' is fastest, 'full' is most accurate
        """
        self.model_capacity = model_capacity
    
    def detect(self, audio: np.ndarray, sr: int = SAMPLE_RATE) -> PitchAnalysis:
        """
        Detect pitch from audio.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate
        
        Returns:
            PitchAnalysis object with times, frequencies, confidences, and MIDI notes
        """
        if len(audio) == 0:
            return PitchAnalysis(
                times=np.array([]),
                frequencies=np.array([]),
                confidences=np.array([]),
                midi_notes=np.array([])
            )
        
        # Run CREPE
        times, frequencies, confidences, _ = crepe.predict(
            audio,
            sr,
            model_capacity=self.model_capacity,
            viterbi=True,  # Use Viterbi decoding for smoother results
            step_size=10  # 10ms hop size
        )
        
        # Filter out low-confidence frames
        valid_mask = confidences > PITCH_CONFIDENCE_THRESHOLD
        times = times[valid_mask]
        frequencies = frequencies[valid_mask]
        confidences = confidences[valid_mask]
        
        # Smooth frequencies with median filter
        if len(frequencies) > PITCH_SMOOTH_WINDOW:
            frequencies = signal.medfilt(frequencies, kernel_size=PITCH_SMOOTH_WINDOW)
        
        # Convert Hz to MIDI note numbers
        midi_notes = self._hz_to_midi(frequencies)
        
        return PitchAnalysis(
            times=times,
            frequencies=frequencies,
            confidences=confidences,
            midi_notes=midi_notes
        )
    
    @staticmethod
    def _hz_to_midi(frequencies: np.ndarray) -> np.ndarray:
        """Convert frequencies in Hz to MIDI note numbers."""
        # MIDI note number = 69 + 12 * log2(f / 440)
        # Handle zeros to avoid log of zero
        frequencies = np.maximum(frequencies, 1e-10)
        midi_notes = 69 + 12 * np.log2(frequencies / 440.0)
        return midi_notes
    
    @staticmethod
    def midi_to_hz(midi_note: float) -> float:
        """Convert MIDI note number to frequency in Hz."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    
    @staticmethod
    def midi_to_note_name(midi_note: int) -> str:
        """Convert MIDI note number to note name (e.g., 60 -> 'C4')."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note = note_names[midi_note % 12]
        return f"{note}{octave}"
