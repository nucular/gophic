from gophic.tk.common import *

class ResourceViewer(tk.Text):
  """Displays a Resource instance."""

  def __init__(self, master, *args, **kwargs):
    """Registers all style tags and initializes the widget."""
    tk.Text.__init__(self, master, *args, **kwargs)
    self.links = {}
    self.resource = None

    self.config(state="disabled")

    def onLinkClick(e):
      for tag in self.tag_names("current"):
        if tag[:5] == "link-":
          self.links[tag](e)

    self.tag_config("link", foreground="blue", underline=1)
    self.tag_bind("link", "<Enter>", lambda e: self.config(cursor="hand2"))
    self.tag_bind("link", "<Leave>", lambda e: self.config(cursor="xterm"))
    self.tag_bind("link", "<Button-1>", onLinkClick)

    self.tag_config("error", foreground="red")

  def link(self, url, search=False):
    """Register a link. Returns a tuple of text tags."""
    def callback(e):
      if search:
        query = simpledialog.askstring("Search query", "Enter a search query string",
          parent=gophic.tk.main)
        if query:
          url.query = query
      gophic.tk.main.navigate(url, force=True)

    tag = "link-{}".format(len(self.links))
    self.links[tag] = callback
    return "link", tag

  def insert(self, *args, **kwargs):
    self.config(state="normal")
    tk.Text.insert(self, *args, **kwargs)
    self.config(state="disabled")

  def delete(self, *args, **kwargs):
    self.config(state="normal")
    tk.Text.delete(self, *args, **kwargs)
    self.config(state="disabled")

  def render(self):
    """Renders the current resource."""
    self.delete(1.0, "end")
    self.links = {}
    if self.resource and hasattr(self.resource, "render"):
      self.resource.render(self)
