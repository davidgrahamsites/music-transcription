"""Rhythm quantization and onset detection."""

import numpy as np
import librosa
from typing import List, Tuple
from dataclasses import dataclass

from utils.config import (
    SAMPLE_RATE, DEFAULT_TEMPO, DEFAULT_TIME_SIGNATURE,
    MIN_NOTE_DURATION, QUANTIZATION_STRENGTH
)


@dataclass
class QuantizedNote:
    """A quantized musical note."""
    start_time: float  # seconds
    duration: float  # seconds
    midi_note: int  # MIDI note number (rounded)
    confidence: float  # average confidence for this note
    start_beat: float  # beat position
    duration_beats: float  # duration in beats


class RhythmQuantizer:
    """Quantizes rhythm using onset detection and tempo."""
    
    def __init__(self):
        self.tempo_bpm = DEFAULT_TEMPO
        self.time_signature = DEFAULT_TIME_SIGNATURE
    
    def set_tempo(self, bpm: float):
        """Set tempo in beats per minute."""
        self.tempo_bpm = bpm
    
    def set_time_signature(self, numerator: int, denominator: int):
        """Set time signature."""
        self.time_signature = (numerator, denominator)
    
    def quantize(
        self,
        audio: np.ndarray,
        pitch_times: np.ndarray,
        pitch_midi: np.ndarray,
        pitch_confidences: np.ndarray,
        sr: int = SAMPLE_RATE
    ) -> List[QuantizedNote]:
        """
        Quantize rhythm from audio and pitch data.
        
        Args:
            audio: Audio signal
            pitch_times: Time stamps of pitch detections
            pitch_midi: MIDI note numbers
            pitch_confidences: Confidence scores
            sr: Sample rate
        
        Returns:
            List of quantized notes
        """
        if len(audio) == 0 or len(pitch_times) == 0:
            return []
        
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=audio,
            sr=sr,
            units='frames',
            backtrack=True
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # If no onsets detected, use pitch change points
        if len(onset_times) == 0:
            onset_times = self._detect_pitch_changes(pitch_times, pitch_midi)
        
        # Group pitches into notes based on onsets
        notes = self._group_pitches_into_notes(
            onset_times,
            pitch_times,
            pitch_midi,
            pitch_confidences
        )
        
        # Quantize note timings
        quantized_notes = self._quantize_timings(notes)
        
        return quantized_notes
    
    def _detect_pitch_changes(
        self,
        times: np.ndarray,
        midi_notes: np.ndarray,
        semitone_threshold: float = 0.5
    ) -> np.ndarray:
        """Detect significant pitch changes as note boundaries."""
        if len(times) < 2:
            return np.array([times[0]] if len(times) > 0 else [])
        
        # Calculate pitch differences
        pitch_diff = np.abs(np.diff(midi_notes))
        
        # Find indices where pitch changes significantly
        change_indices = np.where(pitch_diff > semitone_threshold)[0] + 1
        
        # Always include the first time
        change_times = np.concatenate([[times[0]], times[change_indices]])
        
        return change_times
    
    def _group_pitches_into_notes(
        self,
        onset_times: np.ndarray,
        pitch_times: np.ndarray,
        pitch_midi: np.ndarray,
        pitch_confidences: np.ndarray
    ) -> List[QuantizedNote]:
        """Group pitch detections into notes based on onset times."""
        notes = []
        
        # Add final onset at end of audio
        onset_times = np.append(onset_times, pitch_times[-1] if len(pitch_times) > 0 else 0)
        
        for i in range(len(onset_times) - 1):
            start_time = onset_times[i]
            end_time = onset_times[i + 1]
            
            # Find pitches in this time range
            mask = (pitch_times >= start_time) & (pitch_times < end_time)
            note_pitches = pitch_midi[mask]
            note_confidences = pitch_confidences[mask]
            
            if len(note_pitches) == 0:
                continue
            
            # Calculate average pitch (weighted by confidence)
            if np.sum(note_confidences) > 0:
                weighted_pitch = np.average(note_pitches, weights=note_confidences)
            else:
                weighted_pitch = np.mean(note_pitches)
            
            avg_confidence = np.mean(note_confidences)
            duration = end_time - start_time
            
            # Skip very short notes
            if duration < MIN_NOTE_DURATION:
                continue
            
            notes.append(QuantizedNote(
                start_time=start_time,
                duration=duration,
                midi_note=int(round(weighted_pitch)),
                confidence=float(avg_confidence),
                start_beat=0.0,  # Will be calculated in quantization
                duration_beats=0.0
            ))
        
        return notes
    
    def _quantize_timings(self, notes: List[QuantizedNote]) -> List[QuantizedNote]:
        """Quantize note timings to grid."""
        if not notes:
            return notes
        
        # Calculate beat duration in seconds
        beat_duration = 60.0 / self.tempo_bpm
        
        # Define quantization grid (16th note resolution)
        grid_subdivision = 4  # 16th notes = quarter note / 4
        grid_duration = beat_duration / grid_subdivision
        
        for note in notes:
            # Convert times to beats
            start_beat = note.start_time / beat_duration
            duration_beats = note.duration / beat_duration
            
            # Quantize with partial strength
            quantized_start_beat = self._quantize_value(
                start_beat, 1.0 / grid_subdivision, QUANTIZATION_STRENGTH
            )
            quantized_duration_beats = self._quantize_value(
                duration_beats, 1.0 / grid_subdivision, QUANTIZATION_STRENGTH
            )
            
            # Ensure minimum duration
            min_duration_beats = MIN_NOTE_DURATION / beat_duration
            quantized_duration_beats = max(quantized_duration_beats, min_duration_beats)
            
            note.start_beat = quantized_start_beat
            note.duration_beats = quantized_duration_beats
            
            # Update time-domain values
            note.start_time = quantized_start_beat * beat_duration
            note.duration = quantized_duration_beats * beat_duration
        
        return notes
    
    @staticmethod
    def _quantize_value(value: float, grid: float, strength: float) -> float:
        """Quantize a value to a grid with given strength."""
        quantized = round(value / grid) * grid
        return value * (1 - strength) + quantized * strength
