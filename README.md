[]: {{{1

    File        : README.md
    Maintainer  : Felix C. Stegerman <flx@obfusk.net>
    Date        : 2015-09-12

    Copyright   : Copyright (C) 2015  Felix C. Stegerman
    Version     : v0.1.0

[]: }}}1

<!-- badge? -->

## Description

netcat.py - python (2+3) netcat

See `netcat.py` for the code (with examples).

## Examples

```
$ ./netcat.py -l -p 8888      # server
hi client!                    # typed on stdin
hi server!                    # from client
^C                            # bye
```

```
$ ./netcat.py localhost 8888  # client
hi client!                    # from server
hi server!                    # typed on stdin
```

## TODO

* find a way to receive ICMP port unreachable etc. so we know when a
  UDP socket is not connected?
* prevent idle waiting (only seems to occur with "fake" I/O where
  select doesn't actually block)?

## License

GPLv3+ [1].

## References

[1] GNU General Public License, version 3
--- https://www.gnu.org/licenses/gpl-3.0.html

[]: ! ( vim: set tw=70 sw=2 sts=2 et fdm=marker : )
