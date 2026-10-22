#!/usr/bin/env python3
"""pi-29 resume: finish an unfinished R2 multipart upload of us.pmtiles.

  resume.py verify    list parts on R2, compare each ETag with the local chunk's MD5 (read-only)
  resume.py upload    upload every part that is missing or mismatched, check each returned ETag
  resume.py complete  re-list, check all parts, then CompleteMultipartUpload

HTTP goes through curl --aws-sigv4; the keys are passed to curl on stdin, never on the command line.
"""
import base64, hashlib, json, os, subprocess, sys, tempfile, time, urllib.parse
import xml.etree.ElementTree as ET

SRC = "/srv/forager-build/out-usca/current/forager-usca.pmtiles"
SIZE = 34141705380
PART = 16 * 1024 * 1024
NPARTS = -(-SIZE // PART)  # 2036
EP = "https://a6a899e01e2194ef8fff048c20130e14.r2.cloudflarestorage.com"
OBJ = EP + "/forager-maps/us.pmtiles"
UPLOAD_ID = open(os.path.join(os.path.dirname(__file__), "upload-id.txt")).read().strip()
DIR = os.path.dirname(os.path.abspath(__file__))
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def keys():
    ak = sk = None
    sect = None
    for line in open(os.path.expanduser("~/.config/rclone/rclone.conf")):
        line = line.strip()
        if line.startswith("["):
            sect = line
        elif sect == "[r2]" and "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            if k == "access_key_id":
                ak = v
            elif k == "secret_access_key":
                sk = v
    return ak, sk


AK, SK = keys()


def curl(method, query, body_path=None, body_sha=None, extra_headers=(), timeout=600):
    sha = body_sha or hashlib.sha256(b"").hexdigest()
    url = OBJ + "?" + query
    cmd = ["curl", "-sS", "-K", "-", "--aws-sigv4", "aws:amz:auto:s3", "--max-time", str(timeout),
           "-X", method, "-H", "x-amz-content-sha256: " + sha, "-D", "-", "-o", "-"]
    for h in extra_headers:
        cmd += ["-H", h]
    if body_path:
        cmd += ["--data-binary", "@" + body_path]
        if not any(h.lower().startswith("content-type:") for h in extra_headers):
            cmd += ["-H", "Content-Type: application/octet-stream"]
    cfg = 'user = "%s:%s"\n' % (AK, SK)
    r = subprocess.run(cmd + [url], input=cfg.encode(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("curl exit %d: %s" % (r.returncode, r.stderr.decode(errors="replace").strip()))
    out = r.stdout.decode(errors="replace")
    head, _, body = out.partition("\r\n\r\n")
    while head.startswith("HTTP/1.1 100") or head.startswith("HTTP/2 100"):
        head, _, body = body.partition("\r\n\r\n")
    status = int(head.split()[1])
    hdrs = {}
    for l in head.split("\r\n")[1:]:
        if ":" in l:
            k, v = l.split(":", 1)
            hdrs[k.strip().lower()] = v.strip()
    return status, hdrs, body


def list_parts():
    parts, marker = {}, 0
    uid = urllib.parse.quote(UPLOAD_ID, safe="")
    while True:
        st, _, body = curl("GET", "max-parts=1000&part-number-marker=%d&uploadId=%s" % (marker, uid))
        if st != 200:
            raise RuntimeError("ListParts HTTP %d: %s" % (st, body[:300]))
        root = ET.fromstring(body)
        for p in root.iter(NS + "Part"):
            n = int(p.find(NS + "PartNumber").text)
            parts[n] = (p.find(NS + "ETag").text.strip('"'), int(p.find(NS + "Size").text))
        if root.find(NS + "IsTruncated").text != "true":
            return parts
        marker = int(root.find(NS + "NextPartNumberMarker").text)


def chunk(n):
    off = (n - 1) * PART
    ln = min(PART, SIZE - off)
    with open(SRC, "rb") as f:
        f.seek(off)
        data = f.read(ln)
    assert len(data) == ln
    return data


def local_md5s():
    cache = os.path.join(DIR, "local-md5s.json")
    if os.path.exists(cache):
        return {int(k): v for k, v in json.load(open(cache)).items()}
    assert os.path.getsize(SRC) == SIZE
    md5s = {}
    for n in range(1, NPARTS + 1):
        md5s[n] = hashlib.md5(chunk(n)).hexdigest()
    json.dump(md5s, open(cache, "w"))
    return md5s


def check(parts, md5s):
    good, bad, missing = [], [], []
    for n in range(1, NPARTS + 1):
        exp_len = min(PART, SIZE - (n - 1) * PART)
        if n not in parts:
            missing.append(n)
        elif parts[n] == (md5s[n], exp_len):
            good.append(n)
        else:
            bad.append(n)
    extra = sorted(set(parts) - set(range(1, NPARTS + 1)))
    return good, bad, missing, extra


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S %Z ") + msg
    print(line, flush=True)


def cmd_verify():
    md5s = local_md5s()
    parts = list_parts()
    good, bad, missing, extra = check(parts, md5s)
    log("verify: %d parts expected, %d on R2, %d match, %d mismatch %s, %d missing, extra %s"
        % (NPARTS, len(parts), len(good), len(bad), bad[:20], len(missing), extra))
    json.dump({"good": good, "bad": bad, "missing": missing, "extra": extra},
              open(os.path.join(DIR, "verify.json"), "w"))
    return not extra


def cmd_upload():
    md5s = local_md5s()
    v = json.load(open(os.path.join(DIR, "verify.json")))
    todo = sorted(v["bad"] + v["missing"])
    uid = urllib.parse.quote(UPLOAD_ID, safe="")
    log("upload: %d parts to send" % len(todo))
    tmp = os.path.join(DIR, "part.bin")
    for i, n in enumerate(todo, 1):
        data = chunk(n)
        with open(tmp, "wb") as f:
            f.write(data)
        sha = hashlib.sha256(data).hexdigest()
        cmd5 = base64.b64encode(bytes.fromhex(md5s[n])).decode()
        for attempt in range(1, 31):
            t0 = time.time()
            try:
                st, h, body = curl("PUT", "partNumber=%d&uploadId=%s" % (n, uid), tmp, sha,
                                   ["Content-MD5: " + cmd5], timeout=300)
                etag = h.get("etag", "").strip('"')
                if st == 200 and etag == md5s[n]:
                    log("part %d ok (%d/%d) %.1fs" % (n, i, len(todo), time.time() - t0))
                    break
                log("part %d attempt %d: HTTP %d etag %s body %s" % (n, attempt, st, etag, body[:200]))
            except Exception as e:
                log("part %d attempt %d: %s" % (n, attempt, e))
            time.sleep(min(60, 2 ** min(attempt, 6)))
        else:
            log("part %d FAILED after 30 attempts; stopping" % n)
            sys.exit(2)
    os.remove(tmp)
    log("upload: done")


def cmd_complete():
    md5s = local_md5s()
    parts = list_parts()
    good, bad, missing, extra = check(parts, md5s)
    log("pre-complete: %d match, %d mismatch, %d missing, extra %s" % (len(good), len(bad), len(missing), extra))
    if bad or missing or extra or len(good) != NPARTS:
        log("not completing")
        sys.exit(3)
    xml = "<CompleteMultipartUpload>" + "".join(
        '<Part><PartNumber>%d</PartNumber><ETag>"%s"</ETag></Part>' % (n, md5s[n]) for n in range(1, NPARTS + 1)
    ) + "</CompleteMultipartUpload>"
    path = os.path.join(DIR, "complete.xml")
    open(path, "w").write(xml)
    sha = hashlib.sha256(xml.encode()).hexdigest()
    uid = urllib.parse.quote(UPLOAD_ID, safe="")
    expected = hashlib.md5(b"".join(bytes.fromhex(md5s[n]) for n in range(1, NPARTS + 1))).hexdigest() + "-%d" % NPARTS
    st, h, body = curl("POST", "uploadId=" + uid, path, sha, ["Content-Type: application/xml"], timeout=900)
    log("complete: HTTP %d body %s" % (st, body[:600]))
    log("expected multipart ETag %s" % expected)
    if st != 200 or "CompleteMultipartUploadResult" not in body:
        sys.exit(4)


if __name__ == "__main__":
    {"verify": cmd_verify, "upload": cmd_upload, "complete": cmd_complete}[sys.argv[1]]()
