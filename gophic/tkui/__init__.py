from gophic.tkui.common import tk
from gophic.tkui.mainframe import MainFrame

NO_CONSOLE = False

root = None # The Tk object
main = None # The main frame

def setup():
  """Sets up the Tk user interface"""
  global root, main
  root = tk.Tk()

  main = MainFrame(root)
  main.setup()

  root.wm_title("gophic")
  root.protocol("WM_DELETE_WINDOW", teardown)

def run():
  """Enters the main loop."""
  global root
  root.mainloop()

def teardown():
  """Destroys all Tk widgets and exits the main loop."""
  global root, main
  main.teardown()
  root.quit()
  try: # might already be gone
    root.destroy()
  except: pass

def restart():
  """Reinstantiates everything and re-enters the main loop."""
  teardown()
  setup()
  run()
