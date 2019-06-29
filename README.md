# sfen_converter
Converter between sfen string and YaneuraOu packed sfen for shogi.

## How to test
Pack:
```sh
$ ./sfen_converter.py pack 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'
153 132 113 61 223 247 92 71 191 224 83 102 102 102 102 2 0 0 32 34 34 34 34 124 128 31 195 114 60 207 177 12
```

Unpack:
```sh
$ ./sfen_converter.py unpack '153 132 113 61 223 247 92 71 191 224 83 102 102 102 102 2 0 0 32 34 34 34 34 124 128 31 195 114 60 207 177 12'
lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1
```

## How to use in your code
Simply import the code and use `pack` and `unpack` functions.

For example, get bytes of packed sfen, unpack it, and print:
```Python
import sfen_converter
packed = bytes(sfen_converter.pack('lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'))

# packed sfen can be in bytes, in list of int, or in any iterable of int
print(sfen_converter.unpack(packed))
```
