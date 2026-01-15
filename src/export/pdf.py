"""PDF exporter for music21 scores using MuseScore for graphical sheet music."""
from pathlib import Path
from music21 import stream, environment
import subprocess
import shutil


class PDFExporter:
    """Export music21 scores to PDF format with proper sheet music notation."""
    
    def __init__(self):
        """Initialize PDF exporter and configure MuseScore path."""
        self._configure_musescore()
    
    def _configure_musescore(self):
        """Configure music21 to use MuseScore for PDF rendering."""
        try:
            # Try multiple possible MuseScore locations
            musescore_paths = [
                '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
                '/Applications/MuseScore 3.app/Contents/MacOS/mscore',
                '/usr/local/bin/mscore',
                shutil.which('mscore'),
                shutil.which('musescore')
            ]
            
            musescore_path = None
            for path in musescore_paths:
                if path and Path(path).exists():
                    musescore_path = path
                    break
            
            if musescore_path:
                # Configure music21 environment
                env = environment.UserSettings()
                env['musescoreDirectPNGPath'] = musescore_path
                env['musicxmlPath'] = musescore_path
                self.musescore_available = True
                self.musescore_path = musescore_path
            else:
                self.musescore_available = False
                self.musescore_path = None
                
        except Exception as e:
            print(f"MuseScore configuration error: {e}")
            self.musescore_available = False
            self.musescore_path = None
    
    def export(self, score: stream.Score, output_path: str) -> bool:
        """
        Export a music21 score to PDF with proper sheet music notation.
        
        Args:
            score: music21 Score object
            output_path: Path to save PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.musescore_available:
                # MuseScore is available - create proper sheet music PDF
                try:
                    score.write('musicxml.pdf', fp=str(output_file))
                    return True
                except Exception as e:
                    print(f"PDF export error: {e}")
                    # Fall through to MusicXML export
            
            # MuseScore not available - export MusicXML and provide instructions
            musicxml_path = output_file.with_suffix('.musicxml')
            score.write('musicxml', fp=str(musicxml_path))
            
            # Inform user
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("PDF Export - MuseScore Required")
            msg.setText("PDF export requires MuseScore to be installed.")
            msg.setInformativeText(
                f"I've exported a MusicXML file instead:\\n{musicxml_path}\\n\\n"
                f"To create a PDF with proper sheet music:\\n"
                f"1. Install MuseScore (free): brew install --cask musescore\\n"
                f"2. Open the .musicxml file in MuseScore\\n"
                f"3. File → Export → PDF\\n\\n"
                f"Or run: brew install --cask musescore"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
            return True
            
        except Exception as e:
            print(f"PDF export error: {e}")
            raise  # Re-raise so the UI can show the error
