"""Built-in MIDI player using pygame."""
import tempfile
import os
from pathlib import Path
from music21 import stream
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class MIDIPlayer:
    """Play MIDI files directly in the app using pygame."""
    
    def __init__(self):
        """Initialize the MIDI player."""
        self.initialized = False
        self.playing = False
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.initialized = True
            except Exception as e:
                print(f"Failed to initialize pygame mixer: {e}")
                self.initialized = False
        else:
            print("pygame not available - MIDI playback disabled")
    
    def play_score(self, score: stream.Score) -> bool:
        """
        Play a music21 score as MIDI.
        
        Args:
            score: music21 Score object
            
        Returns:
            True if playback started successfully, False otherwise
        """
        if not self.initialized:
            return False
        
        try:
            # Create temporary MIDI file
            temp_dir = tempfile.gettempdir()
            midi_path = os.path.join(temp_dir, 'melody_transcriber_playback.mid')
            
            # Write score to MIDI file
            score.write('midi', fp=midi_path)
            
            # Play the MIDI file
            pygame.mixer.music.load(midi_path)
            pygame.mixer.music.play()
            self.playing = True
            
            return True
            
        except Exception as e:
            print(f"MIDI playback error: {e}")
            return False
    
    def stop(self):
        """Stop playback."""
        if self.initialized and self.playing:
            try:
                pygame.mixer.music.stop()
                self.playing = False
            except Exception as e:
                print(f"Error stopping playback: {e}")
    
    def is_playing(self) -> bool:
        """Check if MIDI is currently playing."""
        if not self.initialized:
            return False
        
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def cleanup(self):
        """Clean up pygame resources."""
        if self.initialized:
            try:
                pygame.mixer.quit()
            except:
                pass
