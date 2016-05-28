import os, sys
import traceback

ERROR_MESSAGE = """Something caused gophic to crash.
Here's the traceback:

%s
"""

from gophic.tk.common import *

if __name__ == "__main__":

  try:
    app_path = os.path.split(os.path.realpath(__file__))[0]

    if os.getcwd() != app_path:
      os.chdir(app_path)
  except AttributeError:
    pass

  NO_CONSOLE = "pythonw" in sys.executable

  if NO_CONSOLE:
    sys.stdout = open("stdout.txt", "wt")
    sys.stderr = open("stderr.txt", "wt")
    
    sys.stdout.write("")
    sys.stderr.write("")

  try:
    gophic.tk.NO_CONSOLE = NO_CONSOLE

    gophic.tk.setup()
    gophic.tk.run()

  except Exception:
    tb = traceback.format_exc()
    if NO_CONSOLE:
      sys.stderr.write(tb + "\n")
    else:
      with open("stderr.txt", "wt") as stream:
        stream.write(tb + "\n")
        
    msgbox.showerror("Runtime Error", ERROR_MESSAGE % tb)

  except (KeyboardInterrupt, SystemExit):
    pass

  finally:
    gophic.tk.teardown()

    if NO_CONSOLE:
      if sys.stdout.tell() == 0:
        sys.stdout.close()
        os.remove("stdout.txt")

      if sys.stderr.tell() == 0:
        sys.stderr.close()
        os.remove("stderr.txt")
