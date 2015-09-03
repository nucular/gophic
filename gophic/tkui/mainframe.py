from gophic.tkui.common import *
from gophic.tkui.handlers import *
from gophic.tkui.content import ContentWidget
import asyncore
import re

class MainFrame(tk.Frame):
  """Encapsulates the main window of the gophic GUI"""

  def __init__(self, master=None):
    """Initializes the main frame"""
    tk.Frame.__init__(self, master)
    self.client = gophic.Client(handlers=[
      lambda c: GeneralHandler(c),
      lambda c: DirectoryHandler(c) if c.location.type in "17" else None,
      lambda c: GeneralHandler(c) if c.location.type == "0" else None,
      lambda c: DownloadHandler(c) if c.location.type in "59" else None,
      lambda c: ImageHandler(c) if c.location.type in "gp" else None
    ])
    self.pack()

  def setup(self):
    """Sets up all widgets"""
    self.location = tk.StringVar()
    self.setupNavFrame()
    self.setupContentFrame()
    self.clientjob = gophic.tkui.root.after(100, self.pollClient)

  def teardown(self):
    """Destroys all widgets and quits the window"""
    gophic.tkui.root.after_cancel(self.clientjob)
    try: # might already be gone
      self.destroy()
    except: pass
    self.quit()

  def setupNavFrame(self):
    """Sets up the navigation bar"""
    self.navframe = tk.Frame()

    self.backbutton = tk.Button(self.navframe)
    self.backbutton.bind("<Button-1>", self.navigateBack)
    self.backbutton["text"] = "<"
    self.backbutton.pack(side="left")
    self.forwardbutton = tk.Button(self.navframe)
    self.forwardbutton["text"] = ">"
    self.forwardbutton.bind("<Button-1>", self.navigateForward)
    self.forwardbutton.pack(side="left")

    if ttk:
      def onComboboxSelected(event):
        i = self.addressbar.current()
        history = self.client.history[:]
        lookup = self.client.future + ["", self.client.location.tourl(), ""] + history
        self.navigate(lookup[i])
        self.content.focus()

      self.addressbar = ttk.Combobox(self.navframe, textvariable=self.location)
      self.addressbar.bind("<<ComboboxSelected>>", onComboboxSelected)

    else:
      self.addressbar = tk.Entry(self.navframe, textvariable=self.location)

    def onReturn(event):
      self.navigate(self.addressbar.get())
      self.content.focus()
    self.addressbar.bind("<Return>", onReturn)

    self.addressbar.pack(side="left", fill="x", expand=1)

    self.navframe.pack(side="top", fill="x", expand=0)
    self.updateNavBar()

  def setupContentFrame(self):
    """Sets up the content widget and its scrollbar"""
    self.contentframe = tk.Frame()

    self.content = ContentWidget(self, self.contentframe)
    self.content.grid_propagate(False)
    self.content.grid(row=1, column=0, sticky="nesw")
    self.contentframe.grid_rowconfigure(1, weight=1)
    self.contentframe.grid_columnconfigure(0, weight=1)

    self.scrollbar = tk.Scrollbar(self.contentframe, command=self.content.yview)
    self.scrollbar.grid(row=1, column=1, sticky="nesw")
    self.content["yscrollcommand"] = self.scrollbar.set

    self.contentframe.pack(fill="both", expand=1)

  def updateNavBar(self):
    """Updates the history combobox"""
    if ttk:
      history = [i.tostring() for i in self.client.history]
      history.reverse()
      future = [i.tostring() for i in self.client.future]
      self.addressbar["values"] = future \
        + ["", self.client.location.tostring(), ""] \
        + history
      self.addressbar.current(len(self.client.future) + 1)
    else:
      self.location.set(self.client.location)

  def navigate(self, url, force=False):
    """Navigates to an URL"""
    if url == "" or url == self.client.location:
      self.addressbar.current(len(self.client.future) + 1)
      if not force:
        return

    # invalidates future
    self.client.future = []
    self.client.navigate(url, force)
    self.updateNavBar()

  def navigateBack(self, event=None):
    """Navigates to the last point in the client history"""
    self.client.navigateBack()
    self.updateNavBar()

  def navigateForward(self, event=None):
    """Navigates to the last point in the client future"""
    self.client.navigateForward()
    self.updateNavBar()

  def pollClient(self):
    """Polls the client for new data."""
    if self.client.socket:
      asyncore.loop(0.1, count=1)
    self.clientjob = gophic.tkui.root.after(100, self.pollClient)
