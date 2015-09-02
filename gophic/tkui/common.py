import gophic
import gophic.tkui
import warnings
import sys

# Tkinter
try: import Tkinter as tk
except ImportError: import tkinter as tk

# Tix
try: import Tix as tix
except ImportError: import tkinter.tix as tix

# message boxes
try: import tkMessageBox as msgbox
except ImportError: import tkinter.messagebox as msgbox
try: import tkFileDialog as filedialog
except ImportError: import tkinter.filedialog as filedialog
try: import tkSimpleDialog as simpledialog
except ImportError: import tkinter.simpledialog as simpledialog

# Tkfont
try: import tkFont as tkfont
except ImportError: import tkinter.font as tkfont

# ttk
if not "--nottk" in sys.argv:
  try:
    import ttk
  except ImportError:
    try:
      import tkinter.ttk as ttk
    except ImportError:
      warnings.warn("No ttk found")
      ttk = None
else:
  ttk = None

# Merge ttk into tk
if not ttk is None:
  for name in ttk.__all__:
    setattr(tk, name, getattr(ttk, name))
