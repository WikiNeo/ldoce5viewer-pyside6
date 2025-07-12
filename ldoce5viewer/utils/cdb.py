"""A pure-python implementation of cdb"""

from struct import Struct

"""Memory-mapped file objects behave like both bytearray and like file objects. You can use mmap objects in most places 
where bytearray are expected; for example, you can use the re module to search through a memory-mapped file. You can 
also change a single byte by doing obj[index] = 97, or change a subsequence by assigning to a 
slice: obj[i1:i2] = b'...'. You can also read and write data starting at the current file position, and seek() through 
the file to different positions.
"""
from mmap import mmap, ACCESS_READ

"""
< little-endian
L unsigned long -> 4 bytes

class struct.Struct(format)
    Return a new Struct object which writes and reads binary data according to the format string format. Creating a 
    Struct object once and calling its methods is more efficient than calling module-level functions with the same 
    format since the format string is only compiled once.
"""
_struct_2L = Struct(b'<LL')
"""
unpack(buffer)
    Unpack from the buffer buffer (presumably packed by pack(format, ...)) according to the format string format. The 
    result is a tuple even if it contains exactly one item. The buffer’s size in bytes must match the size required by the 
    format, as reflected by calcsize().
"""
_read_2L = _struct_2L.unpack
"""
pack(v1, v2, ...)
    Pack the values v1, v2, … according to the format string format and write the packed bytes into the writable 
    buffer buffer starting at position offset. Note that offset is a required argument.
"""
_write_2L = _struct_2L.pack
_read_512L = Struct(b'<512L').unpack

try:
    import __builtin__
    range = __builtin__.xrange
except ImportError:
    pass

import itertools
zip = getattr(itertools, 'izip', zip)

def hashfunc(s):
    """
    Positions, lengths, and hash values are 32-bit quantities, stored in
    little-endian form in 4 bytes. Thus a cdb must fit into 4 gigabytes.

    The cdb hash function is ``h = ((h << 5) + h) ^ c'', with a starting
    hash of 5381.
    """
    h = 5381
    for c in bytearray(s):
        h = h * 33 & 0xffffffff ^ c
    return h


class CDBError(Exception):
    pass


class CDBReader(object):
    __slots__ = ('_mmap', '_maintable')

    def __init__(self, path):
        self._mmap = None
        with open(path, 'rb') as f:
            mm = self._mmap = mmap(f.fileno(), 0, access=ACCESS_READ)
        if len(mm) < 2048:
            raise CDBError('file too small')
        mt = _read_512L(mm.read(2048))
        self._maintable = tuple(zip(mt[0::2], mt[1::2]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        if self._mmap:
            self._mmap.close()
            self._mmap = None

    def get(self, key, default=None):
        """
        A record is located as follows.
        The hash value divided by 256, modulo the length of that table, is a
        slot number. Probe that slot, the next higher slot, and so on, until
        you find the record or run into an empty slot.
        """
        mm = self._mmap
        # Compute the hash value of the key in the record.
        hashed = hashfunc(key)
        # Return the tuple (x//y, x%y).  Invariant: div*y + mod == x.
        # The hash value modulo 256 is the number of a hash table.
        (hashed_high, table_index) = divmod(hashed, 256)
        """
        Each of the 256 initial pointers states a position and a length. The
        position is the starting byte position of the hash table. The length
        is the number of slots in the hash table.
        """
        (pos_hash_table, num_of_slots) = self._maintable[table_index]
        if pos_hash_table <= 2048:
            raise CDBError('broken file')

        def iter_subtable():
            # The hash value divided by 256, modulo the length of that table, is a slot number.
            init_slot = hashed_high % num_of_slots
            """
            Each hash table slot states a hash value and a byte position. If the
            byte position is 0, the slot is empty. Otherwise, the slot points to
            a record whose key has that hash value.
            """
            pa = pos_hash_table + 8 * init_slot
            pb = pos_hash_table + 8 * num_of_slots
            for p in range(pa, pb, 8):
                yield _read_2L(mm[p:p+8])
            for p in range(pos_hash_table, pa, 8):
                yield _read_2L(mm[p:p+8])

        if num_of_slots:
            for (hash_value, byte_position) in iter_subtable():
                if byte_position == 0:
                    # not exist
                    break
                if hash_value == hashed:
                    pk = byte_position + 8
                    (klen, vlen) = _read_2L(mm[byte_position:pk])
                    pv = pk + klen
                    if key == mm[pk:pv]:
                        return mm[pv:(pv+vlen)]
        return default

    def __getitem__(self, key):
        r = self.get(key)
        if r is None:
            raise KeyError
        return r

    def __contains__(self, key):
        return (self.get(key) is not None)

    def iteritems(self):
        mm = self._mmap
        read = mm.read
        num = sum(n for (p, n) in self._maintable) // 2
        mm.seek(2048)
        for _ in range(num):
            (klen, vlen) = _read_2L(read(8))
            yield (read(klen), read(vlen))


class CDBMaker(object):
    def __init__(self, f):
        self._f = f
        self._f.seek(2048)
        self._total_size = 0
        self._sub_num = [0] * 256
        self._sub = tuple([] for _ in range(256))

    def add(self, k, v):
        write = self._f.write
        pointer = self._f.tell()
        lenk = len(k)
        lenv = len(v)
        write(_write_2L(lenk, lenv))
        write(k)
        write(v)
        self._total_size += 8 + lenk + lenv
        hashed = hashfunc(k)
        s = hashed & 0xFF
        self._sub_num[s] += 2
        self._sub[s].append((hashed, pointer))

    def finalize(self):
        f = self._f
        sub_num = self._sub_num
        sub_pos = []

        # subtable entries
        def write_subbuf(buf, hashed, pointer):
            hashed_high, subidx = divmod(hashed, 256)
            ini = hashed_high % sub_num[subidx]
            for pos in range(ini * 8, sub_num[subidx] * 8, 8):
                h, p = _read_2L(bytes(buf[pos: pos+8]))
                if p == 0:
                    buf[pos:pos+8] = _write_2L(hashed, pointer)
                    return
            for pos in range(0, ini * 8, 8):
                h, p = _read_2L(bytes(buf[pos: pos+8]))
                if p == 0:
                    buf[pos:pos+8] = _write_2L(hashed, pointer)
                    return

        sub_pos = []
        for s in range(256):
            buf = bytearray(self._sub_num[s] * 8)
            for hashed, pos in self._sub[s]:
                write_subbuf(buf, hashed, pos)
            sub_pos.append(f.tell())
            f.write(bytes(buf))

        # header
        f.seek(0)
        for i in range(256):
            f.write(_write_2L(sub_pos[i], sub_num[i]))
