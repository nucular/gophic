try: import urlparse
except ImportError: import urllib.parse as urlparse

class Link(object):
  """Encapsulates a link to a resource on a gopher server."""

  def __init__(self, host, type="1", path="", port=70, name=""):
    self.host = host
    self.type = type
    self.path = path.strip("/")
    self.port = int(port)
    self.name = name

  def __str__(self):
    return self.tourl()

  @classmethod
  def fromurl(cls, url):
    """Parses a link from an URL."""
    url = url.strip()
    parsed = urlparse.urlparse(url)
    if parsed.scheme == "":
      parsed = urlparse.urlparse("gopher://" + url)

    path = parsed.path.strip("/")

    if parsed.netloc == "":
      if parsed.scheme == "":
        host = parsed.path
        path = ""
      else:
        host = parsed.scheme
    else:
      host = parsed.netloc

    if path != "" and parsed.scheme == "gopher":
      type = path[0]
      path = path[1:]
    else:
      type = "1"
    if parsed.scheme == "about":
      host = "about"

    port = parsed.port or 70
    if parsed.query:
      path = path + "?" + parsed.query

    if not parsed.scheme in ["gopher", "about"]:
      raise NotImplementedError("{0} protocol".format(parsed.scheme))

    return cls(host, type=type, path=path, port=port)

  def tourl(self):
    """Assembles an URL from the link."""
    return "gopher://{}{}/{}/{}".format(
      self.host,
      "" if self.port == 70 else ":70",
      self.type,
      self.path
    )

  @classmethod
  def fromline(cls, line):
    """
    Parses a link from a line inside a directory listing. May raise
    exceptions if line is invalid.
    """
    split = line[1:].split("\t")
    return cls(
      type=line[0],
      name=split[0],
      path=split[1] if len(split) > 1 else "",
      host=split[2] if len(split) > 2 else "",
      port=split[3] if len(split) > 3 else 70
    )

  def toline(self):
    """Assembles a directory listing line from the string."""
    return "{}{}\t{}\t{}\t{}".format(
      self.type,
      self.name,
      self.path,
      self.host,
      self.port
    )
