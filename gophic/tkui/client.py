from gophic.tkui.common import *

class Client(gophic.Client):
  """A Client that is connected to the Tk interface."""

  def onConnect(self):
    log("C {}".format(self.location))

  def onRead(self, chunk):
    log("< {}...".format(len(chunk)))

  def onWritten(self, chunk):
    log("> {}".format(len(chunk)))

  def onClose(self):
    log("X {}".format(self.location))
