#!/usr/bin/python3
'Converter between sfen string and YaneuraOu packed sfen for shogi'

## Bitstreams
def int2bits(x, n):
    'Generate @n bits from LSB side of @x'
    for i in range(n):
        yield (x >> i) & 1

def bits2int8(g):
    y = 0
    for i,x in enumerate(g):
        j = i & 7
        y |= x << j
        if j == 7:
            yield y
            y = 0
    if j != 7:
        yield y

def int8s2bits(l):
    'Generate bits from list(generator) of int8'
    for i in l:
        yield from int2bits(i, 8)

def bits2int(gen, n):
    x = 0
    for i in range(n):
        x |= next(gen) << i
    return x

## converter from sfen to packed sfen
sfen_dict = {
    'P': (1, 0),
    'L': (2, 0),
    'N': (3, 0),
    'S': (4, 0),
    'G': (5, 0),
    'B': (6, 0),
    'R': (7, 0),
    'K': (8, 0),
    'p': (1, 1),
    'l': (2, 1),
    'n': (3, 1),
    's': (4, 1),
    'g': (5, 1),
    'b': (6, 1),
    'r': (7, 1),
    'k': (8, 1),
}

huffman = (
    (0, ),               # PAWN
    (1, 0, 0),           # LANCE
    (1, 0, 1),           # KNIGHT
    (1, 1, 0),           # SILVER
    (1, 1, 1, 0),        # GOLD
    (1, 1, 1, 1, 0),     # BISHOP
    (1, 1, 1, 1, 1))     # ROOK

def pack_board(board):
    'Generate bits from sfen board string'
    l = []
    king = [0, 0]
    promoted = 0
    for y,rank in enumerate(board.split('/')):
        x = 0
        for code in rank:
            if code == '+':
                promoted = 1
                continue
            try:
                for i in range(int(code)):
                    l.append(0)
                    x += 1
            except ValueError:
                p, c = sfen_dict[code]
                if p == 8:
                    king[c] = y * 9 + x
                else:
                    l.append(1)
                    l.extend(huffman[p - 1])
                    if p != 5:
                        l.append(promoted)
                    promoted = 0
                    l.append(c)
                x += 1
    yield from int2bits(king[0], 7)
    yield from int2bits(king[1], 7)
    yield from l
def pack_turn(turn):
    'Generate bits from sfen turn charactor'
    yield 0 if turn == 'b' else 1
def pack_hands(hands):
    'Generate bits from sfen hand string'
    if hands == '-':
        return
    n = 1
    for code in hands:
        try:
            d = int(code)
            n = n * 10 + d
        except ValueError:
            p, c = sfen_dict[code]
            for i in range(n):
                yield from huffman[p - 1]
                if p != 5:
                    yield 0
                yield c
            n = 1
def pack2bits(sfen):
    'Generate bits from sfen string'
    board, turn, hands, ply = sfen.split()
    yield from pack_turn(turn)
    yield from pack_board(board)
    yield from pack_hands(hands)
def pack(sfen):
    'Generate int8 from sfen string'
    # For 'startpos', sfen string is 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'
    yield from bits2int8(pack2bits(sfen))

## converter from packed sfen to sfen
huffman_invert = {
    0: 'Pp',
    4: 'Ll',
    5: 'Nn',
    6: 'Ss',
    14: 'Gg',
    30: 'Bb',
    31: 'Rr'
}
def bits2piece(gen):
    sym = None
    x = 0
    for i,b in enumerate(gen):
        x = x << 1 | b
        try:
            sym = huffman_invert[x]
            break
        except KeyError:
            pass
    if not sym:
        raise StopIteration
    promoted = False if sym == 'Gg' else next(gen)
    sym = sym[next(gen)]
    return "+" + sym if promoted else sym
def unpack_compact_row(row):
    'Generate sfen string of @row, which has 0 for empty'
    zrl = 0 # Zero Run Length
    for s in row:
        if not s:
            zrl += 1
        else:
            if zrl:
                yield str(zrl)
                zrl = 0
            yield s
    if zrl:
        yield str(zrl)
def unpack_board(flatboard):
    return "/".join("".join(s for s in unpack_compact_row(flatboard[y * 9 : y * 9 + 9])) for y in range(9))
def unpack_compact_hands(hands):
    'Generate compact @hands (Duplicated pieces are packed)'
    if not hands:
        yield '-'
    else:
        n, q = 0, None
        for p in hands:
            if q is None:
                n, q = 1, p
            elif q == p:
                n += 1
            elif q:
                if 1 < n:
                    yield str(n)
                yield q
                n, q = 0, None
        if q:
            if 1 < n:
                yield str(n)
            yield q
def unpack_hands(hands):
    return "".join(unpack_compact_hands(hands))
def unpack(psfen, ply=1):
    'Return sfen symbols from packed sfen int8 list'
    gen = int8s2bits(psfen)
    turn = 'w' if next(gen) else 'b'
    king = [ (bits2int(gen, 7), 'K'), (bits2int(gen, 7), 'k') ]
    king.sort()
    board = list(bits2piece(gen) if next(gen) else 0 for i in range(79)) # Except for kings
    for i, s in king:
        board.insert(i, s)
    hands = []
    while True:
        try:
            hands.append(bits2piece(gen))
        except StopIteration:
            break
    return " ".join((unpack_board(board), turn, unpack_hands(hands), str(ply)))

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'pack':
        print(" ".join(str(x) for x in pack(sys.argv[2])))
    elif sys.argv[1] == 'unpack':
        print(unpack(int(x) for x in sys.argv[2].split()))
    else:
        print("USAGE: sfen_converter.py pack <sfen-string>\n"
              "       sfen_converter.py unpack <packed-sfen-numbers>", file=sys.stderr)
        sys.exit(1)
