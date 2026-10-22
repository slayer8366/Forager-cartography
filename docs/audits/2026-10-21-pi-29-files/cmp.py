import gzip, hashlib, math, subprocess, sys, time
SRC = "/srv/forager-build/out-usca/current/forager-usca.pmtiles"
URL = "https://forager-pmtiles.brandonlee1-894.workers.dev/us/%d/%d/%d.mvt?cb=pi29r-%d-%s"
def ungz(b): return gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b
def deg2tile(lat, lon, z):
    n = 2 ** z; x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n); return x, y
def check(label, z, x, y, want=None):
    local = ungz(subprocess.run(["pmtiles", "tile", "-q", SRC, str(z), str(x), str(y)], capture_output=True).stdout)
    r = subprocess.run(["curl", "-sS", "--compressed", "-D", "hdr.txt", "-o", "body.bin", "-w", "%{http_code}",
                        URL % (z, x, y, time.time_ns(), label.replace(" ", ""))], capture_output=True, text=True)
    hdr = open("hdr.txt").read().lower().splitlines()
    origin = next((l.split(":", 1)[1].strip() for l in hdr if l.startswith("x-forager-origin")), "-")
    served = ungz(open("body.bin", "rb").read())
    extra = ""
    if want: extra = " contains " + ",".join("%s=%s" % (w, w.encode() in local) for w in want)
    print("%-17s %2d/%d/%d HTTP %s origin %-4s local %7d B served %7d B %s%s" % (label, z, x, y, r.stdout, origin,
          len(local), len(served), "MATCH" if local == served and local else "DIFFERS", extra))
    print("   sha256 %s" % hashlib.sha256(served).hexdigest())
check("z15 trail", 15, 5303, 11553)
check("z11 track", 11, 5303 >> 4, 11553 >> 4, ["track"])
check("z12 path", 12, 5303 >> 3, 11553 >> 3, ["path"])
for name, lat, lon in [("Seattle", 47.6062, -122.3321), ("Miami", 25.7617, -80.1918), ("Anchorage", 61.2181, -149.9003),
        ("Honolulu", 21.3069, -157.8583), ("Toronto", 43.6532, -79.3832), ("Whitehorse", 60.7212, -135.0568),
        ("St. John's", 47.5615, -52.7126), ("San Juan", 18.4655, -66.1057), ("Charlotte Amalie", 18.3419, -64.9307)]:
    check(name, 12, *deg2tile(lat, lon, 12))
