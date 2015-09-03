try: import urlparse
except ImportError: import urllib.parse as urlparse

class Url(object):
  """Encapsulates the location of a resource on a gopher server."""

  def __init__(self, host, type="1", path="", port=70, name="", query=""):
    """Initializes the URL."""
    self.host = host
    self.type = type
    self.path = path.strip("/")
    self.port = int(port)
    self.name = name
    self.query = query

  @classmethod
  def fromstring(cls, url):
    """Creates an Url from a string."""
    url = url.strip()
    parsed = urlparse.urlparse(url)
    if parsed.scheme == "":
      parsed = urlparse.urlparse("gopher://" + url)

    host = parsed.netloc

    split = list(filter(bool, parsed.path.split("/")))
    if len(split) == 0:
      type = "1"
      path = ""
    elif len(split[0]) == 1:
      type = split[0]
      path = "/".join(split[1:])
    else:
      type = "1"
      path = "/".join(split)

    port = parsed.port or 70

    if not parsed.scheme == "gopher":
      raise NotImplementedError("{0} protocol".format(parsed.scheme))

    return cls(host, type=type, path=path, port=port,
      query=urlparse.unquote(parsed.query))

  def tostring(self):
    """Assembles a string from the Url."""
    return "gopher://{}{}/{}/{}{}".format(
      self.host,
      "" if self.port == 70 else ":70",
      self.type,
      self.path,
      ("?" + urlparse.quote(self.query)) if self.query else ""
    )
  __str__ = tostring

  @classmethod
  def fromline(cls, line):
    """
    Parses an Url from a line inside a directory listing. May raise exceptions
    if line is empty.
    """
    split = line[1:].split("\t")
    return cls(
      type=line[0],
      name=split[0] if len(split) > 1 else "",
      path=split[1] if len(split) > 1 else "",
      host=split[2] if len(split) > 2 else "",
      port=split[3] if len(split) > 3 else 70
    )

  def toline(self, name=None):
    """Assembles a directory listing line from the Url."""
    return "{}{}\t{}\t{}\t{}".format(
      self.type,
      name if name else self.name,
      self.path,
      self.host,
      self.port
    )
