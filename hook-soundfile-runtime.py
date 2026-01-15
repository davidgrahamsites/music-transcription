"""
Runtime hook for soundfile to find bundled libsndfile library.
This patches soundfile to use our bundled library instead of system paths.
"""
import os
import sys

# When frozen by PyInstaller
if getattr(sys, 'frozen', False):
    # Monkey-patch soundfile BEFORE it loads
    import ctypes.util
    original_find_library = ctypes.util.find_library
    
    def patched_find_library(name):
        if name == 'sndfile':
            # Return path to our bundled library
            bundle_dir = sys._MEIPASS
            bundled_lib = os.path.join(bundle_dir, 'libsndfile.dylib')
            if os.path.exists(bundled_lib):
                return bundled_lib
        return original_find_library(name)
    
    ctypes.util.find_library = patched_find_library
