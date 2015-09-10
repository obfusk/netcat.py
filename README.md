[]: {{{1

    File        : README.md
    Maintainer  : Felix C. Stegerman <flx@obfusk.net>
    Date        : 2015-09-10

    Copyright   : Copyright (C) 2015  Felix C. Stegerman
    Version     : v0.0.1

[]: }}}1

<!-- badge? -->

## Description

netcat.py - python (2+3) netcat

See `netcat.py` for the code (with examples).

## Examples

```
$ ./netcat.py -l -p 8888      # server
hi there                      # user input
^C
```

```
$ ./netcat.py localhost 8888  # client
hi there                      # from server
```

## TODO

* `-c COMMAND` etc?
* UDP multiple addrs?!
* no idle waiting?!

## License

LGPLv3+ [1].

## References

[1] GNU Lesser General Public License, version 3
--- https://www.gnu.org/licenses/lgpl-3.0.html

[]: ! ( vim: set tw=70 sw=2 sts=2 et fdm=marker : )
