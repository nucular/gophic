from gophic.tkui.common import *
from gophic.tkui.resources import *
from gophic.tkui.resourceviewer import ResourceViewer
from gophic.tkui.client import Client
import asyncore
import re

class MainFrame(tk.Frame):
  """Encapsulates the main window of the gophic GUI"""

  def __init__(self, master=None):
    """Initializes the main frame"""
    tk.Frame.__init__(self, master)
    self.client = Client(factory=gophic.ResourceFactory(
      lambda c: TextResource(c) if c.location.type in "0" else None,
      lambda c: DirectoryResource(c) if c.location.type in "17" else None,
      lambda c: WebResource(c) if c.location.path.startswith("URL:") else None,
      lambda c: TextResource(c) # TODO
    ))
    self.pack()

  def setup(self):
    """Sets up all widgets"""
    self.location = tk.StringVar()
    self.setupNavFrame()
    self.setupViewer()
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
    self.backbutton.icon = tk.PhotoImage(file="icons/go-previous.gif")
    self.backbutton.config(image=self.backbutton.icon, state="disabled")
    self.backbutton.pack(side="left")

    self.forwardbutton = tk.Button(self.navframe)
    self.forwardbutton.icon = tk.PhotoImage(file="icons/go-next.gif")
    self.forwardbutton.config(image=self.forwardbutton.icon, state="disabled")
    self.forwardbutton.bind("<Button-1>", self.navigateForward)
    self.forwardbutton.pack(side="left")

    self.reloadbutton = tk.Button(self.navframe)
    self.reloadbutton.reloadicon = tk.PhotoImage(file="icons/view-refresh.gif")
    self.reloadbutton.stopicon = tk.PhotoImage(file="icons/process-stop.gif")
    self.reloadbutton.bind("<Button-1>", self.reload)
    self.reloadbutton.config(image=self.reloadbutton.reloadicon)
    self.reloadbutton.pack(side="left")

    if ttk:
      def onComboboxSelected(event):
        i = self.addressbar.current()
        history = self.client.history[:]
        lookup = self.client.future + ["", self.client.location, ""] + history
        self.navigate(lookup[i])
        self.viewer.focus()

      self.addressbar = ttk.Combobox(self.navframe, textvariable=self.location)
      self.addressbar.bind("<<ComboboxSelected>>", onComboboxSelected)

    else:
      self.addressbar = tk.Entry(self.navframe, textvariable=self.location)

    def onReturn(event):
      self.navigate(self.addressbar.get())
      self.viewer.focus()
    self.addressbar.bind("<Return>", onReturn)

    self.addressbar.pack(side="left", fill="x", expand=1)

    self.navframe.pack(side="top", fill="x", expand=0)
    self.updateNavBar()

  def setupViewer(self):
    """Sets up the ResourceViewer and its scrollbar"""
    self.viewerframe = tk.Frame()

    self.viewer = ResourceViewer(self.viewerframe)
    self.viewer.grid_propagate(False)
    self.viewer.grid(row=1, column=0, sticky="nesw")
    self.viewerframe.grid_rowconfigure(1, weight=1)
    self.viewerframe.grid_columnconfigure(0, weight=1)

    self.scrollbar = tk.Scrollbar(self.viewerframe, command=self.viewer.yview)
    self.scrollbar.grid(row=1, column=1, sticky="nesw")
    self.viewer["yscrollcommand"] = self.scrollbar.set

    self.viewerframe.pack(fill="both", expand=1)

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

      if len(history) > 0: self.backbutton.config(state="default")
      else: self.backbutton.config(state="disabled")
      if len(future) > 0: self.forwardbutton.config(state="default")
      else: self.forwardbutton.config(state="disabled")
    else:
      self.location.set(self.client.location)

  def navigate(self, url, force=False):
    """Navigates to an URL"""
    if url == "" or url == self.client.location:
      self.addressbar.current(len(self.client.future) + 1)
      if not force:
        return

    self.client.navigate(url, force)
    self.viewer.resource = self.client.resource
    self.updateNavBar()

  def navigateBack(self, event=None):
    """Navigates to the last point in the client history"""
    self.client.navigateBack()
    self.viewer.resource = self.client.resource
    self.updateNavBar()

  def navigateForward(self, event=None):
    """Navigates to the last point in the client future"""
    self.client.navigateForward()
    self.viewer.resource = self.client.resource
    self.updateNavBar()

  def reload(self, event=None):
    if self.client.connected:
      self.client.close()
    else:
      self.viewer.resource = self.client.connect()

  def pollClient(self):
    """Polls the client for new data."""
    if self.client.socket:
      asyncore.loop(0.1, count=1)
    if self.client.connected:
      self.reloadbutton.configure(image=self.reloadbutton.stopicon)
      self.viewer.render()
    else:
      self.reloadbutton.configure(image=self.reloadbutton.reloadicon)
    self.clientjob = gophic.tkui.root.after(100, self.pollClient)
