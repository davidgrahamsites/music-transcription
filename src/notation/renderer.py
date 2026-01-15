"""Simple ASCII/text-based notation renderer."""
from music21 import stream


class NotationRenderer:
    """Render musical notation as readable text/ASCII."""
    
    @staticmethod
    def render_to_text(score: stream.Score) -> str:
        """
        Render score as readable text notation.
        
        Args:
            score: music21 Score object
            
        Returns:
            String representation of the notation
        """
        try:
            output = []
            output.append("=" * 60)
            output.append("MUSICAL NOTATION")
            output.append("=" * 60)
            
            # Get metadata
            if score.metadata:
                if score.metadata.title:
                    output.append(f"Title: {score.metadata.title}")
                if score.metadata.composer:
                    output.append(f"Composer: {score.metadata.composer}")
                output.append("")
            
            # Get all parts
            for part_num, part in enumerate(score.parts, 1):
                instrument_name = part.partName if part.partName else f"Part {part_num}"
                output.append(f"\n{instrument_name}:")
                output.append("-" * 60)
                
                # Get all measures
                for measure in part.getElementsByClass('Measure'):
                    measure_num = measure.number if hasattr(measure, 'number') else "?"
                    
                    # Get time signature if present
                    ts = measure.timeSignature
                    ts_str = f" [{ts.numerator}/{ts.denominator}]" if ts else ""
                    
                    # Get key signature if present  
                    ks = measure.keySignature
                    ks_str = f" {ks.asKey().name}" if ks else ""
                    
                    output.append(f"\nMeasure {measure_num}{ts_str}{ks_str}:")
                    
                    # Get all notes and rests
                    notes_line = []
                    durations_line = []
                    
                    for element in measure.notesAndRests:
                        if element.isNote:
                            # Show note name with octave
                            notes_line.append(f"{element.nameWithOctave:>5}")
                            # Show duration - convert to float for formatting
                            ql = float(element.quarterLength)
                            if ql == 1.0:
                                durations_line.append("  ♩  ")
                            elif ql == 0.5:
                                durations_line.append("  ♪  ")
                            elif ql == 2.0:
                                durations_line.append("  𝅗𝅥  ")
                            elif ql == 4.0:
                                durations_line.append("  𝅝  ")
                            else:
                                durations_line.append(f" {ql:>3.1f}")
                        elif element.isRest:
                            notes_line.append(" REST")
                            durations_line.append(f" {float(element.quarterLength):>3.1f}")
                    
                    if notes_line:
                        output.append("  Notes:     " + " ".join(notes_line))
                        output.append("  Durations: " + " ".join(durations_line))
            
            output.append("\n" + "=" * 60)
            output.append("Legend:")
            output.append("  ♩ = Quarter note (1 beat)")
            output.append("  ♪ = Eighth note (0.5 beats)")  
            output.append("  𝅗𝅥 = Half note (2 beats)")
            output.append("  𝅝 = Whole note (4 beats)")
            output.append("=" * 60)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error rendering notation: {e}"
