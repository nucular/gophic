from gophic.tkui.common import *
import gophic.client
import re

class MainFrame(tk.Frame):
  """Encapsulates the main window of the gophic GUI"""

  def __init__(self, master=None):
    """Initializes the main frame"""
    tk.Frame.__init__(self, master)
    self.client = gophic.client.GopherClient()
    self.pack()

  def setup(self):
    """Sets up all widgets"""
    self.location = tk.StringVar()
    self.setupNavFrame()
    self.setupContentFrame()

  def teardown(self):
    """Destroys all widgets and quits the window"""
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
        self.navigate(self.location.get())
        self.content.focus()
      self.addressbar = ttk.Combobox(self.navframe, textvariable=self.location)
      self.addressbar.bind(onComboboxSelected)
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

    self.content = tk.Text(self.contentframe)
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
      rhistory = self.client.history[:]
      rhistory.reverse()
      self.addressbar["values"] = self.client.future \
        + ["", self.client.location, ""]             \
        + rhistory
      self.addressbar.current(len(self.client.future) + 1)
    else:
      self.location.set(self.client.location)

  def navigate(self, url):
    """Navigates to an URL"""
    if url == "" or url == self.client.location:
      self.addressbar.current(len(self.client.future) + 1)
      return

    url = self.client.navigate(url)
    self.location.set(url)
    self.updateNavBar()

  def navigateBack(self, event=None):
    """Navigates to the last point in the client history"""
    url = self.client.navigateBack()
    self.updateNavBar()

  def navigateForward(self, event=None):
    """Navigates to the last point in the client future"""
    url = self.client.navigateForward()
    self.updateNavBar()
