from gophic.tkui.common import *
import webbrowser

class ContentWidget(tk.Text):
  def __init__(self, main, *args, **kwargs):
    """Registers all style tags and initializes the Content widget."""
    tk.Text.__init__(self, *args, **kwargs)
    self.main = main
    self.links = {}
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

  def resetLinks(self):
    self.links = {}

  def link(self, url, search=False):
    def callback(e):
      if search:
        query = simpledialog.askstring("Search query", "Enter a search query string",
          parent=gophic.tkui.main)
        if query:
          url.query = query
      if url.path.startswith("URL:"):
        webbrowser.get().open(url.path[4:], autoraise=True)
      else:
        self.main.navigate(url, force=True)

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
