/* bds3d.js — bộ chạy khung cho skill bds_model_3d.
 * Nhận window.KH (kế hoạch đã giải giờ bởi scripts/ke_hoach.py), vẽ đúng khung ở giây t qua window.__seek(t).
 * Mọi chuyển động là hàm thuần của t (tua tới đâu cũng ra đúng một hình) — không dùng requestAnimationFrame / CSS animation.
 */
(() => {
'use strict';
const KH = window.KH;
const FPS = KH.fps || 30;
const stage = document.getElementById('stage');

/* ---------------- tiện ích ---------------- */
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const E = {
  lin: u => u,
  outQ: u => 1 - (1 - u) * (1 - u),
  outC: u => 1 - Math.pow(1 - u, 3),
  inOutC: u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2,
  inOutS: u => -(Math.cos(Math.PI * u) - 1) / 2,
  outB: u => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); },
  drop: u => { // rơi + nảy nhẹ
    if (u < .62) { const v = u / .62; return v * v; }
    const v = (u - .62) / .38; return 1 - .14 * Math.sin(Math.PI * v) * (1 - v * .4);
  },
};
const P = (t, a, d, e = E.outC) => e(clamp((t - a) / d));
const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || stage).appendChild(e); return e; };
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const dam = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
const setSrc = (img, url) => { if (url && img.dataset.u !== url) { img.dataset.u = url; img.src = url; } };
const pad5 = i => String(i).padStart(5, '0');
function rng(seed) { let s = 0; for (const c of String(seed)) s = (s * 31 + c.charCodeAt(0)) >>> 0; s = s || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

/* ---------------- icon ---------------- */
const IC = {
  google_maps: `<svg viewBox="0 0 64 64"><defs><clipPath id="gmc"><path d="M32 3C20.4 3 11 12.3 11 23.8c0 15.6 21 37.2 21 37.2s21-21.6 21-37.2C53 12.3 43.6 3 32 3z"/></clipPath></defs><g clip-path="url(#gmc)"><rect width="64" height="64" fill="#4285F4"/><path d="M0 0h40L18 40 0 50z" fill="#EA4335"/><path d="M0 38l22-12 8 38H0z" fill="#FBBC04"/><path d="M18 64l20-36 26 6v30z" fill="#34A853"/><path d="M40 0h24v30L34 26z" fill="#4285F4"/></g><circle cx="32" cy="23.5" r="7.8" fill="#fff"/></svg>`,
  claude: (() => { let p = ''; const n = 12; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2 + .13, L = [27, 22, 29, 24, 28, 21, 27, 23, 29, 22, 26, 24][i]; p += `<line x1="${32 + 5 * Math.cos(a)}" y1="${32 + 5 * Math.sin(a)}" x2="${32 + L * Math.cos(a)}" y2="${32 + L * Math.sin(a)}"/>`; } return `<svg viewBox="0 0 64 64"><g stroke="#D97757" stroke-width="6.2" stroke-linecap="round">${p}</g></svg>`; })(),
  video: `<svg viewBox="0 0 64 64"><rect x="6" y="11" width="52" height="42" rx="10" fill="none" stroke="#fff" stroke-width="4.5"/><path d="M27 23v18l15-9z" fill="#fff"/></svg>`,
  ae: `<svg viewBox="0 0 64 64"><rect x="2" y="2" width="60" height="60" rx="13" fill="#00005B" stroke="#9999FF" stroke-width="3"/><text x="32" y="43" text-anchor="middle" font-family="BVP" font-weight="700" font-size="28" fill="#9999FF">Ae</text></svg>`,
  dong_ho: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round"><circle cx="32" cy="32" r="25"/><path d="M32 17v16l10 7"/></svg>`,
  tai_lieu: `<svg viewBox="0 0 48 62"><path d="M4 0h28l16 16v42a4 4 0 0 1-4 4H4a4 4 0 0 1-4-4V4a4 4 0 0 1 4-4z" fill="#4285F4"/><path d="M32 0v12a4 4 0 0 0 4 4h12z" fill="#A1C2FA"/><g fill="#fff"><rect x="10" y="28" width="28" height="4" rx="1"/><rect x="10" y="36" width="28" height="4" rx="1"/><rect x="10" y="44" width="20" height="4" rx="1"/></g></svg>`,
  ban_do: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.2" stroke-linejoin="round"><path d="M6 14l16-6 20 8 16-6v40l-16 6-20-8-16 6z"/><path d="M22 8v40M42 16v40"/></svg>`,
  nha: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"><path d="M8 30L32 9l24 21"/><path d="M15 25v30h34V25"/><path d="M27 55V39h10v16"/></svg>`,
  toa_nha: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.2" stroke-linejoin="round"><rect x="12" y="6" width="26" height="52"/><path d="M38 22h14v36H38"/><path d="M19 15h4M27 15h4M19 24h4M27 24h4M19 33h4M27 33h4M19 42h4M27 42h4"/></svg>`,
  tien: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round"><circle cx="32" cy="32" r="25"/><path d="M40 22c-2-3-5-4-8-4-5 0-8 3-8 6.5 0 9 16 5 16 14 0 4-4 7-8.5 7-3.5 0-6.5-1.5-8.5-4.5M32 13v5M32 46v5"/></svg>`,
  dien_thoai: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5"><rect x="17" y="4" width="30" height="56" rx="7"/><path d="M28 51h8" stroke-linecap="round"/></svg>`,
  camera: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"><path d="M6 20h12l5-7h18l5 7h12v32H6z"/><circle cx="32" cy="35" r="10"/></svg>`,
  check: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="25"/><path d="M20 33l8 8 16-17"/></svg>`,
  sao: `<svg viewBox="0 0 64 64"><path d="M32 5l8 17 18.5 2.3-13.6 12.8 3.5 18.4L32 46.6 15.6 55.5l3.5-18.4L5.5 24.3 24 22z" fill="#FDF02A"/></svg>`,
  chat: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"><path d="M8 12h48v32H28l-12 10V44H8z"/></svg>`,
  ai: `<svg viewBox="0 0 64 64" fill="#fff"><path d="M28 6l5 15 15 5-15 5-5 15-5-15-15-5 15-5z"/><path d="M48 36l2.5 7.5L58 46l-7.5 2.5L48 56l-2.5-7.5L38 46l7.5-2.5z"/></svg>`,
  tim: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"><circle cx="28" cy="28" r="17"/><path d="M41 41l15 15"/></svg>`,
  nguoi: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5"><circle cx="32" cy="22" r="11"/><path d="M11 57c2-12 11-18 21-18s19 6 21 18" stroke-linecap="round"/></svg>`,
  vi_tri: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5"><path d="M32 58S12 38 12 24a20 20 0 0 1 40 0c0 14-20 34-20 34z"/><circle cx="32" cy="24" r="7"/></svg>`,
  may_tinh: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"><rect x="6" y="10" width="52" height="34" rx="4"/><path d="M22 54h20M32 44v10"/></svg>`,
  link: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"><path d="M27 37l10-10"/><path d="M22 30l-6 6a9 9 0 0 0 12.7 12.7l6-6M42 34l6-6A9 9 0 0 0 35.3 15.3l-6 6"/></svg>`,
  file: `<svg viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"><path d="M14 6h24l12 12v40H14z"/><path d="M38 6v12h12"/></svg>`,
};
let _uid = 0;
const uniq = svg => { const n = ++_uid; return svg.replace(/id="(\w+)"/g, `id="$1_${n}"`).replace(/url\(#(\w+)\)/g, `url(#$1_${n})`); };
function icon(name) {
  name = String(name || '');
  if (name.startsWith('chu:')) { // chu:Pr:#2D0C4E:#E68CFF  — ô vuông bo có 1–3 chữ
    const [, t, bg = '#1f2937', fg = '#fff'] = name.split(':');
    return `<svg viewBox="0 0 64 64"><rect x="2" y="2" width="60" height="60" rx="13" fill="${bg}" stroke="${fg}" stroke-opacity=".55" stroke-width="3"/><text x="32" y="${t.length > 2 ? 41 : 43}" text-anchor="middle" font-family="BVP" font-weight="800" font-size="${t.length > 2 ? 21 : 28}" fill="${fg}">${esc(t)}</text></svg>`;
  }
  if (name.startsWith('anh:')) return `<img src="${esc(name.slice(4))}">`;
  return uniq(IC[name] || IC.check);
}

/* ---------------- footage ---------------- */
const ST = {
  card: { cx: 550, cy: 1158, w: 712, h: 1266, rz: -3.6, rx: 3, ry: -2, r: 38, blur: 0, dim: 0, op: 1, s: 1 },
  full: { cx: 540, cy: 960, w: 1080, h: 1920, rz: 0, rx: 0, ry: 0, r: 0, blur: 0, dim: 0, op: 1, s: 1 },
  blur: { cx: 540, cy: 960, w: 1080, h: 1920, rz: 0, rx: 0, ry: 0, r: 0, blur: 30, dim: .58, op: 1, s: 1.07 },
  uibox: { cx: 540, cy: 1130, w: 880, h: 1400, rz: 0, rx: 0, ry: 0, r: 52, blur: 0, dim: 0, op: 1, s: 1 },
};
const mixS = (A, B, u) => { const o = {}; for (const k in A) o[k] = A[k] + (B[k] - A[k]) * u; return o; };
const SHOT = Object.fromEntries((KH.shots || []).map(s => [s.id, s]));

const nen = mk('div'); nen.id = 'nen';
const pFoot = mk('div', 'persp');
const FL = [0, 1].map(() => { const d = mk('div', 'foot', pFoot); const im = mk('img', '', d); const v = mk('div', 'vien', d); d.style.opacity = 0; return { d, im, v }; });
const toiTren = mk('div'); toiTren.id = 'toi_tren';

function sceneAt(t) {
  const sc = KH.scenes; for (let i = 0; i < sc.length; i++) if (t < sc[i].den || i === sc.length - 1) return i; return sc.length - 1;
}
function footStates(t) {
  const sc = KH.scenes, i = sceneAt(t), cur = sc[i], prev = sc[i - 1], u = t - cur.tu, out = [];
  if (prev && prev.mode !== 'none' && (cur.mode === 'none' || prev.shot !== cur.shot) && u < .32) {
    const S = { ...ST[prev.mode] }, k = E.outQ(clamp(u / .28)); S.op = 1 - k; S.blur += 10 * k;
    out.push({ shot: prev.shot, S, z: 1 });
  }
  if (cur.mode !== 'none') {
    let S;
    const same = prev && prev.mode !== 'none' && prev.shot === cur.shot;
    if (same && prev.mode !== cur.mode) {
      const pair = prev.mode + '>' + cur.mode;
      const d = { 'card>full': .5, 'full>blur': .7, 'blur>full': .5, 'full>card': .55, 'card>blur': .6, 'blur>card': .55 }[pair] || .5;
      const e = { 'full>blur': E.inOutS, 'card>full': E.outC }[pair] || E.inOutC;
      S = mixS(ST[prev.mode], ST[cur.mode], e(clamp(u / d)));
    } else if (same) {
      S = { ...ST[cur.mode] };
    } else if (cur.mode === 'card') {
      const k = E.outC(clamp(u / .6)); S = { ...ST.card }; S.op = k; S.s = .94 + .06 * k; S.blur = 14 * (1 - k); S.dim = .5 * (1 - k);
    } else if (cur.mode === 'full' && prev && prev.loai === 'giao_dien' && cur.vao !== 'hoa_tan') {
      if (u < .22) { S = { ...ST.uibox }; S.op = E.outQ(u / .22); }
      else S = mixS(ST.uibox, ST.full, E.inOutC(clamp((u - .22) / .55)));
    } else {
      const k = E.outQ(clamp(u / .32)); S = { ...ST[cur.mode] }; S.op = k; S.dim = Math.max(S.dim, .45 * (1 - k));
    }
    out.push({ shot: cur.shot, S, z: 2 });
  }
  for (const o of out) { // trôi nhẹ khi đang là thẻ: xoay dần −3,6° → −1,4° suốt hook + lắc rất nhẹ
    const c = clamp(o.S.r / 38) * (o.S.w < 1000 ? 1 : 0), t0 = (SHOT[o.shot] || {}).t0 || 0;
    o.S.rz += c * (2.2 * E.inOutS(clamp((t - t0) / 6)) + .45 * Math.sin(t * 2 * Math.PI / 6.5));
    o.S.rx += c * .6 * Math.sin(t * 2 * Math.PI / 8 + 1);
    o.S.cy += c * 7 * Math.sin(t * 2 * Math.PI / 5.2);
  }
  return out;
}
function frameUrl(shot, t) {
  if (shot.image) return shot.image;
  const i = clamp(Math.round((t - shot.ext0) * FPS) + 1, 1, shot.n);
  return shot.dir + pad5(i) + '.jpg';
}
function drawFoot(t) {
  const st = footStates(t); let full = 0;
  const used = new Set();
  for (const o of st) {
    const sh = SHOT[o.shot]; if (!sh) continue;
    const L = FL[sh.layer % 2]; used.add(L);
    const S = o.S, c = clamp(S.r / 38);
    setSrc(L.im, frameUrl(sh, t));
    if (sh.image) { const k = clamp((t - sh.t0) / Math.max(.1, sh.t1 - sh.t0)); L.im.style.transform = `scale(${lerp(sh.kb[0], sh.kb[1], k)})`; }
    Object.assign(L.d.style, {
      left: (S.cx - S.w / 2) + 'px', top: (S.cy - S.h / 2) + 'px', width: S.w + 'px', height: S.h + 'px', borderRadius: S.r + 'px',
      transform: `rotateZ(${S.rz}deg) rotateX(${S.rx}deg) rotateY(${S.ry}deg) scale(${S.s})`,
      filter: `blur(${S.blur.toFixed(2)}px) brightness(${(1 - S.dim).toFixed(3)})`, opacity: S.op.toFixed(3), zIndex: o.z,
      boxShadow: c > .02 ? `0 ${30 * c}px ${80 * c}px rgba(0,0,0,${.6 * c})` : 'none',
    });
    L.v.style.opacity = c;
    full = Math.max(full, S.op * clamp((S.w - 712) / (1080 - 712)) * (1 - clamp(S.blur / 20)));
  }
  for (const L of FL) if (!used.has(L)) L.d.style.opacity = 0;
  toiTren.style.opacity = full.toFixed(3);
}

/* ---------------- thẻ giao diện (giao_dien) ---------------- */
const pUI = mk('div', 'persp');
const UI = [];
function mapSVG(seed, nhan) {
  // toạ độ thế giới 1680×2200, đặt lệch (-400,-400) → vùng nhìn thấy trong thẻ: x 400..1280, y 400..1800
  const R = rng(seed); let g = '';
  g += `<rect x="0" y="0" width="1680" height="2200" fill="#F4F2EE"/>`;
  for (let i = 0; i < 90; i++) { const x = R() * 1680, y = R() * 2200, w = 30 + R() * 90, h = 26 + R() * 70; g += `<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="${w.toFixed(0)}" height="${h.toFixed(0)}" rx="5" fill="#E9E6E0"/>`; }
  let mn = '';
  for (let k = -20; k <= 26; k++) { const o = k * 74 + R() * 18; mn += `M${o.toFixed(0)} -400L${(o + 1100).toFixed(0)} 2600`; }
  for (let k = -12; k <= 40; k++) { const o = k * 70 + R() * 16; mn += `M-400 ${o.toFixed(0)}L2100 ${(o - 900).toFixed(0)}`; }
  g += `<path d="${mn}" stroke="#E0DCD3" stroke-width="10" fill="none"/><path d="${mn}" stroke="#FFFFFF" stroke-width="7" fill="none"/>`;
  const sec = `M-200 1280L1900 360M520 -200L1180 2400M-200 900L1900 1880M200 -200L760 2400`;
  g += `<path d="${sec}" stroke="#D5D1C8" stroke-width="19" fill="none"/><path d="${sec}" stroke="#FFFFFF" stroke-width="15" fill="none"/>`;
  const major = `M-200 1900L1900 560M760 -200L1420 2400`;
  g += `<path d="${major}" stroke="#F2C14E" stroke-width="24" fill="none"/><path d="${major}" stroke="#FDE293" stroke-width="18" fill="none"/>`;
  g += `<path d="M-100 1500L1800 2350" stroke="#8AB4F8" stroke-width="7" stroke-dasharray="22 14" fill="none" opacity=".6"/>`;
  const sh = (d, f, cx, cy, k) => `<path d="${d}" fill="${f}" transform="translate(${cx} ${cy}) scale(${k}) translate(${-cx} ${-cy})"/>`;
  g += sh('M430 640c70-80 230-95 290-25s30 180-55 215-225 15-260-50-35-95 25-140z', '#AECBFA', 440, 700, .55);
  g += sh('M900 1380c110-35 230 0 255 80s-55 150-170 150-175-55-185-125 35-90 100-105z', '#C8E6C9', 1000, 1460, .5);
  g += sh('M1090 560c80-18 160 26 150 98s-80 98-150 80-98-80-70-125 35-45 70-53z', '#C8E6C9', 1150, 630, .6);
  g += `<path d="M1180 400C1120 700 1260 900 1200 1200S1240 1600 1180 1900" stroke="#AECBFA" stroke-width="16" fill="none"/>`;
  for (let i = 0; i < 22; i++) { const x = 420 + R() * 840, y = 420 + R() * 1360; if (Math.abs(x - 840) < 120 && Math.abs(y - 900) < 120) continue; g += `<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="10" fill="#7986A3" opacity=".8"/><circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="4" fill="#fff"/>`; }
  const pho = ['Ng. 12', 'P. Láng', 'Ng. 85', 'P. Hoàng Cầu', 'Ng. 7', 'P. Trần Duy Hưng', 'Ng. 41', 'P. Nguyễn Tuân'];
  for (let i = 0; i < 30; i++) { const x = 440 + R() * 800, y = 440 + R() * 1320; if (Math.abs(x - 840) < 170 && Math.abs(y - 900) < 130) continue; g += `<text x="${x.toFixed(0)}" y="${y.toFixed(0)}" font-family="BVP" font-weight="500" font-size="16" fill="#8A8F96" transform="rotate(${(-40 + R() * 10).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})">${pho[i % pho.length]}</text>`; }
  const L = (nhan || []).slice(0, 6); const pos = [[600, 1010], [1110, 1260], [1010, 640], [700, 1580], [520, 1300], [1150, 1640]];
  L.forEach((s, i) => { const [x, y] = pos[i]; const up = i % 2 === 1; g += `<text x="${x}" y="${y}" text-anchor="middle" font-family="BVP" font-weight="${up ? 600 : 500}" font-size="${up ? 27 : 24}" letter-spacing="${up ? 4 : 0}" fill="${up ? '#6B6E73' : '#3F7D5B'}">${esc(up ? s.toUpperCase() : s)}</text>`; });
  return `<svg class="map-svg" viewBox="0 0 1680 2200" style="left:-400px;top:-400px;width:1680px;height:2200px">${g}</svg>`;
}
const PIN = `<svg viewBox="0 0 74 96"><path d="M37 2C18 2 4 16 4 34c0 24 33 58 33 58s33-34 33-58C70 16 56 2 37 2z" fill="#EA4335" stroke="#B3261E" stroke-width="3"/><circle cx="37" cy="33" r="12" fill="#A50E0E"/></svg>`;
const COPY = `<svg class="m-copy" viewBox="0 0 48 48" fill="none" stroke="#0B57D0" stroke-width="4"><rect x="16" y="16" width="24" height="26" rx="4"/><path d="M10 32V10a4 4 0 0 1 4-4h18"/></svg>`;
const ARROW_UP = `<svg viewBox="0 0 40 40" width="34" height="34" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 32V9M10 18l10-10 10 10"/></svg>`;

function typed(t, a, b, s) { // số ký tự đã gõ
  if (t < a) return 0; const d = Math.max(.2, (b ?? (a + s.length / 16)) - a); return Math.min(s.length, Math.floor(s.length * (t - a) / d + 1e-6));
}
function caret(t, a, b, s) { const end = (b ?? (a + s.length / 16)); if (t < a || t > end + .7) return ''; return (Math.floor((t - a) * 2.2) % 2 === 0 || t < end) ? '<span class="caret"></span>' : ''; }

function tplBanDo(sc, root) {
  const D = sc.data || {}, ot = D.o_tim || {}, gh = D.ghim, bg = D.bang, ch = D.cham, tb = D.thong_bao;
  const world = mk('div', '', root); world.style.cssText = 'position:absolute;left:0;top:0;width:880px;height:1400px';
  world.innerHTML = mapSVG(sc.id, D.nhan_ban_do);
  const PX = 440, PY = 520;
  const pin = mk('div', 'm-pin', world, PIN); pin.style.left = (PX - 37) + 'px'; pin.style.top = (PY - 96) + 'px';
  const lab = mk('div', 'm-pinlab', world, esc(gh?.ten || '')); lab.style.left = (PX + 42) + 'px'; lab.style.top = (PY - 86) + 'px';
  const search = mk('div', 'm-search', root, `${uniq(IC.google_maps).replace('<svg', '<svg width="46" height="46"')}<div class="txt"></div><div class="m-av">${esc(D.avatar || 'V')}</div>`);
  const stx = search.querySelector('.txt');
  const sheet = mk('div', 'm-sheet', root, `<div class="bar"></div><div class="ten">${esc(bg?.ten || gh?.ten || '')}</div>${bg?.phu ? `<div class="phu">${esc(bg.phu)}</div>` : ''}<div class="m-btns"><div class="m-btn c">Chỉ đường</div><div class="m-btn">Lưu</div><div class="m-btn">Chia sẻ</div></div><div class="m-addr"><svg width="40" height="40" viewBox="0 0 64 64" fill="none" stroke="#0B57D0" stroke-width="5"><path d="M32 58S12 38 12 24a20 20 0 0 1 40 0c0 14-20 34-20 34z"/><circle cx="32" cy="24" r="7"/></svg><div class="tx">${esc(bg?.dia_chi || '')}</div>${COPY}</div>`);
  const rip = mk('div', 'm-rip', root);
  const toast = mk('div', 'm-toast', root, `<svg width="34" height="34" viewBox="0 0 40 40" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21l8 8 16-17"/></svg>${esc(tb?.chu || 'Đã sao chép')}`);
  return t => {
    const s = ot.chu || '';
    const n = typed(t, ot.luc ?? 1e9, ot.den, s);
    stx.innerHTML = n > 0 ? esc(s.slice(0, n)) + caret(t, ot.luc, ot.den, s) : `<span class="ph">${esc(D.goi_y || 'Tìm kiếm tại đây')}</span>`;
    // bản đồ: zoom về ghim, dịch lên khi bảng trượt
    let sc_ = 1, ty = 0;
    if (gh) sc_ = 1 + .2 * P(t, gh.luc - .55, .7, E.inOutC);
    if (bg) ty = -150 * P(t, bg.luc, .4, E.outC);
    world.style.transformOrigin = `${PX}px ${PY}px`;
    world.style.transform = `translateY(${ty}px) scale(${sc_ + .03 * clamp((t - sc.tu) / (sc.den - sc.tu))})`;
    if (gh) {
      const u = clamp((t - gh.luc) / .42), k = E.drop(u);
      pin.style.opacity = t < gh.luc ? 0 : clamp(u * 4);
      pin.style.transform = `translateY(${-160 * (1 - k)}px) scale(${1 / sc_})`;
      lab.style.opacity = P(t, gh.luc + .22, .25); lab.style.transform = `scale(${1 / sc_})`; lab.style.transformOrigin = '0 50%';
    } else { pin.style.opacity = 0; lab.style.opacity = 0; }
    sheet.style.transform = `translateY(${bg ? 100 * (1 - P(t, bg.luc, .4)) : 100}%)`;
    // chạm nút copy
    if (ch && t >= ch.luc && t < ch.luc + .5) {
      const u = (t - ch.luc) / .5, r = 18 + 44 * E.outC(u);
      Object.assign(rip.style, { display: 'block', width: 2 * r + 'px', height: 2 * r + 'px', left: (880 - 40 - 23 - r) + 'px', top: (1400 - 560 + 22 + 330 + 59 - r + 150 * 0) + 'px', opacity: (.9 * (1 - u)).toFixed(3) });
    } else rip.style.display = 'none';
    toast.style.transform = `translateY(${tb ? 160 * (1 - P(t, tb.luc, .32, E.outB)) : 200}px)`;
    toast.style.opacity = tb ? P(t, tb.luc, .2) : 0;
  };
}

function tplChat(sc, root) {
  const D = sc.data || {}, V = (D.viec || []).slice().sort((a, b) => a.luc - b.luc);
  root.parentElement.classList.add('kem');
  mk('div', 'c-head', root, `<div class="c-ham"><i></i><i></i><i style="width:70%"></i></div>${IC.claude.replace('<svg', '<svg width="44" height="44"')}${esc(D.ten_app || 'Claude')}`);
  const chao = mk('div', 'c-chao', root, `${IC.claude}${esc(D.loi_chao || 'Hôm nay mình làm gì nhỉ?').replace(/\n/g, '<br>')}`);
  const msgs = mk('div', 'c-msgs', root);
  const inp = mk('div', 'c-input', root);
  const vid = mk('div', 'c-vid', root);
  const t0 = V.length ? V[0].luc : 1e9;
  return t => {
    chao.style.opacity = (1 - P(t, t0 - .05, .25)).toFixed(3);
    chao.style.transform = `translateY(${-30 * P(t, t0 - .05, .3)}px)`;
    // dựng lại trạng thái từ đầu tới t
    let pages = [[]], draft = { chips: [], text: null, thumb: null }, sendAt = -9, xoaAt = -9, vidState = null;
    for (const a of V) {
      if (a.luc > t) break;
      const page = pages[pages.length - 1];
      if (a.lam === 'dan') draft.chips.push({ k: 'dan', a });
      else if (a.lam === 'tep') draft.chips.push({ k: 'tep', a });
      else if (a.lam === 'go') draft.text = a;
      else if (a.lam === 'video') vidState = { a, vao: null };
      else if (a.lam === 'video_vao_o') { if (vidState) vidState.vao = a; draft.thumb = { a, src: vidState?.a.anh_url }; }
      else if (a.lam === 'gui') { page.push({ k: 'user', a, chips: draft.chips, text: draft.text ? draft.text.chu : '', thumb: draft.thumb, mini: a.the_nho }); draft = { chips: [], text: null, thumb: null }; sendAt = a.luc; vidState = null; }
      else if (a.lam === 'dang_lam') page.push({ k: 'ai', a });
      else if (a.lam === 'xoa') { pages.push([]); xoaAt = a.luc; }
    }
    // khung tin nhắn: trang hiện tại + trang cũ đang cuộn đi
    let h = '';
    const renderPage = (pg, extra) => {
      let s = `<div style="position:absolute;left:0;right:0;top:${20}px;display:flex;flex-direction:column;gap:34px;${extra}">`;
      for (const m of pg) {
        const k = P(t, m.a.luc, .35);
        if (m.k === 'user') {
          s += `<div style="align-self:flex-end;margin-right:36px;max-width:700px;display:flex;flex-direction:column;align-items:flex-end;gap:14px;opacity:${k};transform:translateY(${70 * (1 - k)}px)">`;
          if (m.thumb) s += `<div class="c-thumb" style="width:124px;height:220px"><img src="${esc(m.thumb.src)}"></div>`;
          if (m.mini && m.mini.length) s += `<div class="c-mini">${m.mini.map((x, i) => `<div class="c-minichip">${i === 0 ? '<span style="color:#9a978e">⌖</span>' : '<span style="color:#d93025">▮</span>'} ${esc(x)}</div>`).join('')}</div>`;
          if (m.text) s += `<div class="c-bub">${dam(m.text)}</div>`;
          s += `</div>`;
        } else {
          const rot = (t - m.a.luc) * 120;
          s += `<div style="margin:0 40px;opacity:${k}"><div class="c-ai"><div class="r1" style="position:relative">${IC.claude.replace('<svg', `<svg width="50" height="50" style="transform:rotate(${rot}deg)"`)}<span class="c-shim" style="background-position:${(100 - ((t - m.a.luc) * 70) % 300)}% 0">${esc(m.a.chu || 'Đang làm…')}</span></div>`;
          (m.a.buoc || []).forEach((b, j) => { const kk = P(t, m.a.luc + .35 * (j + 1), .3); const ok = t > m.a.luc + .35 * (j + 2) + .4; s += `<div class="c-step" style="opacity:${kk}"><b class="${ok ? 'ok' : ''}"></b>${esc(b)}</div>`; });
          s += `</div></div>`;
        }
      }
      return s + '</div>';
    };
    if (pages.length > 1 && t < xoaAt + .35) { const u = P(t, xoaAt, .32, E.inOutC); h += renderPage(pages[pages.length - 2], `opacity:${1 - u};transform:translateY(${-260 * u}px)`); }
    h += renderPage(pages[pages.length - 1], '');
    msgs.innerHTML = h;
    // ô nhập
    let ih = '';
    if (draft.thumb && (!vidState || !vidState.vao || t >= vidState.vao.luc + .45)) ih += `<div class="c-thumb"><img src="${esc(draft.thumb.src)}"></div>`;
    if (draft.chips.length) ih += `<div class="c-chips">${draft.chips.map(c => { const k = P(t, c.a.luc, .28, E.outB); return c.k === 'dan' ? `<div class="c-chip" style="opacity:${clamp(k)};transform:scale(${.9 + .1 * k})"><div class="n">${esc(c.a.nhan || 'ĐÃ DÁN')}</div><div class="v">${esc(c.a.chu)}</div></div>` : `<div class="c-chip" style="opacity:${clamp(k)};transform:scale(${.9 + .1 * k})"><div class="f">${esc(c.a.ten)}</div><div class="s">${esc(c.a.phu || '')}</div></div>`; }).join('')}</div>`;
    let has = draft.chips.length || draft.thumb;
    if (draft.text) { const s = draft.text.chu || '', n = typed(t, draft.text.luc, draft.text.den, s); has = has || n > 0; ih += `<div class="c-txt">${esc(s.slice(0, n))}${caret(t, draft.text.luc, draft.text.den, s)}</div>`; }
    else ih += `<div class="c-txt c-ph">${esc(D.goi_y || ('Trả lời ' + (D.ten_app || 'Claude') + '...'))}</div>`;
    const press = t >= sendAt && t < sendAt + .25 ? .86 + .14 * ((t - sendAt) / .25) : 1;
    ih += `<div class="c-bot"><div class="c-plus">+</div><div class="c-mod">${esc(D.mo_hinh || 'Opus 5.5')} ⌄<div class="c-send ${has ? '' : 'off'}" style="transform:scale(${press})">${ARROW_UP}</div></div></div>`;
    inp.innerHTML = ih;
    // video thả vào giữa
    if (vidState) {
      const a = vidState.a, k = P(t, a.luc, .38, E.outB), W0 = 380, H0 = 676;
      let x = 440 - W0 / 2, y = 230, w = W0, hh = H0, op = clamp(P(t, a.luc, .2)), lbOp = 1;
      if (vidState.vao) { const u = P(t, vidState.vao.luc, .45, E.inOutC); x = lerp(x, 56, u); y = lerp(y, 1400 - 30 - 354 + 22, u); w = lerp(W0, 96, u); hh = lerp(H0 + 0, 170, u); lbOp = 1 - clamp(u * 3); if (t >= vidState.vao.luc + .45) op = 0; }
      vid.style.cssText = `left:${x}px;top:${y - (lbOp > 0 ? 0 : 0)}px;opacity:${op};transform:scale(${vidState.vao ? 1 : 1.12 - .12 * k});transform-origin:50% 40%;filter:blur(${(1 - clamp(P(t, a.luc, .25))) * 10}px)`;
      vid.innerHTML = `<div class="lb" style="opacity:${lbOp}">${esc(a.nhan || 'Video mẫu')}</div><div class="im" style="width:${w}px;height:${hh}px;border-radius:${lerp(26, 14, clamp((w - W0) / (96 - W0)))}px"><img src="${esc(a.anh_url || '')}"></div>`;
      if (vidState.vao) vid.querySelector('.lb').style.display = lbOp <= 0 ? 'none' : '';
    } else vid.style.opacity = 0;
  };
}

function tplAnh(sc, root) {
  const D = sc.data || {};
  const im = mk('img', 'a-im', root);
  const rip = mk('div', 'm-rip', root); rip.style.background = 'rgba(30,30,30,.35)';
  const z = D.zoom || [1, 1.06];
  return t => {
    const k = clamp((t - sc.tu) / Math.max(.1, sc.den - sc.tu));
    if (D.khung) setSrc(im, D.khung.dir + pad5(clamp(Math.round((t - D.khung.ext0) * FPS) + 1, 1, D.khung.n)) + '.jpg'); else setSrc(im, D.anh_url);
    im.style.transform = `scale(${lerp(z[0], z[1], k)})`;
    const c = (D.cham || []).find(c => t >= c.luc && t < c.luc + .5);
    if (c) { const u = (t - c.luc) / .5, r = 20 + 50 * E.outC(u); Object.assign(rip.style, { display: 'block', left: (c.x * 880 - r) + 'px', top: (c.y * 1400 - r) + 'px', width: 2 * r + 'px', height: 2 * r + 'px', opacity: (.8 * (1 - u)).toFixed(3) }); }
    else rip.style.display = 'none';
  };
}

for (const sc of KH.scenes) {
  if (sc.loai !== 'giao_dien') continue;
  const card = mk('div', 'uicard', pUI); const inn = mk('div', 'ui-in', card); const fro = mk('div', 'fro', card);
  const f = ({ ban_do: tplBanDo, chat_ai: tplChat, anh: tplAnh })[sc.mau] || tplAnh;
  UI.push({ sc, card, fro, draw: f(sc, inn) });
}
function drawUI(t) {
  const sc = KH.scenes;
  for (const u of UI) {
    const s = u.sc, i = sc.indexOf(s), nx = sc[i + 1];
    const frost = nx && nx.mode === 'full' && nx.loai === 'tran_man' && nx.vao !== 'hoa_tan';
    const end = s.den + (frost ? .22 : .27);
    if (t < s.tu - .01 || t > end) { u.card.style.display = 'none'; continue; }
    u.card.style.display = 'block';
    const k = P(t, s.tu, .32); let op = k, blur = 6 * (1 - k), br = .65 + .35 * k, fo = 0;
    if (frost) { const q = P(t, s.den - .12, .34, E.inOutS); fo = .9 * q; blur += 10 * q; op *= 1 - E.outQ(clamp((t - s.den - .05) / .17)); }
    else { const q = P(t, s.den, .25, E.outQ); op *= 1 - q; blur += 8 * q; }
    const zoom = 1 + .035 * clamp((t - s.tu) / Math.max(.1, s.den - s.tu));
    Object.assign(u.card.style, { opacity: op.toFixed(3), transform: `scale(${((.965 + .035 * k) * zoom).toFixed(4)})`, filter: `blur(${blur.toFixed(2)}px) brightness(${br.toFixed(3)})` });
    u.fro.style.opacity = fo;
    u.draw(t);
  }
}

/* ---------------- điện thoại CTA ---------------- */
const pPh = mk('div', 'persp'); pPh.style.perspective = '2200px';
const PH = [];
const SIG = `<svg width="92" height="30" viewBox="0 0 92 30"><g fill="#000"><rect x="0" y="18" width="6" height="10" rx="1.5"/><rect x="9" y="13" width="6" height="15" rx="1.5"/><rect x="18" y="8" width="6" height="20" rx="1.5"/><rect x="27" y="3" width="6" height="25" rx="1.5"/></g><rect x="46" y="5" width="40" height="20" rx="6" fill="none" stroke="#000" stroke-width="2.5"/><rect x="50" y="9" width="30" height="12" rx="3" fill="#000"/><rect x="88" y="11" width="3" height="8" rx="1" fill="#000"/></svg>`;
for (const sc of KH.scenes) {
  if (sc.loai !== 'dien_thoai') continue;
  const D = sc.data || {};
  const ph = mk('div', 'phone', pPh);
  ph.style.left = '200px'; ph.style.top = '250px';
  ph.innerHTML = `<div class="ph-scr"></div><div class="ph-isl"></div><div class="ph-sb"><span>${esc(D.gio_may || '9:41')}</span>${SIG}</div>
   <div class="ph-head"><svg width="34" height="34" viewBox="0 0 40 40" fill="none" stroke="#111" stroke-width="4.5" stroke-linecap="round"><path d="M26 6L12 20l14 14"/></svg><div class="ph-av"><svg width="44" height="44" viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="5"><circle cx="32" cy="22" r="11"/><path d="M11 57c2-12 11-18 21-18s19 6 21 18"/></svg></div><div style="flex:1"><div class="ph-name">${esc(D.ten || 'Khách hàng')}</div><div class="ph-st">${esc(D.trang_thai || 'Vừa mới truy cập')}</div></div><svg width="44" height="44" viewBox="0 0 64 64" fill="none" stroke="#111" stroke-width="4.5"><path d="M20 8l8 12-5 6c3 7 8 12 15 15l6-5 12 8-4 9C34 53 11 30 11 12z" stroke-linejoin="round"/></svg></div>
   <div class="ph-day">${esc(D.ngay || 'Hôm nay')}</div><div class="ph-msgs"></div>
   <div class="ph-inp"><span>${esc(D.goi_y || 'Tin nhắn')}</span><div class="ph-sendb">${ARROW_UP}</div></div><div class="ph-home"></div>`;
  PH.push({ sc, ph, box: ph.querySelector('.ph-msgs'), tin: (D.tin || []).slice().sort((a, b) => a.luc - b.luc) });
}
function drawPhone(t) {
  for (const p of PH) {
    const s = p.sc;
    if (t < s.tu - .01 || t > s.den + .3) { p.ph.style.display = 'none'; continue; }
    p.ph.style.display = 'block';
    const k = P(t, s.tu, .5, E.outC), q = P(t, s.den, .25);
    const rz = -9 + 3.5 * k + .5 * Math.sin(t * 2 * Math.PI / 6), ry = -12 + 9 * k + .8 * Math.sin(t * 2 * Math.PI / 7.5);
    Object.assign(p.ph.style, {
      opacity: (k * (1 - q)).toFixed(3), filter: `blur(${(8 * (1 - k) + 8 * q).toFixed(2)}px)`,
      transform: `translateY(${150 * (1 - k)}px) rotateZ(${rz}deg) rotateX(4deg) rotateY(${ry}deg) scale(${.9 + .1 * k})`,
    });
    let h = '<div style="display:flex;flex-direction:column;gap:38px">';
    for (const m of p.tin) {
      if (m.luc > t) break;
      if (m.lam === 'dang_go') {
        if (t >= (m.den ?? m.luc + 1)) continue;
        const kk = P(t, m.luc, .25, E.outB);
        h += `<div class="ph-m r" style="position:relative;opacity:${clamp(kk)};transform:scale(${.8 + .2 * kk});transform-origin:100% 100%"><div class="ph-dots">${[0, 1, 2].map(j => `<i style="opacity:${(.35 + .65 * Math.max(0, Math.sin(2 * Math.PI * t * 1.6 - j * 1.1))).toFixed(2)}"></i>`).join('')}</div></div>`;
        continue;
      }
      const kk = P(t, m.luc, .3, E.outB), b = clamp(P(t, m.luc, .22)), right = m.ben !== 'khach';
      const st = `position:relative;opacity:${b};transform:scale(${.86 + .14 * kk});transform-origin:${right ? '100%' : '0'} 100%;filter:blur(${(1 - b) * 8}px)`;
      if (m.loai === 'tai_lieu') h += `<div class="ph-m ${right ? 'r' : ''}" style="${st}"><div class="ph-doc"><div class="in">${IC.tai_lieu}<div style="flex:1"><div class="t1">${esc(m.tieu_de)}</div><div class="t2">${esc(m.phu || '')}</div></div></div><div class="gio">${esc(m.gio || '')}</div></div></div>`;
      else { const to = !right && (m.chu || '').replace(/\*/g, '').length <= 16; h += `<div class="ph-m ${right ? 'r' : ''}" style="${st}"><div class="ph-b ${right ? 'd' : 'w'}"><div class="tt ${to ? 'to' : ''}">${dam(m.chu)}</div>${m.gio ? `<div class="gio">${esc(m.gio)}</div>` : ''}</div></div>`; }
    }
    p.box.innerHTML = h + '</div>';
  }
}

/* ---------------- viên kính + ô kính ---------------- */
const OV = mk('div'); OV.style.cssText = 'position:absolute;inset:0';
const PILLS = (KH.pills || []).map(p => {
  const w = mk('div', 'pill-wrap', OV, `${p.dan ? `<div class="pill-dan">${esc(p.dan)}</div>` : ''}<div class="pill"><div class="ic">${icon(p.icon)}</div><div class="ch">${esc(p.chu)}</div>${p.gach != null ? '<div class="gach"></div>' : ''}</div>`);
  w.style.top = (p.y - 61 - (p.dan ? 70 : 0)) + 'px';
  return { p, w, pill: w.querySelector('.pill'), dan: w.querySelector('.pill-dan'), g: w.querySelector('.gach') };
});
const TILES = (KH.tiles || []).map(T => {
  const n = T.muc.length, size = n > 3 ? Math.max(170, Math.floor((1080 - 80 - (n - 1) * 34) / n)) : 250;
  const w = mk('div', 'tiles', OV); w.style.top = (T.y - size / 2) + 'px'; if (n > 3) w.style.gap = '34px';
  const items = T.muc.map((m, i) => {
    const el = mk('div', 'tile', w, `<div class="o" style="width:${size}px;height:${size}px;border-radius:${size * .265}px"><div class="so">${T.so === false ? '' : (m.so ?? i + 1)}</div>${icon(m.icon)}</div><div class="nhan">${esc(m.nhan)}</div>`);
    el.style.width = size + 'px';
    if (size < 250) { const sv = el.querySelector('.o svg, .o img'); if (sv) { sv.style.width = sv.style.height = (size * .45) + 'px'; } el.querySelector('.nhan').style.fontSize = Math.round(36 * size / 250 + 4) + 'px'; }
    return { m, el, parts: [el.querySelector('.o'), el.querySelector('.nhan')] };
  });
  return { T, w, items };
});
function drawOV(t) {
  for (const o of PILLS) {
    const p = o.p;
    if (t < p.tu - .01 || t > p.den) { o.w.style.display = 'none'; continue; }
    o.w.style.display = 'flex';
    const k = P(t, p.tu, .28), q = P(t, p.den - .22, .22, E.inOutS);
    o.w.style.transform = `scale(${.94 + .06 * k})`;
    const op = k * (1 - q), bl = 10 * (1 - k) + 10 * q;
    for (const el of [o.pill, o.dan]) if (el) { el.style.opacity = op >= .999 ? '' : op.toFixed(3); el.style.filter = bl > .05 ? `blur(${bl.toFixed(2)}px)` : ''; }
    if (o.g) { const g = P(t, p.gach, .22); o.g.style.transform = `scaleX(${t < p.gach ? 0 : g})`; o.g.style.opacity = t < p.gach ? 0 : 1; }
    const dimk = p.gach != null ? clamp((t - p.gach - .15) / .2) : 0;
    for (const c of o.pill.querySelectorAll('.ic,.ch')) c.style.opacity = (1 - .45 * dimk).toFixed(3);
  }
  for (const o of TILES) {
    const T = o.T;
    if (t < T.tu - .01 || t > T.den) { o.w.style.display = 'none'; continue; }
    o.w.style.display = 'flex';
    const q = P(t, T.den - .25, .25, E.inOutS);
    o.items.forEach((it, i) => {
      const a = it.m.luc ?? (T.tu + .1 * i), u = clamp((t - a) / .32);
      const op = E.outC(u) * (1 - q), bl = 12 * (1 - E.outC(u)) + 10 * q;
      it.el.style.transform = `scale(${(.7 + .3 * E.outB(u)).toFixed(4)})`;
      for (const el of it.parts) { el.style.opacity = op >= .999 ? '' : op.toFixed(3); el.style.filter = bl > .05 ? `blur(${bl.toFixed(2)}px)` : ''; }
    });
  }
}

/* ---------------- chữ 2 tầng ---------------- */
const CAPL = mk('div'); CAPL.style.cssText = 'position:absolute;inset:0';
const CAPS = (KH.caps || []).map(c => {
  const box = mk('div', 'cap', CAPL); box.style.top = c.top + 'px';
  const spans = [];
  for (const dong of c.dong) {
    const d = mk('div', 'dong', box);
    for (const ch of dong) {
      const cls = 'w k-' + ch.k;
      if (ch.whole) { const s = mk('span', cls, d, esc(ch.k === 'trich' ? `“${ch.text}”` : ch.text)); spans.push({ s, t: ch.t }); }
      else for (const w of ch.words) { const s = mk('span', cls, d, esc(w.w)); spans.push({ s, t: w.t }); }
    }
  }
  return { c, box, spans };
});
function drawCaps(t) {
  for (const o of CAPS) {
    const c = o.c;
    if (t < c.tu - .3 || t > c.den) { o.box.style.display = 'none'; continue; }
    o.box.style.display = 'flex';
    const q = P(t, c.den - .22, .22, E.inOutS);
    for (const sp of o.spans) {
      const p = P(t, sp.t, .22);
      sp.s.style.opacity = (p * (1 - q)).toFixed(3);
      const b = (1 - p) * 10 + q * 10; sp.s.style.filter = b > .05 ? `blur(${b.toFixed(2)}px)` : 'none';
    }
  }
}

/* ---------------- vòng chính ---------------- */
const raf2 = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
window.__seek = async t => {
  drawFoot(t); drawUI(t); drawPhone(t); drawOV(t); drawCaps(t);
  await Promise.all([...document.images].filter(i => i.src).map(i => i.decode().catch(() => { })));
  await raf2();
  return true;
};
window.__bao_cao = () => {
  const out = [];
  const add = (loai, el) => { const r = el.getBoundingClientRect(); const op = +getComputedStyle(el).opacity; if (r.width > 0 && op > .5) out.push({ loai, chu: el.textContent.trim(), x0: Math.round(r.left), y0: Math.round(r.top), x1: Math.round(r.right), y1: Math.round(r.bottom) }); };
  for (const o of CAPS) if (o.box.style.display !== 'none') for (const sp of o.spans) add('chu', sp.s);
  for (const o of PILLS) if (o.w.style.display !== 'none') add('vien_kinh', o.pill);
  for (const o of TILES) if (o.w.style.display !== 'none') for (const it of o.items) add('o_kinh', it.el);
  for (const u of UI) if (u.card.style.display !== 'none' && +u.card.style.opacity > .5) add('the_giao_dien', u.card);
  for (const p of PH) if (p.ph.style.display !== 'none' && +p.ph.style.opacity > .5) add('dien_thoai', p.ph);
  return out;
};
window.__ready = (async () => {
  await document.fonts.ready;
  await Promise.all(['400', '800', 'italic 800'].map(w => document.fonts.load(`${w} 40px BVP`)));
  await window.__seek(0);
})();
})();
