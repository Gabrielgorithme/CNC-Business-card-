/* Three behaviours, nothing else:
   1. the name engraves once on load, stroke by stroke, with the tool point following (the page's one orchestrated moment);
   2. the card section replays the real engraving program when it scrolls into view, and on "Replay";
   3. the CAD / prototype slider. */
(function () {
  "use strict";
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";

  /* 1. engrave the name */
  (function () {
  var name = document.querySelector(".name svg");
  if (name && !reduce && name.getBoundingClientRect().top < innerHeight) {
    var paths = Array.prototype.slice.call(name.querySelectorAll("path"));
    var lens = paths.map(function (p) { return p.getTotalLength(); });
    var total = lens.reduce(function (a, b) { return a + b; }, 0);
    var sw = parseFloat(name.querySelector("g").getAttribute("stroke-width"));
    paths.forEach(function (p, i) { p.style.strokeDasharray = lens[i] + " " + (lens[i] + 1); p.style.strokeDashoffset = lens[i]; });
    var dot = document.createElementNS(NS, "circle"); dot.setAttribute("r", (sw * 1.2).toFixed(2)); dot.setAttribute("class", "tool"); name.appendChild(dot);
    var DUR = 2100, RAPID = 22, cut = DUR - RAPID * paths.length, t0 = null;
    var frame = function (now) {
      if (t0 === null) t0 = now + 120;
      var t = Math.max(0, now - t0), acc = 0, busy = false;
      for (var i = 0; i < paths.length; i++) {
        var st = acc + RAPID, et = st + cut * lens[i] / total;
        if (t >= et) paths[i].style.strokeDashoffset = 0;
        else if (t > st) {
          var f = (t - st) / (et - st), pt = paths[i].getPointAtLength(lens[i] * f);
          paths[i].style.strokeDashoffset = lens[i] * (1 - f); dot.setAttribute("cx", pt.x); dot.setAttribute("cy", pt.y); busy = true;
        } else busy = true;
        acc = et;
      }
      if (busy) requestAnimationFrame(frame);
      else { dot.style.transition = "opacity .5s"; dot.style.opacity = 0; paths.forEach(function (p) { p.style.strokeDasharray = ""; p.style.strokeDashoffset = ""; }); }
    };
    requestAnimationFrame(frame);
  }
  })();

  /* 3. slider */
  Array.prototype.forEach.call(document.querySelectorAll(".compare input"), function (r) {
    var set = function () { r.parentNode.style.setProperty("--pos", r.value + "%"); };
    r.addEventListener("input", set); set();
  });

  /* 2. toolpath replay */
  var cv = document.getElementById("toolpath");
  if (!cv) return;
  var plate = cv.parentNode, ctx = cv.getContext("2d"), tool = document.createElement("canvas");
  tool.setAttribute("aria-hidden", "true"); plate.appendChild(tool); var tc = tool.getContext("2d");
  var xy = document.getElementById("dro-xy"), btn = document.getElementById("replay");
  var W = 85.6, H = 53.98, R = 3.18, polys = null, total = 0, s, pw, ph, dpr, run = 0;
  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 2.5); pw = plate.clientWidth; ph = plate.clientHeight;
    cv.width = tool.width = Math.round(pw * dpr); cv.height = tool.height = Math.round(ph * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); s = pw / W;
  }
  function blank() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, pw, ph);
    var g = ctx.createLinearGradient(0, 0, pw, ph); g.addColorStop(0, "#e2e5e8"); g.addColorStop(.55, "#cfd3d7"); g.addColorStop(1, "#dadde0");
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(.5, .5, pw - 1, ph - 1, R * s); else ctx.rect(.5, .5, pw - 1, ph - 1);
    ctx.fillStyle = g; ctx.fill(); ctx.strokeStyle = "rgba(255,255,255,.7)"; ctx.lineWidth = 1.5; ctx.stroke();
  }
  // Model frame: origin at the card centre, Y up seen from the recto. Seen from the verso, X is mirrored.
  function X(x) { return pw / 2 - x * s; } function Y(y) { return ph / 2 + y * s; }
  function style(p) { ctx.strokeStyle = p.op === "09" ? "rgba(63,69,76,.45)" : "#2b3035"; ctx.lineWidth = Math.max(.75, p.w * s); ctx.lineCap = "round"; ctx.lineJoin = "round"; }
  function drawAll() {
    blank(); polys.forEach(function (p) { style(p); ctx.beginPath(); p.pts.forEach(function (q, i) { i ? ctx.lineTo(X(q[0]), Y(q[1])) : ctx.moveTo(X(q[0]), Y(q[1])); }); ctx.stroke(); });
  }
  function readout(text) { xy.textContent = text; }
  function play() {
    var my = ++run; size(); blank();
    if (reduce) { drawAll(); readout("M30"); return; }
    var DUR = 6500, pi = 0, pj = 1, done = 0, t0 = null;
    function frame(now) {
      if (my !== run) return;
      if (t0 === null) t0 = now;
      var target = Math.min(total, total * Math.pow((now - t0) / DUR, 1.15));
      while (pi < polys.length && done < target) {
        var p = polys[pi]; style(p); ctx.beginPath(); ctx.moveTo(X(p.pts[pj - 1][0]), Y(p.pts[pj - 1][1]));
        while (pj < p.pts.length && done < target) {
          done += Math.hypot(p.pts[pj][0] - p.pts[pj - 1][0], p.pts[pj][1] - p.pts[pj - 1][1]);
          ctx.lineTo(X(p.pts[pj][0]), Y(p.pts[pj][1])); pj++;
        }
        ctx.stroke(); if (pj >= p.pts.length) { pi++; pj = 1; }
      }
      if (pi < polys.length) {
        var q = polys[pi].pts[pj - 1];
        readout("X" + q[0].toFixed(2) + "  Y" + q[1].toFixed(2));
        // the tool point lives on its own layer so the cut stays clean
        tc.setTransform(dpr, 0, 0, dpr, 0, 0); tc.clearRect(0, 0, pw, ph);
        tc.fillStyle = "#0f1113"; tc.beginPath(); tc.arc(X(q[0]), Y(q[1]), 3, 0, 7); tc.fill();
        tc.strokeStyle = "rgba(255,255,255,.9)"; tc.lineWidth = 1; tc.beginPath(); tc.arc(X(q[0]), Y(q[1]), 6, 0, 7); tc.stroke();
        requestAnimationFrame(frame);
      } else { tc.clearRect(0, 0, pw, ph); drawAll(); readout("M30"); }
    }
    requestAnimationFrame(frame);
  }
  function load() {
    if (polys) return Promise.resolve();
    return fetch(cv.getAttribute("data-src")).then(function (r) { return r.json(); }).then(function (tp) {
      polys = tp.map(function (p) {
        var pts = [], x = 0, y = 0;
        for (var i = 0; i < p.d.length; i += 2) { x += p.d[i]; y += p.d[i + 1]; pts.push([x / 100, y / 100]); }
        var depth = Math.max(0.04, -p.z - 0.15);
        var o = { pts: pts, op: p.o, w: p.o === "08" ? 0.28 : p.o === "09" ? 0.2 : 2 * depth, len: 0 };
        for (var j = 1; j < pts.length; j++) o.len += Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]);
        total += o.len; return o;
      });
    });
  }
  size(); blank();
  btn.addEventListener("click", function () { load().then(play); });
  var started = false;
  var start = function () { if (!started) { started = true; load().then(play); } };
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { start(); io.disconnect(); } }); }, { threshold: .45 });
    io.observe(plate);
  } else start();
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { if (polys) { size(); drawAll(); } }, 200); });
})();
