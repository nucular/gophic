import gophic
import sys, traceback
from asyncore import dispatcher
import socket
from abc import ABCMeta

class Handler(object):
  """Abstract base class that handles Connection events forwarded from a Client."""
  __metaclass__ = ABCMeta

  def onClose(self):
    """Called when the client connection closed."""
    pass

  def onRead(self, chunk):
    """Handles a chunk of data received from the connection"""
    pass

  def onLine(self, line):
    """Handles a line of data received from the connection."""
    pass

  def onError(self, t, v, tb):
    """Handles an exception that wasn't handled otherwise."""
    traceback.print_tb(tb)

class Client(dispatcher):
  """
  Provides a high-level backend for Gopher clients, dispatching Connection
  events to a list of handlers and keeping track of the navigation history.
  """

  def __init__(self, type="1", url=None, handlers=[]):
    """Initializes the client and immediately navigates to an Url if provided"""
    dispatcher.__init__(self)

    self.location = gophic.Url("about", path="blank")
    self.history = []
    self.future = []
    self.handlers = handlers
    if url:
      self.location = url
      self.connect()

    self.inputbuffer = ""
    self.outputbuffer = ""
    self.chunksize = 8192

  def connect(self):
    """Connects to the current location."""
    if not self.location:
      raise ValueError("Client has no location")

    if self.socket:
      self.close()
      if self.handler:
        self.handler.onClose()

    self.handler = None
    for i in self.handlers:
      r = i(self)
      if r:
        self.handler = r
    if not self.handler:
      raise NotImplementedError("No handler found for {}".format(self.location))

    if self.location.host == "about":
      self.handler.onConnect()
      page = self.location.path
      
      if page == "blank":
        pass
      if page == "gophic":
        for line in gophic.__doc__.split("\n"):
          self.handler.onRead(line + "\r\n")
          self.handler.onLine(line + "\r\n")
      else:
        self.handler.onLine("3Error: about page not found\r\n")

      self.handler.onLine(".")
      self.handler.onClose()
      return

    self.inputbuffer = ""
    self.outputbuffer = self.location.path
    if self.location.query:
      self.outputbuffer += "?" + self.location.query
    self.outputbuffer += "\r\n"

    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    dispatcher.connect(self, (self.location.host, self.location.port))

  def navigate(self, url, force=False):
    """
    Navigates to an Url, pushing the current location to the history.
    Returns True if location changed.
    """
    if type(url) == str:
      url = gophic.Url.fromstring(url)

    if force or self.location.tostring() != url.tostring():
      self.history.append(self.location)
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

  def handle_connect(self):
    """Calls onConnect."""
    self.handler.onConnect()

  def handle_read(self):
    """Reads a chunk, splits it into lines and calls onRead and onLine."""
    print("Read")
    chunk = self.recv(self.chunksize)
    self.handler.onRead(chunk)
    lines = chunk.splitlines(True)

    for i in lines:
      if type(i) != str:
        try:
          i = i.decode("utf-8")
        except UnicodeError: continue

      if i.endswith("\n"):
        self.handler.onLine(self.inputbuffer + i)
        self.inputbuffer = ""
      else:
        self.inputbuffer += i
      
  def handle_write(self):
    """Writes buffered input to the socket."""
    print("Write")
    if len(self.outputbuffer) > 0:
      sent = self.send(self.outputbuffer.encode("utf-8"))
      self.outputbuffer = self.outputbuffer[:sent]

  def handle_error(self):
    """Calls onError."""
    self.close()
    t, v, tb = sys.exc_info()
    self.handler.onError(t, v, tb)
  
  def handle_close(self):
    """Calls onClose."""
    print("Close")
    self.handler.onClose()
    self.close()
