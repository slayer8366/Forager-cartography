#!/usr/bin/env python3
"""coder-12 R2 content check (Willow, 2026-11-02; Aspen's condition 2 for deleting the parts, 13:48 PST).

  relief_content_check.py PARTS_DIR MERGED.mbtiles

For every tile, sha256(tile_data) in the merged MBTiles must equal the sha256 of the same z/x/y in the part
files. Each side gives one digest: sha256 over the lines "z/x/y sha256(tile_data)\n", sorted by (z, x, y), y in
XYZ. Prints both digests; exit 0 only if they are equal and every z/x/y is on both sides exactly once.
Read only: the files are opened with mode=ro.
"""
import glob, hashlib, os, sqlite3, sys, time


def tile_hashes(path):
    """{(z, x, y): sha256 hex} of one MBTiles, and the number of rows read."""
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out, rows = {}, 0
    for z, x, row, data in db.execute("select zoom_level, tile_column, tile_row, cast(tile_data as blob) from tiles"):
        rows += 1
        out[(z, x, (2**z - 1) - row)] = hashlib.sha256(data).hexdigest()
    db.close()
    return out, rows


def digest(hashes):
    h = hashlib.sha256()
    for (z, x, y) in sorted(hashes):
        h.update(f"{z}/{x}/{y} {hashes[(z, x, y)]}\n".encode())
    return h.hexdigest()


def main():
    parts_dir, merged = sys.argv[1], sys.argv[2]
    t0 = time.time()
    parts, part_rows = {}, 0
    files = sorted(glob.glob(f"{parts_dir}/part-*.mbtiles"))
    for f in files:
        hs, n = tile_hashes(f)
        part_rows += n
        dup = parts.keys() & hs.keys()
        if dup:
            print(f"FAIL: {len(dup)} z/x/y in more than one part file, e.g. {sorted(dup)[:3]}"); return 1
        parts.update(hs)
        print(f"{os.path.basename(f)}: {n} rows", flush=True)
    m, m_rows = tile_hashes(merged)
    dp, dm = digest(parts), digest(m)
    print(f"parts  ({len(files)} files): {part_rows} rows, {len(parts)} distinct z/x/y, digest {dp}")
    print(f"merged ({os.path.basename(merged)}): {m_rows} rows, {len(m)} distinct z/x/y, digest {dm}")
    only_p = sorted(parts.keys() - m.keys()); only_m = sorted(m.keys() - parts.keys())
    differ = sorted(t for t in parts.keys() & m.keys() if parts[t] != m[t])
    for label, ts in (("only in the parts", only_p), ("only in the merged file", only_m), ("bytes differ", differ)):
        if ts:
            print(f"  {label}: {len(ts)}, e.g. " + ", ".join(f"{z}/{x}/{y}" for z, x, y in ts[:10]))
    ok = dp == dm and part_rows == len(parts) and m_rows == len(m) and not (only_p or only_m or differ)
    print(f"content check: {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f} s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
