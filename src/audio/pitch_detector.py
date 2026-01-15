"""Pitch detection using librosa's pYIN algorithm."""

import numpy as np
import librosa
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
    """Detects pitch from monophonic audio using librosa's pYIN."""
    
    def __init__(self, fmin=50.0, fmax=2000.0):
        """
        Initialize pitch detector.
        
        Args:
            fmin: Minimum frequency in Hz (default: 50 Hz, ~G1)
            fmax: Maximum frequency in Hz (default: 2000 Hz, ~B6)
        """
        self.fmin = fmin
        self.fmax = fmax
    
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
        
        # Use librosa's pYIN for pitch detection
        # pYIN is a probabilistic version of YIN, robust for monophonic pitch
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=self.fmin,
            fmax=self.fmax,
            sr=sr,
            frame_length=2048,
            hop_length=512  # ~11.6ms hop at 44.1kHz
        )
        
        # Create time array
        hop_length = 512
        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)
        
        # Use voiced probabilities as confidence
        confidences = voiced_probs
        
        # Filter out unvoiced frames and low confidence
        valid_mask = (voiced_flag) & (confidences > PITCH_CONFIDENCE_THRESHOLD)
        
        times = times[valid_mask]
        frequencies = f0[valid_mask]
        confidences = confidences[valid_mask]
        
        # Replace NaN frequencies with interpolation
        if len(frequencies) > 0:
            nan_mask = np.isnan(frequencies)
            if np.any(nan_mask):
                # Interpolate over NaNs
                if np.all(nan_mask):
                    # All NaN, can't interpolate
                    frequencies = np.full_like(frequencies, 440.0)
                else:
                    valid_indices = np.where(~nan_mask)[0]
                    if len(valid_indices) > 1:
                        from scipy.interpolate import interp1d
                        f = interp1d(
                            times[~nan_mask], 
                            frequencies[~nan_mask],
                            kind='linear',
                            fill_value='extrapolate'
                        )
                        frequencies[nan_mask] = f(times[nan_mask])
                    else:
                        frequencies[nan_mask] = frequencies[~nan_mask][0]
        
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
