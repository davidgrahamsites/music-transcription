"""MusicXML export functionality."""

import music21
import os
from typing import Optional

from utils.config import MUSICXML_VERSION, DEFAULT_COMPOSER


class MusicXMLExporter:
    """Handles export to MusicXML format."""
    
    @staticmethod
    def export(
        score: music21.stream.Score,
        output_path: str,
        composer: str = DEFAULT_COMPOSER,
        title: Optional[str] = None
    ) -> bool:
        """
        Export score to MusicXML file.
        
        Args:
            score: music21 Score object
            output_path: Path to output .musicxml or .xml file
            composer: Composer name for metadata
            title: Title for metadata (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            score.metadata = music21.metadata.Metadata()
            score.metadata.composer = composer
            
            if title:
                score.metadata.title = title
            else:
                # Use filename as title
                title = os.path.splitext(os.path.basename(output_path))[0]
                score.metadata.title = title
            
            # Write to file
            score.write('musicxml', fp=output_path)
            
            return True
        
        except Exception as e:
            print(f"MusicXML export error: {e}")
            return False
    
    @staticmethod
    def export_concert_pitch(
        score: music21.stream.Score,
        output_path: str,
        **kwargs
    ) -> bool:
        """
        Export score in concert pitch (sounding pitch).
        
        This assumes the score was already built in concert pitch.
        """
        return MusicXMLExporter.export(score, output_path, **kwargs)
    
    @staticmethod
    def export_written_pitch(
        score: music21.stream.Score,
        output_path: str,
        **kwargs
    ) -> bool:
        """
        Export score in written pitch (for transposing instruments).
        
        This assumes the score was already built in written pitch.
        """
        return MusicXMLExporter.export(score, output_path, **kwargs)
