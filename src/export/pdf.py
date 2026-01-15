"""PDF exporter for music21 scores.

Since MuseScore/LilyPond may not be available, this exports 
MusicXML first and provides instructions to convert to PDF.
"""
from pathlib import Path
from music21 import stream
from PySide6.QtWidgets import QMessageBox
import subprocess
import shutil


class PDFExporter:
    """Export music21 scores to PDF format."""
    
    def export(self, score: stream.Score, output_path: str) -> bool:
        """
        Export a music21 score to PDF.
        
        Since PDF export requires external tools (MuseScore or LilyPond),
        this method tries multiple approaches:
        1. Direct PDF export via MuseScore (if available)
        2. Export MusicXML and inform user to open in MuseScore
        
        Args:
            score: music21 Score object
            output_path: Path to save PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to find MuseScore
            musescore_paths = [
                '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
                '/Applications/MuseScore 3.app/Contents/MacOS/mscore',
                shutil.which('mscore'),
                shutil.which('musescore')
            ]
            
            musescore_path = None
            for path in musescore_paths:
                if path and Path(path).exists():
                    musescore_path = path
                    break
            
            if musescore_path:
                # MuseScore is available - try direct PDF export
                try:
                    score.write('musicxml.pdf', fp=str(output_file))
                    return True
                except Exception as e:
                    print(f"Direct PDF export failed: {e}")
                    # Fall through to MusicXML export
            
            # MuseScore not available - export MusicXML and provide instructions
            musicxml_path = output_file.with_suffix('.musicxml')
            score.write('musicxml', fp=str(musicxml_path))
            
            # Inform user
            from PySide6.QtWidgets import QApplication
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("PDF Export - MuseScore Required")
            msg.setText("PDF export requires MuseScore to be installed.")
            msg.setInformativeText(
                f"I've exported a MusicXML file instead:\\n{musicxml_path}\\n\\n"
                f"To create a PDF:\\n"
                f"1. Install MuseScore (free): https://musescore.org\\n"
                f"2. Open the .musicxml file in MuseScore\\n"
                f"3. File → Export → PDF"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
            return True
            
        except Exception as e:
            print(f"PDF export error: {e}")
            raise  # Re-raise so the UI can show the error
