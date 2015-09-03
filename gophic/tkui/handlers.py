from gophic.tkui.common import *
import gophic.client
import traceback, webbrowser, base64

class GeneralHandler(gophic.client.Handler):
  def __init__(self, client):
    self.client = client
    self.content = gophic.tkui.main.content;

  def onConnect(self):
    self.content.delete("1.0", "end")

  def onLine(self, line):
    self.content.insert("end", line)

  def onError(self, v, t, tb):
    self.content.insert("end", traceback.format_exc(), "error")

class DirectoryHandler(GeneralHandler):
  def onLine(self, line):
    if len(line.split("\t")) < 4:
      return

    url = gophic.Url.fromline(line)
    if url.type == ".":
      self.client.close()
    elif url.type == "i":
      self.content.insert("end", url.name + "\n",)
    elif url.type == "3":
      self.content.insert("end", url.name + "\n", "error")
    elif url.type == "7":
      self.content.insert("end", url.name + "\n", self.content.link(url, search=True))
    else:
      self.content.insert("end", url.name + "\n", self.content.link(url))

class DownloadHandler(GeneralHandler):
  def onConnect(self):
    GeneralHandler.onConnect(self)
    self.file = filedialog.asksaveasfile(
      "wb",
      parent=gophic.tkui.main,
      initialfile=self.client.location.path.split("/")[-1],
      title="Save binary file as..."
    )
    self.lastsize = 0
    self.content.insert("1.0", "Downloading...\r\n")

  def onRead(self, chunk):
    self.file.write(chunk)
    size = self.file.tell()
    if size - self.lastsize > 1024*5:
      self.content.delete("2.0", "2 linend")
      if size > 1024*1024*1024:
        text = "{} GB\r".format(int(size / (1024*1024*1024)))
      elif size > 1024*1024:
        text = "{} MB\r".format(int(size / (1024*1024)))
      elif size > 1024:
        text = "{} kB\r".format(int(size / 1024))
      else:
        text = "{} B\r".format(int(size))
      self.content.insert("2.0", text)
      lastsize = size

  def onLine(self, line):
    pass

  def onClose(self):
    self.file.flush()
    self.file.close()
    gophic.tkui.main.navigateBack()

class ImageHandler(GeneralHandler):
  def onConnect(self):
    GeneralHandler.onConnect(self)
    try:
      import PIL.ImageTk
    except ImportError:
      if self.client.location.type != "g":
        self.content.insert("1.0", "Could not load image, PIL required")
        self.client.close()
        return
    self.content.insert("1.0", "Loading image...")
    self.data = bytes()

  def onRead(self, chunk):
    self.data += chunk

  def onLine(self, line):
    pass

  def onClose(self):
    try:
      from PIL.ImageTk import PhotoImage
      img = PhotoImage(data=self.data)
    except ImportError:
      img = tk.PhotoImage(data=base64.b64encode(self.data))
    self.content.image_create("1.0", image=img)
