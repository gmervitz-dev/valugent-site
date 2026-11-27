(() => {
  // An original brain, seen first from the side. Its outline is drawn once in the side view (front lobe, crown,
  // back, cerebellum tucked under the back, stem, temporal lobe), and the 3D form is that outline narrowing toward
  // each side, so it is one continuous shape. Folds are traced on its surface; nearby points are joined, and signals
  // travel along the joins. A touch or a mouse over it lights the connections near that spot.
  const canvas = document.getElementById("brain");
  const hero = canvas && canvas.closest(".hero");
  if (!window.THREE || !canvas) return;
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: "low-power" });
  } catch (e) { return; }
  renderer.setClearColor(0x05070b, 1);

  let seed = 20261127;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const TAU = Math.PI * 2;

  // ---- the side outline: radius from the centre by angle (0 = the front, a quarter turn = the top)
  const OUT = [  // [degrees, radius, half-width]
    [0, 0.98, 0.7], [25, 1.0, 0.72], [55, 0.93, 0.74], [90, 0.84, 0.75], [120, 0.86, 0.75], [150, 0.95, 0.73],
    [178, 1.04, 0.66], [198, 0.97, 0.6], [214, 0.8, 0.52], [232, 0.9, 0.5], [250, 0.86, 0.42], [262, 0.82, 0.24],
    [272, 1.06, 0.16], [281, 0.8, 0.2], [292, 0.58, 0.45], [312, 0.66, 0.62], [334, 0.74, 0.62], [347, 0.68, 0.55],
    [356, 0.86, 0.64]];
  function along(deg, col) {           // a smooth (Catmull-Rom) reading of the table, wrapping round
    const n = OUT.length;
    let i = 0;
    while (i < n - 1 && OUT[i + 1][0] <= deg) i++;
    const p = k => OUT[(k + n) % n], a0 = p(i - 1), a1 = p(i), a2 = p(i + 1), a3 = p(i + 2);
    const d1 = a1[0], d2 = i + 1 >= n ? a2[0] + 360 : a2[0];
    const t = (deg - d1) / (d2 - d1);
    const y0 = a0[col], y1 = a1[col], y2 = a2[col], y3 = a3[col];
    return 0.5 * (2 * y1 + (-y0 + y2) * t + (2 * y0 - 5 * y1 + 4 * y2 - y3) * t * t + (-y0 + 3 * y1 - 3 * y2 + y3) * t * t * t);
  }
  const R = th => along(((th * 180 / Math.PI) % 360 + 360) % 360, 1);
  const W = th => along(((th * 180 / Math.PI) % 360 + 360) % 360, 2);
  const LEN = 1.05;                     // stretch front to back
  // a point of the surface from the side-view angle th, how far out r (0 centre, 1 rim) and which side (+1, -1)
  function surface(th, r, side, inset = 1) {
    const rr = R(th) * r;
    const z = Math.cos(th) * rr * LEN, y = Math.sin(th) * rr;
    const x = side * W(th) * Math.sqrt(Math.max(0, 1 - r * r)) * inset;
    return [x, y, z];
  }

  // ---- the points the signals run between
  const pts = [];
  for (let i = 0; i < 2100; i++) {
    const th = rnd() * TAU;
    const r = Math.min(0.999, Math.sqrt(rnd()) * (1 + 0.025 * Math.sin(th * 23)));
    const p = surface(th, r, rnd() < 0.5 ? 1 : -1, rnd() < 0.86 ? 1 : 0.2 + rnd() * 0.7);
    pts.push(p);
  }
  const N = pts.length;

  // ---- the folds: the two great grooves, winding folds over the cerebrum, fine bands on the cerebellum
  const folds = [];
  function trace(path, side) {         // path: [th, r] pairs in the side view
    for (let k = 0; k < path.length - 1; k++)
      folds.push(surface(path[k][0], path[k][1], side, 1.004), surface(path[k + 1][0], path[k + 1][1], side, 1.004));
  }
  const rad = d => d * Math.PI / 180;
  const cerebrum = th => { const d = ((th * 180 / Math.PI) % 360 + 360) % 360; return d < 200 || d > 300; };
  function line(a, b, steps, wob) {
    const out = [];
    for (let s = 0; s <= steps; s++) {
      const t = s / steps;
      out.push([a[0] + (b[0] - a[0]) * t + wob * Math.sin(t * 9 + a[0] * 3), a[1] + (b[1] - a[1]) * t + wob * 0.6 * Math.sin(t * 13)]);
    }
    return out;
  }
  for (const side of [1, -1]) {
    trace(line([rad(345), 0.95], [rad(200), 0.42], 28, 0.03), side);            // the lateral groove
    trace(line([rad(82), 0.99], [rad(10), 0.42], 24, 0.03), side);              // the central groove
    for (let n = 0; n < 46; n++) {                                              // winding folds
      let th = rnd() * TAU, r = 0.25 + rnd() * 0.72;
      if (!cerebrum(th)) continue;
      const path = [[th, r]];
      let heading = rnd() * TAU;
      for (let s = 0; s < 16; s++) {
        heading += (rnd() - 0.5) * 1.3;
        th += Math.cos(heading) * 0.045; r += Math.sin(heading) * 0.03;
        r = Math.min(0.98, Math.max(0.15, r));
        if (!cerebrum(th)) break;
        path.push([th, r]);
      }
      if (path.length > 4) trace(path, side);
    }
    for (let b = 0; b < 7; b++) {                                               // the cerebellum's bands
      const r = 0.62 + b * 0.055, path = [];
      for (let d = 205; d <= 258; d += 3) path.push([rad(d), r + 0.012 * Math.sin(d * 0.7)]);
      trace(path, side);
    }
  }

  // ---- the connections: each point to its nearest neighbours, plus a few longer tracts through the inside
  const edges = [], seen = new Set();
  const dist = (i, j) => Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1], pts[i][2] - pts[j][2]);
  function join(i, j) {
    const k = i < j ? i + "," + j : j + "," + i;
    if (i === j || seen.has(k)) return;
    seen.add(k);
    edges.push({ a: i, b: j, len: dist(i, j) });
  }
  for (let i = 0; i < N; i++) {
    const near = [];
    for (let j = 0; j < N; j++) if (j !== i) { const d = dist(i, j); if (d < 0.16) near.push([d, j]); }
    near.sort((p, q) => p[0] - q[0]);
    for (const [, j] of near.slice(0, 3)) join(i, j);
  }
  for (let n = 0; n < 50; n++) {
    const i = Math.floor(rnd() * N), j = Math.floor(rnd() * N), d = dist(i, j);
    if (d > 0.3 && d < 0.75) join(i, j);
  }
  const E = edges.length;
  const adj = Array.from({ length: N }, () => []);
  edges.forEach((e, k) => { adj[e.a].push(k); adj[e.b].push(k); });

  // ---- the scene
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50);
  camera.position.set(0, 0.05, 4.6);
  const brain = new THREE.Group();
  const SIDE = -Math.PI / 2;           // the left side faces the viewer, the front to the right
  brain.rotation.set(0.1, SIDE, 0);
  scene.add(brain);

  const dot = document.createElement("canvas");
  dot.width = dot.height = 64;
  const g = dot.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.25, "rgba(255,255,255,0.55)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  const sprite = new THREE.CanvasTexture(dot);

  const BASE = [0.5, 0.58, 0.72], FLASH = [1.0, 0.97, 0.9], LINE = [0.07, 0.09, 0.125], LIT = [0.6, 0.75, 1.0];
  const add = { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending };

  const foldGeo = new THREE.BufferGeometry();
  foldGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(folds.flat()), 3));
  brain.add(new THREE.LineSegments(foldGeo, new THREE.LineBasicMaterial({ color: 0x6f86aa, opacity: 0.7, ...add })));

  const nodePos = new Float32Array(N * 3), nodeCol = new Float32Array(N * 3);
  pts.forEach((p, i) => nodePos.set(p, i * 3));
  const nodeGeo = new THREE.BufferGeometry();
  nodeGeo.setAttribute("position", new THREE.BufferAttribute(nodePos, 3));
  nodeGeo.setAttribute("color", new THREE.BufferAttribute(nodeCol, 3));
  brain.add(new THREE.Points(nodeGeo, new THREE.PointsMaterial({ size: 0.04, map: sprite, vertexColors: true, ...add })));

  const linePos = new Float32Array(E * 6), lineCol = new Float32Array(E * 6);
  edges.forEach((e, k) => { linePos.set(pts[e.a], k * 6); linePos.set(pts[e.b], k * 6 + 3); });
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute("position", new THREE.BufferAttribute(linePos, 3));
  lineGeo.setAttribute("color", new THREE.BufferAttribute(lineCol, 3));
  brain.add(new THREE.LineSegments(lineGeo, new THREE.LineBasicMaterial({ vertexColors: true, ...add })));

  const MAXP = 160;
  const pulsePos = new Float32Array(MAXP * 3);
  const pulseGeo = new THREE.BufferGeometry();
  pulseGeo.setAttribute("position", new THREE.BufferAttribute(pulsePos, 3));
  pulseGeo.setDrawRange(0, 0);
  brain.add(new THREE.Points(pulseGeo, new THREE.PointsMaterial({ size: 0.07, map: sprite, color: 0xe8f0ff, ...add })));

  // ---- the activity
  const flash = new Float32Array(N), glow = new Float32Array(E);
  const pulses = [];
  let clock = 0, nextSpark = 0;
  function fire(from, avoid, speed = 1) {
    const out = adj[from].filter(k => k !== avoid);
    if (!out.length || pulses.length >= MAXP) return;
    const k = out[Math.floor(rnd() * out.length)], e = edges[k];
    pulses.push({ k, from, to: e.a === from ? e.b : e.a, t: 0, speed: (0.55 + rnd() * 0.35) * speed });
  }
  function step(dt) {
    clock += dt;
    if (clock >= nextSpark) {
      const i = Math.floor(rnd() * N);
      flash[i] = 1; fire(i, -1);
      nextSpark = clock + 0.15 + rnd() * 0.3;
    }
    for (let n = pulses.length - 1; n >= 0; n--) {
      const p = pulses[n];
      p.t += dt * p.speed / Math.max(edges[p.k].len, 0.02);
      glow[p.k] = 1;
      if (p.t >= 1) {
        pulses.splice(n, 1);
        flash[p.to] = 1;
        if (rnd() < 0.62) fire(p.to, p.k, p.speed > 1.2 ? 1.3 : 1);
        if (rnd() < 0.12) fire(p.to, p.k);
      }
    }
    const fd = Math.exp(-dt * 2.2), gd = Math.exp(-dt * 1.4);
    for (let i = 0; i < N; i++) {
      flash[i] *= fd;
      const f = flash[i];
      nodeCol[i * 3] = BASE[0] + (FLASH[0] - BASE[0]) * f;
      nodeCol[i * 3 + 1] = BASE[1] + (FLASH[1] - BASE[1]) * f;
      nodeCol[i * 3 + 2] = BASE[2] + (FLASH[2] - BASE[2]) * f;
    }
    for (let k = 0; k < E; k++) {
      glow[k] *= gd;
      const q = glow[k];
      const r = LINE[0] + LIT[0] * q, gg = LINE[1] + LIT[1] * q, b = LINE[2] + LIT[2] * q;
      lineCol[k * 6] = lineCol[k * 6 + 3] = r;
      lineCol[k * 6 + 1] = lineCol[k * 6 + 4] = gg;
      lineCol[k * 6 + 2] = lineCol[k * 6 + 5] = b;
    }
    pulses.forEach((p, n) => {
      const a = pts[p.from], b = pts[p.to];
      pulsePos[n * 3] = a[0] + (b[0] - a[0]) * p.t;
      pulsePos[n * 3 + 1] = a[1] + (b[1] - a[1]) * p.t;
      pulsePos[n * 3 + 2] = a[2] + (b[2] - a[2]) * p.t;
    });
    pulseGeo.setDrawRange(0, pulses.length);
    nodeGeo.attributes.color.needsUpdate = true;
    lineGeo.attributes.color.needsUpdate = true;
    pulseGeo.attributes.position.needsUpdate = true;
  }

  // ---- touch: the points near the finger or the pointer light up, and send signals outward
  const v = new THREE.Vector3();
  let lastTouch = 0;
  let hover = null;                    // where the pointer rests over the brain: a soft glow stays with it
  function touch(ev) {
    if (ev.pointerType === "mouse") { const bx = canvas.getBoundingClientRect(); hover = [ev.clientX - bx.left, ev.clientY - bx.top]; }
    const now = performance.now();
    if (now - lastTouch < 60) return;
    lastTouch = now;
    const box = canvas.getBoundingClientRect();
    const px = ev.clientX - box.left, py = ev.clientY - box.top;
    brain.updateMatrixWorld();
    const reach = Math.max(36, box.width * 0.035);
    let lit = 0;
    for (let i = 0; i < N && lit < 14; i++) {
      v.fromArray(pts[i]).applyMatrix4(brain.matrixWorld).project(camera);
      const sx = (v.x + 1) / 2 * box.width, sy = (1 - v.y) / 2 * box.height;
      if (Math.hypot(sx - px, sy - py) < reach) {
        flash[i] = 1; fire(i, -1, 1.6);
        lit++;
      }
    }
    if (still && lit) { step(1 / 60); render(); }
  }
  // ---- click (or press) and hold to turn it by hand; it carries on turning by itself shortly after
  let yaw = 0, pitch = 0, spin = 0, drag = null, idle = 10;
  function grab(ev) {
    if (ev.button !== undefined && ev.button > 0) return;
    if (ev.target.closest && ev.target.closest("a, button")) return;   // links in the hero stay clickable
    drag = { x: ev.clientX, y: ev.clientY, id: ev.pointerId, t: performance.now() };
    hero.classList.add("dragging");
    try { hero.setPointerCapture(ev.pointerId); } catch (e) {}
  }
  function move(ev) {
    if (!drag || ev.pointerId !== drag.id) return touch(ev);
    const now = performance.now();
    const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
    const k = 4.2 / Math.max(canvas.clientWidth, 1);
    yaw += dx * k;
    pitch = Math.max(-0.9, Math.min(0.9, pitch + dy * k));
    spin = dx * k / Math.max((now - drag.t) / 1000, 0.008);
    drag.x = ev.clientX; drag.y = ev.clientY; drag.t = now;
    idle = 0;
    touch(ev);
    if (still) { place(); render(); }
  }
  function release(ev) {
    if (!drag || ev.pointerId !== drag.id) return;
    if (performance.now() - drag.t > 80) spin = 0;   // held still before letting go: no throw
    drag = null;
    hero.classList.remove("dragging");
  }
  if (hero) {
    hero.addEventListener("pointerdown", ev => { touch(ev); grab(ev); });
    hero.addEventListener("pointermove", move);
    hero.addEventListener("pointerup", release);
    hero.addEventListener("pointercancel", release);
    hero.addEventListener("pointerleave", () => { hover = null; });
  }
  function halo() {                    // the points near a resting pointer glow, brightest at its centre
    if (!hover) return;
    const w = canvas.clientWidth, h = canvas.clientHeight, reach = Math.max(80, w * 0.09);
    brain.updateMatrixWorld();
    for (let i = 0; i < N; i++) {
      v.fromArray(pts[i]).applyMatrix4(brain.matrixWorld).project(camera);
      const d = Math.hypot((v.x + 1) / 2 * w - hover[0], (1 - v.y) / 2 * h - hover[1]);
      if (d < reach) flash[i] = Math.max(flash[i], 0.6 * (1 - d / reach));
    }
  }
  let auto = 0;
  function place() {
    const a = auto * 0.16;
    brain.rotation.y = SIDE + a + 0.35 * Math.sin(2 * a) + yaw;
    brain.rotation.x = 0.1 + 0.12 * Math.sin(auto * 0.21) + pitch;
  }

  // ---- framing: to the right of the headline on wide screens, above it on narrow ones
  function size() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    const wide = w / h > 1.05;
    brain.scale.setScalar(wide ? 1.12 : Math.max(0.6, (w / h) * 1.1));
    camera.setViewOffset(w, h, wide ? -w * 0.2 : 0, wide ? h * 0.12 : h * 0.18, w, h);
    camera.updateProjectionMatrix();
  }
  const render = () => renderer.render(scene, camera);
  size();
  window.addEventListener("resize", () => { size(); if (still) render(); });

  if (still) {                         // one settled side view, mid-thought; a touch still lights it
    for (let i = 0; i < 240; i++) step(1 / 60);
    place();
    render();
    return;
  }
  let last = performance.now(), turn = 0;
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    turn += dt;
    if (!drag) {
      yaw += spin * dt;                              // a throw carries on and slows
      spin *= Math.exp(-dt * 2.5);
      idle += dt;
      if (idle > 2.5) auto += dt * Math.min(1, (idle - 2.5) / 2);   // then its own slow turn eases back in
    }
    // a slow full turn, lingering on the sides, with a gentle rise and fall
    place();
    brain.position.y = 0.04 * Math.sin(turn * 0.33);
    halo();
    step(dt);
    render();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
