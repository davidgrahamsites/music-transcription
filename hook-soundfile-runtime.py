"""
Runtime hook for soundfile to find bundled libsndfile library.
This fixes the issue where soundfile looks for libsndfile in system paths.
"""
import os
import sys

# When frozen by PyInstaller
if getattr(sys, 'frozen', False):
    # Get the bundled library path
    bundle_dir = sys._MEIPASS
    
    # Set environment variable to point to our bundled library
    libsndfile_path = os.path.join(bundle_dir, 'libsndfile.dylib')
    
    if os.path.exists(libsndfile_path):
        os.environ['SNDFILE_LIBRARY_PATH'] = libsndfile_path
        
        # Also try to preload it
        try:
            import ctypes
            ctypes.CDLL(libsndfile_path)
        except:
            pass
