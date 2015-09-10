import gophic
import gophic.resources
from asyncore import dispatcher
import socket

class Client(dispatcher):
  """
  Provides a high-level backend for Gopher clients, dispatching Connection
  events to a resource and even keeping track of the navigation history.
  """

  def __init__(self, url=None, factory=None):
    """Initializes the client and immediately navigates to an Url if provided"""
    dispatcher.__init__(self)

    self.location = gophic.Url("about", path="blank")
    self.history = []
    self.future = []

    if url:
      self.location = url
      self.connect()
    if factory:
      self.factory = factory
    else:
      self.factory = gophic.ResourceFactory(
        lambda c: gophic.resources.DirectoryResource(c) if c.location.type in "1" else None,
        lambda c: gophic.resources.TextResource(c) if c.location.type in "07" else None,
        lambda c: gophic.resource.Resource(c)
      )

    self.inputbuffer = ""
    self.outputbuffer = ""
    self.chunksize = 1024
    self.terminator = "\r\n"

  def connect(self, url=None):
    """
    Connects to the current location or an Url. Doesn't touch the navigation
    history.
    Returns the created Resource.
    """
    if url:
      self.location = url

    if self.socket:
      self.close()
      if self.resource:
        self.resource.onClose()

    self.resource = self.factory.construct(self)

    if self.resource.finished:
      # instance doesn't need data so don't even connect
      return self.resource


    if self.location.host == "about":
      self.resource.onConnect()
      page = self.location.path
      
      if page == "blank":
        pass
      if page == "gophic":
        for line in gophic.__doc__.split("\n"):
          self.resource.onRead(line + self.terminator)
      else:
        self.resource.onRead("3Error: about page not found" + self.terminator)

      self.resource.onRead("." + self.terminator)
      self.resource.onClose()
      return

    self.inputbuffer = ""
    self.outputbuffer = self.location.path
    if self.location.query:
      self.outputbuffer += "?" + self.location.query
    self.outputbuffer += self.terminator

    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    dispatcher.connect(self, (self.location.host, self.location.port))

  def navigate(self, url, force=False):
    """
    Navigates to an Url, pushing the current location to the history.
    Invalidates future.
    Returns True if location changed.
    """
    if type(url) == str:
      url = gophic.Url.fromstring(url)

    if force or self.location.tostring() != url.tostring():
      self.history.append(self.location)
      self.future = []
      self.location = url
      self.connect()
      return True
    return False

  def navigateBack(self):
    """
    Navigates to the last point in the history, pushing the current location to
    the future. Returns True if history was not empty.
    """
    if len(self.history) > 0:
      self.future.append(self.location)
      self.location = self.history.pop()
      self.connect()
      return True
    return False

  def navigateForward(self):
    """
    Navigates to the last point in the future, pushing the current location to
    the history. Returns True if history was not empty.
    """
    if len(self.future) > 0:
      self.history.append(self.location)
      self.location = self.future.pop()
      self.connect()
      return True
    return False

  def onConnect(self):
    """Called when the client connected to a Gopher server."""
    pass

  def onRead(self, chunk):
    """Called when the client received data for the Resource."""
    pass

  def onWritten(self, chunk):
    """Called when the client sent data to the server."""

  def onClose(self):
    """Called when the connection of the client closed remotely."""
    pass

  def onError(self):
    """Called when a socket error occured."""
    pass

  def handle_connect(self):
    """Calls onConnect on the resource."""
    self.onConnect()
    self.resource.onConnect()

  def handle_read(self):
    """Reads a chunk and calls onRead on the resource."""
    chunk = self.recv(self.chunksize)
    self.onRead(chunk)
    self.resource.onRead(chunk)
      
  def handle_write(self):
    """Writes buffered input to the socket."""
    if len(self.outputbuffer) > 0:
      sent = self.send(self.outputbuffer.encode("utf-8"))
      self.onWritten(self.outputbuffer[:sent])
      self.outputbuffer = self.outputbuffer[sent:]

  def handle_error(self):
    """Closes the socket and calls onError on the resource."""
    self.close()
    self.onError()
    self.resource.onError()
  
  def handle_close(self):
    """Flushes the socket and calls onClose on the resource."""
    self.onClose()
    self.resource.onClose()
    self.close()
