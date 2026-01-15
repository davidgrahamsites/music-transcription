"""Audio recording with level monitoring."""

import numpy as np
import sounddevice as sd
from typing import Optional, Tuple, Callable
import threading
import time

from utils.config import (
    SAMPLE_RATE, CHANNELS, DTYPE,
    CLIPPING_THRESHOLD, TOO_QUIET_THRESHOLD
)


class AudioRecorder:
    """Handles audio recording with real-time level monitoring."""
    
    def __init__(self):
        self.is_recording = False
        self.recorded_frames = []
        self.current_rms = -80.0
        self.current_peak = -80.0
        self.stream = None
        self.level_callbacks = []
        
    def start_recording(self, callback: Optional[Callable] = None):
        """Start recording audio."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recorded_frames = []
        
        def audio_callback(indata, frames, time_info, status):
            """Callback for audio stream."""
            if status:
                print(f"Audio status: {status}")
            
            # Store audio data
            self.recorded_frames.append(indata.copy())
            
            # Calculate levels
            rms = np.sqrt(np.mean(indata ** 2))
            peak = np.max(np.abs(indata))
            
            # Convert to dBFS
            self.current_rms = 20 * np.log10(max(rms, 1e-10))
            self.current_peak = 20 * np.log10(max(peak, 1e-10))
            
            # Notify level callbacks
            for cb in self.level_callbacks:
                try:
                    cb(self.current_rms, self.current_peak)
                except Exception as e:
                    print(f"Level callback error: {e}")
        
        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=audio_callback
        )
        self.stream.start()
        
        if callback:
            callback()
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return recorded audio."""
        if not self.is_recording:
            return np.array([], dtype=DTYPE)
        
        self.is_recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Concatenate all frames
        if self.recorded_frames:
            audio_data = np.concatenate(self.recorded_frames, axis=0)
            return audio_data.flatten()
        else:
            return np.array([], dtype=DTYPE)
    
    def get_levels(self) -> Tuple[float, float]:
        """Get current RMS and peak levels in dBFS."""
        return self.current_rms, self.current_peak
    
    def is_clipping(self) -> bool:
        """Check if signal is clipping."""
        return self.current_peak > CLIPPING_THRESHOLD
    
    def is_too_quiet(self) -> bool:
        """Check if signal is too quiet."""
        return self.current_rms < TOO_QUIET_THRESHOLD
    
    def add_level_callback(self, callback: Callable[[float, float], None]):
        """Add callback for level updates."""
        self.level_callbacks.append(callback)
    
    def remove_level_callback(self, callback: Callable[[float, float], None]):
        """Remove level callback."""
        if callback in self.level_callbacks:
            self.level_callbacks.remove(callback)
    
    @staticmethod
    def get_input_devices():
        """Get list of available input devices."""
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels']
                })
        return input_devices
