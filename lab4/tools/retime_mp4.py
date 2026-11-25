"""Scale MP4 movie/media timescales while preserving every encoded frame."""
from pathlib import Path
import struct
import sys

def retime(path, factor):
    path = Path(path)
    data = bytearray(path.read_bytes())
    patched = []
    def walk(start, end):
        pos = start
        while pos+8 <= end:
            size,kind = struct.unpack_from('>I4s',data,pos)
            header = 8
            if size == 1:
                size = struct.unpack_from('>Q',data,pos+8)[0]
                header = 16
            elif size == 0:
                size = end-pos
            if size < header or pos+size > end:
                raise ValueError('Invalid MP4 atom bounds')
            payload = pos+header
            if kind in [b'mvhd',b'mdhd']:
                offset = payload+(20 if data[payload] == 1 else 12)
                previous = struct.unpack_from('>I',data,offset)[0]
                updated = round(previous*factor)
                if not 0 < updated < 2**32:
                    raise ValueError('Invalid resulting timescale')
                struct.pack_into('>I',data,offset,updated)
                patched.append((kind.decode(),previous,updated))
            if kind in [b'moov',b'trak',b'mdia',b'edts']:
                walk(payload,pos+size)
            pos += size
    walk(0,len(data))
    assert any(x[0]=='mvhd' for x in patched)
    assert any(x[0]=='mdhd' for x in patched)
    path.write_bytes(data)
    return patched

if __name__ == '__main__':
    print(retime(sys.argv[1],float(sys.argv[2])))
