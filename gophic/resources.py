import gophic
import sys

class ResourceFactory(object):
  """
  Dispatches handling requests by Clients to a list of Resource classes.
  """
  def __init__(self, *args):
    """
    Initialize the ResourceFactory. The positional arguments should be lambdas
    or functions that either return None or an instance of a Resource-like
    class when being passed the Client that requested the instance.
    Remember, client.location.type is the Gopher type you'll want to check.
    
    Functions are searched in order until one doesn't return None.
    """
    self.constructors = args

  def construct(self, client):
    """
    Search through the list of constructors and return a Resource-like
    instance that can handle the properties of the client.
    Might raise NotImplementedError if no match is found.
    """
    for i in self.constructors:
      inst = i(client)
      if inst:
        return inst

    raise NotImplementedError("No Resource match found for {}".format(client.location))


class Resource(object):
  """
  Abstract Gopher resource that does nothing.
  """
  def __init__(self, client):
    """Initialize the Resource."""
    self.client = client
    self.finished = False

  def onConnect(self):
    """Called when the self.client connected to a Gopher server."""
    pass

  def onRead(self, chunk):
    """Called when the self.client received data for the Resource."""
    pass

  def onClose(self):
    """Called when the connection of the self.client closed remotely."""
    pass

  def onError(self):
    """Called when a socket error occured."""
    t, v = sys.exc_info()[:2]
    raise t(v)

class DataResource(Resource):
  """
  Generic Gopher resource that stores received chunks.
  """
  def __init__(self, client):
    """Initialize the DataResource."""
    self.client = client
    self.data = bytes()
    self.finished = False

  def onConnect(self):
    """Called when the self.client connected to a Gopher server."""
    self.data = bytes() # empty

  def onRead(self, chunk):
    """Called when the self.client received data for the Resource."""
    self.data += chunk

  def onClose(self):
    """Called when the connection of the self.client closed remotely."""
    self.finished = True


class TextResource(Resource):
  """
  Generic text resource that splits fully received lines to an array and closes
  the client connection once a "." line is received.
  """
  def __init__(self, client):
    Resource.__init__(self, client)
    self.lines = []
    self.buffer = ""
    self.encoding = "ascii"
    self.terminator = "\r\n"

  def onConnect(self):
    """Empties out the buffer and list of lines."""
    self.lines = []
    self.buffer = ""

  def onRead(self, chunk):
    """Splits the received data to lines and dispatches them to onLine."""
    Resource.onRead(self, chunk)
    lines = (self.buffer + chunk.decode(self.encoding, "ignore") + self.terminator).split(self.terminator)
    for i in lines[:-1]:
      self.lines.append(i)
      self.onLine(i)
      if i == ".":
        self.client.close()
    if lines[-1] != "":
      self.buffer += i

  def onLine(self, line):
    """Called when a line is completed. To be overriden by subclasses."""
    pass


class DirectoryResource(TextResource):
  """
  Resource class that parses received lines to a list of Url instances (links).
  """
  def __init__(self, client):
    TextResource.__init__(self, client)
    self.links = []

  def onConnect(self):
    """Empties out the list of links."""
    self.links = []

  def onLine(self, line):
    """Parses the line to a link and appends it to self.links."""
    TextResource.onLine(self, line)
    try:
      link = gophic.Url.fromline(line)
    except IndexError:
      link = None
    self.links.append(link)
