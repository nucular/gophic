from gophic.tkui.common import *
import webbrowser

class TextResource(gophic.resources.TextResource):
  """A TextResource that supports rendering to a ResourceViewer."""
  def render(self, viewer):
    for i in self.lines:
      viewer.insert("insert", i + "\n")

class DirectoryResource(gophic.resources.DirectoryResource):
  """A DirectoryResource that supports rendering to a ResourceViewer."""
  def render(self, viewer):
    for i in self.links:
      if i:
        if i.type == "i":
          viewer.insert("insert", i.name + "\n")
        elif i.type == "3":
          viewer.insert("insert", i.name + "\n", "error")
        elif i.type == "7":
          viewer.insert("insert", i.name + "\n", viewer.link(i, search=True))
        else:
          viewer.insert("insert", i.name + "\n", viewer.link(i))
      else:
        viewer.insert("insert", "\n")

class DownloadResource(gophic.resources.Resource):
  """A Resource that will be downloaded to a file instead of rendered."""
  def __init__(self, client):
    self.client = client
    self.file = filedialog.asksaveasfile(
      "wb",
      parent=gophic.tkui.main,
      initialfile=client.location.path.split("/")[-1],
      title="Save {} as...".format(client.location)
    )
    if not self.file:
      self.finished = True

  def onRead(self, chunk):
    self.file.write(chunk)

  def render(self, viewer):
    size = self.file.tell()
    if size > 1024*1024*1024:
      text = "{} GB\r".format(int(size / (1024*1024*1024)))
    elif size > 1024*1024:
      text = "{} MB\r".format(int(size / (1024*1024)))
    elif size > 1024:
      text = "{} kB\r".format(int(size / 1024))
    else:
      text = "{} B\r".format(int(size))
    self.content.insert("insert", text)

class WebResource(gophic.resources.Resource):
  """A Resource that is opened in the browser instead of renderer."""
  def __init__(self, client):
    webbrowser.get().open(client.location.path[3:], autoraise=True)
    self.finished = True
