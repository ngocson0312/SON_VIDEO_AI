/* ngang.js — trang dựng 1920×1080 của TuanJp_DuLich_ManNgang.
 * Nhận window.KH (kế hoạch đã giải giờ bởi scripts/ke_hoach.py + KH.part từ dung.py), vẽ đúng khung ở giây t qua window.__seek(t).
 * Không dùng thời gian thực: mọi chuyển động là hàm thuần của t → dựng tất định, chia luồng được.
 */
const KH = window.KH;
const W = 1920, H = 1080, FPS = KH.fps || 30;
const stage = document.getElementById('stage');

// ---------------- tiện ích ----------------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const E = {
  lin: u => u, outC: u => 1 - Math.pow(1 - u, 3), inC: u => u * u * u,
  ioC: u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2,
  outE: u => u >= 1 ? 1 : 1 - Math.pow(2, -10 * u), ioS: u => -(Math.cos(Math.PI * u) - 1) / 2,
  outB: u => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); },
  outQ: u => 1 - (1 - u) * (1 - u),
};
const P = (t, a, d, e = E.outC) => e(clamp((t - a) / Math.max(1e-6, d)));
const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || stage).appendChild(e); if (cls === 'dh') e.style.display = 'none'; return e; };
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pad5 = i => String(i).padStart(5, '0');
const chars = s => Array.from(String(s ?? '').normalize('NFC'));
const words = s => String(s ?? '').trim().split(/\s+/).filter(Boolean);
function css(el, o) { for (const k in o) { const v = o[k]; if (el.style[k] !== v) el.style[k] = v; } }
function show(el, on) { const v = on ? '' : 'none'; if (el.style.display !== v) el.style.display = v; }
const DS = [];   // ảnh vừa đổi src → chờ decode trước khi chụp
function setSrc(img, u) { if (u && img.dataset.u !== u) { img.dataset.u = u; img.src = u; DS.push(img); } }
const NN = KH.ngon_ngu || 'vi';
const T = KH.T || {};

// ---------------- icon (nét 24×24) ----------------
const S = p => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
const SONG = '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>';
const RUONG = '<path d="M2 20h20"/><path d="M3 16c3-1 6-1 9 0s6 1 9 0"/><path d="M4 12c3-1 5-1 8 0s5 1 8 0"/><path d="M6 8c2-1 4-1 6 0s4 1 6 0"/>';
const IC = {
  ghim: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
  nui: '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
  bien: SONG, song_nuoc: SONG,
  dao: '<path d="M13 8c0-2.76-2.46-5-5.5-5S2 5.24 2 8h2l1-1 1 1h4"/><path d="M13 7.14A5.82 5.82 0 0 1 16.5 6c3.04 0 5.5 2.24 5.5 5h-3l-1-1-1 1h-3"/><path d="M5.89 9.71c-2.15 2.15-2.3 5.47-.35 7.43l4.24-4.25.7-.7.71-.71 2.12-2.12c-1.95-1.96-5.27-1.8-7.42.35"/><path d="M11 15.5c.5 2.5-.17 4.5-1 6.5h4c2-5.5-.5-12-1-14"/>',
  thac: '<path d="M4 3h16"/><path d="M7 3v13"/><path d="M12 3v15"/><path d="M17 3v12"/><path d="M3 20c2 0 2-1.5 4.5-1.5S10 20 12 20s2.5-1.5 4.5-1.5S19 20 21 20"/>',
  may: '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
  mat_troi: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  trang: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  sao: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
  tim: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
  may_anh: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
  tau: '<path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><path d="M12 10v4"/><path d="M12 2v3"/>',
  tau_hoa: '<rect x="4" y="3" width="16" height="16" rx="2"/><path d="M4 11h16"/><path d="M12 3v8"/><path d="m8 19-2 3"/><path d="m18 22-2-3"/><path d="M8 15h.01"/><path d="M16 15h.01"/>',
  cap_treo: '<path d="M3 3l18 4"/><path d="M12 5v4"/><rect x="5" y="9" width="14" height="11" rx="2"/><path d="M5 14h14"/><path d="M12 9v5"/>',
  xe_may: '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5"/><path d="M5.5 17.5 9 10h7l-3 7.5"/>',
  o_to: '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
  may_bay: '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
  di_bo: '<path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z"/><path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z"/>',
  co: '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22v-7"/>',
  den_long: '<path d="M12 2v2"/><path d="M9 4h6"/><ellipse cx="12" cy="12" rx="6" ry="7"/><path d="M12 5v14"/><path d="M8.5 6.5c-1.5 3.5-1.5 7.5 0 11M15.5 6.5c1.5 3.5 1.5 7.5 0 11"/><path d="M10 19h4v2h-4z"/>',
  phao_hoa: '<path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/>',
  drone: '<circle cx="5" cy="5" r="2.5"/><circle cx="19" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M7 7l3 3M17 7l-3 3M7 17l3-3M17 17l-3-3"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/>',
  hoa: '<circle cx="12" cy="12" r="3"/><path d="M12 16.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 1 1 12 7.5a4.5 4.5 0 1 1 4.5 4.5 4.5 4.5 0 1 1-4.5 4.5"/>',
  la: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
  lua: RUONG, ruong: RUONG,
  chua: '<path d="M12 2v2"/><path d="M6 7h12l-2-3H8z"/><path d="M8 7v3"/><path d="M16 7v3"/><path d="M4 12h16l-2-2H6z"/><path d="M7 12v4M17 12v4"/><path d="M3 18h18l-2-2H5z"/><path d="M10 22v-4h4v4"/>',
  cau: '<path d="M2 18h20"/><path d="M4 18v-6M20 18v-6"/><path d="M2 12c4 0 6-6 10-6s6 6 10 6"/><path d="M8 18v-4M12 18v-6M16 18v-4"/>',
  thanh_pho: '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4M10 10h4M10 14h4M10 18h4"/>',
  lich_su: '<path d="M3 22h18"/><path d="M6 18v-7M10 18v-7M14 18v-7M18 18v-7"/><path d="m12 2 8 5H4z"/>',
  dong_ho: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  nhiet_do: '<path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/>',
  an_uong: '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
  ca_phe: '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><path d="M6 2v2M10 2v2M14 2v2"/>',
  lap_lanh: '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4M22 5h-4"/>',
  balo: '<path d="M4 10a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/><path d="M8 10h8"/><path d="M8 18h8"/><path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>',
  la_ban: '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"/>',
  ban_do: '<path d="M14.1 4.6 9.9 2.4a2 2 0 0 0-1.8 0L3.6 4.6A1 1 0 0 0 3 5.5v14.3a1 1 0 0 0 1.5.9l3.6-1.8a2 2 0 0 1 1.8 0l4.2 2.1a2 2 0 0 0 1.8 0l4.5-2.2a1 1 0 0 0 .6-.9V4.2a1 1 0 0 0-1.5-.9l-3.6 1.8a2 2 0 0 1-1.8 0z"/><path d="M15 5.8v15M9 3.2v15"/>',
  nguoi: '<circle cx="12" cy="7" r="4"/><path d="M5.5 21a6.5 6.5 0 0 1 13 0"/>',
  gio: '<path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>',
  tuyet: '<path d="M2 12h20M12 2v20M20 16l-4-4 4-4M4 8l4 4-4 4M16 4l-4 4-4-4M8 20l4-4 4 4"/>',
  mua: '<path d="M4 14.9A7 7 0 1 1 15.7 8h1.8a4.5 4.5 0 0 1 2.5 8.2"/><path d="M16 14v6M8 14v6M12 16v6"/>',
  non_la: '<path d="M2 18 12 4l10 14"/><path d="M2 18c3 2 17 2 20 0"/><path d="M7 13h10"/>',
  cay: '<path d="M12 22v-7"/><path d="M12 15H7c-2 0-3-2-2-3l3-4c-1 0-2-1-1-2l5-4 5 4c1 1 0 2-1 2l3 4c1 1 0 3-2 3z"/>',
  tich: '<path d="M20 6 9 17l-5-5"/>',
  ve: '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2M13 17v2M13 11v2"/>',
  gia: '<path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
  khach_san: '<path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/>',
  leu: '<path d="M3.5 21 14 3M20.5 21 10 3M15.5 21 12 15l-3.5 6M2 21h20"/>',
  hang: '<path d="M2 20c0-7 4-14 10-14s10 7 10 14"/><path d="M8 20c0-3 2-6 4-6s4 3 4 6"/><path d="M2 20h20"/>',
  chuong: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
  thich: '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>',
  chia_se: '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/>',
  binh_luan: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
};
const icon = n => S(IC[n] || IC.sao);
const TAY = `<svg viewBox="0 0 120 170" width="120" height="170"><defs><linearGradient id="gtay" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E4E0DA"/></linearGradient></defs>
<g fill="url(#gtay)" stroke="#2b2b2b" stroke-width="4" stroke-linejoin="round"><rect x="28" y="3" width="22" height="80" rx="11"/><rect x="48" y="44" width="21" height="46" rx="10.5"/><rect x="66.5" y="50" width="20" height="42" rx="10"/><rect x="84.5" y="58" width="18" height="36" rx="9"/><path d="M27 66 L103 72 L103 116 Q103 146 76 150 L54 150 Q30 147 27 124 Z"/><rect x="9" y="76" width="22" height="50" rx="11" transform="rotate(-36 20 101)"/></g></svg>`;
const TAY_DIEM = [39, 4];          // đầu ngón trỏ trong khung 120×170

// ---------------- lớp nền: footage ----------------
const CL = mk('div', '', stage); CL.id = 'canh_lop';
const PART = KH.part || {};
function partUrl(pid, t, a) {
  const p = PART[pid]; if (!p) return '';
  if (p.anh) return p.src;
  const i = clamp(Math.floor((t - a) * FPS + 1e-4), 0, p.n - 1) + 1;
  return p.dir + pad5(i) + '.jpg';
}
const THE_DOC_W = Math.round(KH.the_doc_cao * 9 / 16);

function dungCanh(c, i) {
  const root = mk('div', 'canh', CL); root.style.display = 'none'; root.style.zIndex = String(i + 1);
  const o = { c, root, i };
  if (c.bo_cuc === 'tran') {
    o.img = mk('img', 'full', root);
  } else if (c.bo_cuc === 'the_doc') {
    o.nen = mk('img', 'nen', root); mk('div', 'nen_phu', root);
    const ch = KH.the_doc_cao, cw = THE_DOC_W, cx = KH.the_doc_x[c.vi_tri] || 960;
    o.card = mk('div', 'the_doc', root);
    css(o.card, { left: (cx - cw / 2) + 'px', top: ((H - ch) / 2 - 6) + 'px', width: cw + 'px', height: ch + 'px' });
    o.img = mk('img', '', o.card); mk('div', 'bong', o.card);
  } else if (c.bo_cuc === 'the_anh') {
    o.nen = mk('img', 'nen', root); mk('div', 'nen_phu', root);
    const p = PART[c.lop[0]] || { w: 1200, h: 800 };
    const mw = c.vi_tri === 'giua' ? 1180 : 790, mh = 720;
    const s = Math.min(mw / p.w, mh / p.h);
    const iw = Math.round(p.w * s), ih = Math.round(p.h * s);
    const cx = c.vi_tri === 'trai' ? 550 : (c.vi_tri === 'phai' ? 1370 : 960);
    o.card = mk('div', 'the_anh', root);
    css(o.card, { left: (cx - iw / 2 - 16) + 'px', top: (500 - ih / 2 - 16) + 'px' });
    o.wrap = mk('div', 'khung_anh', o.card); css(o.wrap, { width: iw + 'px', height: ih + 'px' });
    o.img = mk('img', '', o.wrap);
  } else if (c.bo_cuc === 'ghep') {
    root.style.background = 'transparent';
    o.bg = mk('div', 'ghep_nen', root);
    const n = c.lop.length, pw = c.pw;
    o.o = c.lop.map((pid, k) => {
      const d = mk('div', 'o_ghep', root); css(d, { left: (k * (pw + KH.khe)) + 'px', width: pw + 'px' });
      const img = mk('img', '', d); mk('div', 'vien', d);
      let nhan = null;
      const nh = (c.nhan || [])[k];
      if (nh) {
        const g = mk('div', 'abs', d); css(g, { left: 0, right: 0, bottom: 0, height: '520px', background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.62))' });
        nhan = mk('div', 'abs', d); css(nhan, { left: 0, width: pw + 'px', top: '600px', textAlign: 'center' });
        const t1 = mk('div', 'serif kem_grad', nhan, esc(nh.chu || '')); css(t1, { fontSize: '68px', whiteSpace: 'nowrap' });
        const t2 = nh.phu ? mk('div', 'tay', nhan, esc(nh.phu)) : null; if (t2) css(t2, { fontSize: '58px', marginTop: '4px', whiteSpace: 'nowrap' });
        nhan._g = g; nhan._t = [t1, t2].filter(Boolean);
      }
      return { d, img, pid, nhan, k };
    });
    const luc = c.luc_o && c.luc_o.length ? c.luc_o : c.lop.map((_, k) => c.a + k * .12);
    o.luc = c.lop.map((_, k) => +(luc[k] ?? luc[luc.length - 1]));
  }
  return o;
}
const SC = KH.canh.map(dungCanh);

function kenBurns(cd, u, manh) {
  const z = .075 * manh, m = manh;
  switch (cd) {
    case 'zoom_vao': return { s: 1 + z * u, x: 0, y: 0 };
    case 'zoom_ra': return { s: 1 + z * (1 - u), x: 0, y: 0 };
    case 'lia_trai': return { s: 1 + z, x: lerp(.028, -.028, u) * m, y: 0 };
    case 'lia_phai': return { s: 1 + z, x: lerp(-.028, .028, u) * m, y: 0 };
    case 'lia_len': return { s: 1 + z, x: 0, y: lerp(.026, -.026, u) * m };
    case 'lia_xuong': return { s: 1 + z, x: 0, y: lerp(-.026, .026, u) * m };
    default: return { s: 1.015, x: 0, y: 0 };
  }
}
const tfKB = (k, w, h) => `translate(${(k.x * w).toFixed(2)}px,${(k.y * h).toFixed(2)}px) scale(${k.s.toFixed(5)})`;

function veCanh(o, t) {
  const c = o.c, u = clamp((t - c.a) / Math.max(.01, c.b - c.a));
  const anh = (c.loai_nguon || [])[0] === 'anh';
  if (c.bo_cuc === 'tran') {
    setSrc(o.img, partUrl(c.lop[0], t, c.a));
    o.img.style.transform = tfKB(kenBurns(c.chuyen_dong, u, anh ? 1 : .55), W, H);
  } else if (c.bo_cuc === 'the_doc' || c.bo_cuc === 'the_anh') {
    setSrc(o.nen, partUrl(c.nen, t, c.a));
    o.nen.style.transform = `scale(${(1.04 + .05 * u).toFixed(4)})`;
    setSrc(o.img, partUrl(c.lop[0], t, c.a));
    o.img.style.transform = tfKB(kenBurns(c.chuyen_dong, u, anh ? .8 : .45), 1, 1);
    // thẻ hạ cánh: nổi lên + phóng nhẹ (không lặp lại khi cảnh trước cũng là thẻ cùng chỗ)
    const truoc = SC[o.i - 1]?.c;
    const noi = !(truoc && truoc.bo_cuc === c.bo_cuc && truoc.vi_tri === c.vi_tri);
    const e = noi ? P(t, c.tu - c.d_in * .2, .75, E.outC) : 1;
    const rot = (c.nghieng || 0) + (c.bo_cuc === 'the_anh' ? (c.vi_tri === 'phai' ? 2.2 : -2.2) * (c.nghieng === 0 ? 1 : 0) : 0);
    o.card.style.transform = `translateY(${((1 - e) * 80).toFixed(1)}px) scale(${(.9 + .1 * e + .015 * u).toFixed(4)}) rotate(${(rot * e).toFixed(2)}deg)`;
    o.card.style.opacity = (noi ? clamp(e * 1.6) : 1).toFixed(3);
    if (o.wrap) o.img.style.transformOrigin = '50% 50%';
  } else if (c.bo_cuc === 'ghep') {
    let het = 0;
    for (const p of o.o) {
      const t0 = o.luc[p.k];
      const e = P(t, t0, .7, E.outE);
      het = Math.max(het, t0 + .7);
      const dir = p.k % 2 ? -1 : 1;
      p.d.style.transform = `translateY(${((1 - e) * H * dir).toFixed(1)}px)`;
      show(p.d, t >= t0 - .02);
      setSrc(p.img, partUrl(p.pid, t, c.a));
      p.img.style.transform = tfKB(kenBurns(p.k % 2 ? 'zoom_ra' : 'zoom_vao', u, (c.loai_nguon || [])[p.k] === 'anh' ? .8 : .45), 1, 1);
      if (p.nhan) {
        const v = P(t, t0 + .45, .55);
        p.nhan._g.style.opacity = v.toFixed(3);
        p.nhan._t.forEach((x, j) => { const w = P(t, t0 + .5 + j * .18, .5); x.style.opacity = w.toFixed(3); x.style.transform = `translateY(${((1 - w) * 26).toFixed(1)}px)`; });
      }
    }
    o.bg.style.opacity = P(t, het - .2, .3).toFixed(3);
  }
}

// ---------------- lớp màu phim, hạt, loé, màn đen, khung điện ảnh ----------------
mk('div', '', stage).id = 'mau';
mk('div', '', stage).id = 'vignette';
mk('div', '', stage).id = 'day_toi';
const HAT = mk('div', '', stage); HAT.id = 'hat';
const LOE = mk('div', '', stage); LOE.id = 'loe';
const TRANG = mk('div', '', stage); TRANG.id = 'trang';
const MAN = mk('div', '', stage); MAN.id = 'man'; show(MAN, false);
const DEN = mk('div', '', stage); DEN.id = 'den';
const BAR_T = mk('div', 'bar', stage); BAR_T.id = 'bar_tren';
const BAR_D = mk('div', 'bar', stage); BAR_D.id = 'bar_duoi';
const MO_DAU_0 = (KH.do_hoa || []).filter(d => d.loai === 'mo_dau').map(d => d.tu)[0];
const BAR_HET = KH.dien_anh === false ? -1 : (MO_DAU_0 != null ? MO_DAU_0 : -1);
// CÚ DROP (người dùng 13/11/2026: đoạn đầu phải có lực): mỗi mo_dau (trừ drop:false) = loé trắng + rung khung 0,4 s đúng lúc chữ đập vào
const DROP = (KH.do_hoa || []).filter(d => d.loai === 'mo_dau' && d.drop !== false).map(d => d.tu);

function veMau(t) {
  const f = Math.floor(t * FPS);
  HAT.style.backgroundPosition = `${(f * 73) % 256}px ${(f * 151) % 256}px`;
  const b = BAR_HET > 0 ? 132 * (1 - P(t, BAR_HET - .02, .32, E.outC)) : 0;
  BAR_T.style.height = b.toFixed(1) + 'px'; BAR_D.style.height = b.toFixed(1) + 'px';
  show(BAR_T, b > .5); show(BAR_D, b > .5);
  let den = 0;                                                   // vào THẲNG hình ở khung 0 (khung đầu = ảnh xem trước YouTube)
  if (KH.dur - t < .5) den = Math.max(den, P(t, KH.dur - .5, .5, E.ioS)); // tắt dần cuối
  DEN.style.opacity = den.toFixed(3);
}

// ---------------- ghép cảnh + chuyển cảnh ----------------
const CAT_O_SAU = 1e-6;
function apDung(o, s) {
  show(o.root, true);
  css(o.root, { opacity: (s.o ?? 1).toFixed ? (s.o ?? 1).toFixed(3) : String(s.o), transform: s.tf || 'none', filter: s.f || 'none', clipPath: s.clip || 'none' });
}
function ghepCanh(t) {
  const vis = SC.filter(o => t >= o.c.a - 1e-6 && t <= o.c.b + 1e-6);
  for (const o of SC) if (!vis.includes(o)) show(o.root, false);
  let loe = 0, trang = 0, man = null;
  if (vis.length === 1) apDung(vis[0], {});
  else if (vis.length >= 2) {
    const ra = vis[vis.length - 2], vao = vis[vis.length - 1];
    for (const o of vis.slice(0, -2)) show(o.root, false);
    const c = vao.c, d = Math.max(.01, c.d_in), u = clamp((t - (c.tu - d / 2)) / d);
    let A = {}, B = {};
    switch (c.chuyen) {
      case 'cat': if (t < c.tu) B = { o: 0 }; else A = { o: 0 }; break;
      case 'hoa_tan': B = { o: E.ioS(u) }; break;
      case 'zoom_muot': {                       // ZOOM MƯỢT: cảnh cũ đẩy vào 1 → 1,18, cảnh mới thu 1,12 → 1 chồng lên từ từ (không loé, không nhoè)
        const e = E.ioS(u);
        A = { tf: `scale(${(1 + .18 * e).toFixed(4)})` };
        B = { o: e, tf: `scale(${(1.12 - .12 * E.outC(u)).toFixed(4)})` };
        break;
      }
      case 'nhoe': { const b = Math.sin(Math.PI * u); A = { f: `brightness(${(1 + .25 * b).toFixed(3)})` }; B = { o: E.ioS(u), f: `brightness(${(1 + .25 * b).toFixed(3)})` }; break; }
      case 'lia': case 'lia_doc': {           // TRƯỢT CÓ CHIỀU SÂU: cảnh cũ lùi chậm + tối dần, cảnh mới trượt phủ lên (êm, sắc nét)
        const e = E.ioC(u), doc = c.chuyen === 'lia_doc';
        A = { tf: (doc ? `translateY(${(-H * .3 * e).toFixed(1)}px)` : `translateX(${(-W * .3 * e).toFixed(1)}px)`) + ` scale(${(1 - .05 * e).toFixed(4)})`,
          f: `brightness(${(1 - .5 * e).toFixed(3)})` };
        B = { tf: doc ? `translateY(${(H * (1 - e)).toFixed(1)}px)` : `translateX(${(W * (1 - e)).toFixed(1)}px)` };
        break;
      }
      case 'zoom': {                            // zoom xuyên sắc nét: cảnh cũ phóng vụt → loé → cảnh mới thu từ 1,3 về 1
        if (u < .5) { A = { tf: `scale(${(1 + .45 * E.inC(u * 2)).toFixed(4)})` }; B = { o: 0 }; }
        else { A = { o: 0 }; B = { tf: `scale(${(1.3 - .3 * E.outC((u - .5) * 2)).toFixed(4)})` }; }
        trang = .55 * Math.max(0, 1 - Math.abs(u - .5) * 5); break;
      }
      case 'phong': {                           // cắt + PHÓNG: cắt cứng ở tu, cảnh mới đập vào từ 1,22 về 1 (nhịp hook)
        if (t < c.tu) { A = { tf: `scale(${(1 + .06 * P(t, c.tu - .15, .15, E.inC)).toFixed(4)})` }; B = { o: 0 }; }
        else { A = { o: 0 }; B = { tf: `scale(${(1.22 - .22 * P(t, c.tu, .32, E.outC)).toFixed(4)})` }; trang = .35 * (1 - P(t, c.tu, .18, E.outC)); }
        break;
      }
      case 'loe': { B = { o: E.ioS(u) }; loe = Math.pow(Math.sin(Math.PI * u), .8); trang = .1 * Math.pow(Math.sin(Math.PI * u), 3); break; }
      case 'truot': {                           // ĐẨY NGANG: 2 cảnh cùng trượt, êm
        const e = E.ioC(u);
        A = { tf: `translateX(${(-W * e).toFixed(1)}px)` };
        B = { tf: `translateX(${(W * (1 - e)).toFixed(1)}px)` }; break;
      }
      case 'man': {
        const e = E.ioC(u), k = Math.tan(18 * Math.PI / 180) * H / 2;
        const bx = lerp(-k - 300, W + k + 300, e);
        B = { clip: `polygon(0 0, ${(bx + k).toFixed(1)}px 0, ${(bx - k).toFixed(1)}px ${H}px, 0 ${H}px)` };
        man = bx; break;
      }
      default: B = { o: E.ioS(u) };
    }
    if (c.bo_cuc === 'ghep') { A = {}; B = {}; }       // ô ghép tự trượt vào, cảnh trước nằm dưới tới khi phủ kín
    ra.root.style.zIndex = '1'; vao.root.style.zIndex = '2';
    apDung(ra, A); apDung(vao, B);
  }
  for (const o of vis) veCanh(o, t);
  let rung = 0;
  for (const dt of DROP) if (t >= dt - .02 && t < dt + .5) {
    trang = Math.max(trang, .9 * (1 - P(t, dt, .38, E.outC)));
    rung = 1 - P(t, dt, .42, E.outC);
  }
  CL.style.transform = rung > .01 ? `translate(${(Math.sin(t * 97) * 14 * rung).toFixed(1)}px, ${(Math.cos(t * 83) * 10 * rung).toFixed(1)}px) scale(${(1 + .03 * rung).toFixed(4)})` : 'none';
  LOE.style.opacity = loe.toFixed(3);
  LOE.style.transform = `translateX(${(Math.sin(t * .9) * 160).toFixed(1)}px) rotate(${(t * 6 % 360).toFixed(1)}deg)`;
  TRANG.style.opacity = trang.toFixed(3);
  if (man != null) { show(MAN, true); MAN.style.transform = `translateX(${(man - 260).toFixed(1)}px) rotate(18deg)`; } else show(MAN, false);
}

// ---------------- đo chữ ----------------
function rong(el) { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect().width; }
function vua(el, base, maxW, min = .42) {
  el.style.fontSize = base + 'px';
  const w = rong(el);
  const s = w > maxW ? Math.max(min, maxW / w) : 1;
  el.style.fontSize = (base * s).toFixed(1) + 'px';
  return base * s;
}
/** chữ khoá: vừa 1 dòng ở ≥ 82 % cỡ gốc thì 1 dòng, không thì ngắt 2 dòng cân rồi mới co. → mảng phần tử dòng */
function dong2(parent, text, base, maxW, cls = '') {
  parent.innerHTML = '';
  const one = mk('span', 'dong ' + cls, parent, esc(text));
  one.style.fontSize = base + 'px';
  const w = rong(one);
  const ws = words(text);
  if (w <= maxW || ws.length < 2 || w <= maxW / .82) { vua(one, base, maxW); return [one]; }
  parent.innerHTML = '';
  let best = null;
  for (let j = 1; j < ws.length; j++) {
    const a = ws.slice(0, j).join(' '), b = ws.slice(j).join(' ');
    const ta = mk('span', 'dong', parent, esc(a)); ta.style.fontSize = base + 'px';
    const tb = mk('span', 'dong', parent, esc(b)); tb.style.fontSize = base + 'px';
    const m = Math.max(rong(ta), rong(tb)); parent.innerHTML = '';
    if (!best || m < best.m) best = { a, b, m };
  }
  const s = Math.min(1, maxW / best.m);
  return [best.a, best.b].map(x => { const e = mk('span', 'dong ' + cls, parent, esc(x)); e.style.fontSize = (base * Math.max(.42, s)).toFixed(1) + 'px'; return e; });
}
function bocMask(el) {     // dòng chữ trượt lên trong mặt nạ
  const m = document.createElement('span'); m.className = 'mask';
  el.parentNode.insertBefore(m, el); m.appendChild(el); el.style.display = 'block';
  return el;
}
const VUNG = { trai: { x: 130, w: 820 }, phai: { x: 980, w: 820 }, giua: { x: 210, w: 1500 } };
const LOP = mk('div', '', stage); LOP.id = 'lop';
const HOP = [];     // chữ cần tự kiểm đè nhau
function scrim(parent, vt, d0 = .62) {
  const s = mk('div', 'man_toi', parent);
  if (vt === 'trai') css(s, { left: 0, top: 0, width: '1300px', height: '1080px', background: `linear-gradient(90deg, rgba(0,0,0,${d0}) 0%, rgba(0,0,0,${d0 * .62}) 45%, rgba(0,0,0,0) 100%)` });
  else if (vt === 'phai') css(s, { right: 0, top: 0, width: '1300px', height: '1080px', background: `linear-gradient(270deg, rgba(0,0,0,${d0}) 0%, rgba(0,0,0,${d0 * .62}) 45%, rgba(0,0,0,0) 100%)` });
  else css(s, { left: 0, top: 0, width: '1920px', height: '1080px', background: `radial-gradient(ellipse 58% 46% at 50% 45%, rgba(0,0,0,${d0}) 0%, rgba(0,0,0,${d0 * .5}) 55%, rgba(0,0,0,0) 100%)` });
  return s;
}
function khoi(vt, y = 470) {   // khối chữ căn theo vùng, tâm dọc ở y (mặc định 470 — trên sub)
  const b = mk('div', 'abs');
  const z = VUNG[vt] || VUNG.giua;
  css(b, { left: z.x + 'px', width: z.w + 'px', top: (y - 470) + 'px', height: '940px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
    alignItems: vt === 'giua' ? 'center' : 'flex-start', textAlign: vt === 'giua' ? 'center' : 'left' });
  return b;
}
function vaoRa(t, d, ra = .45) { return { on: t >= d.tu - .02 && t <= d.den + .02, r: P(t, d.den - ra, ra, E.inC) }; }
const tachChu = (parent, text) => chars(text).map(ch => mk('span', 'ch', parent, esc(ch)));

// bản đồ Việt Nam cách điệu (đường viền Natural Earth, LUÔN có Hoàng Sa / Trường Sa)
const VN = window.VN_BAN_DO || null;
function chieu(lat, lon, bb, w, h) {        // equirectangular có hiệu chỉnh cos(vĩ độ giữa)
  const k = Math.cos((bb[1] + bb[3]) / 2 * Math.PI / 180);
  const sx = w / ((bb[2] - bb[0]) * k), sy = h / (bb[3] - bb[1]), s = Math.min(sx, sy);
  const ox = (w - (bb[2] - bb[0]) * k * s) / 2, oy = (h - (bb[3] - bb[1]) * s) / 2;
  return [ox + (lon - bb[0]) * k * s, oy + (bb[3] - lat) * s];
}
function svgBanDo(w, h, mau = 'rgba(255,246,230,.9)') {
  if (!VN) return '';
  const bb = VN.bbox;
  const path = VN.duong.map(ring => 'M' + ring.map(([lo, la]) => chieu(la, lo, bb, w, h).map(v => v.toFixed(1)).join(',')).join('L') + 'Z').join('');
  const dao = (VN.dao || []).map(q => {
    const pts = q.diem.map(([la, lo]) => chieu(la, lo, bb, w, h));
    const nhan = chieu(q.nhan[0], q.nhan[1], bb, w, h);
    return pts.map(p => `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${(w / 210).toFixed(1)}" fill="${mau}"/>`).join('') +
      `<text x="${nhan[0].toFixed(1)}" y="${nhan[1].toFixed(1)}" fill="rgba(255,246,230,.75)" font-family="BVP" font-weight="600" font-size="${(w / 24).toFixed(1)}" text-anchor="middle">${esc(q.ten)}</text>`;
  }).join('');
  return `<path d="${path}" fill="rgba(244,198,106,.16)" stroke="${mau}" stroke-width="${(w / 170).toFixed(1)}" stroke-linejoin="round"/>${dao}`;
}
const LAM = {};
// 1. MỞ ĐẦU — CÚ DROP: tên chủ đề ĐẬP vào trọn chữ ngay khung đầu (phóng 1,28 → 1 trong 0,32 s), vệt sáng vàng quét qua,
//    dòng chữ in giãn trên, viết tay vàng quét ngay sau 0,2 s, dòng dưới. Kèm loé trắng + rung khung (ghepCanh) + tiếng nổ trầm.
//    Người dùng 13/11/2026: "đoạn đầu edit chưa oki" — chữ phải hiện NGAY (≤ 0,4 s), không chạy từng chữ, không nhoè.
LAM.mo_dau = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .5);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const tren = d.tren ? mk('div', '', b) : null;
  let l1, l2, trenTxt;
  if (tren) {
    css(tren, { display: 'flex', alignItems: 'center', gap: '26px', marginBottom: '14px' });
    l1 = mk('div', 'vach', tren); css(l1, { position: 'relative', width: '150px' });
    trenTxt = mk('div', 'caps', tren, esc(d.tren)); css(trenTxt, { fontSize: '34px', color: 'var(--kem)', textShadow: '0 2px 12px rgba(0,0,0,.6)' });
    l2 = mk('div', 'vach', tren); css(l2, { position: 'relative', width: '150px' });
  }
  const chinh = mk('div', 'serif chu_drop', b, esc(d.chinh)); css(chinh, { whiteSpace: 'nowrap', lineHeight: '1' });
  const tay = d.viet_tay ? mk('div', 'tay', b, esc(d.viet_tay)) : null;
  const duoi = d.duoi ? mk('div', 'caps', b, esc(d.duoi)) : null;
  if (duoi) css(duoi, { fontSize: '28px', color: 'rgba(255,246,230,.92)', marginTop: '26px', letterSpacing: '.34em', textShadow: '0 2px 12px rgba(0,0,0,.7)' });
  return {
    el, init() {
      const co = vua(chinh, d.co || 230, VUNG[d.vi_tri].w * .94);
      if (tay) { vua(tay, 96, VUNG[d.vi_tri].w * .9); css(tay, { marginTop: (co * .02) + 'px', transform: 'rotate(-3deg)' }); }
      HOP.push({ el: chinh, d }); if (tay) HOP.push({ el: tay, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .35); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .2) * (1 - v.r)).toFixed(3);
      const e = P(t, d.tu, .32, E.outC);
      chinh.style.opacity = P(t, d.tu - .02, .08).toFixed(3);
      chinh.style.transform = `scale(${(1.28 - .28 * e).toFixed(4)})`;
      chinh.style.letterSpacing = (.12 - .09 * P(t, d.tu, .9, E.outE)).toFixed(4) + 'em';
      chinh.style.backgroundPosition = `${(100 - 100 * P(t, d.tu + .2, .9, E.ioS)).toFixed(1)}% 50%`;
      if (tren) {
        const a = P(t, d.tu + .04, .25, E.outC);
        trenTxt.style.opacity = a.toFixed(3); trenTxt.style.letterSpacing = (.6 - .2 * a).toFixed(3) + 'em';
        l1.style.transform = `scaleX(${a.toFixed(3)})`; l1.style.transformOrigin = '100% 50%';
        l2.style.transform = `scaleX(${a.toFixed(3)})`; l2.style.transformOrigin = '0% 50%';
      }
      if (tay) { const w = P(t, d.tu + .2, .5, E.outC); tay.style.clipPath = `inset(-20% ${((1 - w) * 100).toFixed(1)}% -20% -5%)`; }
      if (duoi) { const a = P(t, d.tu + .35, .3); duoi.style.opacity = a.toFixed(3); duoi.style.transform = `translateY(${((1 - a) * 14).toFixed(1)}px)`; }
      b.style.opacity = (1 - v.r).toFixed(3);
      b.style.transform = `scale(${(1 + .03 * v.r).toFixed(4)})`;
    },
  };
};

// 1b. HOOK_TU — chữ khoá của từng vế câu hook: KHỐI CHỮ in đậm đập vào ĐÚNG khung cắt (≤ 0,25 s), nhãn địa danh nhỏ có ghim,
//     hoặc kieu "cau" = câu hỏi serif nghiêng (khung đầu video). Tắt gọn ở den (0,12 s) — cảnh sau có chữ mới.
LAM.hook_tu = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const cau = d.kieu === 'cau';
  const sc = scrim(el, d.vi_tri, cau ? .62 : .45);
  const b = khoi(d.vi_tri, d.y ?? (cau ? 560 : 520)); el.appendChild(b);
  const nh = d.nhan ? mk('div', '', b) : null;
  if (nh) {
    css(nh, { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' });
    const ic = mk('span', '', nh, icon(d.icon || 'ghim')); css(ic, { width: '42px', height: '42px', color: 'var(--vang)', display: 'inline-flex', filter: 'drop-shadow(0 2px 6px rgba(0,0,0,.7))' });
    const tx = mk('span', 'caps', nh, esc(d.nhan)); css(tx, { fontSize: '34px', color: 'var(--vang)', letterSpacing: '.3em', textShadow: '0 2px 10px rgba(0,0,0,.75)' });
  }
  const chu = mk('div', cau ? 'bong_chu' : 'kem_grad', b, esc(d.chu));
  if (cau) css(chu, { fontFamily: 'PFI', fontWeight: '700', color: '#FFFFFF', lineHeight: '1.1', whiteSpace: 'nowrap',
    textShadow: '0 3px 18px rgba(0,0,0,.85), 0 1px 3px rgba(0,0,0,.8)' });
  else css(chu, { fontFamily: 'AN', lineHeight: '1', letterSpacing: '.02em', whiteSpace: 'nowrap', textTransform: 'uppercase' });
  return {
    el, init() { vua(chu, d.co || (cau ? 92 : 190), VUNG[d.vi_tri].w * .96); HOP.push({ el: chu, d }); },
    ve(t) {
      const on = t >= d.tu - .02 && t < d.den; show(el, on); if (!on) return;
      const r = P(t, d.den - .12, .12, E.inC);
      sc.style.opacity = ((d.tu <= .01 ? 1 : P(t, d.tu, .12)) * (1 - r)).toFixed(3);
      const ngay = d.tu <= .01;                 // chữ ở khung 0 (ảnh xem trước YouTube) phải ĐỦ ngay, không chạy vào
      const e = ngay ? 1 : P(t, d.tu, .25, E.outC);
      chu.style.opacity = ngay ? '1' : P(t, d.tu - .02, .06).toFixed(3);
      chu.style.transform = `scale(${(1.25 - .25 * e + .04 * P(t, d.tu + .25, d.den - d.tu, E.lin)).toFixed(4)})`;
      if (nh) { const a = P(t, d.tu + .08, .2, E.outC); nh.style.opacity = a.toFixed(3); nh.style.transform = `translateX(${((1 - a) * -30).toFixed(1)}px)`; }
      b.style.opacity = (1 - r).toFixed(3);
    },
  };
};

// 2. CHƯƠNG — số viền vàng tô dần + "ĐIỂM ĐẾN" + TÊN serif lớn + dòng mô tả; đặt ở vùng trống cạnh thẻ dọc
LAM.chuong = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .66);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const hang = mk('div', '', b); css(hang, { display: 'flex', alignItems: 'flex-end', gap: '30px', marginBottom: '8px' });
  const so = mk('div', 'so_vien', hang, esc(d.so || '01'));
  const so2 = mk('div', 'to', so, esc(d.so || '01'));
  const nh = mk('div', 'nhan_chuong', hang); css(nh, { marginBottom: '38px' });
  const g = mk('div', 'gach', nh);
  const nt = mk('div', 'caps', nh, esc(d.nhan || T.dan_chuong || 'Điểm đến')); css(nt, { fontSize: '30px', color: 'var(--vang)' });
  const ten = mk('div', '', b); css(ten, { lineHeight: '1.02' });
  const phu = d.phu ? mk('div', '', b) : null;
  if (phu) { css(phu, { display: 'flex', alignItems: 'center', gap: '14px', marginTop: '22px', fontWeight: '600', fontSize: '38px', color: 'var(--kem)' });
    const ic = mk('span', '', phu, icon(d.icon || 'ghim')); css(ic, { width: '40px', height: '40px', color: 'var(--vang)', display: 'inline-flex' });
    mk('span', 'bong_chu', phu, esc(d.phu)); }
  // thẻ bản đồ góc: Việt Nam (có Hoàng Sa, Trường Sa) + ghim toả sóng ở điểm đến — khi có toa_do
  let the = null;
  if (d.toa_do && VN) {
    const mw = 230, mh = 262, phaiThe = d.vi_tri !== 'phai';
    the = mk('div', 'abs', el);
    css(the, { [phaiThe ? 'right' : 'left']: '96px', top: '64px', width: (mw + 36) + 'px', padding: '18px 18px 14px', borderRadius: '24px',
      background: 'linear-gradient(170deg, rgba(18,22,30,.78), rgba(8,10,14,.70))', boxShadow: '0 20px 50px rgba(0,0,0,.45), inset 0 0 0 1.5px rgba(244,198,106,.45)' });
    const [px, py] = chieu(d.toa_do[0], d.toa_do[1], VN.bbox, mw, mh);
    the.innerHTML = `<svg width="${mw}" height="${mh}" viewBox="0 0 ${mw} ${mh}" style="display:block;overflow:visible">${svgBanDo(mw, mh, 'rgba(255,246,230,.85)')}
      <circle class="song_ghim" cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="10" fill="none" stroke="#F4C66A" stroke-width="3"/>
      <circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="7.5" fill="#FF3B3B" stroke="#FFF6E6" stroke-width="2.5"/></svg>`;
    const nt2 = mk('div', 'caps', the, esc(d.ten_ngan || d.ten)); css(nt2, { fontSize: '19px', color: 'var(--vang)', textAlign: 'center', marginTop: '8px', letterSpacing: '.22em', whiteSpace: 'nowrap', overflow: 'hidden' });
    the._song = the.querySelector('.song_ghim');
  }
  let dong = [];
  return {
    el, init() {
      dong = dong2(ten, d.ten, d.co || 150, VUNG[d.vi_tri].w * .98, 'serif kem_grad').map(bocMask);
      if (d.vi_tri === 'giua') hang.style.justifyContent = 'center';
      HOP.push({ el: ten, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      const e0 = P(t, d.tu, .3, E.outE);
      so.style.opacity = e0.toFixed(3); so.style.transform = `translateX(${((1 - e0) * -50).toFixed(1)}px)`;
      const f = P(t, d.tu + .15, .6, E.ioS); so2.style.clipPath = `inset(${((1 - f) * 100).toFixed(1)}% 0 0 0)`;
      const e1 = P(t, d.tu + .05, .35, E.outE); g.style.transform = `scaleX(${e1.toFixed(3)})`; g.style.transformOrigin = '0 50%';
      nt.style.opacity = e1.toFixed(3); nt.style.letterSpacing = (.6 - .28 * e1).toFixed(3) + 'em';
      dong.forEach((x, i) => { const e = P(t, d.tu + .05 + i * .08, .4, E.outC); x.style.transform = `translateY(${((1 - e) * 105).toFixed(1)}%)`; });
      if (phu) { const e = P(t, d.tu + .3, .35); phu.style.opacity = e.toFixed(3); phu.style.transform = `translateY(${((1 - e) * 18).toFixed(1)}px)`; }
      b.style.opacity = (1 - v.r).toFixed(3); b.style.transform = `translateX(${(-40 * v.r).toFixed(1)}px)`;
      if (the) {
        const e = P(t, d.tu + .25, .4, E.outB);
        the.style.opacity = (P(t, d.tu + .25, .2) * (1 - v.r)).toFixed(3); the.style.transform = `scale(${(.7 + .3 * e).toFixed(3)})`;
        the.style.transformOrigin = d.vi_tri !== 'phai' ? '100% 0' : '0 0';
        const r = ((t - d.tu) % 1.4 + 1.4) % 1.4 / 1.4;
        the._song.setAttribute('r', (8 + 26 * r).toFixed(1)); the._song.setAttribute('opacity', (1 - r).toFixed(3));
      }
    },
  };
};

// 3. ĐỊA DANH — thẻ góc dưới (lower third): vòng vàng có icon, tên serif, dòng nhỏ chữ in giãn
LAM.dia_danh = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const g = mk('div', 'man_toi', el);
  const phai = d.vi_tri === 'phai';
  css(g, { [phai ? 'right' : 'left']: 0, top: '560px', width: '1100px', height: '420px',
    background: `radial-gradient(ellipse 60% 55% at ${phai ? '80%' : '20%'} 60%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 100%)` });
  const k = mk('div', 'abs', el);
  const tron = mk('div', 'ld_tron', k, icon(d.icon || 'ghim')); css(tron, { width: '96px', height: '96px' });
  const ten = mk('div', 'abs serif bong_chu', k, esc(d.ten)); css(ten, { fontWeight: '800', color: 'var(--kem)', whiteSpace: 'nowrap' });
  const phu = d.phu ? mk('div', 'abs caps', k, esc(d.phu)) : null;
  if (phu) css(phu, { fontSize: '27px', color: 'var(--vang)', whiteSpace: 'nowrap', textShadow: '0 2px 10px rgba(0,0,0,.7)' });
  const vach = mk('div', 'abs', k); css(vach, { height: '3px', background: 'linear-gradient(90deg, var(--vang), rgba(244,198,106,0))' });
  return {
    el, init() {
      const co = vua(ten, 78, 820);
      const wt = rong(ten), wp = phu ? rong(phu) : 0, wmax = Math.max(wt, wp);
      const x0 = phai ? W - 96 - 84 - 26 - wmax : 96, by = 830;          // đáy khối y 830 (trên sub)
      css(k, { left: '0px', top: '0px' });
      css(tron, { left: (phai ? W - 96 - 96 : 96) + 'px', top: (by - 96 - (phu ? 14 : 0)) + 'px' });
      const tx = phai ? x0 - 12 : 96 + 96 + 28;
      css(ten, { left: tx + 'px', top: (by - co * 1.18 - (phu ? 46 : 0)) + 'px', textAlign: phai ? 'right' : 'left', width: wmax + 'px' });
      if (phu) css(phu, { left: tx + 'px', top: (by - 34) + 'px', textAlign: phai ? 'right' : 'left', width: wmax + 'px' });
      css(vach, { left: tx + 'px', top: (by - (phu ? 46 : 0) + 4) + 'px', width: Math.min(wmax, 460) + 'px' });
      if (phai) vach.style.background = 'linear-gradient(270deg, var(--vang), rgba(244,198,106,0))', vach.style.left = (tx + wmax - Math.min(wmax, 420)) + 'px';
      HOP.push({ el: ten, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      g.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      const e0 = P(t, d.tu, .55, E.outB);
      tron.style.transform = `scale(${e0.toFixed(3)}) rotate(${((1 - e0) * -90).toFixed(1)}deg)`;
      const e1 = P(t, d.tu + .06, .38, E.outC);
      ten.style.clipPath = phai ? `inset(-30% -5% -30% ${((1 - e1) * 100).toFixed(1)}%)` : `inset(-30% ${((1 - e1) * 100).toFixed(1)}% -30% -5%)`;
      ten.style.transform = `translateX(${((1 - e1) * (phai ? 30 : -30)).toFixed(1)}px)`;
      const e2 = P(t, d.tu + .2, .4, E.outC);
      vach.style.transform = `scaleX(${e2.toFixed(3)})`; vach.style.transformOrigin = phai ? '100% 50%' : '0 50%';
      if (phu) { phu.style.opacity = e2.toFixed(3); phu.style.letterSpacing = (.5 - .2 * e2).toFixed(3) + 'em'; }
      k.style.opacity = (1 - v.r).toFixed(3); k.style.transform = `translateX(${(v.r * (phai ? 40 : -40)).toFixed(1)}px)`;
    },
  };
};

// 4. TỪ KHOÁ — từng chữ bật đúng giây đọc (kiểu serif / tay / sans)
LAM.tu_khoa = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .5);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const hang = mk('div', '', b); css(hang, { display: 'flex', alignItems: 'baseline', gap: '30px', whiteSpace: 'nowrap', flexWrap: 'nowrap' });
  const ms = (d.muc || []).map(m => {
    const k = m.kieu || 'serif';
    const e = mk('span', k === 'tay' ? 'tay' : (k === 'sans' ? 'bong_chu' : 'serif kem_grad'), hang, esc(m.chu));
    if (k === 'sans') css(e, { fontWeight: '900', textTransform: 'uppercase', color: 'var(--kem)' });
    e.style.display = 'inline-block';
    return { e, m, k };
  });
  return {
    el, init() {
      const base = d.co || 120;
      ms.forEach(x => x.e.style.fontSize = (base * (x.k === 'tay' ? 1.0 : (x.k === 'sans' ? .8 : 1))) + 'px');
      const w = rong(hang), mw = VUNG[d.vi_tri].w;
      if (w > mw) ms.forEach(x => x.e.style.fontSize = (parseFloat(x.e.style.fontSize) * mw / w).toFixed(1) + 'px');
      HOP.push({ el: hang, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      for (const x of ms) {
        const e = P(t, x.m.luc, .5, E.outB), a = P(t, x.m.luc, .3);
        x.e.style.opacity = a.toFixed(3);
        x.e.style.transform = `translateY(${((1 - P(t, x.m.luc, .5)) * 40).toFixed(1)}px) scale(${(.75 + .25 * e).toFixed(4)})`;
        if (x.k === 'tay') x.e.style.clipPath = `inset(-30% ${((1 - P(t, x.m.luc, .7, E.ioS)) * 100).toFixed(1)}% -30% -5%)`;
      }
      b.style.opacity = (1 - v.r).toFixed(3);
    },
  };
};

// 5. TIÊU ĐỀ ĐOẠN — dòng dẫn chữ in + chữ khoá serif vàng (2 dòng cân) + viết tay kem
LAM.tieu_de = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .55);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const dan = d.dan ? mk('div', 'caps', b, esc(d.dan)) : null;
  if (dan) css(dan, { fontSize: '36px', color: 'var(--vang)', marginBottom: '64px', textShadow: '0 2px 12px rgba(0,0,0,.6)' });
  const khoa = mk('div', '', b); css(khoa, { lineHeight: '1.0' });
  const tay = d.viet_tay ? mk('div', 'tay', b, esc(d.viet_tay)) : null;
  if (tay) css(tay, { color: 'var(--kem)', marginTop: '22px', transform: 'rotate(-2deg)' });
  let dong = [];
  return {
    el, init() {
      dong = dong2(khoa, d.khoa, d.co || 150, VUNG[d.vi_tri].w * .97, 'serif vang_grad').map(bocMask);
      if (tay) vua(tay, 84, VUNG[d.vi_tri].w * .9);
      HOP.push({ el: khoa, d }); if (tay) HOP.push({ el: tay, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      if (dan) { const e = P(t, d.tu, .35, E.outE); dan.style.opacity = e.toFixed(3); dan.style.letterSpacing = (.7 - .38 * e).toFixed(3) + 'em'; }
      dong.forEach((x, i) => { const e = P(t, d.tu + .03 + i * .08, .4, E.outC); x.style.transform = `translateY(${((1 - e) * 105).toFixed(1)}%)`; });
      if (tay) { const e = P(t, d.tu + .3, .5, E.outC); tay.style.clipPath = `inset(-30% ${((1 - e) * 100).toFixed(1)}% -30% -5%)`; }
      b.style.opacity = (1 - v.r).toFixed(3); b.style.transform = `scale(${(1 + .03 * v.r).toFixed(4)})`;
    },
  };
};

// 6. CHIP — viên kính có icon vàng, bật lần lượt (mặc định hàng TRÊN, trời thường trống)
LAM.chip = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const ms = (d.muc || []).map(m => {
    const c = mk('div', 'chip', el); mk('div', 'ic', c, icon(m.icon || 'sao')); mk('span', '', c, esc(m.chu));
    return { c, m };
  });
  return {
    el, init() {
      const y = d.y ?? 96, gap = 18;
      const ws = ms.map(x => x.c.getBoundingClientRect().width);
      let tong = ws.reduce((a, b) => a + b, 0) + gap * (ws.length - 1);
      let x = d.vi_tri === 'phai' ? W - 96 - tong : (d.vi_tri === 'giua' ? (W - tong) / 2 : 96);
      if (tong > W - 192) {                         // quá dài → xếp dọc
        ms.forEach((m, i) => css(m.c, { left: (d.vi_tri === 'phai' ? W - 96 - ws[i] : 96) + 'px', top: (y + i * 92) + 'px' }));
      } else ms.forEach((m, i) => { css(m.c, { left: x + 'px', top: y + 'px' }); x += ws[i] + gap; });
      ms.forEach(m => HOP.push({ el: m.c, d }));
    },
    ve(t) {
      const v = vaoRa(t, d, .35); show(el, v.on); if (!v.on) return;
      for (const x of ms) {
        const e = P(t, x.m.luc, .5, E.outB), a = P(t, x.m.luc, .25);
        x.c.style.opacity = (a * (1 - v.r)).toFixed(3);
        x.c.style.transform = `translateY(${((1 - P(t, x.m.luc, .4)) * -24 - v.r * 20).toFixed(1)}px) scale(${(.6 + .4 * e).toFixed(4)})`;
      }
    },
  };
};

// 7. SỐ LỚN — đếm lên đúng giây đọc số
const fmtSo = x => { const s = String(Math.round(x)); return s.replace(/\B(?=(\d{3})+(?!\d))/g, ['vi', 'de', 'id', 'es', 'it', 'pt'].includes(NN) ? '.' : ','); };
LAM.so_lon = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .55);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const hang = mk('div', '', b); css(hang, { display: 'flex', alignItems: 'baseline', gap: '14px', whiteSpace: 'nowrap' });
  const tt = d.tien_to ? mk('span', 'serif kem_grad', hang, esc(d.tien_to)) : null;
  const so = mk('span', 'vang_grad', hang); css(so, { fontFamily: 'AN', fontSize: (d.co || 230) + 'px', lineHeight: '1' });
  const ht = d.hau_to ? mk('span', 'serif kem_grad', hang, esc(d.hau_to)) : null;
  [tt, ht].forEach(x => x && css(x, { fontSize: ((d.co || 230) * .42) + 'px' }));
  const nhan = d.nhan ? mk('div', 'caps', b, esc(d.nhan)) : null;
  if (nhan) css(nhan, { fontSize: '30px', color: 'var(--kem)', marginTop: '6px', textShadow: '0 2px 12px rgba(0,0,0,.6)' });
  const dich = parseFloat(String(d.so).replace(/[^\d.,]/g, '').replace(/\./g, '').replace(',', '.')) || 0;
  const dem = +(d.dem_tu ?? d.tu + .3);
  return {
    el, init() { so.textContent = fmtSo(dich); vua(hang, 1, 99999); HOP.push({ el: hang, d }); },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      so.textContent = fmtSo(dich * P(t, dem, 1.3, E.outE));
      const e = P(t, d.tu, .55, E.outB);
      hang.style.transform = `scale(${(.7 + .3 * e).toFixed(4)})`; hang.style.opacity = P(t, d.tu, .3).toFixed(3);
      if (nhan) { const a = P(t, d.tu + .5, .6); nhan.style.opacity = a.toFixed(3); nhan.style.letterSpacing = (.6 - .28 * a).toFixed(3) + 'em'; }
      b.style.opacity = (1 - v.r).toFixed(3);
    },
  };
};

// 8. LIỆT KÊ — bảng kính tối, dòng dẫn vàng, mục tick vàng hiện đúng giây đọc
LAM.liet_ke = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const bg = mk('div', 'bang', el);
  const dan = d.dan ? mk('div', 'dan', bg, esc(d.dan)) : null;
  const ms = (d.muc || []).map(m => {
    const r = mk('div', 'muc', bg); const tk = mk('div', 'tick', r, icon(m.icon || 'tich')); const tx = mk('span', 'bong_chu', r, esc(m.chu));
    return { r, tk, tx, m };
  });
  return {
    el, init() {
      const wmax = Math.max(...ms.map(x => rong(x.tx))) + 82 + 96, wd = dan ? rong(dan) + 96 : 0;
      const w = Math.min(VUNG[d.vi_tri === 'phai' ? 'phai' : 'trai'].w, Math.max(wmax, wd, 520));
      if (wmax > w) ms.forEach(x => vua(x.tx, 50, w - 82 - 96));
      const h = bg.getBoundingClientRect().height;
      const x = d.vi_tri === 'phai' ? W - 130 - w : (d.vi_tri === 'giua' ? (W - w) / 2 : 130);
      css(bg, { left: x + 'px', top: Math.max(80, 470 - h / 2) + 'px', width: w + 'px' });
      HOP.push({ el: bg, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      const e = P(t, d.tu, .55, E.outE);
      bg.style.opacity = (e * (1 - v.r)).toFixed(3);
      bg.style.transform = `translateX(${((1 - e) * (d.vi_tri === 'phai' ? 60 : -60) + v.r * -30).toFixed(1)}px)`;
      if (dan) dan.style.letterSpacing = (.5 - .22 * e).toFixed(3) + 'em';
      for (const x of ms) {
        const a = P(t, x.m.luc, .45, E.outC), s = P(t, x.m.luc, .5, E.outB);
        x.r.style.opacity = a.toFixed(3); x.r.style.transform = `translateX(${((1 - a) * -36).toFixed(1)}px)`;
        x.tk.style.transform = `scale(${(.4 + .6 * s).toFixed(3)})`;
        x.tk.style.background = `rgba(244,198,106,${(.22 * P(t, x.m.luc + .2, .3)).toFixed(3)})`;
      }
    },
  };
};

// 9. TRÍCH — câu nói nổi bật trong ngoặc kép lớn
LAM.trich = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .6);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const ng = mk('div', 'serif vang_grad', b, '“'); css(ng, { fontSize: '220px', lineHeight: '.6', height: '110px' });
  const noi = mk('div', 'bong_chu', b); css(noi, { fontFamily: 'PFI', fontWeight: '600', fontSize: (d.co || 68) + 'px', lineHeight: '1.2', maxWidth: (VUNG[d.vi_tri].w * .92) + 'px' });
  const ws = words(d.noi).map(w => mk('span', 'ch', noi, esc(w + ' ')));
  const tg = d.tac_gia ? mk('div', 'tay', b, esc('— ' + d.tac_gia)) : null; if (tg) css(tg, { fontSize: '60px', marginTop: '16px' });
  return {
    el, init() { HOP.push({ el: noi, d }); },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      ng.style.opacity = P(t, d.tu, .4).toFixed(3); ng.style.transform = `scale(${(.6 + .4 * P(t, d.tu, .6, E.outB)).toFixed(3)})`;
      const L = Math.max(.6, (d.den - d.tu) * .45);
      ws.forEach((w, i) => { const e = P(t, d.tu + .2 + i * L / ws.length, .4); w.style.opacity = (.12 + .88 * e).toFixed(3); });
      if (tg) tg.style.opacity = P(t, d.tu + .3 + L, .5).toFixed(3);
      b.style.opacity = (1 - v.r).toFixed(3);
    },
  };
};

// 10. BẢN ĐỒ — Việt Nam, ghim rơi đúng giây đọc tên
LAM.ban_do = d => {
  const el = mk('div', 'dh', LOP); css(el, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const sc = scrim(el, d.vi_tri, .62);
  const mw = 520, mh = 880, x0 = d.vi_tri === 'phai' ? W - 140 - mw : (d.vi_tri === 'giua' ? (W - mw) / 2 : 140), y0 = 70;
  const box = mk('div', 'abs', el); css(box, { left: x0 + 'px', top: y0 + 'px', width: mw + 'px', height: mh + 'px' });
  box.innerHTML = `<svg width="${mw}" height="${mh}" viewBox="0 0 ${mw} ${mh}">${svgBanDo(mw, mh)}</svg>`;
  const bb = VN ? VN.bbox : [102, 8, 110, 23.5];
  const ps = (d.diem || []).map(p => {
    const [x, y] = chieu(p.toa_do[0], p.toa_do[1], bb, mw, mh);
    const g = mk('div', 'abs', box); css(g, { left: x + 'px', top: y + 'px' });
    const vong = mk('div', 'abs', g); css(vong, { left: '-30px', top: '-30px', width: '60px', height: '60px', borderRadius: '50%', border: '3px solid var(--vang)' });
    const ghim = mk('div', 'abs', g, icon('ghim')); css(ghim, { left: '-24px', top: '-50px', width: '48px', height: '48px', color: 'var(--vang)', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,.6))' });
    ghim.querySelector('svg').setAttribute('fill', 'rgba(244,198,106,.95)');
    const ten = mk('div', 'abs bong_chu', g, esc(p.ten)); const trai = p.nhan === 'trai';
    css(ten, { top: '-34px', [trai ? 'right' : 'left']: '34px', fontWeight: '800', fontSize: '38px', whiteSpace: 'nowrap', color: 'var(--kem)' });
    return { g, vong, ghim, ten, p };
  });
  return {
    el, init() {},
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      const e = P(t, d.tu, .8, E.outE);
      box.style.opacity = (e * (1 - v.r)).toFixed(3); box.style.transform = `translateY(${((1 - e) * 40).toFixed(1)}px) scale(${(.94 + .06 * e).toFixed(3)})`;
      for (const x of ps) {
        const l = +(x.p.luc ?? d.tu + .5), a = P(t, l, .45, E.outB);
        x.ghim.style.opacity = P(t, l, .2).toFixed(3); x.ghim.style.transform = `translateY(${((1 - P(t, l, .45, E.outC)) * -60).toFixed(1)}px) scale(${(.6 + .4 * a).toFixed(3)})`;
        const r = ((t - l) % 1.6 + 1.6) % 1.6 / 1.6; x.vong.style.opacity = t >= l ? ((1 - r) * .9).toFixed(3) : '0'; x.vong.style.transform = `scale(${(.3 + 1.2 * r).toFixed(3)})`;
        x.ten.style.opacity = P(t, l + .2, .4).toFixed(3);
      }
    },
  };
};

const DH = (KH.do_hoa || []).map(d => { const f = LAM[d.loai]; if (!f) { console.error('loại đồ hoạ lạ: ' + d.loai); return null; } const g = f(d); g.d = d; return g; }).filter(Boolean);

// ---------------- sub karaoke ----------------
const SUB = mk('div', '', stage); SUB.id = 'sub';
css(SUB, { bottom: (H - 990) + 'px' });
let subCum = -1, subW = [];
function veSub(t) {
  const ds = KH.sub || [];
  const cta = KH.cta;
  let k = -1;
  for (let i = 0; i < ds.length; i++) if (ds[i].tu <= t && t < ds[i].den) { k = i; break; }
  if (cta && t >= cta.tu + .35) k = -1;               // màn kết có chữ riêng
  if (k !== subCum) {
    SUB.innerHTML = ''; subW = []; subCum = k;
    if (k >= 0) for (const dg of ds[k].dong) {
      const line = mk('div', 'sd', SUB);
      dg.forEach((w, j) => { const s = mk('span', 'w', line, esc(w.w)); subW.push({ s, w }); if (j < dg.length - 1) line.appendChild(document.createTextNode(' ')); });
      if (rong(line) > 1720) line.style.fontSize = (50 * 1720 / rong(line)).toFixed(1) + 'px';
    }
  }
  if (k < 0) return;
  const c = ds[k], e = P(t, c.tu, .14);
  SUB.style.opacity = e.toFixed(3); SUB.style.transform = `translateY(${((1 - e) * 10).toFixed(1)}px)`;
  subW.forEach((x, i) => {
    const nx = subW[i + 1]?.w.s ?? x.w.e + .3;
    const on = t >= x.w.s - .02 && t < Math.max(nx, x.w.e) - .02;
    x.s.classList.toggle('on', on);
    const p = on ? 1 + .06 * (1 - P(t, x.w.s, .2)) : 1;
    x.s.style.transform = p > 1.001 ? `scale(${p.toFixed(3)})` : 'none';
  });
}

// ---------------- màn kết YouTube: kênh + câu hỏi / lựa chọn + nút ĐĂNG KÝ có tay bấm, chuông, thích ----------------
const C = KH.cta;
const CT = mk('div', '', stage); CT.id = 'cta'; show(CT, false);
let CTA = null;
if (C) {
  const toi = mk('div', 'cta_toi', CT);
  const X = 150;
  const vong = mk('div', 'vong', CT); css(vong, { left: (X - 12) + 'px', top: '108px' });
  const vt = mk('div', 'vong_trong', CT); css(vt, { left: (X - 6) + 'px', top: '114px' });
  const av = mk('div', 'avatar', CT); css(av, { left: X + 'px', top: '120px' });
  const ten = (KH.kenh && KH.kenh.ten) || '';
  if (KH.kenh && KH.kenh.avatar_url) mk('img', '', av).src = KH.kenh.avatar_url;
  else av.innerHTML = ten ? esc(chars(ten)[0].toUpperCase()) : S(IC.la_ban).replace('<svg', '<svg width="96" height="96"');
  const tk = mk('div', 'ten_kenh', CT); css(tk, { left: (X + 240) + 'px', top: '150px' });
  if (ten) { mk('span', 'bong_chu', tk, esc(ten)); mk('span', 'tich', tk, S(IC.tich)); }
  const hd = KH.kenh && KH.kenh.handle ? mk('div', 'handle', CT, esc(KH.kenh.handle)) : null; if (hd) css(hd, { left: (X + 242) + 'px', top: '226px' });
  const cau = mk('div', 'abs', CT); css(cau, { left: X + 'px', top: '350px', width: '760px' });
  const chu_cau = C.cau_hoi || C.tieu_de;
  const lc = (C.lua_chon || []).map((x, i) => { const c = mk('div', 'chip', CT); const n = mk('div', 'ic', c); n.innerHTML = `<span style="font-family:AN;font-size:32px">${i + 1}</span>`; mk('span', '', c, esc(x)); return c; });
  const nut = mk('div', 'nut_dk', CT); css(nut, { left: X + 'px', top: '800px', width: '420px' });
  const nutIc = mk('span', '', nut, S(IC.chuong)); show(nutIc, false); nutIc.style.display = 'none';
  const nutTx = mk('span', '', nut, esc(C.nut));
  const quet = mk('div', 'quet', nut);
  const song = mk('div', 'song', CT); css(song, { left: X + 'px', top: '800px', width: '420px', height: '104px' });
  const thich = mk('div', 'nut_tron', CT, S(IC.thich)); css(thich, { left: (X + 460) + 'px', top: '800px' });
  const chiase = mk('div', 'nut_tron', CT, S(IC.chia_se)); css(chiase, { left: (X + 588) + 'px', top: '800px' });
  const nThich = mk('div', 'nhan_nut', CT, esc(C.thich)); css(nThich, { left: (X + 432) + 'px', top: '914px' });
  const nCs = mk('div', 'nhan_nut', CT, esc(C.chia_se)); css(nCs, { left: (X + 560) + 'px', top: '914px' });
  const tay = C.viet_tay ? mk('div', 'tay', CT, esc(C.viet_tay)) : null; if (tay) css(tay, { position: 'absolute', left: X + 'px', top: '935px', fontSize: '56px', whiteSpace: 'nowrap', transform: 'rotate(-2deg)', transformOrigin: '0 50%' });
  const hand = mk('div', 'tay_bam', CT, TAY);
  const tims = [0, 1, 2, 3, 4, 5].map(i => { const h = mk('div', 'tim_bay', CT, S(IC.tim)); h.querySelector('svg').setAttribute('fill', '#FF3355'); return h; });
  let dongCau = [], YN = 800;
  CTA = {
    init() {
      dongCau = dong2(cau, chu_cau, 80, 760, 'serif kem_grad').map(bocMask);
      const hc = cau.getBoundingClientRect().height;
      let y = 360 + hc + 34, x = X;
      lc.forEach((c, i) => { const w = c.getBoundingClientRect().width; if (x + w > X + 780) { x = X; y += 92; } css(c, { left: x + 'px', top: y + 'px' }); x += w + 18; });
      if (tay) { vua(tay, 56, 760); css(tay, { top: (y + 98) + 'px' }); y += 98 + 70; } else y += 98;
      YN = Math.max(780, Math.min(840, y + 14));
      [nut, song, thich, chiase].forEach(e => e.style.top = YN + 'px');
      [nThich, nCs].forEach(e => e.style.top = (YN + 112) + 'px');
    },
    ve(t) {
      const on = t >= C.tu - .02; show(CT, on); if (!on) return;
      const e = P(t, C.tu, .6, E.ioS);
      toi.style.opacity = e.toFixed(3);
      const a = P(t, C.tu + .1, .55, E.outB);
      [vong, vt, av].forEach(x => { x.style.transform = `scale(${a.toFixed(3)})`; x.style.opacity = P(t, C.tu + .1, .25).toFixed(3); });
      vong.style.transform += ` rotate(${((t - C.tu) * 70).toFixed(1)}deg)`;
      const b = P(t, C.tu + .3, .6, E.outE);
      tk.style.opacity = b.toFixed(3); tk.style.transform = `translateX(${((1 - b) * -40).toFixed(1)}px)`;
      if (hd) hd.style.opacity = P(t, C.tu + .45, .5).toFixed(3);
      dongCau.forEach((x, i) => { const f = P(t, C.tu + .45 + i * .14, .8, E.outE); x.style.transform = `translateY(${((1 - f) * 105).toFixed(1)}%)`; });
      lc.forEach((c, i) => { const f = P(t, C.tu + .95 + i * .16, .5, E.outB); c.style.opacity = P(t, C.tu + .95 + i * .16, .25).toFixed(3); c.style.transform = `scale(${(.6 + .4 * f).toFixed(3)})`; });
      const n = P(t, C.tu + 1.1, .55, E.outB);
      [nut, thich, chiase, nThich, nCs].forEach(x => { x.style.opacity = P(t, C.tu + 1.1, .3).toFixed(3); x.style.transform = `translateY(${((1 - n) * 40).toFixed(1)}px)`; });
      if (tay) tay.style.clipPath = `inset(-30% ${((1 - P(t, C.tu + 1.4, 1.0, E.ioS)) * 100).toFixed(1)}% -30% -5%)`;
      // nút đăng ký: bóng quét + sóng lan trước khi bấm; bấm → xám "ĐÃ ĐĂNG KÝ" + chuông lắc
      const da = t >= C.luc_bam;
      nut.classList.toggle('da', da);
      nutTx.textContent = da ? C.nut_da : C.nut;
      nutIc.style.display = da ? 'inline-flex' : 'none';
      if (da) { const r = clamp((t - C.luc_chuong) / .8); nutIc.style.transform = `rotate(${(Math.sin(r * Math.PI * 5) * 22 * (1 - r)).toFixed(1)}deg)`; nutIc.style.transformOrigin = '50% 10%'; }
      const q = ((t - C.tu - 1.3) % 1.4 + 1.4) % 1.4 / 1.4;
      quet.style.left = (-160 + q * 640).toFixed(1) + 'px'; show(quet, !da && t > C.tu + 1.3);
      const sq = ((t - C.tu - 1.3) % 1.1 + 1.1) % 1.1 / 1.1;
      show(song, !da && t > C.tu + 1.3); song.style.opacity = ((1 - sq) * .8).toFixed(3); song.style.transform = `scale(${(1 + sq * .22).toFixed(3)}, ${(1 + sq * .6).toFixed(3)})`;
      const ep = da ? 1 - .06 * Math.sin(clamp((t - C.luc_bam) / .25) * Math.PI) : 1;
      nut.style.transform += ` scale(${ep.toFixed(3)})`;
      // thích: tô xanh + tim bay
      const th = t >= C.luc_thich;
      thich.style.background = th ? '#3EA6FF' : 'rgba(255,255,255,.14)';
      const tp = th ? 1 + .25 * Math.sin(clamp((t - C.luc_thich) / .35) * Math.PI) : 1;
      thich.style.transform += ` scale(${tp.toFixed(3)})`;
      tims.forEach((h, i) => {
        const r = clamp((t - C.luc_thich - i * .07) / 1.1);
        show(h, th && r > 0 && r < 1);
        const ang = -90 + (i - 2.5) * 22;
        h.style.left = (X + 512 + Math.cos(ang * Math.PI / 180) * 120 * r).toFixed(1) + 'px';
        h.style.top = (YN + 30 + Math.sin(ang * Math.PI / 180) * 160 * r).toFixed(1) + 'px';
        h.style.opacity = (1 - r).toFixed(3); h.style.transform = `scale(${(.6 + .6 * r).toFixed(3)})`;
      });
      // tay: vào → bấm Đăng ký → sang bấm Thích → ra
      const p1 = [X + 300, YN + 52], p2 = [X + 512, YN + 52], p0 = [X + 700, 1180], p3 = [X + 760, 1200];
      let hx, hy, nhan = 0;
      if (t < C.luc_bam - .75) { hx = p0[0]; hy = p0[1]; }
      else if (t < C.luc_bam) { const u = P(t, C.luc_bam - .75, .65, E.ioC); hx = lerp(p0[0], p1[0], u); hy = lerp(p0[1], p1[1], u); nhan = P(t, C.luc_bam - .12, .12); }
      else if (t < C.luc_thich - .5) { hx = p1[0]; hy = p1[1]; nhan = 1 - P(t, C.luc_bam + .05, .15); }
      else if (t < C.luc_thich) { const u = P(t, C.luc_thich - .5, .4, E.ioC); hx = lerp(p1[0], p2[0], u); hy = lerp(p1[1], p2[1], u); nhan = P(t, C.luc_thich - .12, .12); }
      else { const u = P(t, C.luc_thich + .35, .7, E.ioC); hx = lerp(p2[0], p3[0], u); hy = lerp(p2[1], p3[1], u); nhan = 1 - P(t, C.luc_thich + .05, .15); }
      show(hand, t > C.luc_bam - .8 && t < C.luc_thich + 1.1);
      css(hand, { left: (hx - TAY_DIEM[0]).toFixed(1) + 'px', top: (hy - TAY_DIEM[1]).toFixed(1) + 'px', transform: `scale(${(1 - .12 * nhan).toFixed(3)})`, transformOrigin: `${TAY_DIEM[0]}px ${TAY_DIEM[1]}px` });
    },
  };
}

// ---------------- vòng đời ----------------
function hatNhieu() {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'), im = g.createImageData(256, 256);
  let s = 12345; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  g.putImageData(im, 0, 0);
  HAT.style.backgroundImage = `url(${c.toDataURL()})`;
}
window.__ready = (async () => {
  const fams = ['900 40px PF', '700 40px PF', '600 40px PFI', '700 40px DS', '400 40px AN', '700 40px BVP', '800 40px BVP', '600 40px BVP', '900 40px BVP', '700 40px MS', '600 40px MS'];
  await Promise.all(fams.map(f => document.fonts.load(f, 'ÀẢÃẠăâđêôơư Việt Nam 0123')));
  await document.fonts.ready;
  hatNhieu();
  // đo chữ cần phần tử ĐANG HIỆN (display:none → bề rộng 0): bật tạm lúc init rồi ẩn lại
  for (const g of DH) { show(g.el, true); g.init && g.init(); show(g.el, false); }
  if (CTA) { show(CT, true); CTA.init(); show(CT, false); }
})();
window.__seek = async (t) => {
  DS.length = 0;
  veMau(t);
  ghepCanh(t);
  for (const g of DH) g.ve(t);
  veSub(t);
  CTA && CTA.ve(t);
  if (DS.length) await Promise.all(DS.map(i => i.decode().catch(() => { })));
  return true;
};
window.__bao_cao = () => {
  const o = [];
  const vis = el => { let e = el; while (e && e !== stage) { const s = getComputedStyle(e); if (s.display === 'none' || +s.opacity < .5) return false; e = e.parentElement; } return true; };
  for (const h of HOP) if (vis(h.el)) { const r = h.el.getBoundingClientRect(); o.push({ loai: h.d.loai, id: h.d.id, x: r.left, y: r.top, w: r.width, h: r.height }); }
  if (SUB.childElementCount && +SUB.style.opacity > .5) for (const l of SUB.children) { const r = document.createRange(); r.selectNodeContents(l); const b = r.getBoundingClientRect(); o.push({ loai: 'sub', id: 'sub', x: b.left, y: b.top, w: b.width, h: b.height }); }
  return o;
};
