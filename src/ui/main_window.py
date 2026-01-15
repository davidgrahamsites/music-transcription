"""Main application window."""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSpinBox,
    QProgressBar, QTextEdit, QGroupBox, QFileDialog,
    QMessageBox, QApplication
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
import numpy as np

from notation.instrument_db import InstrumentDatabase, Instrument
from audio.recorder import AudioRecorder
from audio.pitch_detector import PitchDetector
from audio.rhythm_quantizer import RhythmQuantizer
from audio.key_detector import KeyDetector
from notation.score_builder import ScoreBuilder
from export.musicxml import MusicXMLExporter
from export.midi import MIDIExporter
from export.pdf import PDFExporter
from utils.config import INSTRUMENTS_DB_PATH, LEVEL_UPDATE_INTERVAL
from utils.git_version import GIT_COMMIT


class MainWindow(QMainWindow):
    """Main application window for MelodyTranscriber."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.instrument_db = InstrumentDatabase(INSTRUMENTS_DB_PATH)
        self.recorder = AudioRecorder()
        self.pitch_detector = PitchDetector()  # Uses librosa pYIN
        self.rhythm_quantizer = RhythmQuantizer()
        self.key_detector = KeyDetector()
        self.score_builder = ScoreBuilder(self.instrument_db)
        
        # State
        self.current_instrument = None
        self.current_score = None
        self.current_notes = None
        self.detected_key = "C major"
        self.key_confidence = 0.0
        
        # Setup UI
        self.init_ui()
        
        # Setup level meter timer
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.update_levels)
        self.level_timer.start(LEVEL_UPDATE_INTERVAL)
        
        # Set default instrument
        self.on_family_changed(0)
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle(f"MelodyTranscriber v1.0.0 (commit: {GIT_COMMIT})")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # === Instrument Selection ===
        inst_group = QGroupBox("Instrument Settings")
        inst_layout = QHBoxLayout()
        
        inst_layout.addWidget(QLabel("Family:"))
        self.family_combo = QComboBox()
        families = self.instrument_db.get_all_families()
        self.family_combo.addItems(families)
        self.family_combo.currentIndexChanged.connect(self.on_family_changed)
        inst_layout.addWidget(self.family_combo)
        
        inst_layout.addWidget(QLabel("Instrument:"))
        self.instrument_combo = QComboBox()
        self.instrument_combo.currentIndexChanged.connect(self.on_instrument_changed)
        inst_layout.addWidget(self.instrument_combo)
        
        inst_group.setLayout(inst_layout)
        main_layout.addWidget(inst_group)
        
        # === Musical Settings ===
        music_group = QGroupBox("Musical Settings")
        music_layout = QHBoxLayout()
        
        music_layout.addWidget(QLabel("Tempo (BPM):"))
        self.tempo_spin = QSpinBox()
        self.tempo_spin.setRange(40, 240)
        self.tempo_spin.setValue(120)
        self.tempo_spin.valueChanged.connect(self.on_tempo_changed)
        music_layout.addWidget(self.tempo_spin)
        
        music_layout.addWidget(QLabel("Time Signature:"))
        self.time_sig_combo = QComboBox()
        self.time_sig_combo.addItems(["4/4", "3/4", "2/4", "6/8", "5/4", "7/8"])
        music_layout.addWidget(self.time_sig_combo)
        
        music_layout.addWidget(QLabel("Key:"))
        self.key_label = QLabel("C major (auto)")
        self.key_label.setStyleSheet("font-weight: bold;")
        music_layout.addWidget(self.key_label)
        
        music_group.setLayout(music_layout)
        main_layout.addWidget(music_group)
        
        # === Recording Controls ===
        rec_group = QGroupBox("Recording")
        rec_layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.record_btn = QPushButton("● Record")
        self.record_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 10px;")
        self.record_btn.clicked.connect(self.on_record_clicked)
        button_layout.addWidget(self.record_btn)
        
        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        button_layout.addWidget(self.stop_btn)
        
        self.transcribe_btn = QPushButton("♪ Transcribe")
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.clicked.connect(self.on_transcribe_clicked)
        button_layout.addWidget(self.transcribe_btn)
        
        rec_layout.addLayout(button_layout)
        
        # Level meter
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Input Level:"))
        self.level_bar = QProgressBar()
        self.level_bar.setRange(-80, 0)
        self.level_bar.setValue(-80)
        self.level_bar.setFormat("%v dBFS")
        level_layout.addWidget(self.level_bar)
        
        self.level_status = QLabel("Ready")
        level_layout.addWidget(self.level_status)
        
        rec_layout.addLayout(level_layout)
        
        rec_group.setLayout(rec_layout)
        main_layout.addWidget(rec_group)
        
        # === Notation Preview ===
        notation_group = QGroupBox("Notation Preview")
        notation_layout = QVBoxLayout()
        
        self.notation_text = QTextEdit()
        self.notation_text.setReadOnly(True)
        self.notation_text.setPlaceholderText("Record and transcribe to see notation preview...")
        notation_layout.addWidget(self.notation_text)
        
        notation_group.setLayout(notation_layout)
        main_layout.addWidget(notation_group)
        
        # === Export Controls ===
        export_group = QGroupBox("Export")
        export_layout = QHBoxLayout()
        
        self.export_mxml_concert_btn = QPushButton("MusicXML (Concert)")
        self.export_mxml_concert_btn.setEnabled(False)
        self.export_mxml_concert_btn.clicked.connect(lambda: self.on_export_musicxml(False))
        export_layout.addWidget(self.export_mxml_concert_btn)
        
        self.export_mxml_written_btn = QPushButton("MusicXML (Written)")
        self.export_mxml_written_btn.setEnabled(False)
        self.export_mxml_written_btn.clicked.connect(lambda: self.on_export_musicxml(True))
        export_layout.addWidget(self.export_mxml_written_btn)
        
        self.export_midi_btn = QPushButton("MIDI")
        self.export_midi_btn.setEnabled(False)
        self.export_midi_btn.clicked.connect(self.on_export_midi)
        export_layout.addWidget(self.export_midi_btn)
        
        self.export_pdf_btn = QPushButton("PDF")
        self.export_pdf_btn.setEnabled(False)
        self.export_pdf_btn.clicked.connect(self.on_export_pdf)
        export_layout.addWidget(self.export_pdf_btn)
        
        export_group.setLayout(export_layout)
        main_layout.addWidget(export_group)
    
    def on_family_changed(self, index):
        """Handle family selection change."""
        if index < 0:
            return
        
        family = self.family_combo.currentText()
        instruments = self.instrument_db.list_by_family(family)
        
        self.instrument_combo.clear()
        for inst in instruments:
            self.instrument_combo.addItem(inst.name, inst.id)
    
    def on_instrument_changed(self, index):
        """Handle instrument selection change."""
        if index < 0:
            return
        
        inst_id = self.instrument_combo.currentData()
        self.current_instrument = self.instrument_db.get_instrument(inst_id)
    
    def on_tempo_changed(self, value):
        """Handle tempo change."""
        self.rhythm_quantizer.set_tempo(value)
    
    def on_record_clicked(self):
        """Start recording."""
        self.recorder.start_recording()
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.transcribe_btn.setEnabled(False)
        self.level_status.setText("Recording...")
        self.level_status.setStyleSheet("color: red; font-weight: bold;")
    
    def on_stop_clicked(self):
        """Stop recording."""
        self.recorded_audio = self.recorder.stop_recording()
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.transcribe_btn.setEnabled(True)
        self.level_status.setText("Stopped")
        self.level_status.setStyleSheet("color: green; font-weight: bold;")
        
        if len(self.recorded_audio) > 0:
            duration = len(self.recorded_audio) / 44100.0
            QMessageBox.information(
                self,
                "Recording Complete",
                f"Recorded {duration:.1f} seconds of audio.\nClick 'Transcribe' to generate notation."
            )
    
    def on_transcribe_clicked(self):
        """Transcribe recorded audio."""
        if not hasattr(self, 'recorded_audio') or len(self.recorded_audio) == 0:
            QMessageBox.warning(self, "No Recording", "Please record audio first.")
            return
        
        if not self.current_instrument:
            QMessageBox.warning(self, "No Instrument", "Please select an instrument.")
            return
        
        # Show progress
        self.notation_text.setText("Analyzing audio...\n")
        QApplication.processEvents()
        
        try:
            # Detect pitch
            self.notation_text.append("- Detecting pitch...\n")
            QApplication.processEvents()
            pitch_analysis = self.pitch_detector.detect(self.recorded_audio)
            
            # Detect key
            self.notation_text.append("- Detecting key...\n")
            QApplication.processEvents()
            self.detected_key, self.key_confidence = self.key_detector.detect(pitch_analysis.midi_notes)
            self.key_label.setText(f"{self.detected_key} (confidence: {self.key_confidence:.2f})")
            
            # Quantize rhythm
            self.notation_text.append("- Quantizing rhythm...\n")
            QApplication.processEvents()
            time_sig = self._parse_time_signature(self.time_sig_combo.currentText())
            self.rhythm_quantizer.set_time_signature(*time_sig)
            
            quantized_notes = self.rhythm_quantizer.quantize(
                self.recorded_audio,
                pitch_analysis.times,
                pitch_analysis.midi_notes,
                pitch_analysis.confidences
            )
            self.current_notes = quantized_notes
            
            # Build score (written pitch)
            self.notation_text.append("- Building score...\n")
            QApplication.processEvents()
            self.current_score = self.score_builder.build(
                quantized_notes,
                self.current_instrument,
                self.detected_key,
                time_sig,
                self.tempo_spin.value(),
                use_written_pitch=True
            )
            
            # Display results
            self.notation_text.append(f"\n✓ Transcription complete!\n")
            self.notation_text.append(f"- Detected notes: {len(quantized_notes)}\n")
            self.notation_text.append(f"- Key: {self.detected_key}\n")
            self.notation_text.append(f"- Instrument: {self.current_instrument.name}\n")
            
            if self.current_instrument.transposition_semitones != 0:
                self.notation_text.append(f"- Transposition: {self.current_instrument.transposition_semitones} semitones\n")
            
            # Enable export buttons
            self.export_mxml_concert_btn.setEnabled(True)
            self.export_mxml_written_btn.setEnabled(True)
            self.export_midi_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Transcription Error", f"Error during transcription:\n{str(e)}")
            self.notation_text.append(f"\n✗ Error: {str(e)}\n")
    
    def on_export_musicxml(self, written_pitch: bool):
        """Export to MusicXML."""
        if not self.current_score:
            return
        
        pitch_type = "Written" if written_pitch else "Concert"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Export MusicXML ({pitch_type} Pitch)",
            f"melody_{pitch_type.lower()}.musicxml",
            "MusicXML Files (*.musicxml *.xml)"
        )
        
        if filename:
            # Rebuild score with correct pitch type
            time_sig = self._parse_time_signature(self.time_sig_combo.currentText())
            score = self.score_builder.build(
                self.current_notes,
                self.current_instrument,
                self.detected_key,
                time_sig,
                self.tempo_spin.value(),
                use_written_pitch=written_pitch
            )
            
            try:
                success = MusicXMLExporter.export(score, filename)
                if success:
                    QMessageBox.information(self, "Export Success", f"Exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export MusicXML.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export MusicXML:\n{str(e)}")
    
    def on_export_midi(self):
        """Export to MIDI."""
        if not self.current_score:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export MIDI",
            "melody.mid",
            "MIDI Files (*.mid *.midi)"
        )
        
        if filename:
            try:
                success = MIDIExporter.export(self.current_score, filename)
                if success:
                    QMessageBox.information(self, "Export Success", f"Exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export MIDI.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export MIDI:\n{str(e)}")
    
    def update_levels(self):
        """Update level meter."""
        if not self.recorder.is_recording:
            return
        
        rms, peak = self.recorder.get_levels()
        self.level_bar.setValue(int(peak))
        
        # Update status
        if self.recorder.is_clipping():
            self.level_status.setText("⚠ CLIPPING!")
            self.level_status.setStyleSheet("color: red; font-weight: bold;")
        elif self.recorder.is_too_quiet():
            self.level_status.setText("⚠ Too quiet")
            self.level_status.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.level_status.setText("Recording...")
            self.level_status.setStyleSheet("color: green; font-weight: bold;")
    
    def on_export_pdf(self):
        """Export to PDF."""
        if not self.current_score:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            "melody.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filename:
            try:
                success = PDFExporter().export(self.current_score, filename)
                if success:
                    QMessageBox.information(self, "Export Success", f"Exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
    
    @staticmethod
    def _parse_time_signature(ts_str: str) -> tuple:
        """Parse time signature string like '4/4' to (4, 4)."""
        parts = ts_str.split('/')
        return (int(parts[0]), int(parts[1]))
