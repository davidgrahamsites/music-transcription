"""PDF exporter for music21 scores."""
from pathlib import Path
from music21 import stream


class PDFExporter:
    """Export music21 scores to PDF format."""
    
    def export(self, score: stream.Score, output_path: str) -> bool:
        """
        Export a music21 score to PDF.
        
        Args:
            score: music21 Score object
            output_path: Path to save PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use music21's write method with musescore backend
            score.write('musicxml.pdf', fp=str(output_file))
            return True
            
        except Exception as e:
            print(f"PDF export error: {e}")
            return False
