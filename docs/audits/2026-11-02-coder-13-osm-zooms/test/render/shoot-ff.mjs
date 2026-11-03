// coder-13 Z2 test 5 (Willow, scratch): phone-sized renders, 412x800 at devicePixelRatio 2, of the same view in three
// styles: OSM's raster (256 px, as the app), Street v5 on the patched test archive, Street v4 on the control archive.
// Headless Firefox over WebDriver BiDi, adapted from ~/street-preview-scratch/render-ff.mjs (Hazel's): headless
// Chromium stops at Page.navigate on this Pi (Hazel's probe.log; the same here at 17:39-17:41).
//   node shoot-ff.mjs VIEWS.json      VIEWS: [[slug, lat, lon, [zooms]], ...]
import { spawn } from "node:child_process";
import fs from "node:fs";
const D = "/home/bwann83/scratch/coder13/molalla/render";
const PORT = 9223;
const STYLES = { osm: "osm-raster.json", v5: "v5-patched.json", v4: "v4-control.json" };
const views = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const shots = [];
for (const [slug, lat, lon, zooms] of views)
  for (const z of zooms) for (const s of Object.keys(STYLES)) shots.push([s, slug, lat, lon, z, `${D}/shots/${slug}-z${z}-${s}.png`]);
fs.mkdirSync(`${D}/ff-profile`, { recursive: true });
const ff = spawn("/usr/bin/firefox", ["--headless", "--no-remote", "--profile", `${D}/ff-profile`, `--remote-debugging-port=${PORT}`, "about:blank"],
  { stdio: ["ignore", "ignore", fs.openSync(`${D}/firefox.err`, "w")] });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
for (let i = 0; i < 60 && !ws; i++) {
  await sleep(1000);
  try {
    const sock = new WebSocket(`ws://127.0.0.1:${PORT}/session`);
    await new Promise((res, rej) => { sock.onopen = res; sock.onerror = rej; });
    ws = sock;
  } catch { /* not up yet */ }
}
if (!ws) { console.log("FAILED: no BiDi connection after 60 s"); ff.kill(); process.exit(1); }
let nextId = 1;
const pending = new Map(), listeners = new Set();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.type === "error" ? reject(new Error(`${msg.error}: ${msg.message}`)) : resolve(msg.result);
  } else for (const l of listeners) l(msg);
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (context, expression) => {
  const r = await send("script.evaluate", { expression, target: { context }, awaitPromise: true });
  if (r.type === "exception") throw new Error(`script: ${JSON.stringify(r.exceptionDetails).slice(0, 300)}`);
  return r.result.value;
};
await send("session.new", { capabilities: {} });
await send("session.subscribe", { events: ["network.responseCompleted", "log.entryAdded"] });
const { contexts } = await send("browsingContext.getTree", {});
const context = contexts[0].context;
await send("browsingContext.setViewport", { context, viewport: { width: 412, height: 800 }, devicePixelRatio: 2 });
let relief = 0;
async function shoot([s, slug, lat, lon, z, file]) {
  const net = { ok: 0, bad: 0 };
  const errors = [];
  const onMsg = (msg) => {
    if (msg.method === "network.responseCompleted") {
      const u = msg.params.request.url;
      if (u.includes("/relief")) relief++;
      if (/\/\d+\/\d+\/\d+(\.png|\.mvt|\.pbf)?$/.test(u)) msg.params.response.status === 200 ? net.ok++ : net.bad++;
    }
    if (msg.method === "log.entryAdded" && msg.params.level === "error") errors.push(String(msg.params.text).slice(0, 200));
  };
  listeners.add(onMsg);
  try {
    await send("browsingContext.navigate", { context, url: "about:blank", wait: "complete" });
    await send("browsingContext.navigate", { context, url: `http://localhost:8766/page.html?style=${STYLES[s]}#${z}/${lat}/${lon}`, wait: "complete" });
    const t0 = Date.now();
    let idle = false;
    while (Date.now() - t0 < 120000) {
      await sleep(500);
      if (await evaluate(context, "window.idle === true")) { idle = true; break; }
    }
    if (!idle) throw new Error("not idle after 120 s");
    await sleep(500);
    const zoom = await evaluate(context, "map.getZoom()");
    const { data } = await send("browsingContext.captureScreenshot", { context, origin: "viewport" });
    fs.writeFileSync(file, Buffer.from(data, "base64"));
    console.log(JSON.stringify({ file: file.replace(D + "/", ""), style: s, z, zoom, net, errors }));
    return true;
  } catch (e) {
    console.log(JSON.stringify({ file: file.replace(D + "/", ""), FAILED: String(e.message), net, errors }));
    return false;
  } finally {
    listeners.delete(onMsg);
  }
}
let ok = 0;
try {
  for (const sh of shots) if (await shoot(sh)) ok++;
} finally {
  console.log(`written ${ok} of ${shots.length}; requests to /relief: ${relief}`);
  await send("browser.close").catch(() => {});
  await sleep(3000);
  ff.kill();
  process.exit(0);
}
