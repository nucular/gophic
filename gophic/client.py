import re, webbrowser
try: import urlparse
except ImportError: import urllib.parse as urlparse

class GopherClient(object):
  """Provides a high-level backend for Gopher clients."""

  def __init__(self, url="about:blank"):
    """Initializes the client and navigates to an URL if provided"""
    self.location = "about:blank"
    self.history = []
    self.future = []

    if url:
      self.navigate(url)

  def connect(self):
    """Connects to the current location and starts processing the response."""
    print(self.location)

  def navigate(self, url, shell=True):
    """
    Navigates to an URL, pushing the current location to the history.
    If shell is True, URLs with an unsupported scheme will be redirected to the
    web browser (and the location not set).
    Returns True if location changed.
    """
    parsed = urlparse.urlsplit(url)
    if parsed.scheme in ["", "gopher", "about"]:
      self.history.append(self.location)
      self.location = url
      self.connect()
      return True
    else:
      if shell:
        webbrowser.get().open(url, autoraise=True)
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
