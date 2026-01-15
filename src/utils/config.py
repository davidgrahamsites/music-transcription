"""Configuration constants for MelodyTranscriber."""

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 1
DTYPE = 'float32'

# Recording settings
DEFAULT_TEMPO = 120
DEFAULT_TIME_SIGNATURE = (4, 4)
LEVEL_UPDATE_INTERVAL = 50  # ms

# Level meter thresholds (dBFS)
CLIPPING_THRESHOLD = -0.5
TOO_QUIET_THRESHOLD = -40.0

# Pitch detection
PITCH_CONFIDENCE_THRESHOLD = 0.5
PITCH_SMOOTH_WINDOW = 5  # frames for median filtering

# Rhythm quantization
ONSET_SILENCE_THRESHOLD = -50.0  # dBFS
MIN_NOTE_DURATION = 0.1  # seconds
QUANTIZATION_STRENGTH = 0.8  # 0.0 = no quantization, 1.0 = full quantization

# Key detection
KEY_CONFIDENCE_THRESHOLD = 0.3

# UI settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
UNDO_STACK_SIZE = 10

# Export settings
MUSICXML_VERSION = '3.1'
DEFAULT_COMPOSER = 'Unknown'

# File paths
INSTRUMENTS_DB_PATH = 'data/instruments.json'
