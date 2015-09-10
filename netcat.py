#!/usr/bin/python

# --                                                            ; {{{1
#
# File        : netcat.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-09-10
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Version     : v0.0.1
# License     : LGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""
Python (2+3) netcat

Examples
--------

>>> port1, port2 = 8888, 9999

>>> import netcat as N, sys, tempfile, time

>>> s = sys.stdin; f = tempfile.TemporaryFile()
>>> _ = f.write(b"GET / HTTP/1.0\r\n\r\n"); _ = f.seek(0)
>>> sys.stdin = f

>>> N.client("obfusk.ch", 80)                     # doctest: +ELLIPSIS
HTTP/1.1 301 Moved Permanently...

>>> sys.stdin = s


>>> import subprocess, threading

>>> c   = [sys.executable, "netcat.py", "-l", "-p", str(port1)]
>>> f1  = tempfile.TemporaryFile(); f2 = tempfile.TemporaryFile()
>>> _   = f1.write(b"Hi!\n"); _ = f1.seek(0)
>>> p   = subprocess.Popen(c, stdin = f1)
>>> s   = sys.stdin; sys.stdin = f2
>>> time.sleep(1)
>>> def killer(p):
...   time.sleep(1)
...   p.terminate()
>>> threading.Thread(target = killer, args = [p]).start()

>>> N.client("localhost", port1)                  # doctest: +ELLIPSIS
Hi!

>>> sys.stdin = s


# TODO
>>> c   = [sys.executable, "netcat.py", "-u", "-l", "-p", str(port2)]
>>> f1  = tempfile.TemporaryFile(); f2 = tempfile.TemporaryFile()
>>> _   = f1.write(b"Hi!\n") ; _ = f1.seek(0)
>>> _   = f2.write(b"DATA\n"); _ = f2.seek(0)
>>> p   = subprocess.Popen(c, stdin = f1, stdout = subprocess.PIPE)
>>> s   = sys.stdin; sys.stdin = f2
>>> time.sleep(1)
>>> def killer(p):
...   time.sleep(2); p.stdout.readline(); p.terminate()
>>> threading.Thread(target = killer, args = [p]).start()

>>> N.client("localhost", port2, True)            # doctest: +ELLIPSIS
Hi!

>>> sys.stdin = s
"""
                                                                # }}}1

from __future__ import print_function

import argparse, fcntl, os, select, sys
import socket as S

if sys.version_info.major == 2:                                 # {{{1
  def b2s(x):
    """convert bytes to str"""
    return x
  def s2b(x):
    """convert str to bytes"""
    return x
  def binread(s, n):
    """read bytes from stream"""
    return s.read(n)
  def binwrite(s, data):
    """write bytes to stream"""
    return s.write(data)
else:
  def b2s(x):
    """convert bytes to str"""
    if isinstance(x, str): return x
    return x.decode("utf8")
  def s2b(x):
    """convert str to bytes"""
    if isinstance(x, bytes): return x
    return x.encode("utf8")
  def binread(s, n):
    """read bytes from stream"""
    if hasattr(s, "buffer"):
      return s.buffer.read(n)
    else:
      return s2b(s.read(n))                                     # TODO
  def binwrite(s, data):
    """write bytes to stream"""
    if hasattr(s, "buffer"):
      return s.buffer.write(data)
    else:
      return s.write(b2s(data))                                 # TODO
  xrange = range
                                                                # }}}1

__version__       = "0.0.1"


def main(*args):                                                # {{{1
  p = argument_parser(); n = p.parse_args(args)
  if n.test:
    import doctest
    doctest.testmod(verbose = n.verbose)
    return 0
  if (not n.listen and (n.host is None or n.port is None)) or \
     (n.listen and n.lport is None) or n.lport and n.port:
    print("{}: error: incompatible arguments".format(p.prog),
          file = sys.stderr)                                    # TODO
    return 2
  try:
    if n.listen:
      server(n.lport, n.udp)
    else:
      client(n.host, n.port, n.udp)
  except KeyboardInterrupt:
    return 1
  return 0
                                                                # }}}1

def argument_parser():                                          # {{{1
  p = argparse.ArgumentParser(description = "netcat")
  p.add_argument("host", metavar = "HOST", nargs = "?",
                 help = "remote host name or IP address")
  p.add_argument("port", metavar = "PORT", nargs = "?", type = int,
                 help = "remote port")
  p.add_argument("--version", action = "version",
                 version = "%(prog)s {}".format(__version__))
  p.add_argument("--udp", "-u", action = "store_true",
                 help = "UDP mode (default is TCP)")
  p.add_argument("--listen", "-l", action = "store_true",
                 help = "listen mode, for inbound connects")
  p.add_argument("--port", "-p", type = int, dest="lport",
                 help = "local port number")
  p.add_argument("--test", action = "store_true",
                 help = "run tests (not netcat)")
  p.add_argument("--verbose", "-v", action = "store_true",
                 help = "run tests verbosely")
  p.set_defaults(
    host      = None,
    port      = None,
    udp       = False,
    listen    = False,
    lport     = None,
    test      = False,
    verbose   = False,
  )
  return p
                                                                # }}}1

def client(host, port, udp = False):
  """connect std{in,out} to TCP (or UDP) socket (client)"""

  set_nonblocking(sys.stdin.fileno())
  sock = create_socket(udp)
  if not udp:
    sock.connect((host, port))
  handle_io(sock, udp = udp, addr = (host, port))

def server(port, udp = False):
  """connect std{in,out} to TCP (or UDP) socket (server)"""

  set_nonblocking(sys.stdin.fileno())
  sock = create_socket(udp)
  sock.bind(('', port))
  if not udp:
    sock.listen(1); clientsock, addr = sock.accept()
    handle_io(clientsock)
  else:
    handle_io(sock, udp = True)

def create_socket(udp = False):
  return S.socket(S.AF_INET, S.SOCK_DGRAM if udp else S.SOCK_STREAM)

def handle_io(sock, udp = False, addr = None):                  # {{{1
  """handle I/O"""
  try:
    while True:
      sin = [sock, sys.stdin] if not udp or addr else [sock]
      rs, _, _ = select.select(sin, [], [])
      if sock in rs:
        data, addr = sock.recvfrom(4096)
        if not data: break  # socket is closed
        binwrite(sys.stdout, data)
        sys.stdout.flush()
      if sys.stdin in rs:
        data = binread(sys.stdin, 4096)
        if udp:
          sock.sendto(data, addr)
        else:
          sock.sendall(data)

  finally:
    sock.close()
                                                                # }}}1

def set_nonblocking(fd):
  """make fd non-blocking."""
  flags = fcntl.fcntl(fd, fcntl.F_GETFL)
  flags = flags | os.O_NONBLOCK
  fcntl.fcntl(fd, fcntl.F_SETFL, flags)

if __name__ == "__main__":
  sys.exit(main(*sys.argv[1:]))

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
