#!/usr/bin/env python3
"""Relief build, coder-12 (Willow, 2026-11-02): Terrarium raster-dem tiles z5-11 for US + Canada.

Dispatch prompts/preserved/2026-11-02-coder-12-relief-build.md; plan docs/design/2026-11-02-relief-build-plan.md.
Generalises the last Mount Hood trial, the owner's reference (/mnt/archive/aspen-hillshade-trial/make-relief.py).
The warp, the Terrarium encoding and the PNG save are the trial's, unchanged, so the look is the approved one.
What changes: the tiles are listed from the cells (not a bounding box), one VRT covers every cell, the tile
bytes go into one MBTiles part file per worker (no loose PNG tree), and there is no WebP pass.

  relief.py tiles  [--cells N52E179,...]   per-zoom tile counts from the cell list
  relief.py build  OUT [--procs 4] [--chunk 32] [--only FILE]
                   render into OUT/parts/part-K.mbtiles; a restart skips tiles already in a part file.
                   Start it under setsid: the process-group id goes in OUT/build.pgid, and
                   relief.py stop OUT stops it. Stops itself under 50G free or on under-voltage/throttling.
  relief.py stop   OUT                     SIGTERM to the build's process group (OUT/build.pgid) with os.killpg,
                                           only if the group is > 1, isn't the caller's, and holds only
                                           relief.py build processes; else it sends nothing and exits 1
  relief.py check  PARTS_DIR|FILE.mbtiles [--only FILE]   per-zoom count check; exit 1 on any gap
  relief.py merge  OUT [--only FILE]       check the parts, merge them into OUT/relief.mbtiles, check that
  relief.py hood   OUT [--only FILE]       Hood against the trial's tiles, on OUT/relief.mbtiles (before converting)
  relief.py verify OUT [--only FILE]       the R2 checks on OUT/relief.pmtiles (and the MBTiles' size)

--only FILE limits the tiles to the z/x/y lines in FILE (the R0 tests). Terrarium: h = R*256 + G + B/256 - 32768
(metres); voids and sea are 0 m, as in the trial. Deletes nothing.

Never stop a build with /usr/bin/kill -TERM -<pgid>: on this Pi (procps-ng 4.0.2) it keeps only the first digit
of the id, so -14750 becomes kill(-1), every process of the user (coder-12, 2026-11-02 12:39). By hand in bash:
kill -TERM -- -<pgid>, never without --, never with sudo.
"""
import argparse, collections, fcntl, glob, hashlib, io, math, multiprocessing as mp, os, re, signal
import sqlite3, subprocess, sys, time
import numpy as np
from osgeo import gdal
from PIL import Image
gdal.UseExceptions()
os.environ["TZ"] = "America/Los_Angeles"; time.tzset()
sys.stdout.reconfigure(line_buffering=True)    # every line reaches the log before a stop or a failure

HGT ="/mnt/storage/elevation/hgt3"
REF = "/mnt/archive/aspen-hillshade-trial/tiles/png256"   # the trial's tiles: the reference (premise 7)
REF_W, REF_S, REF_E, REF_N = -123.0, 45.0, -121.0, 46.0    # the trial's area
ZOOMS = range(5, 12)
PX = 256
MIN_FREE = 50 * 2**30          # "50 GB", as df -h counts it
GUARD_EVERY, LOG_EVERY = 30, 600
PNG_SIG = b"\x89PNG\r\n\x1a\n"
METADATA = {"name": "forager-relief", "format": "png", "type": "baselayer", "minzoom": "5", "maxzoom": "11",
            "bounds": "-180,17,180,84", "encoding": "terrarium", "attribution": "Heights: USGS 3DEP; NRCan MRDEM"}


def log(*a):
    print(time.strftime("%F %T %Z"), *a, flush=True)


# --- The trial's functions, unchanged (make-relief.py) -------------------------------------------------------
R = 6378137.0
def tile_bounds(z, x, y):
    n = 2**z; size = 2*math.pi*R/n; ox = -math.pi*R
    return ox+x*size, math.pi*R-(y+1)*size, ox+(x+1)*size, math.pi*R-y*size
def ty(lat, n): return int((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n)
def terrarium(h):
    h = np.where(np.isfinite(h), h, 0.0)
    v = h + 32768.0
    r = np.floor(v/256); g = np.floor(v) % 256; b = np.floor((v - np.floor(v))*256)
    return np.dstack([r, g, b]).astype(np.uint8)


def render(vrt, z, x, y):
    """The trial's warp and encoding for one tile; PNG bytes, saved with optimize=True as the trial did."""
    b = tile_bounds(z, x, y)
    ds = gdal.Warp("", vrt, format="MEM", dstSRS="EPSG:3857", outputBounds=b, width=PX, height=PX,
                   resampleAlg="bilinear", srcNodata=-32768, dstNodata=np.nan, outputType=gdal.GDT_Float32)
    img = Image.fromarray(terrarium(ds.GetRasterBand(1).ReadAsArray()), "RGB")
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def decode(png):
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.float64)
    return a[..., 0]*256 + a[..., 1] + a[..., 2]/256 - 32768


# --- The tile list, from the cells ----------------------------------------------------------------------------
def cells(names=None):
    out = []
    for p in sorted(glob.glob(f"{HGT}/*.hgt")):
        m = re.fullmatch(r"([NS])(\d\d)([EW])(\d{3})\.hgt", os.path.basename(p))
        if not m:
            sys.exit(f"unexpected file name in {HGT}: {p}")
        if names is None or m[0][:-4] in names:
            out.append((m[0][:-4], int(m[2]) * (1 if m[1] == "N" else -1), int(m[4]) * (1 if m[3] == "E" else -1), p))
    return out


def cell_tiles(z, lat, lon):
    """The trial's tiles(z) with W, S, E, N set to the cell's edges. The -1e-9 keeps a cell ending at 180 E
    on x = 2^z - 1 instead of wrapping to x = 2^z (that is, 0)."""
    n = 2**z
    x0 = int((lon+180)/360*n); x1 = int((lon+1+180)/360*n - 1e-9)
    for x in range(x0, x1+1):
        for y in range(ty(lat+1, n), ty(lat, n)+1):
            yield x, y


def all_tiles(cs):
    return sorted({(z, x, y) for z in ZOOMS for _, lat, lon, _ in cs for x, y in cell_tiles(z, lat, lon)})


def scope(only):
    """Every tile from the cells, or just the z/x/y lines of --only (which must all be in the full list)."""
    full = all_tiles(cells())
    if not only:
        return full
    want = sorted({tuple(int(v) for v in l.split("/")) for l in open(only) if l.strip()})
    bad = set(want) - set(full)
    if bad:
        sys.exit(f"--only lists tiles no cell touches: {sorted(bad)[:5]}")
    return want


def per_zoom(ts):
    c = collections.Counter(z for z, _, _ in ts)
    return {z: c[z] for z in ZOOMS}


# --- MBTiles part files ---------------------------------------------------------------------------------------
def open_part(path):
    db = sqlite3.connect(path, timeout=60)
    db.execute("pragma journal_mode=wal")    # a killed worker loses only its uncommitted chunk
    db.execute("pragma synchronous=normal")
    db.executescript("create table if not exists metadata(name text, value text);"
                     "create table if not exists tiles(zoom_level integer, tile_column integer, tile_row integer,"
                     " tile_data blob);"
                     "create unique index if not exists tile_index on tiles(zoom_level, tile_column, tile_row);")
    return db


def mbtiles_files(path):
    return [path] if path.endswith(".mbtiles") else sorted(glob.glob(f"{path}/part-*.mbtiles"))


def read_tiles(path, heads=False):
    """(z, x, y[, first 8 bytes]) rows of an MBTiles, y in XYZ. Opening it recovers a WAL a kill left behind."""
    db = sqlite3.connect(path)
    q = "select zoom_level, tile_column, tile_row" + (", substr(tile_data, 1, 8)" if heads else "") + " from tiles"
    rows = [(r[0], r[1], (2**r[0]-1)-r[2]) + tuple(r[3:]) for r in db.execute(q)]
    db.close()
    return rows


def worker(k, parts, vrt_path, q, done, delay):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    vrt = gdal.Open(vrt_path)
    db = open_part(f"{parts}/part-{k}.mbtiles")
    while True:
        chunk = q.get()
        if chunk is None:
            break
        rows = [(z, x, (2**z-1)-y, render(vrt, z, x, y)) for z, x, y in chunk]
        db.executemany("insert into tiles values(?,?,?,?)", rows)
        db.commit()
        with done.get_lock():
            for z, _, _ in chunk:
                done[z] += 1
        if delay:
            time.sleep(delay)                          # RELIEF_TEST_CHUNK_DELAY: the R0 stop test only
    db.execute("pragma wal_checkpoint(truncate)")
    db.execute("pragma journal_mode=delete")
    db.close()


# --- Readings for the log and the guards ------------------------------------------------------------------------
def vcgencmd(*a):
    return subprocess.run(["vcgencmd", *a], capture_output=True, text=True, check=True).stdout.strip()


def throttled():
    return int(vcgencmd("get_throttled").split("=")[1], 16)


def temp_c():
    return float(re.search(r"([\d.]+)", vcgencmd("measure_temp"))[1])


def free_bytes(path):
    s = os.statvfs(path)
    return s.f_bavail * s.f_frsize


def gib(b):
    return f"{b / 2**30:.1f}G"


def make_vrt(out, cs):
    """One VRT over every cell, built as the trial built its two-cell one. Reused on a restart if it lists the
    same cells; never overwritten."""
    path = f"{out}/relief.vrt"
    files = [c[3] for c in cs]
    if os.path.exists(path):
        ds = gdal.Open(path); have = sorted(os.path.realpath(f) for f in ds.GetFileList()[1:]); ds = None
        if have != sorted(os.path.realpath(f) for f in files):
            sys.exit(f"{path} lists other cells ({len(have)}); not overwriting it")
        return path
    ds = gdal.BuildVRT(path, files); ds = None
    return path


# --- build ------------------------------------------------------------------------------------------------------
def build(a):
    out = os.path.abspath(a.out); parts = f"{out}/parts"
    if os.getpgrp() != os.getpid():
        sys.exit(f"start this under setsid, so that relief.py stop {a.out} stops this build and nothing else")
    delay = float(os.environ.get("RELIEF_TEST_CHUNK_DELAY") or 0)
    if delay and not out.startswith("/tmp/"):
        sys.exit(f"RELIEF_TEST_CHUNK_DELAY={delay:g} is for the R0 tests under /tmp only, not {out}")
    if os.nice(0) < 10:
        os.nice(10 - os.nice(0))
    os.makedirs(parts, exist_ok=True)
    lock = open(f"{out}/build.lock", "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(f"another build holds {out}/build.lock")
    with open(f"{out}/build.pgid", "w") as f:
        f.write(f"{os.getpgrp()}\n")

    cs = cells(); want = scope(a.only); want_set = set(want)
    seen = collections.Counter(t[:3] for p in mbtiles_files(parts) for t in read_tiles(p))
    dup = [t for t, c in seen.items() if c > 1]; extra = [t for t in seen if t not in want_set]
    if dup or extra:
        sys.exit(f"the part files hold {len(dup)} duplicated and {len(extra)} unexpected tiles, e.g. {(dup + extra)[:5]};"
                 " stopping")
    todo = [t for t in want if t not in seen]
    vrt_path = make_vrt(out, cs)
    exp = per_zoom(want)
    log(f"start: pid {os.getpid()} pgid {os.getpgrp()} nice {os.nice(0)}; GDAL {gdal.__version__}, numpy {np.__version__},"
        f" Pillow {Image.__version__}; {len(cs)} cells; procs {a.procs}, chunk {a.chunk};"
        f" chunk delay {f'{delay:g} s (test only)' if delay else 'off'}")
    log("tiles wanted:", " ".join(f"z{z} {exp[z]}" for z in ZOOMS), f"total {len(want)}")
    log(f"already in part files: {len(seen)}; to do: {len(todo)}")
    if not todo:
        log("nothing to do"); return 0
    log(f"to stop it: {os.path.abspath(sys.argv[0])} stop {out}")

    # Fork, not spawn: a forked worker keeps this process's command line (relief.py build ...), which is what
    # stop checks before it signals the group. A spawned one runs "python3 -c from multiprocessing.spawn ...".
    # No thread is running here yet (the queue's feeder thread starts at the first put, after the forks).
    ctx = mp.get_context("fork")
    done = ctx.Array("q", 12)
    for z, c in per_zoom(seen).items():
        done[z] = c
    q = ctx.Queue()
    procs = [ctx.Process(target=worker, args=(k, parts, vrt_path, q, done, delay), name=f"relief-{k}") for k in range(a.procs)]
    for p in procs:
        p.start()

    def stop(reason, code):
        log(f"stopping: {reason}")
        for p in procs:
            if p.is_alive():
                p.terminate()
        for p in procs:
            p.join(30)
        log(f"stopped; part files hold {sum(done[z] for z in ZOOMS)} of {len(want)} tiles; a restart resumes")
        os._exit(code)
    signal.signal(signal.SIGTERM, lambda *_: stop("SIGTERM", 143))

    for i in range(0, len(todo), a.chunk):
        q.put(todo[i:i+a.chunk])
    for _ in procs:
        q.put(None)

    t0 = time.time(); n0 = len(seen); thr0 = throttled(); peak = temp_c(); last_guard = last_log = 0.0
    n_logged, stalls = None, 0
    def line(t, thr):
        n = sum(done[z] for z in ZOOMS); dt = time.time() - t0
        return (" ".join(f"z{z} {done[z]}/{exp[z]}" for z in ZOOMS) + f"; total {n}/{len(want)}; this run {n - n0}"
                f" in {dt:.0f} s ({(n - n0) / max(dt, 1):.1f}/s); free {gib(free_bytes(out))}; {t:.1f}'C"
                f" (peak {peak:.1f}'C); throttled={thr:#x}")
    log(f"guards: stop under {gib(MIN_FREE)} free, or on get_throttled bit 0 or 2 (or bit 16 or 18 newly set),"
        f" or after two {LOG_EVERY // 60}-minute lines in a row with no new tiles;"
        f" now free {gib(free_bytes(out))}, throttled={thr0:#x}, {peak:.1f}'C")
    while True:
        bad = [p for p in procs if p.exitcode not in (None, 0)]
        if bad:
            stop(f"worker {bad[0].name} exited with {bad[0].exitcode}", 1)
        if not any(p.is_alive() for p in procs):
            break
        now = time.time()
        if now - last_guard >= GUARD_EVERY:
            last_guard = now
            free, thr, t = free_bytes(out), throttled(), temp_c(); peak = max(peak, t)
            if free < MIN_FREE:
                log(line(t, thr)); stop(f"free space on {out} is {gib(free)}, under {gib(MIN_FREE)}", 2)
            if thr & 0x5 or (thr & ~thr0 & 0x50000):
                log(line(t, thr)); stop(f"get_throttled={thr:#x} (under-voltage or throttling)", 2)
            if now - last_log >= LOG_EVERY:
                last_log = now; log(line(t, thr))
                n = sum(done[z] for z in ZOOMS)
                stalls = stalls + 1 if n == n_logged else 0; n_logged = n
                if stalls >= 2:
                    stop(f"stalled: two {LOG_EVERY // 60}-minute lines in a row with no new tiles ({n} done)", 3)
        time.sleep(1)
    log(line(temp_c(), throttled()))
    left = len(want) - sum(done[z] for z in ZOOMS)
    if left:
        log(f"workers finished but {left} tiles are not in the part files"); return 1
    log("done: every wanted tile is in a part file"); return 0


# --- stop -------------------------------------------------------------------------------------------------------
def group_members(pgid):
    """[(pid, state, argv)] of the live processes in process group pgid (pgrep -g), zombies left out."""
    r = subprocess.run(["pgrep", "-g", str(pgid)], capture_output=True, text=True)
    out = []
    for pid in r.stdout.split():
        try:
            state = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[0]
            argv = open(f"/proc/{pid}/cmdline", "rb").read().split(b"\0")[:-1]
        except OSError:
            continue                                   # gone since pgrep listed it
        if state != "Z":
            out.append((int(pid), state, [v.decode(errors="replace") for v in argv]))
    return out


def is_build(argv):
    """python3 [flags] .../relief.py build ...: the build and its forked workers, nothing else."""
    if not argv or not os.path.basename(argv[0]).startswith("python"):
        return False
    i = next((i for i, v in enumerate(argv) if os.path.basename(v) == "relief.py"), None)
    return i is not None and i + 1 < len(argv) and argv[i + 1] == "build"


def stop_build(a):
    """The one way to stop a build: os.killpg(pgid, SIGTERM), after three checks; on any doubt it sends nothing."""
    out = os.path.abspath(a.out)
    try:
        pgid = int(open(f"{out}/build.pgid").read().strip())
    except (OSError, ValueError) as e:
        print(f"stop: refusing, sending nothing: can't read a pgid from {out}/build.pgid ({e})"); return 1
    if pgid <= 1:
        print(f"stop: refusing, sending nothing: pgid {pgid} is not greater than 1"); return 1
    if pgid == os.getpgrp():
        print(f"stop: refusing, sending nothing: pgid {pgid} is this process's own group"); return 1
    members = group_members(pgid)
    if not members:
        print(f"stop: refusing, sending nothing: no live process in group {pgid}"); return 1
    others = [m for m in members if not is_build(m[2])]
    for pid, state, argv in members:
        print(f"stop: group {pgid}: pid {pid} {state} {' '.join(argv)[:160]}")
    if others:
        print(f"stop: refusing, sending nothing: group {pgid} holds {len(others)} process(es) that aren't"
              f" relief.py build, e.g. pid {others[0][0]} {' '.join(others[0][2])[:80]}"); return 1
    print(f"stop: os.killpg({pgid}, SIGTERM) to {len(members)} relief.py build process(es)")
    os.killpg(pgid, signal.SIGTERM)
    t0 = time.time()
    while time.time() - t0 < 60:
        left = group_members(pgid)
        if not left:
            print(f"stop: group {pgid} is empty after {time.time() - t0:.1f} s"); return 0
        time.sleep(0.2)
    print(f"stop: group {pgid} still holds {[m[0] for m in left]} after 60 s; sent nothing more"); return 1


# --- check ------------------------------------------------------------------------------------------------------
def check(path, want, show=20):
    """Every wanted tile exactly once, nothing else, every blob a PNG. Prints a per-zoom table; True if clean."""
    seen = collections.Counter(); notpng = []
    for f in mbtiles_files(path):
        for z, x, y, head in read_tiles(f, heads=True):
            seen[(z, x, y)] += 1
            if head != PNG_SIG:
                notpng.append((z, x, y))
    want_set = set(want); failed = []
    print(f"count check of {path} ({len(mbtiles_files(path))} file(s))")
    print("zoom  expected   present   missing  duplicated  unexpected  not-png")
    for z in ZOOMS:
        e = [t for t in want if t[0] == z]
        miss = [t for t in e if t not in seen]
        dup = [t for t, c in seen.items() if t[0] == z and c > 1]
        extra = [t for t in seen if t[0] == z and t not in want_set]
        npng = [t for t in notpng if t[0] == z]
        present = sum(1 for t in e if t in seen)
        print(f"z{z:<3} {len(e):>9} {present:>9} {len(miss):>9} {len(dup):>11} {len(extra):>11} {len(npng):>8}")
        for label, ts in (("missing", miss), ("duplicated", dup), ("unexpected", extra), ("not png", npng)):
            if ts:
                failed.append(f"z{z} {label} {len(ts)}")
                print(f"  z{z} {label}: " + ", ".join(f"{a}/{b}/{c}" for a, b, c in sorted(ts)[:show])
                      + (f" ... and {len(ts) - show} more" if len(ts) > show else ""))
    print("count check:", "FAIL: " + "; ".join(failed) if failed else "PASS")
    return not failed


# --- merge ------------------------------------------------------------------------------------------------------
def merge(a):
    out = os.path.abspath(a.out); parts = f"{out}/parts"; dst = f"{out}/relief.mbtiles"; tmp = dst + ".partial"
    for f in (dst, tmp):
        if os.path.exists(f):
            sys.exit(f"{f} exists; not overwriting it (nothing is deleted without Aspen's word)")
    want = scope(a.only)
    if not check(parts, want):
        sys.exit("the count check on the part files failed: not merging")
    need = sum(os.path.getsize(f) for f in mbtiles_files(parts)); free = free_bytes(out)
    log(f"merge: parts {gib(need)}, free {gib(free)}")
    if free - need < MIN_FREE:
        sys.exit(f"merging would leave {gib(free - need)} free, under {gib(MIN_FREE)}: not merging")
    db = sqlite3.connect(tmp)
    db.execute("pragma journal_mode=off"); db.execute("pragma synchronous=off")
    db.executescript("create table metadata(name text, value text);"
                     "create table tiles(zoom_level integer, tile_column integer, tile_row integer, tile_data blob);"
                     "create unique index tile_index on tiles(zoom_level, tile_column, tile_row);")
    db.executemany("insert into metadata values(?,?)", METADATA.items())
    for f in mbtiles_files(parts):
        db.execute("attach ? as p", (f,))
        db.execute("insert into tiles select zoom_level, tile_column, tile_row, tile_data from p.tiles")
        db.commit()
        db.execute("detach p")
        log(f"merged {os.path.basename(f)}")
    db.close()
    os.rename(tmp, dst)
    log(f"wrote {dst}, {os.path.getsize(dst)} bytes")
    return 0 if check(dst, want) else 1


# --- verify (R2's checks on the result) -------------------------------------------------------------------------
def tile_of(z, lat, lon):
    n = 2**z
    return z, int((lon+180)/360*n), ty(lat, n)


def lonlat(z, x, y):
    n = 2**z
    return x/n*360-180, math.degrees(math.atan(math.sinh(math.pi*(1-2*y/n))))


def pm_tile(pmt, z, x, y):
    r = subprocess.run(["pmtiles", "tile", "-q", pmt, str(z), str(x), str(y)], capture_output=True)
    return r.stdout if r.returncode == 0 and r.stdout else None


def highest(pmt, z, lat, lon):
    """Highest decoded pixel in the 3x3 tiles around (lat, lon), from the PMTiles. (metres, tile, tiles found)."""
    _, x0, y0 = tile_of(z, lat, lon); best = (None, None); found = 0
    for x in range(x0-1, x0+2):
        for y in range(y0-1, y0+2):
            b = pm_tile(pmt, z, x, y)
            if b is None:
                continue
            found += 1; m = decode(b).max()
            if best[0] is None or m > best[0]:
                best = (m, f"{z}/{x}/{y}")
    return best[0], best[1], found


STEP = 1 / 256                 # one Terrarium step, in metres


def tile_diff(b, ref):
    """(byte-identical, differing pixels, largest decoded difference in m) of tile bytes b against ref."""
    if b == ref:
        return True, 0, 0.0
    d = np.abs(decode(b) - decode(ref))
    return False, int((d > 0).sum()), float(d.max())


def mb_tile(mbt):
    """A z/x/y -> PNG bytes getter on an MBTiles (y in XYZ), like pm_tile on a PMTiles."""
    db = sqlite3.connect(f"file:{mbt}?mode=ro", uri=True)
    def get(z, x, y):
        r = db.execute("select tile_data from tiles where zoom_level=? and tile_column=? and tile_row=?",
                       (z, x, (2**z-1)-y)).fetchone()
        return r[0] if r else None
    return get


def hood_vs_reference(get, want=None):
    """Hood's z11 tiles against the trial's. Inner tiles (wholly inside 45-46 N, 123-121 W) must each be within one
    Terrarium step (1/256 m) of the reference (planner, 13:14); edge tiles are reported, not judged. Prints the
    counts; returns {label: (identical, different, missing, largest difference m, differing pixels)}."""
    inner, edge = [], []
    for p in sorted(glob.glob(f"{REF}/11/*/*.png")):
        x, y = int(p.split("/")[-2]), int(p.split("/")[-1][:-4])
        if want is not None and (11, x, y) not in want:
            continue
        w, n = lonlat(11, x, y); e, s = lonlat(11, x+1, y+1)
        (inner if REF_W < w and e < REF_E and REF_S < s and n < REF_N else edge).append((x, y, p))
    res = {}
    for label, ts in (("wholly inside", inner), ("on the edge of", edge)):
        same = diff = missing = px = 0; worst = (0.0, None)
        for x, y, p in ts:
            b = get(11, x, y)
            if b is None:
                missing += 1; continue
            ident, npx, d = tile_diff(b, open(p, "rb").read())
            if ident:
                same += 1; continue
            diff += 1; px += npx
            if d >= worst[0]:
                worst = (d, f"11/{x}/{y}")
        print(f"Hood z11 tiles {label} the trial area: {len(ts)}; byte-identical {same}, different {diff},"
              f" missing {missing}" + (f"; {px} differing pixels in all, largest decoded difference"
                                       f" {worst[0]:.4f} m in {worst[1]}" if diff else ""))
        res[label] = (same, diff, missing, worst[0], px)
    return res


def hood(a):
    """R2's Hood check on OUT/relief.mbtiles, before converting: exit 1 if an inner tile is missing or is more than
    1/256 m off."""
    out = os.path.abspath(a.out); want = set(scope(a.only)) if a.only else None
    same, diff, missing, worst, _ = hood_vs_reference(mb_tile(f"{out}/relief.mbtiles"), want)["wholly inside"]
    ok = missing == 0 and same + diff > 0 and worst <= STEP + 1e-9
    print(f"Hood check (inner tiles within {STEP} m, none missing): {'PASS' if ok else 'FAIL: do not convert'}")
    return 0 if ok else 1


def verify(a):
    out = os.path.abspath(a.out); pmt = f"{out}/relief.pmtiles"; mbt = f"{out}/relief.mbtiles"
    want = set(scope(a.only)) if a.only else None
    print(subprocess.run(["pmtiles", "show", pmt], capture_output=True, text=True, check=True).stdout)
    hood_vs_reference(lambda z, x, y: pm_tile(pmt, z, x, y), want)
    for name, lat, lon, near in (("Mount Hood", 45.3735, -121.6959, "about 3,390 m (the trial read 3,392)"),
                                 ("Denali", 63.0692, -151.0070, "near 6,190 m"),
                                 ("Mount Logan", 60.5672, -140.4053, "near 5,959 m")):
        if want is not None and tile_of(11, lat, lon) not in want:
            continue
        m, where, found = highest(pmt, 11, lat, lon)
        print(f"{name}: highest z11 pixel {m:.2f} m in {where} ({found} of 9 tiles around the summit found); expected {near}")
    if want is None:
        for name, lat, lon in (("Gulf of Maine sea", 43.3, -67.6), ):
            t = tile_of(11, lat, lon); b = pm_tile(pmt, *t)
            h = decode(b) if b else None
            print(f"{name}: tile {'/'.join(map(str, t))} " + ("MISSING" if b is None else
                  f"min {h.min():.3f} m, max {h.max():.3f} m"))
        for name, lat, lon in (("Kiska, 177.6 E", 52.103, 177.602), ("Semisopochnoi, 179.6 E", 51.93, 179.58)):
            t = tile_of(11, lat, lon); b = pm_tile(pmt, *t)
            print(f"Aleutian tile east of 180 ({name}): {'/'.join(map(str, t))} " + ("MISSING" if b is None else
                  f"present, {len(b)} bytes, highest pixel {decode(b).max():.1f} m"))
    h = hashlib.sha256()
    with open(pmt, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""):
            h.update(blk)
    print(f"relief.pmtiles: {os.path.getsize(pmt)} bytes, sha256 {h.hexdigest()}")
    if os.path.exists(mbt):
        print(f"relief.mbtiles: {os.path.getsize(mbt)} bytes")
    print(f"now: {temp_c():.1f}'C, throttled={throttled():#x}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    t = sp.add_parser("tiles"); t.add_argument("--cells")
    b = sp.add_parser("build"); b.add_argument("out"); b.add_argument("--procs", type=int, default=4)
    b.add_argument("--chunk", type=int, default=32); b.add_argument("--only")
    c = sp.add_parser("check"); c.add_argument("path"); c.add_argument("--only")
    m = sp.add_parser("merge"); m.add_argument("out"); m.add_argument("--only")
    v = sp.add_parser("verify"); v.add_argument("out"); v.add_argument("--only")
    s = sp.add_parser("stop"); s.add_argument("out")
    h = sp.add_parser("hood"); h.add_argument("out"); h.add_argument("--only")
    a = ap.parse_args()
    if a.cmd == "build" and not 1 <= a.procs <= 4:
        sys.exit("--procs is 1 to 4 (dispatch: up to 4 processes)")
    if a.cmd == "tiles":
        ts = all_tiles(cells(a.cells.split(",") if a.cells else None)); c = per_zoom(ts)
        print(" ".join(f"z{z} {c[z]}" for z in ZOOMS), f"total {len(ts)}")
        return 0
    if a.cmd == "build":
        rc = build(a); log(f"end: build exit {rc}"); return rc
    if a.cmd == "check":
        return 0 if check(a.path, scope(a.only)) else 1
    if a.cmd == "merge":
        return merge(a)
    if a.cmd == "stop":
        return stop_build(a)
    if a.cmd == "hood":
        return hood(a)
    return verify(a)


if __name__ == "__main__":
    sys.exit(main())
