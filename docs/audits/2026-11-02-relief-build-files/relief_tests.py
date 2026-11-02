#!/usr/bin/env python3
"""coder-12 R0 tests for relief.py (Willow, 2026-11-02). Each test can fail, and prints what it read.

  relief_tests.py [WORKDIR]    WORKDIR is a new folder under /tmp (default /tmp/coder12-r0-<time>); nothing is
                               written anywhere else. The hgt3 cells and the trial's tiles are only read.
                               It re-runs itself under unshare -Urpf --mount-proc; no test runs outside that.

1. tile counts: the enumeration from the cells equals the planner's table (dispatch premise 4)
2. antimeridian: N52E179's z11 tiles have x >= 2040 and none wrap to x = 0 (control: without the 1e-9 one would)
3. Terrarium round trip: -86, 0, 3392.4 and 6190.5 m decode within 1/256 m (control: dropping B fails)
4. stop and resume, inside a private PID namespace: relief.py stop refuses (no signal syscall, a sentinel lives)
   for pgid 1, its own group and the sentinel's group; then 20 z11 tiles, 2 workers, stopped partway with
   relief.py stop OUT (strace: only kill(-pgid, SIGTERM)), restarted: each tile once, the sentinel alive.
   Run 1 has RELIEF_TEST_CHUNK_DELAY=1 (1 s after each chunk), so the stop lands partway; run 2 has it off
5. the count check catches a gap (positive control): one row dropped from a copy of a part file -> FAIL naming
   z11; and on a synthetic full set (every tile, empty PNG stubs): passes, then one z7 row dropped and one z9 tile
   duplicated -> FAIL naming z7 and z9
6. the chain on the same 20 tiles: merge, hood (before converting), pmtiles convert, verify. Hood passes if the
   trial's two-cell VRT gives 20/20 byte-identical and the full VRT every tile within 1/256 m (control: a tile
   0.01 m off is rejected); the summit equals the reference's 3391.582 m
7. antimeridian render: the tiles at 180 E (z11 x 2047, z5 x 31) render in about the time of their neighbours
"""
import argparse, collections, contextlib, io, os, shutil, sqlite3, subprocess, sys, time
import numpy as np
from osgeo import gdal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relief

TABLE = {5: 103, 6: 330, 7: 1163, 8: 4349, 9: 16757, 10: 65689, 11: 260118}   # premise 4
TWENTY = [(11, x, y) for x in range(330, 335) for y in range(731, 735)]      # inside the trial area; 11/331/733 is Hood
results = []


def result(name, ok, why=""):
    results.append((name, ok))
    print(f"==> {name}: {'PASS' if ok else 'FAIL'}{' - ' + why if why else ''}\n", flush=True)


def captured(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a)
    print(buf.getvalue(), end="")
    return r, buf.getvalue()


def t1_counts():
    got = relief.per_zoom(relief.all_tiles(relief.cells()))
    print("enumerated:", " ".join(f"z{z} {got[z]}" for z in relief.ZOOMS), "total", sum(got.values()))
    print("table:     ", " ".join(f"z{z} {TABLE[z]}" for z in relief.ZOOMS), "total", sum(TABLE.values()))
    result("1 tile counts", got == TABLE)


def t2_antimeridian():
    xs = sorted({x for x, _ in relief.cell_tiles(11, 52, 179)})
    print(f"N52E179 z11 columns: {xs}")
    full = relief.all_tiles(relief.cells())
    out_of_range = [t for t in full if not 0 <= t[1] < 2**t[0]]
    print(f"tiles in the full list with x outside 0..2^z-1: {len(out_of_range)}")
    east = collections.Counter(z for z, x, _ in full if x == 2**z - 1)
    west = collections.Counter(z for z, x, _ in full if x == 0)
    print("tiles at x = 2^z-1 (from cells ending at 180 E):", dict(sorted(east.items())))
    print("tiles at x = 0 (from cells starting at 180 W):  ", dict(sorted(west.items())))
    # Control: the trial's x formula without its 1e-9 puts a cell that ends at 180 E on x = 2^z (that is, 0).
    n = 2**11; bad_x1 = int((179+1+180)/360*n)
    print(f"control, without the 1e-9: N52E179's last column would be {bad_x1} (= {bad_x1 % n} wrapped)")
    ok = xs and min(xs) >= 2040 and max(xs) == 2047 and 0 not in xs and not out_of_range and bad_x1 == 2048
    result("2 antimeridian", bool(ok))


def t3_terrarium():
    vals = [-86.0, 0.0, 3392.4, 6190.5]
    def dec(rgb): return rgb[..., 0].astype(float)*256 + rgb[..., 1] + rgb[..., 2]/256 - 32768
    h = np.array([vals + [np.nan]], dtype=np.float32)        # float32, as the warp gives it; NaN is a void
    rgb = relief.terrarium(h)
    img = relief.Image.fromarray(rgb, "RGB"); buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    back = relief.decode(buf.getvalue())[0]                   # through a PNG, as the tiles are
    errs = [abs(back[i] - v) for i, v in enumerate(vals)]
    for v, d, e, c in zip(vals, back, errs, rgb[0]):
        print(f"{v:>8} m -> RGB {tuple(int(t) for t in c)} -> {d:.6f} m, error {e:.6f} m")
    print(f"void (NaN) -> {back[4]:.6f} m")
    # Control: an encoder that drops the B channel must fail the same tolerance.
    broken = rgb.copy(); broken[..., 2] = 0
    berr = max(abs(dec(broken)[0][i] - v) for i, v in enumerate(vals))
    print(f"control, B dropped: largest error {berr:.4f} m (must exceed 1/256 = {1/256:.6f})")
    result("3 Terrarium round trip", max(errs) <= 1/256 and back[4] == 0 and berr > 1/256,
           f"largest error {max(errs):.6f} m")


def rows_now(parts):
    n = 0
    for f in relief.mbtiles_files(parts):
        try:
            db = sqlite3.connect(f"file:{f}?mode=ro", uri=True, timeout=1)
            n += db.execute("select count(*) from tiles").fetchone()[0]; db.close()
        except sqlite3.Error:
            pass
    return n


def run_build(out, only, log, delay=None):
    cmd = ["setsid", "nohup", sys.executable, f"{HERE}/relief.py", "build", out, "--procs", "2", "--chunk", "2",
           "--only", only]
    env = {k: v for k, v in os.environ.items() if k != "RELIEF_TEST_CHUNK_DELAY"}
    if delay:
        env["RELIEF_TEST_CHUNK_DELAY"] = delay       # 1 s after each chunk, so the stop lands partway (planner, 13:14)
    return subprocess.Popen(cmd, stdout=open(log, "w"), stderr=subprocess.STDOUT, env=env)


SIGCALLS = "kill,tkill,tgkill,rt_sigqueueinfo,rt_tgsigqueueinfo,pidfd_send_signal"


def traced_stop(out, trace, prefix=()):
    """relief.py stop OUT under strace, which records every signal-sending syscall (none is skipped; the namespace
    is the guard). Returns (exit, output, the calls with their pid prefix dropped and spaces squeezed)."""
    cmd = [*prefix, "strace", "-f", "-qq", "-e", f"trace={SIGCALLS}", "-e", "signal=none", "-o", trace,
           sys.executable, f"{HERE}/relief.py", "stop", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    calls = []
    for l in open(trace).read().splitlines():
        w = l.split()
        if w:
            calls.append(" ".join(w[1:] if w[0].isdigit() else w))
    return r.returncode, (r.stdout + r.stderr).strip(), calls


def proc_stat(pid):
    """(state, pgid) of pid from /proc, or None if it's gone."""
    try:
        f = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
        return f[0], int(f[2])
    except OSError:
        return None


def alive(pid):
    st = proc_stat(pid)
    return st is not None and st[0] != "Z"


def t4_resume(work):
    name = "4 stop and resume"
    nproc = sum(1 for d in os.listdir("/proc") if d.isdigit())
    print(f"namespace: this runner is pid {os.getpid()}, /proc/1 is {open('/proc/1/comm').read().strip()!r},"
          f" {nproc} processes visible, {NS_ENV}={os.environ.get(NS_ENV)}")
    if os.getpid() != 1 or os.environ.get(NS_ENV) != "1":
        return result(name, False, "not inside the private PID namespace: test 4 not run (dispatch 13:02)")
    out = f"{work}/resume"; parts = f"{out}/parts"; only = f"{work}/twenty.txt"; ctl = f"{work}/stopctl"
    os.makedirs(out); os.makedirs(ctl)
    open(only, "w").write("".join(f"{z}/{x}/{y}\n" for z, x, y in TWENTY))

    # The sentinel: a process in its own group that no stop may touch.
    sentinel = subprocess.Popen(["setsid", "sleep", "900"]); time.sleep(0.3)
    st = proc_stat(sentinel.pid)
    print(f"sentinel: pid {sentinel.pid}, state/pgid {st} (setsid sleep 900)")
    ok_ctl = st is not None and st[1] == sentinel.pid

    # Controls: stop must refuse, and make no signal syscall, for pgid 1, its own group, and the sentinel's group.
    own = ["setsid", "sh", "-c", f'echo $$ > {ctl}/build.pgid && exec "$@"', "sh"]   # pgid = the stop's own group
    for n, (label, value, prefix, why) in enumerate((
            ("build.pgid holds 1", "1", (), "is not greater than 1"),
            ("build.pgid holds the caller's own group", None, own, "this process's own group"),
            ("build.pgid holds the sentinel's group", str(sentinel.pid), (), "aren't relief.py build")), 1):
        if value is not None:
            open(f"{ctl}/build.pgid", "w").write(value + "\n")
        rc, text, calls = traced_stop(ctl, f"{work}/trace-control-{n}.txt", prefix)
        got = open(f"{ctl}/build.pgid").read().strip()
        ok = rc != 0 and "refusing, sending nothing" in text and why in text and not calls and alive(sentinel.pid)
        print(f"control {n}, {label} ({got}): exit {rc}; signal syscalls {calls or 'none'};"
              f" sentinel {'alive' if alive(sentinel.pid) else 'GONE'} -> {'ok' if ok else 'FAILED'}")
        print("  " + text.replace("\n", "\n  "))
        ok_ctl = ok_ctl and ok

    p = run_build(out, only, f"{work}/run1.log", delay="1")
    pgid, t0 = None, time.time()
    while time.time() - t0 < 180 and p.poll() is None:
        if pgid is None:
            try:
                pgid = int(open(f"{out}/build.pgid").read())
            except (OSError, ValueError):
                pass
        if pgid and rows_now(parts) >= 1:
            break
        time.sleep(0.05)
    n_at_stop = rows_now(parts)
    if p.poll() is not None or not pgid:
        print(open(f"{work}/run1.log").read())
        return result(name, False, f"run 1 ended before the stop (exit {p.poll()}, pgid {pgid})")
    members = relief.group_members(pgid)
    print(f"run 1: pid {p.pid}, pgid {pgid}; {n_at_stop} tile(s) committed; the group before the stop:")
    for pid, state, argv in members:
        print(f"  pid {pid} {state} {' '.join(argv)[:150]}")
    rc_stop, text, calls = traced_stop(out, f"{work}/trace-stop.txt")
    print(f"relief.py stop {out}: exit {rc_stop}; signal syscalls {calls}")
    print("  " + text.replace("\n", "\n  "))
    rc1 = p.wait(60); time.sleep(1)
    left = relief.group_members(pgid)
    ok_stop = (rc_stop == 0 and calls == [f"kill(-{pgid}, SIGTERM) = 0"] and pgid == p.pid and not left
               and alive(sentinel.pid))
    leftovers = sorted(os.listdir(parts))
    after_stop = sum(len(relief.read_tiles(f)) for f in relief.mbtiles_files(parts))
    print(f"run 1 exit {rc1}; live processes left in the group: {left or 'none'}; sentinel"
          f" {'alive' if alive(sentinel.pid) else 'GONE'}; files: {leftovers}")
    print(f"tiles in the part files after the stop: {after_stop} of {len(TWENTY)}")
    print("run 1 log:\n  " + open(f"{work}/run1.log").read().strip().replace("\n", "\n  "))
    p2 = run_build(out, only, f"{work}/run2.log"); rc2 = p2.wait(600)
    print(f"run 2 exit {rc2}; log:\n  " + open(f"{work}/run2.log").read().strip().replace("\n", "\n  "))
    seen = collections.Counter(t for f in relief.mbtiles_files(parts) for t in relief.read_tiles(f))
    once = all(seen[t] == 1 for t in TWENTY); missing = [t for t in TWENTY if t not in seen]
    extra = [t for t in seen if t not in TWENTY]
    print(f"after run 2: {len(seen)} distinct tiles, {sum(seen.values())} rows; missing {missing}; extra {extra}")
    ok_check, _ = captured(relief.check, parts, TWENTY)
    log1, log2 = open(f"{work}/run1.log").read(), open(f"{work}/run2.log").read()
    skipped = f"already in part files: {after_stop}; to do: {len(TWENTY) - after_stop}" in log2
    delays = "chunk delay 1 s (test only)" in log1 and "chunk delay off" in log2
    print(f"start lines: run 1 {'shows' if 'chunk delay 1 s (test only)' in log1 else 'does NOT show'} the 1 s test"
          f" delay; run 2 {'shows' if 'chunk delay off' in log2 else 'does NOT show'} it off")
    print(f"controls {'ok' if ok_ctl else 'FAILED'}; the real stop {'ok' if ok_stop else 'FAILED'}; sentinel"
          f" {'alive' if alive(sentinel.pid) else 'GONE'} at the end")
    result(name, ok_ctl and ok_stop and rc1 != 0 and 0 < after_stop < len(TWENTY) and rc2 == 0 and once
           and not missing and not extra and ok_check and skipped and delays and alive(sentinel.pid),
           f"3 refusals sent nothing; stop sent only kill(-{pgid}, SIGTERM); stopped at {after_stop}/20, restart did"
           f" {len(TWENTY) - after_stop}, each tile once; the sentinel lived")


def t5_gap(work):
    parts = f"{work}/resume/parts"; gap = f"{work}/gap"
    shutil.copytree(parts, gap)
    f = next(f for f in relief.mbtiles_files(gap) if relief.read_tiles(f))
    db = sqlite3.connect(f)
    rowid, z, x, r = db.execute("select rowid, zoom_level, tile_column, tile_row from tiles limit 1").fetchone()
    db.execute("delete from tiles where rowid = ?", (rowid,)); db.commit(); db.close()
    print(f"dropped {z}/{x}/{(2**z-1)-r} from the copy {os.path.basename(f)}")
    ok_gap, text = captured(relief.check, gap, TWENTY)
    a = not ok_gap and "FAIL: z11 missing 1" in text and f"{z}/{x}/{(2**z-1)-r}" in text

    syn = f"{work}/synthetic"; os.makedirs(syn)
    full = relief.all_tiles(relief.cells())
    db = relief.open_part(f"{syn}/part-0.mbtiles")
    db.executemany("insert into tiles values(?,?,?,?)", ((z, x, (2**z-1)-y, relief.PNG_SIG) for z, x, y in full))
    db.commit(); db.close()
    ok_full, _ = captured(relief.check, syn, full)
    z7 = next(t for t in full if t[0] == 7); z9 = next(t for t in full if t[0] == 9)
    db = sqlite3.connect(f"{syn}/part-0.mbtiles")
    db.execute("delete from tiles where zoom_level = 7 and tile_column = ? and tile_row = ?", (z7[1], (2**7-1)-z7[2]))
    db.commit(); db.close()
    db = relief.open_part(f"{syn}/part-1.mbtiles")
    db.execute("insert into tiles values(?,?,?,?)", (9, z9[1], (2**9-1)-z9[2], relief.PNG_SIG)); db.commit(); db.close()
    print(f"synthetic: dropped z7 {z7[1]}/{z7[2]}, duplicated z9 {z9[1]}/{z9[2]} in part-1")
    ok_syn, text2 = captured(relief.check, syn, full)
    b = ok_full and not ok_syn and "z7 missing 1" in text2 and "z9 duplicated 1" in text2
    result("5 count check catches a gap", a and b,
           "20-tile copy: FAIL naming z11; synthetic full set: PASS, then FAIL naming z7 and z9")


def t6_chain(work):
    name = "6 merge, convert, verify (20 tiles)"
    out = f"{work}/resume"; only = f"{work}/twenty.txt"
    try:
        rc, _ = captured(relief.merge, argparse.Namespace(out=out, only=only))
    except SystemExit as e:
        return result(name, False, f"merge stopped: {e}")
    hd = subprocess.run([sys.executable, f"{HERE}/relief.py", "hood", out, "--only", only], capture_output=True, text=True)
    print(f"relief.py hood (on relief.mbtiles, before converting): exit {hd.returncode}\n  "
          + (hd.stdout + hd.stderr).strip().replace("\n", "\n  "))
    os.makedirs(f"{out}/tmp")
    cv = subprocess.run(["pmtiles", "convert", "--tmpdir", f"{out}/tmp", f"{out}/relief.mbtiles", f"{out}/relief.pmtiles"],
                        capture_output=True, text=True)
    print(f"pmtiles convert exit {cv.returncode}" + (f": {cv.stderr.strip()[-400:]}" if cv.returncode else ""))
    db = sqlite3.connect(f"{out}/relief.mbtiles"); md = dict(db.execute("select name, value from metadata")); db.close()
    print("metadata:", md)
    _, text = captured(relief.verify, argparse.Namespace(out=out, only=only))
    pmt = f"{out}/relief.pmtiles"
    same, diff, missing, worst, px = relief.hood_vs_reference(lambda z, x, y: relief.pm_tile(pmt, z, x, y),
                                                              set(TWENTY))["wholly inside"]
    within = missing == 0 and same + diff == len(TWENTY) and worst <= relief.STEP + 1e-9
    print(f"full VRT, from relief.pmtiles: {same} byte-identical, {diff} different ({px} pixels), missing {missing};"
          f" largest {worst:.4f} m -> {'within' if within else 'NOT within'} 1/256 m")

    # The trial's own two cells: the render must give the trial's bytes exactly.
    os.makedirs(f"{work}/two")
    v2 = gdal.Open(relief.make_vrt(f"{work}/two", relief.cells(["N45W123", "N45W122"])))
    two_same = sum(relief.render(v2, z, x, y) == open(f"{relief.REF}/{z}/{x}/{y}.png", "rb").read() for z, x, y in TWENTY)
    print(f"trial's two-cell VRT: {two_same} of {len(TWENTY)} byte-identical to the reference")

    # Control: the same comparison must reject a tile 0.01 m off (more than one step).
    ref = open(f"{relief.REF}/11/331/733.png", "rb").read()
    img = relief.Image.fromarray(relief.terrarium(relief.decode(ref) + 0.01), "RGB"); buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    c_ident, c_px, c_d = relief.tile_diff(buf.getvalue(), ref)
    rejects = not c_ident and c_d > relief.STEP
    print(f"control, 11/331/733 + 0.01 m: {c_px} pixels differ, largest {c_d:.4f} m ->"
          f" {'rejected' if rejects else 'NOT rejected'} by the 1/256 m rule")

    m, where, found = relief.highest(pmt, 11, 45.3735, -121.6959)
    ok = (rc == 0 and hd.returncode == 0 and cv.returncode == 0 and md == relief.METADATA and "tile type: png" in text
          and within and two_same == len(TWENTY) and rejects and abs(m - 3391.582) < 0.01)
    result(name, ok, f"two-cell VRT {two_same}/20 identical; full VRT {same} identical, {diff} within 1/256 m"
                     f" ({px} px); Hood summit {m:.3f} m in {where}, the reference reads 3391.582 m")


def t7_render(work):
    vrt = gdal.Open(relief.make_vrt(work, relief.cells()))
    y11 = relief.ty(51.93, 2**11); y5 = relief.ty(52.0, 2**5)
    times = {}
    for z, x, y in ((11, 2045, y11), (11, 2046, y11), (11, 2047, y11), (5, 30, y5), (5, 31, y5)):
        t = time.time(); h = relief.decode(relief.render(vrt, z, x, y)); times[(z, x)] = time.time() - t
        w, n = relief.lonlat(z, x, y); e, s = relief.lonlat(z, x + 1, y + 1)
        print(f"{z}/{x}/{y} ({w:.3f}..{e:.3f} E, {s:.2f}..{n:.2f} N): {times[(z, x)]:.2f} s; highest {h.max():.1f} m,"
              f" land pixels {(h > 0).sum()}, east column highest {h[:, -1].max():.1f} m")
    ok = times[(11, 2047)] < 5 * max(times[(11, 2045)], times[(11, 2046)], 0.2) and times[(5, 31)] < 5 * max(times[(5, 30)], 1)
    result("7 antimeridian render", ok, "the 180 E tiles take about as long as their neighbours")


NS_ENV = "RELIEF_TESTS_IN_PIDNS"


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else time.strftime("/tmp/coder12-r0-%Y%m%dT%H%M%S")
    if not work.startswith("/tmp/"):
        sys.exit("the tests write only under /tmp")
    if os.environ.get(NS_ENV) != "1":
        # The whole run goes inside a private PID namespace (dispatch, update 13:02): there a wrong signal can
        # reach only the test's own processes. No test runs outside it.
        cmd = ["unshare", "-Urpf", "--mount-proc", sys.executable, "-u", os.path.abspath(__file__), work]
        print(f"{time.strftime('%F %T %Z')} running inside a private PID namespace: {' '.join(cmd)}", flush=True)
        r = subprocess.run(cmd, env={**os.environ, NS_ENV: "1"})
        print(f"{time.strftime('%F %T %Z')} namespace run exit {r.returncode}", flush=True)
        return r.returncode
    os.makedirs(work)
    print(f"{time.strftime('%F %T %Z')} relief_tests.py in {work}; relief.py at {HERE}\n", flush=True)
    t1_counts(); t2_antimeridian(); t3_terrarium(); t4_resume(work); t5_gap(work); t6_chain(work); t7_render(work)
    print(time.strftime("%F %T %Z"), "summary:", "; ".join(f"{n} {'PASS' if ok else 'FAIL'}" for n, ok in results))
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
