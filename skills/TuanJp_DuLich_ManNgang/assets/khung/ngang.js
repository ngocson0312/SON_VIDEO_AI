/* ngang.js — trang dựng 1920×1080 của TuanJp_DuLich_ManNgang.
 * Nhận window.KH (kế hoạch đã giải giờ bởi scripts/ke_hoach.py + KH.part từ dung.py), vẽ đúng khung ở giây t qua window.__seek(t).
 * Không dùng thời gian thực: mọi chuyển động là hàm thuần của t → dựng tất định, chia luồng được.
 * Khách 14/11/2026: ảnh / clip LUÔN TRÀN MÀN; chữ kiểu riêng bản ngang (Barlow Condensed in hoa + Montserrat nghiêng + xanh ngọc);
 * bản đồ A → B kiểu Google Maps (vệ tinh thật, km + giờ); bình luận ảo Anh / Hàn; teaser mở màn; màn kết CẢM ƠN + Thích / Đăng ký.
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
  drop: u => { if (u < .62) { const k = u / .62; return k * k; } const k = (u - .62) / .38; return 1 - .16 * Math.sin(Math.PI * k) * (1 - k); },
};
const P = (t, a, d, e = E.outC) => e(clamp((t - a) / Math.max(1e-6, d)));
const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || stage).appendChild(e); if (cls === 'dh') e.style.display = 'none'; return e; };
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pad5 = i => String(i).padStart(5, '0');
const chars = s => Array.from(String(s ?? '').normalize('NFC'));
const words = s => String(s ?? '').trim().split(/\s+/).filter(Boolean);
const md = (a, n) => ((a % n) + n) % n;
const f1 = x => (+x).toFixed(1);
function css(el, o) { for (const k in o) { const v = o[k]; if (el.style[k] !== v) el.style[k] = v; } }
function show(el, on) { const v = on ? '' : 'none'; if (el.style.display !== v) el.style.display = v; }
const DS = [];   // ảnh vừa đổi src → chờ decode trước khi chụp
function setSrc(img, u) { if (u && img.dataset.u !== u) { img.dataset.u = u; img.src = u; DS.push(img); } }
const NN = KH.ngon_ngu || 'vi';
const T = KH.T || {};
const FULL = { left: '0px', top: '0px', width: W + 'px', height: H + 'px' };

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
  xe_buyt: '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M3 10h18"/><path d="M7 17v3M17 17v3"/><path d="M7 14h.01M17 14h.01"/>',
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
  khong_thich: '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>',
  chia_se: '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/>',
  binh_luan: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
};
const icon = n => S(IC[n] || IC.sao);
const TAY = `<svg viewBox="0 0 120 170" width="120" height="170"><defs><linearGradient id="gtay" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E4E0DA"/></linearGradient></defs>
<g fill="url(#gtay)" stroke="#2b2b2b" stroke-width="4" stroke-linejoin="round"><rect x="28" y="3" width="22" height="80" rx="11"/><rect x="48" y="44" width="21" height="46" rx="10.5"/><rect x="66.5" y="50" width="20" height="42" rx="10"/><rect x="84.5" y="58" width="18" height="36" rx="9"/><path d="M27 66 L103 72 L103 116 Q103 146 76 150 L54 150 Q30 147 27 124 Z"/><rect x="9" y="76" width="22" height="50" rx="11" transform="rotate(-36 20 101)"/></g></svg>`;
const TAY_DIEM = [39, 4];          // đầu ngón trỏ trong khung 120×170

// ---------------- lớp nền: footage (LUÔN TRÀN MÀN) ----------------
const CL = mk('div', '', stage); CL.id = 'canh_lop';
const PART = KH.part || {};
function partUrl(pid, t, a) {
  const p = PART[pid]; if (!p) return '';
  if (p.anh) return p.src;
  const i = clamp(Math.floor((t - a) * FPS + 1e-4), 0, p.n - 1) + 1;
  return p.dir + pad5(i) + '.jpg';
}
function dungCanh(c, i) {
  const root = mk('div', 'canh', CL); root.style.display = 'none'; root.style.zIndex = String(i + 1);
  return { c, root, i, img: mk('img', 'full', root) };
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
function kbOf(o, t) {
  const c = o.c, u = clamp((t - c.a) / Math.max(.01, c.b - c.a));
  return kenBurns(c.chuyen_dong, u, (c.loai_nguon || [])[0] === 'anh' ? 1 : .55);
}
function veCanh(o, t) {
  setSrc(o.img, partUrl(o.c.lop[0], t, o.c.a));
  o.img.style.transform = tfKB(kbOf(o, t), W, H);
}
// vẽ 1 khung cảnh lên canvas y hệt <img class="full"> (object-fit: cover, tâm giữa) + Ken Burns k
function veKhung(g, img, k) {
  const iw = img.naturalWidth || W, ih = img.naturalHeight || H, s = Math.max(W / iw, H / ih);
  g.save(); g.translate(W / 2 + k.x * W, H / 2 + k.y * H); g.scale(k.s, k.s);
  g.drawImage(img, -iw * s / 2, -ih * s / 2, iw * s, ih * s); g.restore();
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
// khung điện ảnh 2.35:1 mở màn: có teaser → mở ra lúc giọng vào (KH.bar_het); không teaser → lúc chữ drop đầu tiên
const BAR_HET = KH.dien_anh === false ? -1 : (KH.bar_het != null ? KH.bar_het : (MO_DAU_0 != null ? MO_DAU_0 : -1));
// CÚ DROP: mỗi mo_dau (trừ drop:false) = loé trắng + rung khung 0,4 s đúng lúc chữ đập vào
const DROP = (KH.do_hoa || []).filter(d => d.loai === 'mo_dau' && d.drop !== false).map(d => d.tu);

// ---------------- KỸ XẢO CAO TRÀO (khách 14/11/2026: "30 s đầu cao trào giật gân… kỹ xảo điện ảnh chuyển cảnh xịn liên tục,
// 5 s đầu phải xịn; sau 30 s bình thường"). KH.cao_trao = {het, mo, dap: [{t, m}]} do ke_hoach.py lập; kiểu chuyển nằm ở c.chuyen.
const CAO_TRAO = KH.cao_trao || null;
CL.style.perspective = '2000px';                                   // cho lat_3d (khối hộp xoay)
const SVG_NS = 'http://www.w3.org/2000/svg';
const SVG_FX = document.createElementNS(SVG_NS, 'svg');
SVG_FX.setAttribute('width', '0'); SVG_FX.setAttribute('height', '0'); SVG_FX.style.position = 'absolute';
// TÁCH MÀU RGB sắc nét (không nhoè): kênh đỏ lệch phải, lam lệch trái, ghép lại bằng screen
SVG_FX.innerHTML = `<filter id="rgb_tach" x="0" y="0" width="1" height="1" color-interpolation-filters="sRGB">
<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>
<feOffset in="r" dx="0" dy="0" result="r2"/>
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>
<feOffset in="b" dx="0" dy="0" result="b2"/>
<feBlend in="r2" in2="g" mode="screen" result="rg"/>
<feBlend in="rg" in2="b2" mode="screen"/></filter>`;
stage.appendChild(SVG_FX);
const [RGB_R, RGB_B] = SVG_FX.querySelectorAll('feOffset');
const FXC = mk('canvas', '', CL); FXC.id = 'fx_ve'; FXC.width = W; FXC.height = H; show(FXC, false);
const FXG = FXC.getContext('2d');
const FX_ANH = new Image();                                        // khung ĐỨNG của cảnh cũ lúc cắt — để vỡ thành mảnh kính
const CHAY = mk('div', '', stage); CHAY.id = 'chay_phim'; show(CHAY, false);
const CHAY_D = [0, 1, 2].map(() => mk('div', 'dom_chay', CHAY));
// đốm cháy: [x0, y0, x1, y1, scale0, scale1] (phần khung) — loang từ mép phải / dưới vào giữa
const CHAY_DUONG = [[1.02, .28, .52, .46, .45, 1.95], [.82, 1.05, .34, .62, .35, 1.7], [1.12, .7, .72, .3, .3, 1.35]];
const VONG = mk('div', '', stage); VONG.id = 'vong_iris'; show(VONG, false);

// ---------------- 5 KỸ XẢO MẪU (người dùng gửi ảnh 14/11/2026: "có 1 vài kỹ xảo chuyển cảnh, hãy ghi nhớ và cho vào skill") ----------------
// A ba_cot · C khung_bung · D dai_truot · E khop_hinh · F hai_nua / hai_nua_doc — chia màn TẠM THỜI, kết thúc luôn tràn màn.
const VIEN = (s, a = 1) => a < .01 ? 'none' : `0 0 0 ${(5 / Math.max(.05, s)).toFixed(1)}px rgba(255,255,255,${(.95 * a).toFixed(3)}), ` +
  `0 ${(16 / Math.max(.05, s)).toFixed(0)}px ${(48 / Math.max(.05, s)).toFixed(0)}px rgba(0,0,0,${(.55 * a).toFixed(3)})`;
const COT_GAP = 10, COT_W = (W - 2 * COT_GAP) / 3, cotX = k => k * (COT_W + COT_GAP) + COT_W / 2;
const COT_Y = 822;   // tâm tên dưới cột: trên dải đen điện ảnh 2.35:1 (mép dưới khung thấy được y ≈ 949)
// A — nhóm BA CỘT: {ids, moc[3], bung, bung_dai, het, nhan[{chu, nhan}]} do ke_hoach._tong_hop lập
const NHOM = (KH.canh || []).filter(c => c.nhom).map(c => {
  const g = c.nhom, o = g.ids.map(id => SC.find(s => s.c.id === id));
  const el = mk('div', 'nhom_cot', CL); show(el, false);
  const toi = [0, 1, 2].map(k => { const d = mk('div', 'cot_toi', el); css(d, { left: f1(cotX(k) - COT_W / 2) + 'px', width: f1(COT_W) + 'px' }); return d; });
  const giua = mk('div', 'cot_giua', el);
  const lb = (g.nhan || []).map(n => {
    const k = mk('div', 'cot_nhan', el);
    if (n.nhan) mk('div', 'nhan_nho', k, esc(n.nhan));
    mk('div', 'tit_i', k, esc(n.chu || ''));
    if (n.chu) mk('div', 'vach_n', k);
    return k;
  });
  return { ...g, o, el, toi, giua, lb };
});
function veNhom(g, t) {
  const e = P(t, g.bung, g.bung_dai, E.outE);                      // cột 3 BUNG đúng phách (outExpo: phần lớn trong 0,1 s đầu)
  let rgb = 0;
  g.o.forEach((o, k) => {
    if (!o) return;
    if (t < g.moc[k] - 1e-4 || (k < 2 && e >= 1)) { show(o.root, false); return; }
    const p = P(t, g.moc[k], .2, E.outC), w = k === 2 ? lerp(COT_W, W, e) : COT_W, x = k === 2 ? lerp(cotX(2), W / 2, e) : cotX(k), l = (W - w) / 2;
    apDung(o, { clip: l > .5 ? `inset(0px ${f1(l)}px 0px ${f1(l)}px)` : 'none', tf: `translate(${f1(x - W / 2)}px, ${f1((1 - p) * -70)}px)`,
      f: p < 1 ? `brightness(${(1 + .9 * (1 - p)).toFixed(3)})` : 'none' });
    o.root.style.zIndex = String(2 + k);
    veCanh(o, t);
    rgb = Math.max(rgb, 14 * (1 - P(t, g.moc[k], .16, E.lin)) * (t >= g.moc[k] ? 1 : 0));
  });
  if (t >= g.bung) rgb = Math.max(rgb, 16 * Math.sin(Math.PI * clamp((t - g.bung) / (g.bung_dai + .15))));
  show(g.el, true);
  g.lb.forEach((L, k) => {
    const a = t >= g.moc[k] ? P(t, g.moc[k] + .04, .18, E.outC) : 0;
    let op = a, x = cotX(k), y = COT_Y, s = 1;
    if (k < 2) op *= 1 - P(t, g.bung, .14, E.lin);
    else { x = lerp(x, W / 2, e); y = lerp(COT_Y, 540, e); s = lerp(1, 2.15, e); op *= 1 - P(t, g.het - .07, .07, E.lin); }
    L.style.opacity = op.toFixed(3);
    L.style.transform = `translate(${f1(x)}px, ${f1(y + (1 - a) * 34)}px) translate(-50%, -50%) scale(${s.toFixed(4)})`;
    g.toi[k].style.opacity = (k < 2 ? op : a * (1 - e)).toFixed(3);
  });
  g.giua.style.opacity = (e * (1 - P(t, g.het - .07, .07, E.lin))).toFixed(3);
  return rgb;
}
// D — dải ảnh trượt: mỗi cảnh `dai_truot` có dải ảnh tĩnh của các cảnh trong c.dai (khung đầu cảnh đó)
const DAI = {};
for (const o of SC) if (o.c.chuyen === 'dai_truot' && (o.c.dai || []).length) {
  const el = mk('div', 'dai_anh', CL); show(el, false);
  DAI[o.c.id] = { el, it: o.c.dai.map(id => SC.find(s => s.c.id === id)).filter(Boolean).map(x => ({ im: mk('img', '', el), x })) };
}
// F — cú ĐẨY hai nửa (vòng 4): cảnh cũ BỊ ĐẨY sang trái, cảnh mới lộ ra sau mép sáng; mép dừng 3 nấc đúng phách (nấc 1 cắt ngang
// NGƯỜI trong cảnh mới → người tách nền nhô qua mép như đang đẩy); CHỮ (day_chu) chạy theo mép rồi đứng giữa, bị đẩy ra cùng cảnh khi cắt tiếp
const xMan = (u, k) => W / 2 + k.x * W + k.s * (u * W - W / 2);   // toạ độ ảnh 0–1 → x màn (ảnh 16:9 tràn khung + Ken Burns k)
for (const o of SC) if (o.c.chuyen === 'hai_nua') {
  let s1 = .66 * W;
  const hop = o.c.nv && o.c.nv.hop;
  if (hop) { const k = kbOf(o, o.c.tu), xl = xMan(hop[0], k), xr = xMan(hop[2], k); s1 = clamp(xl + .25 * (xr - xl), .45 * W, .8 * W); }
  o.s1 = s1;
}
const VACH = mk('div', '', CL); VACH.id = 'vach_day'; show(VACH, false);
const NV = SC.filter(o => o.c.nv && o.c.nv.src).map(o => { const el = mk('div', 'nv_lop', CL); show(el, false); return { o, el, im: mk('img', '', el) }; });
const DC = SC.filter(o => o.c.day_chu && o.c.day_chu.chu).map(o => {
  const el = mk('div', 'day_chu', CL); show(el, false);
  const t1 = mk('div', 'tit_i', el, esc(o.c.day_chu.chu));
  if (o.c.day_chu.nhan) mk('div', 'nhan_nho', el, esc(o.c.day_chu.nhan));
  mk('div', 'vach_n', el);
  return { o, el, t1, w: 0, h: 0, y0: 0, cd: false };
});
function veDayChu(D, st) {
  if (!st) { show(D.el, false); return; }
  show(D.el, true);
  const doc = D.o.c.chuyen === 'hai_nua_doc';
  if (!D.cd) {                                                      // đo 1 lần: chữ vừa phần mép mới ở nấc 1, chọn dải trên / dưới né người
    vua(D.t1, 150, doc ? 1300 : Math.max(420, W - (D.o.s1 || .66 * W) - 110));
    D.w = D.el.offsetWidth; D.h = D.el.offsetHeight; D.cd = true;
    const hop = D.o.c.nv && D.o.c.nv.hop;
    if (hop && !doc) {
      const pt = hop[1] * H, pb = hop[3] * H, tr = [170, 170 + D.h], du = [930 - D.h, 930];
      const ch = (a, b) => Math.max(0, Math.min(b, pb) - Math.max(a, pt));
      D.y0 = ch(...tr) <= ch(...du) ? tr[0] : du[0];
    } else D.y0 = 540 - D.h / 2;
  }
  let left, top;
  if (doc) { left = W / 2 - D.w / 2; top = Math.max(D.y0, st.x + 30); }
  else { left = Math.max(W / 2 - D.w / 2, st.x + 44); top = D.y0; }
  const op = st.op * clamp(((doc ? H : W) - st.x) / 140);
  css(D.el, { opacity: op.toFixed(3), transform: `translate(${f1(left + st.dx)}px, ${f1(top)}px)` });
}

function rngSeed(s) {
  return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let x = Math.imul(s ^ s >>> 15, 1 | s); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; };
}
const MANH = {};
// mảnh kính: 10 tia toả từ điểm va + 3 vòng gãy → ~60 mảnh (tam giác giữa, tứ giác vòng 1, tam giác vòng ngoài); tất định theo id cảnh
function manhKinh(id) {
  if (MANH[id]) return MANH[id];
  let sd = 7; for (const ch of String(id)) sd = Math.imul(sd, 31) + ch.charCodeAt(0) | 0;
  const r = rngSeed(sd), n = 10;
  const I = [W * (.42 + .16 * r()), H * (.4 + .2 * r())], goc = [], RR = [];
  for (let j = 0; j < n; j++) { goc.push((j + (r() - .5) * .6) / n * 2 * Math.PI); RR.push([0, 140 + 120 * r(), 400 + 240 * r(), 850 + 300 * r(), 2600]); }
  const pt = (j, q) => { const jj = j % n; return [I[0] + Math.cos(goc[jj]) * RR[jj][q], I[1] + Math.sin(goc[jj]) * RR[jj][q]]; };
  const poly = [];
  for (let j = 0; j < n; j++) {
    const k = j + 1;
    poly.push([I, pt(j, 1), pt(k, 1)]);
    poly.push([pt(j, 1), pt(j, 2), pt(k, 2), pt(k, 1)]);
    for (const q of [2, 3]) {
      const a = pt(j, q), b = pt(j, q + 1), c = pt(k, q + 1), d = pt(k, q);
      if (r() < .5) { poly.push([a, b, c]); poly.push([a, c, d]); } else { poly.push([a, b, d]); poly.push([b, c, d]); }
    }
  }
  const ds = poly.map(p => {
    const cx = p.reduce((s, v) => s + v[0], 0) / p.length, cy = p.reduce((s, v) => s + v[1], 0) / p.length;
    const dx = cx - I[0], dy = cy - I[1], L = Math.hypot(dx, dy) || 1;
    return { p, cx, cy, ux: dx / L, uy: dy / L, L, v: 500 + 900 * r(), z: .15 + .85 * r() * (1 - Math.min(1, L / 1400)),
      rz: (r() - .5) * 2.4, tx: (r() - .5) * 2.8, ty: (r() - .5) * 2.8, tre: Math.min(.3, L / 4200) };
  });
  ds.sort((a, b) => a.z - b.z);                                   // mảnh bay gần máy quay vẽ sau (nằm trên)
  return (MANH[id] = { I, ds });
}
const duongManh = (g, p) => { g.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) g.lineTo(p[i][0], p[i][1]); g.closePath(); };
function veFx(j, t) {
  const g = FXG;
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.clearRect(0, 0, W, H);
  if (j.loai === 'nut') {                                         // vết nứt toả ra từ điểm va (0,16 s trước cắt)
    const M = manhKinh(j.id), rr = 90 + j.k * 1500;
    g.save(); g.strokeStyle = 'rgba(255,255,255,.92)'; g.lineWidth = 2.4; g.lineJoin = 'round';
    g.shadowColor = 'rgba(190,255,248,.95)'; g.shadowBlur = 12; g.beginPath();
    for (const s of M.ds) if (s.L < rr) duongManh(g, s.p);
    g.stroke(); g.restore();
    const gr = g.createRadialGradient(M.I[0], M.I[1], 0, M.I[0], M.I[1], 80 + 70 * j.k);
    gr.addColorStop(0, `rgba(255,255,255,${(.9 * j.k).toFixed(3)})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(M.I[0] - 200, M.I[1] - 200, 400, 400);
  } else if (j.loai === 'vo') {                                    // mảnh kính bay ra: tịnh tiến + rơi + xoay + lật + phóng về máy quay
    const M = manhKinh(j.id);
    for (const s of M.ds) {
      const q = clamp((j.p - s.tre) / (1 - s.tre)), al = 1 - clamp((q - .55) / .45);
      if (al <= 0) continue;
      const D = s.v * .6 * q + 300 * q * q, x = s.cx + s.ux * D, y = s.cy + s.uy * D + 520 * q * q;
      const sc = 1 + s.z * E.outQ(q) * 1.2, sx = Math.cos(s.tx * q), sy = Math.cos(s.ty * q);
      g.save(); g.globalAlpha = al;
      g.translate(x, y); g.rotate(s.rz * q); g.scale(sc * sx, sc * sy); g.translate(-s.cx, -s.cy);
      g.beginPath(); duongManh(g, s.p); g.clip();
      veKhung(g, FX_ANH, j.kb);
      const toi = .45 * (1 - Math.abs(sx * sy)), sang = .4 * Math.abs(Math.sin(s.tx * q * 1.6)) * (1 - .5 * q);
      if (toi > .02) { g.fillStyle = `rgba(0,0,0,${toi.toFixed(3)})`; g.fill(); }
      if (sang > .02) { g.fillStyle = `rgba(235,255,252,${sang.toFixed(3)})`; g.fill(); }
      g.strokeStyle = `rgba(255,255,255,${(.85 * (1 - .6 * q)).toFixed(3)})`; g.lineWidth = 3 / Math.max(.2, sc * Math.max(Math.abs(sx), Math.abs(sy))); g.stroke();
      g.restore();
    }
  } else if (j.loai === 'glitch') {                                // dải ngang lệch + dải lẫn cảnh kia + vạch xanh-hồng
    const r = rngSeed(1000 + Math.floor(j.f / 2)), K = 4 + Math.round(8 * j.g);
    const sA = { img: j.a.img, kb: kbOf(j.a, t) }, sB = { img: j.b.img, kb: kbOf(j.b, t) };
    for (let i = 0; i < K; i++) {
      const y0 = r() * H, h = 8 + r() * (40 + 120 * j.g), off = (r() - .5) * 2 * (40 + 240 * j.g), khac = r() < .28;
      const src = (j.hienB !== khac) ? sB : sA, mau = r();
      g.save(); g.beginPath(); g.rect(0, y0, W, h); g.clip(); g.translate(off, 0); veKhung(g, src.img, src.kb);
      if (mau < .35) { g.globalCompositeOperation = 'screen'; g.fillStyle = mau < .17 ? 'rgba(0,255,230,.35)' : 'rgba(255,0,150,.35)'; g.fillRect(-off, y0, W, h); }
      g.restore();
    }
    for (let i = 0; i < 4; i++) { g.fillStyle = i % 2 ? 'rgba(255,60,170,.75)' : 'rgba(60,255,235,.75)'; g.fillRect(r() * W * .7, r() * H, 120 + r() * 700 * j.g, 2 + r() * 8); }
  }
}

function veMau(t) {
  const f = Math.floor(t * FPS);
  HAT.style.backgroundPosition = `${(f * 73) % 256}px ${(f * 151) % 256}px`;
  const b = BAR_HET > 0 ? 132 * (1 - P(t, BAR_HET - .02, .32, E.outC)) : 0;
  BAR_T.style.height = b.toFixed(1) + 'px'; BAR_D.style.height = b.toFixed(1) + 'px';
  show(BAR_T, b > .5); show(BAR_D, b > .5);
  let den = 0;                                                   // vào THẲNG hình ở khung 0 (khung đầu = ảnh xem trước YouTube)
  if (KH.dur - t < .5) den = Math.max(den, P(t, KH.dur - .5, .5, E.ioS));
  DEN.style.opacity = den.toFixed(3);
}

// ---------------- ghép cảnh + chuyển cảnh ----------------
function apDung(o, s) {
  show(o.root, true);
  css(o.root, { opacity: (s.o ?? 1).toFixed ? (s.o ?? 1).toFixed(3) : String(s.o), transform: s.tf || 'none', filter: s.f || 'none',
    clipPath: s.clip || 'none', transformOrigin: s.org || '50% 50%', boxShadow: s.shadow || 'none' });
}
function ghepCanh(t) {
  const gN = NHOM.find(g => t >= g.moc[0] - 1e-6 && t < g.het);       // A — nhóm ba cột đang chạy thì nó điều khiển cảnh
  for (const g of NHOM) if (g !== gN) show(g.el, false);
  const vis = gN ? [] : SC.filter(o => t >= o.c.a - 1e-6 && t <= o.c.b + 1e-6);
  for (const o of SC) if (!vis.includes(o) && !(gN && gN.o.includes(o))) show(o.root, false);
  let loe = 0, trang = 0, man = null;
  let rgb = 0, clS = 1, clX = 0, rungFx = 0, chay = 0, chayU = 0, iris = null, fx = null, po = null;   // kỹ xảo cao trào
  let dai = null;                                                   // D — dải ảnh trượt đang hiện
  let vach = null, dayX = null, raDx = null, nvO = null, raDxV = 0;  // F — mép đẩy (x), chữ theo mép, chữ bị đẩy ra, người nhô qua mép
  if (gN) rgb = veNhom(gN, t);
  else if (vis.length === 1) apDung(vis[0], {});
  else if (vis.length >= 2) {
    const ra = vis[vis.length - 2], vao = vis[vis.length - 1];
    for (const o of vis.slice(0, -2)) show(o.root, false);
    // cửa sổ chuyển LỆCH được (montage): dt trước cú cắt, ds sau cú cắt — u = 0,5 luôn đúng cú cắt
    const c = vao.c, d = Math.max(.01, c.d_in), dt = Math.max(.005, c.d_t ?? d / 2), ds = Math.max(.005, c.d_s ?? d / 2);
    const u = t < c.tu ? .5 * clamp((t - (c.tu - dt)) / dt) : .5 + .5 * clamp((t - c.tu) / ds);
    const gc = Math.max(0, t < c.tu ? 1 - (c.tu - t) / dt : 1 - (t - c.tu) / ds);   // 1 đúng cú cắt → 0 ở 2 mép cửa sổ
    let A = {}, B = {};
    switch (c.chuyen) {
      case 'cat': if (t < c.tu) B = { o: 0 }; else A = { o: 0 }; break;
      case 'hoa_tan': B = { o: E.ioS(u) }; break;
      case 'zoom_muot': {
        const e = E.ioS(u);
        A = { tf: `scale(${(1 + .18 * e).toFixed(4)})` };
        B = { o: e, tf: `scale(${(1.12 - .12 * E.outC(u)).toFixed(4)})` };
        break;
      }
      case 'nhoe': { const b = Math.sin(Math.PI * u); A = { f: `brightness(${(1 + .25 * b).toFixed(3)})` }; B = { o: E.ioS(u), f: `brightness(${(1 + .25 * b).toFixed(3)})` }; break; }
      case 'lia': case 'lia_doc': {
        const e = E.ioC(u), doc = c.chuyen === 'lia_doc';
        A = { tf: (doc ? `translateY(${(-H * .3 * e).toFixed(1)}px)` : `translateX(${(-W * .3 * e).toFixed(1)}px)`) + ` scale(${(1 - .05 * e).toFixed(4)})`,
          f: `brightness(${(1 - .5 * e).toFixed(3)})` };
        B = { tf: doc ? `translateY(${(H * (1 - e)).toFixed(1)}px)` : `translateX(${(W * (1 - e)).toFixed(1)}px)` };
        break;
      }
      case 'zoom': {
        if (u < .5) { A = { tf: `scale(${(1 + .45 * E.inC(u * 2)).toFixed(4)})` }; B = { o: 0 }; }
        else { A = { o: 0 }; B = { tf: `scale(${(1.3 - .3 * E.outC((u - .5) * 2)).toFixed(4)})` }; }
        trang = .55 * Math.max(0, 1 - Math.abs(u - .5) * 5); break;
      }
      case 'phong': {
        if (t < c.tu) { A = { tf: `scale(${(1 + .06 * P(t, c.tu - .15, .15, E.inC)).toFixed(4)})` }; B = { o: 0 }; }
        else { A = { o: 0 }; B = { tf: `scale(${(1.22 - .22 * P(t, c.tu, .32, E.outC)).toFixed(4)})` }; trang = .35 * (1 - P(t, c.tu, .18, E.outC)); }
        break;
      }
      case 'loe': { B = { o: E.ioS(u) }; loe = Math.pow(Math.sin(Math.PI * u), .8); trang = .1 * Math.pow(Math.sin(Math.PI * u), 3); break; }
      case 'truot': {
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
      // ---------- KỸ XẢO ĐIỆN ẢNH (đoạn cao trào) — tâm cửa sổ = cú cắt đúng phách ----------
      case 'vo_kinh': {
        if (t < c.tu) {                                             // nứt toả 0,16 s cuối
          const kn = Math.min(.16, dt), k = P(t, c.tu - kn, kn, E.outC);
          A = { tf: `scale(${(1 + .025 * k).toFixed(4)})` }; B = { o: 0 };
          if (k > 0) fx = { loai: 'nut', id: c.id, k };
        } else {                                                    // vỡ: mảnh khung đứng của cảnh cũ bay ra, cảnh mới đập vào
          const p = clamp((t - c.tu) / Math.max(.2, ds));
          A = { o: 0 }; B = { tf: `scale(${(1.16 - .16 * E.outC(p)).toFixed(4)})` };
          setSrc(FX_ANH, partUrl(ra.c.lop[0], c.tu, ra.c.a));
          fx = { loai: 'vo', id: c.id, p, kb: kbOf(ra, c.tu) };
          trang = .5 * (1 - P(t, c.tu, .2, E.outC)); rgb = 16 * (1 - E.outC(p)); rungFx = .5 * (1 - P(t, c.tu, .3, E.outC));
        }
        break;
      }
      case 'xoay': {
        if (u < .5) { const k = E.inC(u * 2); A = { tf: `rotate(${(24 * k).toFixed(2)}deg) scale(${(1 + .9 * k).toFixed(4)})` }; B = { o: 0 }; }
        else { const k = 1 - E.outC((u - .5) * 2); A = { o: 0 }; B = { tf: `rotate(${(-24 * k).toFixed(2)}deg) scale(${(1 + .9 * k).toFixed(4)})` }; }
        trang = .5 * gc ** 4; rgb = 24 * gc ** 2; break;
      }
      case 'glitch': {
        const f = Math.floor(t * FPS + 1e-4), nhay = gc > .45 && rngSeed(7919 * f + 13)() < .3;
        const hienB = (t >= c.tu) !== nhay;
        if (hienB) A = { o: 0 }; else B = { o: 0 };
        rgb = 30 * gc; clX = (rngSeed(31 * f + 7)() - .5) * 26 * gc;
        if (gc > .02) fx = { loai: 'glitch', a: ra, b: vao, hienB, g: gc, f };
        break;
      }
      case 'lat_3d': {
        const e = E.ioC(u);
        A = { org: '100% 50%', tf: `translateX(${(-W * e).toFixed(1)}px) rotateY(${(-90 * e).toFixed(2)}deg)`, f: `brightness(${(1 - .6 * e).toFixed(3)})` };
        B = { org: '0% 50%', tf: `translateX(${(W * (1 - e)).toFixed(1)}px) rotateY(${(90 * (1 - e)).toFixed(2)}deg)`, f: `brightness(${(.4 + .6 * e).toFixed(3)})` };
        rgb = 8 * Math.sin(Math.PI * u);
        clS = 1 + .28 * Math.sin(Math.PI * e);                      // phóng theo lúc xoay: mép xa của khối không hở nền đen
        po = W * (1 - e);                                           // điểm nhìn bám cạnh khối → luôn thấy 2 mặt từ NGOÀI (không lộ mặt trong)
        break;
      }
      case 'chay_phim': {
        const k = Math.sin(Math.PI * u), f = `brightness(${(1 + .8 * k ** 1.5).toFixed(3)}) saturate(${(1 + .3 * k).toFixed(3)})`;
        if (t < c.tu) { A = { f }; B = { o: 0 }; } else { A = { o: 0 }; B = { f }; }
        chay = k; chayU = u; trang = .45 * k ** 6; break;
      }
      case 'xuyen': {
        if (u < .5) { const k = E.inC(u * 2); A = { tf: `scale(${(1 + 1.2 * k).toFixed(4)})`, f: `brightness(${(1 + .7 * k).toFixed(3)})` }; B = { o: 0 }; }
        else { const k = 1 - E.outC((u - .5) * 2); A = { o: 0 }; B = { tf: `scale(${(1 + .55 * k).toFixed(4)})`, f: `brightness(${(1 + .6 * k).toFixed(3)})` }; }
        trang = .55 * gc ** 3; rgb = 30 * gc ** 1.5;
        if (t >= c.tu) rungFx = .7 * (1 - P(t, c.tu, .35, E.outC));
        break;
      }
      case 'iris': {
        const e = E.ioC(u), R = e * Math.hypot(W, H) / 2 * 1.04, sB = 1.12 - .12 * e;
        A = { tf: `scale(${(1 + .1 * e).toFixed(4)})`, f: `brightness(${(1 - .35 * e).toFixed(3)})` };
        B = { clip: `circle(${R.toFixed(1)}px at 50% 50%)`, tf: `scale(${sB.toFixed(4)})` };
        iris = { R: R * sB, o: Math.min(1, 4 * (1 - e), e * 12) }; rgb = 10 * Math.sin(Math.PI * u); break;
      }
      case 'tia_sang': {
        const e = E.ioC(u), k = Math.tan(18 * Math.PI / 180) * H / 2, bx = lerp(-k - 300, W + k + 300, e), s = Math.sin(Math.PI * u);
        B = { clip: `polygon(0 0, ${(bx + k).toFixed(1)}px 0, ${(bx - k).toFixed(1)}px ${H}px, 0 ${H}px)` };
        man = bx; loe = Math.pow(s, .8); trang = .22 * s ** 4; rgb = 8 * s; break;
      }
      // ---------- CẮT NHANH (montage tổng hợp ≤ 10 s đầu) — cắt cứng đúng phách + lực ----------
      case 'dap': {
        if (t < c.tu) { A = { tf: `scale(${(1 + .05 * P(t, c.tu - dt, dt, E.inC)).toFixed(4)})` }; B = { o: 0 }; }
        else { const k = 1 - P(t, c.tu, .2, E.outC); A = { o: 0 }; B = { tf: `scale(${(1 + .14 * k).toFixed(4)})` }; rgb = 20 * k; rungFx = .5 * k; trang = .06 * k; }
        break;
      }
      case 'nhay_trang': {
        if (t < c.tu) { B = { o: 0 }; trang = .25 * P(t, c.tu - dt, dt, E.inC); }
        else { const k = 1 - P(t, c.tu, .1, E.outC); A = { o: 0 }; B = { tf: `scale(${(1 + .08 * (1 - P(t, c.tu, .25, E.outC))).toFixed(4)})` }; trang = .85 * k; rgb = 10 * k; }
        break;
      }
      case 'nhay_den': {
        if (t < c.tu) { const k = P(t, c.tu - Math.min(.08, dt), Math.min(.08, dt)); A = { f: `brightness(${(1 - .9 * k).toFixed(3)})` }; B = { o: 0 }; }
        else { const k = 1 - P(t, c.tu, .13, E.outC); A = { o: 0 }; B = { f: `brightness(${(1 + .9 * k).toFixed(3)}) contrast(${(1 + .15 * k).toFixed(3)})`, tf: `scale(${(1 + .1 * k).toFixed(4)})` }; rgb = 14 * k; }
        break;
      }
      case 'day_nhanh': {                                           // ĐẨY phải → trái mỗi 1 phách (đoạn dồn 1 hướng = nối mạch)
        if (t < c.tu) { B = { o: 0 }; break; }
        const q = clamp((t - c.tu) / Math.max(.12, ds)), e = E.outC(q);   // vòng 5: cửa sổ = DAY_S 0,34 s (script), chậm dần đều (0,2 s outE "nhanh quá, khó chịu")
        A = { tf: `translateX(${f1(-W * e)}px)`, f: `brightness(${(1 - .3 * e).toFixed(3)})` };
        B = { tf: `translateX(${f1(W * (1 - e))}px)` };
        raDxV = -W * e;
        if (e < .995) vach = W * (1 - e);
        rgb = 12 * (1 - q); break;
      }
      // ---------- 5 KỸ XẢO MẪU người dùng gửi (C, D, E, F; A = nhóm ba cột ở trên) ----------
      case 'khung_bung': {                                          // C — khung nhỏ viền trắng giữa cảnh cũ → lớn dần → tràn
        if (t < c.tu) { B = { o: 0 }; break; }
        const tt = t - c.tu, p = clamp(tt / ds), p_ = c.p || 0;
        let s, nhay, vien;
        if (p_) {                                                   // montage: BẬT nhỏ (phách) → vừa (½ phách) → TRÀN (phách sau) — mỗi nấc 1 cú nảy
          const n1 = clamp(tt / .2), n2 = clamp((tt - .5 * p_) / .2), n3 = clamp((tt - p_) / .17);
          s = lerp(.12, .36, E.outB(n1));
          if (n2 > 0) s = lerp(s, .64, E.outB(n2));
          if (n3 > 0) s = lerp(s, 1, E.outE(n3));
          nhay = Math.max(1 - n1, n2 > 0 ? 1 - n2 : 0, n3 > 0 ? 1 - n3 : 0); vien = 1 - n3;
        } else {
          s = p < .16 ? lerp(.12, .3, E.outB(p / .16)) : p < .6 ? lerp(.3, .78, E.ioS((p - .16) / .44)) : lerp(.78, 1, E.ioC((p - .6) / .4));
          nhay = 1 - clamp(p / .16); vien = 1 - clamp((p - .8) / .2);
        }
        A = { f: `brightness(${(1 - .32 * Math.min(1, p * 4)).toFixed(3)})`, tf: `scale(${(1 + .07 * p).toFixed(4)})` };
        B = { tf: `scale(${s.toFixed(4)})`, shadow: VIEN(s, vien) };
        rgb = 10 * nhay; break;
      }
      case 'hai_nua': {                                             // F — ĐẨY: cảnh cũ bị đẩy sang trái, cảnh mới lộ sau mép sáng; 3 nấc đúng phách
        if (t < c.tu) { B = { o: 0 }; break; }
        const tt = t - c.tu, p_ = c.p || 0, s1 = vao.s1 || .66 * W, s2 = Math.min(.33 * W, .55 * s1);
        const nac = p_ ? [[0, s1], [.5 * p_, s2], [p_, 0]] : [[0, s1], [.36 * ds, s2], [.72 * ds, 0]], dn = p_ ? .17 : .22 * ds;
        let x = W, nhay = 0;
        for (const [t0, v] of nac) { const q = clamp((tt - t0) / dn); if (q > 0) { x = lerp(x, v, E.outE(q)); nhay = Math.max(nhay, 1 - q); } }
        if (x <= .5) { A = { o: 0 }; B = {}; }
        else {
          A = { tf: `translateX(${f1(x - W)}px)`, f: `brightness(${(1 - .28 * (1 - x / W)).toFixed(3)})` };
          B = { clip: `inset(0px 0px 0px ${f1(x)}px)` };
          vach = x < W - 1 ? x : null;
        }
        dayX = { o: vao, x };
        if (vao.c.nv && vao.c.nv.src) {                             // người nhô qua mép ở nấc 1, về đúng chỗ khi mép qua hết người
          const t2 = nac[1][0], op = 1 - clamp((tt - t2 - dn) / .12);
          if (op > 0) nvO = { o: vao, op, pop: 1 - E.outC(clamp((tt - t2) / dn)) };
        }
        rgb = 9 * nhay; break;
      }
      case 'hai_nua_doc': {                                         // F' — chia TRÊN / DƯỚI: cảnh mới dâng từ nửa dưới lên
        if (t < c.tu) { B = { o: 0 }; break; }
        const p = clamp((t - c.tu) / ds), p_ = c.p || 0, tt = t - c.tu, L = H, g = 10;
        let x = L, nhay = 0;
        for (const [t0, v] of (p_ ? [[0, .5], [p_, 0]] : [[0, .5], [.5 * ds, 0]])) {
          const q = clamp((tt - t0) / (p_ ? .17 : .22 * ds)); if (q > 0) { x = lerp(x, v * L, E.outE(q)); nhay = Math.max(nhay, 1 - q); }
        }
        const wa = Math.max(0, x - g / 2), wb = Math.max(0, L - x - g / 2);
        if (x <= .5) { A = { o: 0 }; B = {}; }
        else {
          A = { clip: `inset(${f1((H - wa) / 2)}px 0px ${f1((H - wa) / 2)}px 0px)`, tf: `translateY(${f1(wa / 2 - H / 2)}px)` };
          B = { clip: `inset(${f1((H - wb) / 2)}px 0px ${f1((H - wb) / 2)}px 0px)`, tf: `translateY(${f1(H / 2 - wb / 2)}px)` };
        }
        dayX = { o: vao, x }; void p;
        rgb = 9 * nhay; break;
      }
      case 'dai_truot': {                                           // D — cảnh cũ tối, dải ảnh trượt ngang, ảnh cảnh mới dừng giữa → phóng tràn
        const S_ = DAI[c.id], tw = W * .3, th = H * .3, st = tw + 22, n = S_ ? S_.it.length : 0;
        if (t < c.tu) {
          const q = clamp((t - (c.tu - dt)) / dt), s0 = tw / W, p_ = c.p || 0;
          let cB;
          if (p_ && dt >= .9 * p_) {                                // montage: dải VÀO đúng phách → KHỰNG ½ phách (ảnh đỉnh vào giữa) → phóng đúng phách
            const a1 = E.outE(clamp((t - (c.tu - dt)) / .2)), a2 = E.outE(clamp((t - (c.tu - .5 * p_)) / .18));
            cB = lerp(lerp(W / 2 + (n + 1.2) * st, W / 2 + st, a1), W / 2, a2);
          } else cB = lerp(W / 2 + (n + 1.2) * st, W / 2, E.outC(q));
          A = { f: `brightness(${(1 - .62 * Math.min(1, q * 3)).toFixed(3)})`, tf: `scale(${(1 + .06 * q).toFixed(4)})` };
          B = { tf: `translateX(${f1(cB - W / 2)}px) scale(${s0.toFixed(4)})`, shadow: VIEN(s0, 1) };
          dai = { S_, cB, xa: 0, op: Math.min(1, q * 6), tw, th, st, n };
        } else {
          const p = clamp((t - c.tu) / ds), e = (c.p ? E.outE : E.ioC)(p), s = lerp(tw / W, 1, e);   // montage: phóng BẬT đúng phách
          A = { f: 'brightness(.38)', tf: 'scale(1.06)' };                // cảnh cũ giữ tối phía sau tới khi cảnh mới phủ kín (không lộ mép đen)
          B = { tf: `scale(${s.toFixed(4)})`, shadow: VIEN(s, 1 - e) };
          dai = { S_, cB: W / 2, xa: e, op: 1, tw, th, st, n }; rgb = 8 * Math.sin(Math.PI * p);
        }
        break;
      }
      case 'khop_hinh': {                                           // E — hình giống nhau trùng CHỖ + CỠ lúc cắt, rồi cảnh mới về khung thường
        const kp = c.khop || {}, ra_ = kp.ra || [.5, .5, .2], vo_ = kp.vao || [.5, .5, .2], ZA = 1.28;
        const PA = [ra_[0] * W, ra_[1] * H], PB = [vo_[0] * W, vo_[1] * H];
        if (t < c.tu) {
          A = { org: `${f1(PA[0])}px ${f1(PA[1])}px`, tf: `scale(${(1 + (ZA - 1) * E.inC(clamp((t - (c.tu - dt)) / dt))).toFixed(4)})` }; B = { o: 0 };
        } else {
          const e = E.outC(clamp((t - c.tu) / ds));
          let dx = PA[0] - PB[0], dy = PA[1] - PB[1];
          const can = Math.max(dx > 0 ? dx / Math.max(1, PB[0]) : -dx / Math.max(1, W - PB[0]), dy > 0 ? dy / Math.max(1, PB[1]) : -dy / Math.max(1, H - PB[1]));
          const k0 = Math.min(2.2, Math.max(1, ra_[2] * ZA / Math.max(.02, vo_[2]), 1 + can));
          dx = Math.min((k0 - 1) * PB[0], Math.max(-(k0 - 1) * (W - PB[0]), dx));
          dy = Math.min((k0 - 1) * PB[1], Math.max(-(k0 - 1) * (H - PB[1]), dy));
          A = { o: 0 };
          B = { org: `${f1(PB[0])}px ${f1(PB[1])}px`, tf: `translate(${f1(dx * (1 - e))}px, ${f1(dy * (1 - e))}px) scale(${lerp(k0, 1, e).toFixed(4)})` };
          trang = .18 * (1 - P(t, c.tu, .1, E.lin));
        }
        break;
      }
      default: B = { o: E.ioS(u) };
    }
    ra.root.style.zIndex = '1'; vao.root.style.zIndex = c.chuyen === 'dai_truot' ? '4' : '2';
    apDung(ra, A); apDung(vao, B);
    if (ra.c.day_chu) raDx = { o: ra, dx: raDxV, op: c.chuyen === 'day_nhanh' ? 1 : 1 - clamp(u * 2) };   // chữ đẩy đi cùng cảnh cũ
  }
  for (const o of vis) veCanh(o, t);
  // F — chữ chạy theo mép đẩy / đứng giữa / bị đẩy ra; người nhô qua mép; vạch sáng ở mép
  for (const D of DC) {
    let st = null;
    if (dayX && dayX.o === D.o) st = { x: dayX.x, dx: 0, op: 1 };
    else if (raDx && raDx.o === D.o) st = { x: 0, dx: raDx.dx, op: raDx.op };
    else if (!gN && vis.length && vis[vis.length - 1] === D.o && t >= D.o.c.tu) st = { x: 0, dx: 0, op: 1 };
    veDayChu(D, st);
  }
  for (const N of NV) {
    if (!nvO || nvO.o !== N.o) { show(N.el, false); continue; }
    show(N.el, true);
    setSrc(N.im, N.o.c.nv.src);
    const k = kbOf(N.o, t), hop = N.o.c.nv.hop, cx = xMan((hop[0] + hop[2]) / 2, k), cy = H / 2 + k.y * H + k.s * ((hop[1] + hop[3]) / 2 * H - H / 2);
    N.im.style.transform = tfKB(k, W, H);
    const pp = nvO.pop;
    css(N.el, { opacity: nvO.op.toFixed(3), transformOrigin: `${f1(cx)}px ${f1(cy)}px`, transform: pp > .002 ? `scale(${(1 + .06 * pp).toFixed(4)})` : 'none',
      filter: pp > .02 ? `drop-shadow(0 0 4px rgba(255,255,255,${(.95 * pp).toFixed(3)})) drop-shadow(0 14px 26px rgba(0,0,0,${(.5 * pp).toFixed(3)}))` : 'none' });
  }
  if (vach != null) { show(VACH, true); VACH.style.transform = `translateX(${f1(vach)}px)`; } else show(VACH, false);
  for (const k in DAI) if (!dai || DAI[k] !== dai.S_) show(DAI[k].el, false);
  if (dai && dai.S_) {
    show(dai.S_.el, true);
    dai.S_.it.forEach((x, j) => {
      const m = Math.ceil(dai.n / 2), off = (j < m ? j - m : j - m + 1) * dai.st;   // ảnh dải 2 bên ảnh cảnh mới (giữa dải)
      const cx = dai.cB + off * (1 + 1.6 * dai.xa);
      setSrc(x.im, partUrl(x.x.c.lop[0], x.x.c.tu + .1, x.x.c.a));
      css(x.im, { width: f1(dai.tw) + 'px', height: f1(dai.th) + 'px', opacity: (dai.op * (1 - dai.xa)).toFixed(3),
        transform: `translate(${f1(cx - dai.tw / 2)}px, ${f1(H / 2 - dai.th / 2)}px)` });
    });
  }
  if (CAO_TRAO) {
    if (CAO_TRAO.mo && t < .7) { const k = 1 - P(t, 0, .6, E.outC); clS *= 1 + .32 * k; rgb = Math.max(rgb, 26 * k); }   // khung 0: đập mở màn
    for (const h of CAO_TRAO.dap || []) if (t >= h.t - .02 && t < h.t + .4) {                 // đập theo PHÁCH giữa 2 cú cắt
      const k = 1 - P(t, h.t, .34, E.outC);
      clS *= 1 + .055 * h.m * k; rgb = Math.max(rgb, 12 * h.m * k); trang = Math.max(trang, .16 * h.m * k);
    }
  }
  css(CL, { perspectiveOrigin: po != null ? `${f1(po)}px 50%` : '50% 50%' });
  if (fx) { show(FXC, true); const j = fx; VE_SAU.push(() => veFx(j, t)); } else show(FXC, false);
  if (chay > .005) {
    show(CHAY, true); CHAY.style.opacity = Math.min(1, chay * 1.25).toFixed(3);
    CHAY_D.forEach((el, i) => {
      const q = CHAY_DUONG[i];
      el.style.transform = `translate(${(lerp(q[0], q[2], chayU) * W).toFixed(1)}px, ${(lerp(q[1], q[3], chayU) * H).toFixed(1)}px) scale(${lerp(q[4], q[5], chayU).toFixed(3)})`;
    });
  } else show(CHAY, false);
  if (iris && iris.o > .01) {
    show(VONG, true);
    css(VONG, { width: f1(2 * iris.R) + 'px', height: f1(2 * iris.R) + 'px', transform: `translate(${f1(W / 2 - iris.R)}px, ${f1(H / 2 - iris.R)}px)`, opacity: iris.o.toFixed(3) });
  } else show(VONG, false);
  let rung = rungFx;
  for (const dt of DROP) if (t >= dt - .02 && t < dt + .5) {
    trang = Math.max(trang, .9 * (1 - P(t, dt, .38, E.outC)));
    rung = Math.max(rung, 1 - P(t, dt, .42, E.outC));
  }
  // tách màu: phóng nhẹ khung cho dải mép thiếu kênh màu ra ngoài khung
  const sc = clS * (1 + .03 * rung) * (rgb > .4 ? 1 + 2.4 * rgb / W : 1);
  const tx = clX + Math.sin(t * 97) * 14 * rung, ty = Math.cos(t * 83) * 10 * rung;
  CL.style.transform = (Math.abs(sc - 1) > 1e-4 || Math.abs(tx) > .05 || Math.abs(ty) > .05) ? `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) scale(${sc.toFixed(4)})` : 'none';
  if (rgb > .4) { RGB_R.setAttribute('dx', rgb.toFixed(1)); RGB_B.setAttribute('dx', (-rgb).toFixed(1)); CL.style.filter = 'url(#rgb_tach)'; }
  else CL.style.filter = 'none';
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
    const ta = mk('span', 'dong ' + cls, parent, esc(a)); ta.style.fontSize = base + 'px';
    const tb = mk('span', 'dong ' + cls, parent, esc(b)); tb.style.fontSize = base + 'px';
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
function hangNhan(parent, text, co = 32, giua = false) {   // ── NHÃN ── (gạch ngọc + chữ in giãn)
  const r = mk('div', '', parent); css(r, { display: 'flex', alignItems: 'center', gap: '18px' });
  const g1 = mk('div', 'gach_n', r); const tx = mk('div', 'nhan_nho', r, esc(text)); css(tx, { fontSize: co + 'px' });
  const g2 = giua ? mk('div', 'gach_n', r) : null;
  return { r, g1, tx, g2 };
}

// bản đồ Việt Nam (đường viền Natural Earth, LUÔN có Hoàng Sa / Trường Sa)
const VN = window.VN_BAN_DO || null;
function chieu(lat, lon, bb, w, h) {        // equirectangular có hiệu chỉnh cos(vĩ độ giữa)
  const k = Math.cos((bb[1] + bb[3]) / 2 * Math.PI / 180);
  const sx = w / ((bb[2] - bb[0]) * k), sy = h / (bb[3] - bb[1]), s = Math.min(sx, sy);
  const ox = (w - (bb[2] - bb[0]) * k * s) / 2, oy = (h - (bb[3] - bb[1]) * s) / 2;
  return [ox + (lon - bb[0]) * k * s, oy + (bb[3] - lat) * s];
}
function svgBanDo(w, h, o = {}) {
  if (!VN) return '';
  const vien = o.vien || 'rgba(255,255,255,.9)', to = o.to || 'rgba(79,227,208,.16)', chu = o.chu || 'rgba(255,255,255,.8)', cham = o.cham || vien;
  const bb = VN.bbox;
  const path = VN.duong.map(ring => 'M' + ring.map(([lo, la]) => chieu(la, lo, bb, w, h).map(v => v.toFixed(1)).join(',')).join('L') + 'Z').join('');
  const dao = (VN.dao || []).map(q => {
    const pts = q.diem.map(([la, lo]) => chieu(la, lo, bb, w, h));
    const nhan = chieu(q.nhan[0], q.nhan[1], bb, w, h);
    return pts.map(p => `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${(w / 190).toFixed(1)}" fill="${cham}"/>`).join('') +
      `<text x="${nhan[0].toFixed(1)}" y="${nhan[1].toFixed(1)}" fill="${chu}" font-family="BVP" font-weight="700" font-size="${(w / 19).toFixed(1)}" text-anchor="middle">${esc(q.ten)}</text>`;
  }).join('');
  return `<path d="${path}" fill="${to}" stroke="${vien}" stroke-width="${(w / 170).toFixed(1)}" stroke-linejoin="round"/>${dao}`;
}

// ---------------- BẢN ĐỒ A → B kiểu Google Maps (ảnh vệ tinh thật, camera tính sẵn ở ban_do_that.py) ----------------
// Ô ảnh nạp theo nhu cầu: __seek chờ ô của khung đó decode xong (CHO) rồi mới vẽ canvas (VE_SAU); ô lâu không dùng thì nhả.
const CHO = [], VE_SAU = [];
const ANH_O = new Map();
let KHUNG_SO = 0;
function oAnh(base, z, x, y) {
  const k = `${z}_${x}_${y}`;
  let o = ANH_O.get(k);
  if (!o) { const im = new Image(); im.src = base + k + '.jpg'; o = { im, p: im.decode().catch(() => null) }; ANH_O.set(k, o); }
  o.dung = KHUNG_SO;
  if (!o.im.complete) CHO.push(o.p);
  return o.im;
}
function donAnhO() {
  if (ANH_O.size < 900) return;
  for (const [k, o] of ANH_O) if (KHUNG_SO - o.dung > 40) { o.im.src = ''; ANH_O.delete(k); }
}
const MAY_BAY_TREN = `<svg viewBox="0 0 100 100"><defs><linearGradient id="mbg" x1="0" x2="1"><stop offset="0" stop-color="#E9EDF2"/><stop offset=".5" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D5DBE3"/></linearGradient></defs>
  <path d="M50 2C55 2 57 9 57 17L57 36L95 57L95 66L57 55L56 79L69 89L69 95L50 90L31 95L31 89L44 79L43 55L5 66L5 57L43 36L43 17C43 9 45 2 50 2Z" fill="url(#mbg)" stroke="rgba(30,40,55,.45)" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M50 8V86" stroke="rgba(30,40,55,.18)" stroke-width="2"/><circle cx="50" cy="12" r="3.2" fill="#22324a"/></svg>`;
const GHIM_GG = `<svg viewBox="0 0 74 98" width="74" height="98"><path d="M37 95C37 95 5 57 5 33.5A32 32 0 0 1 69 33.5C69 57 37 95 37 95Z" fill="#EA4335" stroke="#B3261E" stroke-width="3" stroke-linejoin="round"/><circle cx="37" cy="33" r="12.5" fill="#7A1C14"/></svg>`;
const IC_PT = { o_to: 'o_to', xe_may: 'xe_may', xe_buyt: 'xe_buyt', tau_hoa: 'tau_hoa', tau_thuy: 'tau', xe_dap: 'xe_may', di_bo: 'di_bo', may_bay: 'may_bay', khong: 'o_to' };
let BD_U = 0;
function banDoAB(d, o) {
  const u = ++BD_U;
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const bd = d.bd;
  if (!bd || !bd.cam || !bd.cam.length) { console.error('bản đồ ' + d.id + ': thiếu bd (chưa chuẩn bị bản đồ thật)'); return { el, init() { }, ve() { show(el, false); } }; }
  const n = mk('div', 'bd_ab', el);
  const cv = mk('canvas', 'bd_cv', n); cv.width = W; cv.height = H;
  const g = cv.getContext('2d'); g.imageSmoothingQuality = 'high';
  mk('div', 'bd_toi', n);
  const [FX, FY] = bd.foc || [1110, 470];
  const R = bd.duong;
  const cum = [0];
  for (let i = 1; i < R.length; i++) cum.push(cum[i - 1] + Math.hypot(R[i][0] - R[i - 1][0], R[i][1] - R[i - 1][1]));
  const LT = cum[cum.length - 1] || 1e-9;
  const pt = d.phuong_tien || 'o_to', may = pt === 'may_bay';
  n.insertAdjacentHTML('beforeend', `<svg class="bd_tuyen" width="${W}" height="${H}">
    <path class="v0" fill="none" stroke="rgba(26,79,176,.8)" stroke-width="${may ? 0 : 15}" stroke-linecap="round" stroke-linejoin="round"/>
    <path class="m0" fill="none" stroke="${may ? 'rgba(255,255,255,.85)' : '#A9C8FB'}" stroke-width="${may ? 5 : 8}" stroke-linecap="round" stroke-linejoin="round" ${may ? 'stroke-dasharray="3 16"' : ''}/>
    <path class="v1" fill="none" stroke="#1A4FB0" stroke-width="${may ? 13 : 17}" stroke-linecap="round" stroke-linejoin="round"/>
    <path class="s1" fill="none" stroke="#4C8DF6" stroke-width="${may ? 8 : 10}" stroke-linecap="round" stroke-linejoin="round"/></svg>`);
  const pV0 = n.querySelector('.v0'), pM0 = n.querySelector('.m0'), pV1 = n.querySelector('.v1'), pS1 = n.querySelector('.s1');
  const songA = mk('div', 'bd_song', n), dotA = mk('div', 'bd_a', n);
  const xe = mk('div', 'bd_xe', n, may ? `<div class="mb">${MAY_BAY_TREN}</div>` : `<div class="ic">${icon(IC_PT[pt] || 'o_to')}</div>`);
  const ghim = mk('div', 'bd_ghim', n, GHIM_GG);
  const tagA = mk('div', 'bd_tag', n, esc(d.xuat_phat.ten)), tagB = mk('div', 'bd_tag den', n, esc(d.diem_den.ten));
  // thẻ thông tin kiểu Google Maps: tuyến · ≈ giờ (xanh lá) · km (đếm theo xe chạy) · ghi chú ước tính
  const the = mk('div', 'the_tt', el);
  const coGio = !!d.chu_gio;
  the.innerHTML = `<div class="tt_nhan">${esc(o.the_nhan || T.tuyen || '')}</div>
    <div class="tt_tuyen"><span>${esc(d.xuat_phat.ten)}</span><span class="mui">→</span><span>${esc(d.diem_den.ten)}</span></div>
    <div class="tt_hang"><div class="tt_ic">${icon(IC_PT[pt] || 'o_to')}</div>${coGio ? `<div class="tt_gio">${esc(d.chu_gio)}</div>` : ''}<div class="${coGio ? 'tt_km' : 'tt_gio'}"></div></div>
    ${d.chu_ghi ? `<div class="tt_ghi">${esc(d.chu_ghi)}</div>` : ''}`;
  const kmEl = the.querySelector('.tt_hang > div:last-child');
  const kmSo = d.km_so, kmChu = d.chu_km || '';
  const fmtKm = x => { let s = x >= 20 ? String(Math.round(x)) : x.toFixed(1); if (NN === 'vi') s = s.replace('.', ','); return s + ' km'; };
  // bản đồ Việt Nam nhỏ góc phải (có Hoàng Sa, Trường Sa) + tuyến A → B
  let vn = null, vnLine = null, vnLen = 1;
  if (VN) {
    const mw = 196, mh = 300;
    vn = mk('div', 'the_vn', el);
    const [ax, ay] = chieu(d.xuat_phat.toa_do[0], d.xuat_phat.toa_do[1], VN.bbox, mw, mh);
    const [bx, by] = chieu(d.diem_den.toa_do[0], d.diem_den.toa_do[1], VN.bbox, mw, mh);
    vnLen = Math.hypot(bx - ax, by - ay) || 1;
    vn.innerHTML = `<svg width="${mw}" height="${mh}" viewBox="0 0 ${mw} ${mh}" style="display:block;overflow:visible">${svgBanDo(mw, mh, { to: '#E6EDF2', vien: '#8D99A6', chu: '#5F6368', cham: '#8D99A6' })}
      <line class="vn_l" x1="${f1(ax)}" y1="${f1(ay)}" x2="${f1(bx)}" y2="${f1(by)}" stroke="#4C8DF6" stroke-width="4" stroke-linecap="round" stroke-dasharray="${f1(vnLen)}" stroke-dashoffset="${f1(vnLen)}"/>
      <circle cx="${f1(ax)}" cy="${f1(ay)}" r="5" fill="#fff" stroke="#1A4FB0" stroke-width="3"/>
      <circle cx="${f1(bx)}" cy="${f1(by)}" r="6.5" fill="#EA4335" stroke="#fff" stroke-width="2.5"/></svg>`;
    vnLine = vn.querySelector('.vn_l');
  }
  // tên điểm đến lớn khi tới nơi
  const tn = mk('div', 'toi_noi', el);
  const tnN = o.nhan ? hangNhan(tn, o.nhan, 32, true) : null;
  const tnMask = mk('div', 'mask', tn); const tnTen = mk('div', 'tit', tnMask, esc(o.ten)); css(tnTen, { whiteSpace: 'nowrap' });
  const tnPhu = o.phu ? mk('div', 'nghieng', tn, esc(o.phu)) : null;
  if (tnPhu) css(tnPhu, { fontSize: '40px', marginTop: '14px', whiteSpace: 'nowrap' });   // 14 px: chừa chỗ dấu nặng (VỊNH HẠ LONG)
  if (tnN) css(tnN.r, { marginBottom: '8px' });
  const camTai = t => {
    const f = clamp((t - d.tu) * FPS, 0, bd.cam.length - 1), i = Math.floor(f), j = Math.min(bd.cam.length - 1, i + 1), k = f - i;
    const a = bd.cam[i], b = bd.cam[j];
    return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
  };
  const diemTai = kp => {
    const L = kp * LT;
    let i = 1; while (i < cum.length - 1 && cum[i] < L) i++;
    const a = R[i - 1], b = R[i], s = cum[i] - cum[i - 1], k = s > 0 ? (L - cum[i - 1]) / s : 0;
    let j = i; while (j < R.length - 1 && Math.hypot(R[j][0] - a[0], R[j][1] - a[1]) < LT * .004) j++;
    const q = R[j];
    return { i, x: lerp(a[0], b[0], k), y: lerp(a[1], b[1], k), goc: Math.atan2(q[1] - a[1], q[0] - a[0]) };
  };
  const dat = (e, x, y) => css(e, { left: f1(x) + 'px', top: f1(y) + 'px' });
  let wA = 0, hA = 0, wB = 0, hB = 0;
  return {
    el,
    init() {
      wA = tagA.offsetWidth; hA = tagA.offsetHeight; wB = tagB.offsetWidth; hB = tagB.offsetHeight;
      vua(tnTen, o.co || 150, 1180);
      const w = tn.offsetWidth;
      css(tn, { left: f1(clamp(FX - w / 2, 640, W - 96 - w)) + 'px', top: (FY + 58) + 'px' });
      if (kmSo == null) kmEl.textContent = kmChu;
      HOP.push({ el: tnTen, d }); HOP.push({ el: the, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      const e = P(t, d.tu, .4, E.outC);
      css(n, { opacity: (clamp(e * 1.6) * (1 - v.r)).toFixed(3), transform: `scale(${(1.07 - .07 * e + .05 * v.r).toFixed(4)})` });
      const [fx, fy, z] = camTai(t), sc = 256 * Math.pow(2, z);
      const P2 = (x, y) => [(x - fx) * sc + FX, (y - fy) * sc + FY];
      const L = Math.max(1, Math.min(18, Math.floor(z + .5))), ve = [];
      for (const lv of [Math.max(1, L - 2), L]) {
        const nn = Math.pow(2, lv), s = 256 * Math.pow(2, z - lv);
        const x0 = Math.floor((fx - FX / sc) * nn), x1 = Math.floor((fx + (W - FX) / sc) * nn);
        const y0 = Math.max(0, Math.floor((fy - FY / sc) * nn)), y1 = Math.min(nn - 1, Math.floor((fy + (H - FY) / sc) * nn));
        for (let tx = x0; tx <= x1; tx++) for (let ty = y0; ty <= y1; ty++) {
          const im = oAnh(bd.tile, lv, md(tx, nn), ty);
          ve.push([im, (tx / nn - fx) * sc + FX, (ty / nn - fy) * sc + FY, s]);
        }
      }
      VE_SAU.push(() => {
        g.fillStyle = '#0d1624'; g.fillRect(0, 0, W, H);
        for (const [im, x, y, s] of ve) if (im.complete && im.naturalWidth) g.drawImage(im, x - .4, y - .4, s + .8, s + .8);
      });
      // tuyến: cả tuyến xanh nhạt hiện trước, tuyến xanh đậm chạy theo xe
      const SS = R.map(p => P2(p[0], p[1]));
      const dd = a => a.map((p, i) => (i ? 'L' : 'M') + f1(p[0]) + ' ' + f1(p[1])).join('');
      const full = dd(SS);
      const hien = P(t, d.tu + .2, .45);
      pV0.setAttribute('d', full); pM0.setAttribute('d', full);
      css(pV0, { opacity: (hien * .85).toFixed(3) }); css(pM0, { opacity: hien.toFixed(3) });
      const kp = P(t, d.luc_di, Math.max(.3, d.luc_den - d.luc_di), E.ioS);
      const vt = diemTai(kp), pv = P2(vt.x, vt.y);
      const chay = kp > 0 ? dd(SS.slice(0, vt.i).concat([pv])) : '';
      pV1.setAttribute('d', chay); pS1.setAttribute('d', chay);
      // xe / máy bay
      const kx = P(t, d.luc_di - .3, .35, E.outB), kr = P(t, d.luc_den - .05, .3);
      dat(xe, pv[0], pv[1]); css(xe, { opacity: (clamp(kx * 2) * (1 - kr)).toFixed(3) });
      if (xe.firstElementChild) {
        if (may) css(xe.firstElementChild, { transform: `rotate(${f1(vt.goc * 57.2958 + 90)}deg) scale(${(.5 + .5 * kx).toFixed(3)})` });
        else css(xe.firstElementChild, { transform: `scale(${(.5 + .5 * kx).toFixed(3)})` });
      }
      // điểm đi: chấm xanh "vị trí" + sóng lan
      const pa = SS[0], pb = SS[SS.length - 1];
      dat(dotA, pa[0], pa[1]); css(dotA, { opacity: P(t, d.tu + .1, .3).toFixed(3) });
      { const pr = md(t - d.tu, 1.6) / 1.2; dat(songA, pa[0], pa[1]); css(songA, { opacity: pr <= 1 ? (.9 * (1 - pr)).toFixed(3) : '0', transform: `scale(${(1 + 1.4 * E.outC(Math.min(1, pr))).toFixed(3)})` }); }
      { const k = P(t, d.tu + .3, .4), duoi = pa[1] + 30 + hA < 900;
        dat(tagA, clamp(pa[0] - wA / 2, 40, W - 40 - wA), duoi ? pa[1] + 30 : pa[1] - 30 - hA);
        css(tagA, { opacity: (k * (1 - .4 * P(t, d.luc_den, .4))).toFixed(3), transform: `translateY(${f1(12 * (1 - k))}px)` }); }
      // điểm đến: nhãn đỏ khi lùi xa → ghim Google rơi lúc tới → tên lớn
      { const k = P(t, d.tu + .45, .4) * (1 - P(t, d.luc_den + .05, .3)), tren = pb[1] - 40 - hB > 120;
        dat(tagB, clamp(pb[0] - wB / 2, 40, W - 40 - wB), tren ? pb[1] - 40 - hB : pb[1] + 26);
        css(tagB, { opacity: k.toFixed(3) }); }
      const kg = P(t, d.luc_den - .1, .55, E.drop);
      css(ghim, { left: f1(pb[0] - 37) + 'px', top: f1(pb[1] - 96) + 'px', opacity: clamp(kg * 3).toFixed(3), transform: `translateY(${f1(-120 * (1 - kg))}px)` });
      // thẻ thông tin + km đếm theo xe chạy
      { const k = P(t, d.tu + .3, .5, E.outB);
        css(the, { opacity: (clamp(k * 1.5) * (1 - v.r)).toFixed(3), transform: `translateX(${f1(-60 * (1 - k))}px) scale(${(.92 + .08 * k).toFixed(3)})` });
        if (kmSo != null) { const s = fmtKm(kmSo * kp); const txt = coGio ? `(${s})` : '≈ ' + s; if (kmEl.textContent !== txt) kmEl.textContent = txt; } }
      if (vn) { const k = P(t, d.tu + .45, .5, E.outB);
        css(vn, { opacity: (clamp(k * 1.5) * (1 - v.r)).toFixed(3), transform: `scale(${(.8 + .2 * k).toFixed(3)})` });
        vnLine.setAttribute('stroke-dashoffset', f1(vnLen * (1 - kp))); }
      // tên điểm đến
      { const ka = P(t, d.luc_den + .15, .45, E.outC);
        css(tn, { opacity: (clamp(ka * 1.6) * (1 - v.r)).toFixed(3) });
        tnTen.style.transform = `translateY(${f1((1 - ka) * 105)}%)`;
        if (tnN) { const a = P(t, d.luc_den + .05, .35, E.outE); tnN.tx.style.letterSpacing = (.6 - .34 * a).toFixed(3) + 'em';
          tnN.g1.style.transform = `scaleX(${a.toFixed(3)})`; if (tnN.g2) tnN.g2.style.transform = `scaleX(${a.toFixed(3)})`; }
        if (tnPhu) { const a = P(t, d.luc_den + .4, .4); tnPhu.style.opacity = a.toFixed(3); tnPhu.style.transform = `translateY(${f1((1 - a) * 16)}px)`; } }
    },
  };
}

const LAM = {};
// 1. MỞ ĐẦU — CÚ DROP: tên chủ đề ĐẬP vào trọn chữ (phóng 1,28 → 1 trong 0,32 s), vệt sáng ngọc quét qua, nhãn giãn chữ trên,
//    dòng nghiêng ngay sau 0,2 s, dòng dưới. Kèm loé trắng + rung khung (ghepCanh) + tiếng nổ trầm. Chữ hiện NGAY, không chạy từng chữ.
LAM.mo_dau = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .5);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const tren = d.tren ? hangNhan(b, d.tren, 36, d.vi_tri === 'giua') : null;
  if (tren) css(tren.r, { marginBottom: '16px' });
  const chinh = mk('div', 'tit chu_sang', b, esc(d.chinh)); css(chinh, { whiteSpace: 'nowrap', lineHeight: '.92' });
  const tay = d.viet_tay ? mk('div', 'nghieng dam', b, esc(d.viet_tay)) : null;
  const duoi = d.duoi ? mk('div', 'nhan_nho', b, esc(d.duoi)) : null;
  if (duoi) css(duoi, { fontSize: '30px', color: '#fff', marginTop: '24px', letterSpacing: '.34em' });
  return {
    el, init() {
      const co = vua(chinh, d.co || 250, VUNG[d.vi_tri].w * .94);
      if (tay) { vua(tay, 68, VUNG[d.vi_tri].w * .9); css(tay, { marginTop: (co * .05) + 'px', transform: 'rotate(-2deg)' }); }
      HOP.push({ el: chinh, d }); if (tay) HOP.push({ el: tay, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .35); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .2) * (1 - v.r)).toFixed(3);
      const e = P(t, d.tu, .32, E.outC);
      chinh.style.opacity = P(t, d.tu - .02, .08).toFixed(3);
      chinh.style.transform = `scale(${(1.28 - .28 * e).toFixed(4)})`;
      chinh.style.letterSpacing = (.1 - .096 * P(t, d.tu, .9, E.outE)).toFixed(4) + 'em';
      chinh.style.backgroundPosition = `${(100 - 100 * P(t, d.tu + .2, .9, E.ioS)).toFixed(1)}% 50%`;
      if (tren) {
        const a = P(t, d.tu + .04, .25, E.outC);
        tren.tx.style.opacity = a.toFixed(3); tren.tx.style.letterSpacing = (.6 - .34 * a).toFixed(3) + 'em';
        tren.g1.style.transform = `scaleX(${a.toFixed(3)})`; tren.g1.style.transformOrigin = '100% 50%';
        if (tren.g2) { tren.g2.style.transform = `scaleX(${a.toFixed(3)})`; tren.g2.style.transformOrigin = '0% 50%'; }
      }
      if (tay) { const w = P(t, d.tu + .2, .45, E.outC); tay.style.clipPath = `inset(-30% ${((1 - w) * 100).toFixed(1)}% -30% -5%)`; }
      if (duoi) { const a = P(t, d.tu + .35, .3); duoi.style.opacity = a.toFixed(3); duoi.style.transform = `translateY(${((1 - a) * 14).toFixed(1)}px)`; }
      b.style.opacity = (1 - v.r).toFixed(3);
      b.style.transform = `scale(${(1 + .03 * v.r).toFixed(4)})`;
    },
  };
};

// 1b. HOOK_TU — chữ khoá của từng vế câu hook / teaser: khối chữ IN HOA nghiêng đập vào ĐÚNG khung cắt (≤ 0,25 s) + vạch ngọc quét
//     dưới chữ, nhãn nhỏ có ghim; kieu "cau" = câu hỏi chữ nghiêng (khung đầu video). Tắt gọn ở den (0,12 s).
LAM.hook_tu = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const cau = d.kieu === 'cau', giua = d.vi_tri === 'giua';
  const sc = scrim(el, d.vi_tri, cau ? .6 : .45);
  const b = khoi(d.vi_tri, d.y ?? (cau ? 560 : 520)); el.appendChild(b);
  const nh = d.nhan ? mk('div', '', b) : null;
  if (nh) {
    css(nh, { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' });
    const ic = mk('span', '', nh, icon(d.icon || 'ghim')); css(ic, { width: '40px', height: '40px', color: 'var(--nhan)', display: 'inline-flex', filter: 'drop-shadow(0 2px 6px rgba(0,0,0,.7))' });
    const tx = mk('span', 'nhan_nho', nh, esc(d.nhan)); css(tx, { fontSize: '34px' });
  }
  const chu = mk('div', cau ? 'nghieng dam' : 'tit_i', b, esc(d.chu)); css(chu, { whiteSpace: 'nowrap' });
  const vach = cau ? null : mk('div', 'vach_n', b);
  return {
    el, init() {
      vua(chu, d.co || (cau ? 84 : 190), VUNG[d.vi_tri].w * .96);
      if (vach) css(vach, { position: 'relative', width: f1(Math.min(rong(chu) * .42, 420)) + 'px', marginTop: '16px' });
      HOP.push({ el: chu, d });
    },
    ve(t) {
      const on = t >= d.tu - .02 && t < d.den; show(el, on); if (!on) return;
      if (d.dap) {                              // MONTAGE: tên ĐẬP đúng cú cắt 1,6 → 1 trong 0,16 s + giật + đẩy chậm, tắt cứng ở cú cắt sau
        const ngay0 = d.tu <= .01, e = ngay0 ? 1 : P(t, d.tu, .16, E.outC), k = 1 - e, r = P(t, d.den - .05, .05);
        const giu = P(t, d.tu + .16, Math.max(.2, d.den - d.tu - .16), E.lin);
        sc.style.opacity = ((ngay0 ? 1 : P(t, d.tu, .06)) * (1 - r)).toFixed(3);
        chu.style.opacity = (ngay0 ? 1 : P(t, d.tu - .01, .03)).toFixed(3);
        chu.style.letterSpacing = (.02 + .1 * k).toFixed(4) + 'em';
        chu.style.transform = `translate(${(Math.sin(t * 131) * 9 * k).toFixed(1)}px, ${(Math.cos(t * 97) * 6 * k).toFixed(1)}px) scale(${(1 + .6 * k + .05 * giu).toFixed(4)})`;
        if (vach) { const a = ngay0 ? 1 : P(t, d.tu + .04, .2, E.outE); vach.style.transform = `scaleX(${a.toFixed(3)})`; vach.style.transformOrigin = giua ? '50% 50%' : '0 50%'; }
        if (nh) { const a = ngay0 ? 1 : P(t, d.tu + .05, .14, E.outC); nh.style.opacity = a.toFixed(3); nh.style.transform = `translateY(${((1 - a) * 18).toFixed(1)}px)`; }
        b.style.opacity = (1 - r).toFixed(3);
        return;
      }
      const r = P(t, d.den - .12, .12, E.inC);
      const ngay = d.tu <= .01;                 // chữ ở khung 0 (ảnh xem trước YouTube) phải ĐỦ ngay
      sc.style.opacity = ((ngay ? 1 : P(t, d.tu, .12)) * (1 - r)).toFixed(3);
      const e = ngay ? 1 : P(t, d.tu, .25, E.outC);
      chu.style.opacity = ngay ? '1' : P(t, d.tu - .02, .06).toFixed(3);
      chu.style.transform = `scale(${(1.25 - .25 * e + .04 * P(t, d.tu + .25, d.den - d.tu, E.lin)).toFixed(4)})`;
      if (vach) { const a = ngay ? 1 : P(t, d.tu + .08, .3, E.outE); vach.style.transform = `scaleX(${a.toFixed(3)})`; vach.style.transformOrigin = giua ? '50% 50%' : '0 50%'; }
      if (nh) { const a = P(t, d.tu + .08, .2, E.outC); nh.style.opacity = (ngay ? 1 : a).toFixed(3); nh.style.transform = `translateX(${((1 - (ngay ? 1 : a)) * -30).toFixed(1)}px)`; }
      b.style.opacity = (1 - r).toFixed(3);
    },
  };
};

// 2. CHƯƠNG — có toa_do (+ bd): BẢN ĐỒ A → B toàn màn (từ điểm trước tới điểm này, km + giờ), tới nơi hiện tên lớn.
//    Không bản đồ: số viền ngọc tô dần + nhãn "ĐIỂM ĐẾN" + TÊN in hoa lớn + dòng nghiêng.
LAM.chuong = d => {
  if (d.bd) return banDoAB(d, { nhan: `${T.dan_chuong || 'Điểm đến'} ${d.so || ''}`.trim(), ten: d.ten, phu: d.phu, co: d.co, the_nhan: T.tuyen });
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .64);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const hang = mk('div', '', b); css(hang, { display: 'flex', alignItems: 'flex-end', gap: '28px', marginBottom: '6px' });
  const so = mk('div', 'so_vien', hang, esc(d.so || '01'));
  const so2 = mk('div', 'to', so, esc(d.so || '01'));
  const nh = mk('div', 'nhan_chuong', hang); css(nh, { marginBottom: '34px' });
  const g = mk('div', 'gach_n', nh);
  const nt = mk('div', 'nhan_nho', nh, esc(d.nhan || T.dan_chuong || 'Điểm đến')); css(nt, { fontSize: '32px' });
  const ten = mk('div', '', b); css(ten, { lineHeight: '.94' });
  const phu = d.phu ? mk('div', '', b) : null;
  if (phu) { css(phu, { display: 'flex', alignItems: 'center', gap: '14px', marginTop: '22px' });
    const ic = mk('span', '', phu, icon(d.icon || 'ghim')); css(ic, { width: '40px', height: '40px', color: 'var(--nhan)', display: 'inline-flex' });
    const tx = mk('span', 'nghieng', phu, esc(d.phu)); css(tx, { fontSize: '40px' }); }
  let dong = [];
  return {
    el, init() {
      dong = dong2(ten, d.ten, d.co || 160, VUNG[d.vi_tri].w * .98, 'tit').map(bocMask);
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
      nt.style.opacity = e1.toFixed(3); nt.style.letterSpacing = (.6 - .34 * e1).toFixed(3) + 'em';
      dong.forEach((x, i) => { const e = P(t, d.tu + .05 + i * .08, .4, E.outC); x.style.transform = `translateY(${((1 - e) * 105).toFixed(1)}%)`; });
      if (phu) { const e = P(t, d.tu + .3, .35); phu.style.opacity = e.toFixed(3); phu.style.transform = `translateY(${((1 - e) * 18).toFixed(1)}px)`; }
      b.style.opacity = (1 - v.r).toFixed(3); b.style.transform = `translateX(${(-40 * v.r).toFixed(1)}px)`;
    },
  };
};

// 2b. HÀNH TRÌNH — lời nói di chuyển A → B: cùng bản đồ vệ tinh kiểu Google Maps (số giờ / km theo lời, không có thì ước tính "≈")
LAM.hanh_trinh = d => banDoAB(d, { nhan: d.nhan || '', ten: d.diem_den.ten, phu: d.phu, co: d.co, the_nhan: T.tuyen });

// 3. ĐỊA DANH — góc dưới: tròn ngọc có icon, vạch ngọc dọc, tên in hoa, dòng nghiêng
LAM.dia_danh = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const gr = mk('div', 'man_toi', el);
  const phai = d.vi_tri === 'phai';
  css(gr, { [phai ? 'right' : 'left']: 0, top: '560px', width: '1100px', height: '420px',
    background: `radial-gradient(ellipse 60% 55% at ${phai ? '80%' : '20%'} 60%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 100%)` });
  const k = mk('div', 'abs', el);
  const tron = mk('div', 'ld_tron', k, icon(d.icon || 'ghim'));
  const vach = mk('div', 'ld_vach', k);
  const ten = mk('div', 'abs tit', k, esc(d.ten)); css(ten, { whiteSpace: 'nowrap' });
  const phu = d.phu ? mk('div', 'abs nghieng ngoc', k, esc(d.phu)) : null;
  if (phu) css(phu, { fontSize: '32px', whiteSpace: 'nowrap' });
  return {
    el, init() {
      const co = vua(ten, 84, 820);
      const wt = rong(ten), wp = phu ? rong(phu) : 0, wmax = Math.max(wt, wp);
      const by = 840;
      css(k, { left: '0px', top: '0px' });
      const hk = co * .96 + (phu ? 46 : 0);
      css(tron, { left: (phai ? W - 96 - 84 : 96) + 'px', top: (by - hk / 2 - 42) + 'px' });
      const tx = phai ? W - 96 - 84 - 30 - wmax : 96 + 84 + 30;
      css(vach, { left: (phai ? W - 96 - 84 - 16 : 96 + 84 + 12) + 'px', top: (by - hk) + 'px', height: hk + 'px' });
      css(ten, { left: tx + (phai ? 0 : 6) + 'px', top: (by - hk) + 'px', textAlign: phai ? 'right' : 'left', width: wmax + 'px' });
      if (phu) css(phu, { left: tx + (phai ? 0 : 6) + 'px', top: (by - 44) + 'px', textAlign: phai ? 'right' : 'left', width: wmax + 'px' });
      HOP.push({ el: ten, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      gr.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      const e0 = P(t, d.tu, .5, E.outB);
      tron.style.transform = `scale(${e0.toFixed(3)}) rotate(${((1 - e0) * -90).toFixed(1)}deg)`;
      const ev = P(t, d.tu + .05, .35, E.outE); vach.style.transform = `scaleY(${ev.toFixed(3)})`; vach.style.transformOrigin = '50% 100%';
      const e1 = P(t, d.tu + .08, .38, E.outC);
      ten.style.clipPath = phai ? `inset(-30% -5% -30% ${((1 - e1) * 100).toFixed(1)}%)` : `inset(-30% ${((1 - e1) * 100).toFixed(1)}% -30% -5%)`;
      ten.style.transform = `translateX(${((1 - e1) * (phai ? 30 : -30)).toFixed(1)}px)`;
      if (phu) { const e2 = P(t, d.tu + .22, .4, E.outC); phu.style.opacity = e2.toFixed(3); phu.style.transform = `translateY(${((1 - e2) * 12).toFixed(1)}px)`; }
      k.style.opacity = (1 - v.r).toFixed(3); k.style.transform = `translateX(${(v.r * (phai ? 40 : -40)).toFixed(1)}px)`;
    },
  };
};

// 4. TỪ KHOÁ — từng chữ bật đúng giây đọc (tit in hoa / nghiêng ngọc)
LAM.tu_khoa = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .5);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const cot = (d.muc || []).length >= 3;   // ≥ 3 từ: xếp CỘT (1 hàng dài đè người / mặt — soát 14/11/2026)
  const hang = mk('div', '', b); css(hang, cot ? { display: 'flex', flexDirection: 'column', alignItems: d.vi_tri === 'giua' ? 'center' : 'flex-start', gap: '0px', whiteSpace: 'nowrap', lineHeight: '1.04' }
    : { display: 'flex', alignItems: 'baseline', gap: '28px', whiteSpace: 'nowrap', flexWrap: 'nowrap' });
  const ms = (d.muc || []).map(m => {
    const k = m.kieu || 'tit';
    const e = mk('span', k === 'tay' ? 'nghieng dam ngoc' : 'tit', hang, esc(m.chu));
    e.style.display = 'inline-block';
    return { e, m, k };
  });
  return {
    el, init() {
      const base = d.co || 130;
      ms.forEach(x => x.e.style.fontSize = (base * (x.k === 'tay' ? .6 : 1)) + 'px');
      const mw = (VUNG[d.vi_tri] || VUNG.giua).w;
      if (cot) ms.forEach(x => { const w = rong(x.e); if (w > mw) x.e.style.fontSize = (parseFloat(x.e.style.fontSize) * mw / w).toFixed(1) + 'px'; });
      else { const w = rong(hang); if (w > mw) ms.forEach(x => x.e.style.fontSize = (parseFloat(x.e.style.fontSize) * mw / w).toFixed(1) + 'px'); }
      HOP.push({ el: hang, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      for (const x of ms) {
        const e = P(t, x.m.luc, .45, E.outB), a = P(t, x.m.luc, .25);
        x.e.style.opacity = a.toFixed(3);
        x.e.style.transform = `translateY(${((1 - P(t, x.m.luc, .45)) * 36).toFixed(1)}px) scale(${(.78 + .22 * e).toFixed(4)})`;
        if (x.k === 'tay') x.e.style.clipPath = `inset(-30% ${((1 - P(t, x.m.luc, .55, E.ioS)) * 100).toFixed(1)}% -30% -5%)`;
      }
      b.style.opacity = (1 - v.r).toFixed(3);
    },
  };
};

// 5. TIÊU ĐỀ ĐOẠN — nhãn ngọc + chữ khoá IN HOA trắng (2 dòng cân, trượt lên trong mặt nạ) + dòng nghiêng ngọc
LAM.tieu_de = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .55);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const dan = d.dan ? hangNhan(b, d.dan, 34, d.vi_tri === 'giua') : null;
  if (dan) css(dan.r, { marginBottom: '22px' });
  const khoa = mk('div', '', b); css(khoa, { lineHeight: '.94' });
  const tay = d.viet_tay ? mk('div', 'nghieng dam ngoc', b, esc(d.viet_tay)) : null;
  if (tay) css(tay, { marginTop: '18px', whiteSpace: 'nowrap' });
  let dong = [];
  return {
    el, init() {
      dong = dong2(khoa, d.khoa, d.co || 160, VUNG[d.vi_tri].w * .97, 'tit').map(bocMask);
      if (tay) vua(tay, 58, VUNG[d.vi_tri].w * .9);
      HOP.push({ el: khoa, d }); if (tay) HOP.push({ el: tay, d });
    },
    ve(t) {
      if (d.dap) {                              // MONTAGE: tít ĐỈNH đập cùng cú vỡ kính 1,5 → 1 trong 0,2 s, đẩy chậm tới lúc giọng vào
        const v = vaoRa(t, d, .2); show(el, v.on); if (!v.on) return;
        const e = P(t, d.tu, .2, E.outC), k = 1 - e, giu = P(t, d.tu + .2, Math.max(.3, d.den - d.tu - .2), E.lin);
        sc.style.opacity = (P(t, d.tu, .1) * (1 - v.r)).toFixed(3);
        if (dan) { const a = P(t, d.tu + .08, .22, E.outE); dan.tx.style.opacity = a.toFixed(3); dan.tx.style.letterSpacing = (.6 - .34 * a).toFixed(3) + 'em';
          dan.g1.style.transform = `scaleX(${a.toFixed(3)})`; dan.g1.style.transformOrigin = '0 50%'; if (dan.g2) dan.g2.style.transform = `scaleX(${a.toFixed(3)})`; }
        dong.forEach(x => { x.style.transform = 'none'; });
        khoa.style.opacity = P(t, d.tu - .01, .04).toFixed(3);
        khoa.style.letterSpacing = (.01 + .08 * k).toFixed(4) + 'em';
        if (tay) { const a = P(t, d.tu + .2, .32, E.outC); tay.style.clipPath = `inset(-30% ${((1 - a) * 100).toFixed(1)}% -30% -5%)`; }
        b.style.opacity = (1 - v.r).toFixed(3);
        b.style.transform = `translate(${(Math.sin(t * 127) * 10 * k).toFixed(1)}px, ${(Math.cos(t * 89) * 7 * k).toFixed(1)}px) scale(${(1 + .5 * k + .045 * giu + .04 * v.r).toFixed(4)})`;
        return;
      }
      const v = vaoRa(t, d, .45); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      if (dan) { const e = P(t, d.tu, .35, E.outE); dan.tx.style.opacity = e.toFixed(3); dan.tx.style.letterSpacing = (.6 - .34 * e).toFixed(3) + 'em';
        dan.g1.style.transform = `scaleX(${e.toFixed(3)})`; dan.g1.style.transformOrigin = '0 50%'; if (dan.g2) dan.g2.style.transform = `scaleX(${e.toFixed(3)})`; }
      dong.forEach((x, i) => { const e = P(t, d.tu + .03 + i * .08, .4, E.outC); x.style.transform = `translateY(${((1 - e) * 105).toFixed(1)}%)`; });
      if (tay) { const e = P(t, d.tu + .3, .45, E.outC); tay.style.clipPath = `inset(-30% ${((1 - e) * 100).toFixed(1)}% -30% -5%)`; }
      b.style.opacity = (1 - v.r).toFixed(3); b.style.transform = `scale(${(1 + .03 * v.r).toFixed(4)})`;
    },
  };
};

// 6. CHIP — viên trắng có icon ngọc, bật lần lượt (mặc định hàng TRÊN, trời thường trống)
LAM.chip = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const ms = (d.muc || []).map(m => {
    const c = mk('div', 'chip', el); mk('div', 'ic', c, icon(m.icon || 'sao')); mk('span', '', c, esc(m.chu));
    return { c, m };
  });
  return {
    el, init() {
      const y = d.y ?? 96, gap = 18;
      const ws = ms.map(x => x.c.getBoundingClientRect().width);
      const tong = ws.reduce((a, b) => a + b, 0) + gap * (ws.length - 1);
      let x = d.vi_tri === 'phai' ? W - 96 - tong : (d.vi_tri === 'giua' ? (W - tong) / 2 : 96);
      if (tong > W - 192) ms.forEach((m, i) => css(m.c, { left: (d.vi_tri === 'phai' ? W - 96 - ws[i] : 96) + 'px', top: (y + i * 88) + 'px' }));
      else ms.forEach((m, i) => { css(m.c, { left: x + 'px', top: y + 'px' }); x += ws[i] + gap; });
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

// 7. SỐ LỚN — số ngọc in hoa đếm lên đúng giây đọc số
const fmtSo = x => { const s = String(Math.round(x)); return s.replace(/\B(?=(\d{3})+(?!\d))/g, ['vi', 'de', 'id', 'es', 'it', 'pt'].includes(NN) ? '.' : ','); };
LAM.so_lon = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .55);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const hang = mk('div', '', b); css(hang, { display: 'flex', alignItems: 'baseline', gap: '16px', whiteSpace: 'nowrap' });
  const tt = d.tien_to ? mk('span', 'tit', hang, esc(d.tien_to)) : null;
  const so = mk('span', 'tit', hang); css(so, { fontSize: (d.co || 260) + 'px', color: 'var(--nhan)', lineHeight: '.9' });
  const ht = d.hau_to ? mk('span', 'tit', hang, esc(d.hau_to)) : null;
  [tt, ht].forEach(x => x && css(x, { fontSize: ((d.co || 260) * .4) + 'px' }));
  const nhan = d.nhan ? mk('div', 'nhan_nho', b, esc(d.nhan)) : null;
  if (nhan) css(nhan, { fontSize: '32px', color: '#fff', marginTop: '10px' });
  const dich = parseFloat(String(d.so).replace(/[^\d.,]/g, '').replace(/\./g, '').replace(',', '.')) || 0;
  const dem = +(d.dem_tu ?? d.tu + .3);
  return {
    el, init() { so.textContent = fmtSo(dich); HOP.push({ el: hang, d }); },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      so.textContent = fmtSo(dich * P(t, dem, 1.3, E.outE));
      const e = P(t, d.tu, .55, E.outB);
      hang.style.transform = `scale(${(.7 + .3 * e).toFixed(4)})`; hang.style.opacity = P(t, d.tu, .3).toFixed(3);
      if (nhan) { const a = P(t, d.tu + .5, .6); nhan.style.opacity = a.toFixed(3); nhan.style.letterSpacing = (.6 - .34 * a).toFixed(3) + 'em'; }
      b.style.opacity = (1 - v.r).toFixed(3);
    },
  };
};

// 8. LIỆT KÊ — KHÔNG hộp (khách chê bảng tối + thẻ ảnh "giống màn dọc"): nhãn ngọc + mục IN HOA, số thứ tự ngọc, hiện đúng giây đọc
LAM.liet_ke = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const phai = d.vi_tri === 'phai';
  const sc = scrim(el, phai ? 'phai' : 'trai', .62);
  const bg = mk('div', 'lk', el);
  const dan = d.dan ? hangNhan(bg, d.dan, 34) : null;
  if (dan) dan.r.classList.add('dan_lk');
  const ms = (d.muc || []).map((m, i) => {
    const r = mk('div', 'muc', bg); const so = mk('span', 'so_m', r, String(i + 1).padStart(2, '0')); const tx = mk('span', 'chu_m', r, esc(m.chu));
    return { r, so, tx, m };
  });
  return {
    el, init() {
      const wmax = Math.max(...ms.map(x => rong(x.tx)));
      if (wmax > 720) ms.forEach(x => vua(x.tx, 70, 720));
      const w = Math.min(820, Math.max(...ms.map(x => rong(x.tx))) + 86);
      const h = bg.getBoundingClientRect().height;
      css(bg, { left: (phai ? W - 130 - w : 130) + 'px', top: Math.max(80, 470 - h / 2) + 'px', width: w + 'px' });
      HOP.push({ el: bg, d });
    },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      sc.style.opacity = (P(t, d.tu, .5) * (1 - v.r)).toFixed(3);
      if (dan) { const e = P(t, d.tu, .4, E.outE); dan.tx.style.opacity = e.toFixed(3); dan.tx.style.letterSpacing = (.6 - .34 * e).toFixed(3) + 'em'; dan.g1.style.transform = `scaleX(${e.toFixed(3)})`; dan.g1.style.transformOrigin = '0 50%'; }
      for (const x of ms) {
        const a = P(t, x.m.luc, .4, E.outC), s = P(t, x.m.luc, .45, E.outB);
        x.r.style.opacity = a.toFixed(3); x.r.style.transform = `translateX(${((1 - a) * -40).toFixed(1)}px)`;
        x.so.style.transform = `scale(${(.5 + .5 * s).toFixed(3)})`;
      }
      bg.style.opacity = (1 - v.r).toFixed(3); bg.style.transform = `translateX(${(v.r * -30).toFixed(1)}px)`;
    },
  };
};

// 9. TRÍCH — ngoặc kép ngọc lớn + câu nghiêng
LAM.trich = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .6);
  const b = khoi(d.vi_tri, d.y ?? 470); el.appendChild(b);
  const ng = mk('div', 'tit', b, '“'); css(ng, { fontSize: '240px', lineHeight: '.6', height: '110px', color: 'var(--nhan)' });
  const noi = mk('div', 'nghieng'); b.appendChild(noi);
  css(noi, { fontSize: (d.co || 64) + 'px', lineHeight: '1.22', maxWidth: (VUNG[d.vi_tri].w * .92) + 'px' });
  const ws = words(d.noi).map(w => mk('span', 'ch', noi, esc(w + ' ')));
  const tg = d.tac_gia ? mk('div', 'nhan_nho', b, esc('— ' + d.tac_gia)) : null; if (tg) css(tg, { fontSize: '32px', marginTop: '18px' });
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

// 10. BẢN ĐỒ VIỆT NAM — ghim đỏ rơi đúng giây đọc tên (tổng kết nhiều điểm)
LAM.ban_do = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const sc = scrim(el, d.vi_tri, .62);
  const mw = 520, mh = 880, x0 = d.vi_tri === 'phai' ? W - 140 - mw : (d.vi_tri === 'giua' ? (W - mw) / 2 : 140), y0 = 70;
  const box = mk('div', 'abs', el); css(box, { left: x0 + 'px', top: y0 + 'px', width: mw + 'px', height: mh + 'px' });
  box.innerHTML = `<svg width="${mw}" height="${mh}" viewBox="0 0 ${mw} ${mh}">${svgBanDo(mw, mh)}</svg>`;
  const bb = VN ? VN.bbox : [102, 8, 110, 23.5];
  const ps = (d.diem || []).map(p => {
    const [x, y] = chieu(p.toa_do[0], p.toa_do[1], bb, mw, mh);
    const g = mk('div', 'abs', box); css(g, { left: x + 'px', top: y + 'px' });
    const vong = mk('div', 'abs', g); css(vong, { left: '-30px', top: '-30px', width: '60px', height: '60px', borderRadius: '50%', border: '3px solid var(--nhan)' });
    const ghim = mk('div', 'abs', g, GHIM_GG); css(ghim, { left: '-22px', top: '-58px', width: '44px', height: '58px' });
    ghim.querySelector('svg').setAttribute('width', '44'); ghim.querySelector('svg').setAttribute('height', '58');
    const ten = mk('div', 'abs bd_tag', g, esc(p.ten)); const trai = p.nhan === 'trai';
    css(ten, { top: '-50px', [trai ? 'right' : 'left']: '30px', fontSize: '28px', padding: '6px 16px 7px' });
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

// 11. BÌNH LUẬN ẢO — thẻ bình luận kiểu YouTube (Anh / Hàn, khen + chê nhẹ) trượt vào cột phải, mỗi thẻ đúng `luc`
const CO = {
  KR: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="5" fill="#CD2E3A"/><path d="M10 10a5 5 0 0 0 10 0a2.5 2.5 0 0 0-5 0a2.5 2.5 0 0 1-5 0z" fill="#0047A0"/><g stroke="#111" stroke-width="1.2"><path d="M4.2 5.6l3-2.2M4.9 6.6l3-2.2M5.6 7.6l3-2.2M21.4 12.4l3 2.2M22.1 11.4l3 2.2M22.8 10.4l3 2.2M21.4 7.6l3-2.2M22.1 8.6l3-2.2M4.2 14.4l3 2.2M4.9 13.4l3 2.2"/></g></svg>',
  US: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#fff"/><g fill="#B22234"><rect y="0" width="30" height="1.54"/><rect y="3.08" width="30" height="1.54"/><rect y="6.16" width="30" height="1.54"/><rect y="9.24" width="30" height="1.54"/><rect y="12.32" width="30" height="1.54"/><rect y="15.4" width="30" height="1.54"/><rect y="18.46" width="30" height="1.54"/></g><rect width="13" height="10.8" fill="#3C3B6E"/><g fill="#fff"><circle cx="2.5" cy="2.2" r=".6"/><circle cx="5.5" cy="2.2" r=".6"/><circle cx="8.5" cy="2.2" r=".6"/><circle cx="11" cy="2.2" r=".6"/><circle cx="4" cy="4.8" r=".6"/><circle cx="7" cy="4.8" r=".6"/><circle cx="10" cy="4.8" r=".6"/><circle cx="2.5" cy="7.4" r=".6"/><circle cx="5.5" cy="7.4" r=".6"/><circle cx="8.5" cy="7.4" r=".6"/><circle cx="11" cy="7.4" r=".6"/></g></svg>',
  GB: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#012169"/><path d="M0 0l30 20M30 0L0 20" stroke="#fff" stroke-width="4"/><path d="M0 0l30 20M30 0L0 20" stroke="#C8102E" stroke-width="1.6"/><path d="M15 0v20M0 10h30" stroke="#fff" stroke-width="6"/><path d="M15 0v20M0 10h30" stroke="#C8102E" stroke-width="3.4"/></svg>',
  AU: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#012169"/><g transform="scale(.5)"><path d="M0 0l30 20M30 0L0 20" stroke="#fff" stroke-width="4"/><path d="M15 0v20M0 10h30" stroke="#fff" stroke-width="6"/><path d="M15 0v20M0 10h30" stroke="#C8102E" stroke-width="3.4"/></g><g fill="#fff"><circle cx="7.5" cy="15.5" r="1.6"/><circle cx="22" cy="5" r="1"/><circle cx="25.5" cy="9" r="1"/><circle cx="19" cy="10" r="1"/><circle cx="22" cy="16" r="1.1"/></g></svg>',
  CA: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#fff"/><rect width="7.5" height="20" fill="#D52B1E"/><rect x="22.5" width="7.5" height="20" fill="#D52B1E"/><path d="M15 4l1.2 2.6 2.2-.8-.8 3.6 2-1-.6 2.4 1.6.6-3.6 2.4.4 1.4H15.6V17h-1.2v-1.8h-1.8l.4-1.4-3.6-2.4 1.6-.6-.6-2.4 2 1-.8-3.6 2.2.8z" fill="#D52B1E"/></svg>',
  VN: '<svg viewBox="0 0 30 20"><rect width="30" height="20" fill="#DA251D"/><path d="M15 4.2l1.5 4.5h4.7l-3.8 2.8 1.4 4.5L15 13.2 11.2 16l1.4-4.5-3.8-2.8h4.7z" fill="#FFCD00"/></svg>',
};
const MAU_AV = ['#E8710A', '#1A73E8', '#9334E6', '#188038', '#D93025', '#007B83', '#C5221F', '#5E35B1', '#F29900', '#00897B'];
const bamChu = s => { let h = 7; for (const c of String(s)) h = (h * 31 + c.codePointAt(0)) >>> 0; return h; };
LAM.binh_luan = d => {
  const el = mk('div', 'dh', LOP); css(el, FULL);
  const cot = mk('div', 'bl_cot', el);
  if (d.vi_tri === 'trai') css(cot, { left: '96px' });
  const ms = (d.muc || []).map(m => {
    const c = mk('div', 'bl', cot);
    const ten = String(m.ten || 'traveler');
    const av = mk('div', 'bl_av', c, esc(chars(ten.replace(/^@/, ''))[0] || 'T').toUpperCase()); av.style.background = MAU_AV[bamChu(ten) % MAU_AV.length];
    const than = mk('div', 'bl_than', c);
    mk('div', 'bl_dau', than, `<b>${esc(ten)}</b>${m.co && CO[m.co] ? `<span class="co">${CO[m.co]}</span>` : ''}<span class="tg">${esc(m.tg || '')}</span>`);
    mk('div', 'bl_chu', than, esc(m.chu));
    const chan = mk('div', 'bl_chan', than, `${icon('thich')}<span>${esc(m.thich || '')}</span>${icon('khong_thich')}<span style="margin-left:14px">${esc(m.tra_loi || '')}</span>`);
    const tim = mk('span', 'tim_tg', chan, S(IC.tim)); tim.querySelector('svg').setAttribute('fill', '#FF2D55');
    return { c, m, tim };
  });
  return {
    el, init() {
      let y = 0;
      for (const x of ms) { css(x.c, { top: y + 'px' }); y += x.c.offsetHeight + 16; }
      ms.forEach(x => HOP.push({ el: x.c, d }));
    },
    ve(t) {
      const v = vaoRa(t, d, .4); show(el, v.on); if (!v.on) return;
      ms.forEach((x, i) => {
        const l = +(x.m.luc ?? d.tu + i * 1.25);
        const a = P(t, l, .45, E.outB), o = P(t, l, .2);
        const r = P(t, d.den - .4 + i * .06, .34, E.inC);
        css(x.c, { opacity: (o * (1 - r)).toFixed(3), transform: `translateX(${f1((1 - a) * 90 + r * 120)}px) scale(${(.94 + .06 * a).toFixed(3)})` });
        const k = P(t, l + 1.1, .35, E.outB);
        css(x.tim, { opacity: P(t, l + 1.1, .15).toFixed(3), transform: `scale(${(.3 + .7 * k).toFixed(3)})` });
      });
    },
  };
};

const DH = (KH.do_hoa || []).map(d => { const f = LAM[d.loai]; if (!f) { console.error('loại đồ hoạ lạ: ' + d.loai); return null; } const g = f(d); g.d = d; return g; }).filter(Boolean);

// ---------------- sub: hộp tối bo góc từng dòng, chữ đang đọc xanh ngọc ----------------
const SUB = mk('div', '', stage); SUB.id = 'sub';
css(SUB, { bottom: (H - 1000) + 'px' });
let subCum = -1, subW = [], subBox = [];
function veSub(t) {
  const ds = KH.sub || [];
  const cta = KH.cta;
  let k = -1;
  for (let i = 0; i < ds.length; i++) if (ds[i].tu <= t && t < ds[i].den) { k = i; break; }
  if (cta && t >= cta.tu + .35) k = -1;               // màn kết có chữ riêng
  if (k !== subCum) {
    SUB.innerHTML = ''; subW = []; subBox = []; subCum = k;
    if (k >= 0) for (const dg of ds[k].dong) {
      const hang = mk('div', 'hang', SUB);
      const line = mk('div', 'sd', hang); subBox.push(line);
      dg.forEach((w, j) => { const s = mk('span', 'w', line, esc(w.w)); subW.push({ s, w }); if (j < dg.length - 1) line.appendChild(document.createTextNode(' ')); });
      if (line.offsetWidth > 1720) line.style.fontSize = (44 * 1680 / line.offsetWidth).toFixed(1) + 'px';
    }
  }
  if (k < 0) return;
  const c = ds[k], e = P(t, c.tu, .12);
  SUB.style.opacity = e.toFixed(3); SUB.style.transform = `translateY(${((1 - e) * 8).toFixed(1)}px)`;
  subW.forEach((x, i) => {
    const nx = subW[i + 1]?.w.s ?? x.w.e + .3;
    x.s.classList.toggle('on', t >= x.w.s - .02 && t < Math.max(nx, x.w.e) - .02);
  });
}

// ---------------- màn kết: CẢM ƠN ĐÃ XEM + mời Thích & Đăng ký (khách 14/11/2026) — câu hỏi / lựa chọn ở trên, nút ĐĂNG KÝ có tay bấm,
//                  chuông, Thích + tim bay, Chia sẻ ----------------
const C = KH.cta;
const CT = mk('div', '', stage); CT.id = 'cta'; show(CT, false);
let CTA = null;
if (C) {
  const toi = mk('div', 'cta_toi', CT);
  const ten = (KH.kenh && KH.kenh.ten) || '';
  let kenh = null;
  if (ten) {
    kenh = mk('div', 'cta_kenh', CT);
    const av = mk('div', 'avatar', kenh);
    if (KH.kenh.avatar_url) mk('img', '', av).src = KH.kenh.avatar_url; else av.textContent = chars(ten)[0].toUpperCase();
    const tk = mk('div', 'ten_kenh', kenh); mk('span', 'bong_chu', tk, esc(ten)); mk('span', 'tich', tk, S(IC.tich));
    if (KH.kenh.handle) mk('div', 'handle', kenh, esc(KH.kenh.handle));
  }
  const coCau = !!C.cau_hoi;
  const cau = coCau ? mk('div', 'abs', CT) : null;
  if (cau) css(cau, { left: '160px', width: '1600px', top: '168px', textAlign: 'center' });
  const lc = (C.lua_chon || []).map((x, i) => { const c = mk('div', 'lua', CT); mk('div', 'so', c, String(i + 1)); mk('span', '', c, esc(x)); return c; });
  const Y0 = coCau ? (lc.length ? 380 : 320) : 250;
  const camOn = mk('div', 'abs', CT); css(camOn, { left: '0px', width: W + 'px', top: Y0 + 'px', textAlign: 'center' });
  const camMask = mk('div', 'mask', camOn); const camTx = mk('div', 'tit', camMask, esc(C.cam_on || T.cam_on || '')); css(camTx, { whiteSpace: 'nowrap', display: 'inline-block' });
  const vach = mk('div', 'vach_n', CT);
  const moi = mk('div', 'abs nghieng', CT, esc(C.loi_moi || T.loi_moi || '')); css(moi, { left: '0px', width: W + 'px', textAlign: 'center', whiteSpace: 'nowrap' });
  const nut = mk('div', 'nut_dk', CT);
  const nutIc = mk('span', '', nut, S(IC.chuong)); nutIc.style.display = 'none';
  const nutTx = mk('span', '', nut, esc(C.nut));
  const quet = mk('div', 'quet', nut);
  const song = mk('div', 'song', CT);
  const thich = mk('div', 'nut_tron', CT, S(IC.thich));
  const chuong = mk('div', 'nut_tron', CT, S(IC.chuong));
  const chiase = mk('div', 'nut_tron', CT, S(IC.chia_se));
  const nThich = mk('div', 'nhan_nut', CT, esc(C.thich)), nCs = mk('div', 'nhan_nut', CT, esc(C.chia_se));
  const nCh = mk('div', 'nhan_nut', CT, esc(C.chuong_nhan || ''));
  const hand = mk('div', 'tay_bam', CT, TAY);
  const tims = [0, 1, 2, 3, 4, 5].map(() => { const h = mk('div', 'tim_bay', CT, S(IC.tim)); h.querySelector('svg').setAttribute('fill', '#FF3355'); return h; });
  let dongCau = [], YN = 760, XN = 552, XT = 0, XC = 0, XS = 0;
  CTA = {
    init() {
      if (cau) dongCau = dong2(cau, C.cau_hoi, 58, 1560, 'nghieng dam').map(bocMask);
      const hc = cau ? cau.getBoundingClientRect().height : 0;
      // lựa chọn: 1 hàng giữa
      const ws = lc.map(c => c.getBoundingClientRect().width), tong = ws.reduce((a, b) => a + b, 0) + 18 * Math.max(0, ws.length - 1);
      let x = (W - tong) / 2;
      lc.forEach((c, i) => { css(c, { left: f1(x) + 'px', top: f1(168 + hc + 30) + 'px' }); x += ws[i] + 18; });
      const co = vua(camTx, 150, 1600);
      const yC = Y0 + co * .94;
      css(vach, { left: (W / 2 - 150) + 'px', width: '300px', top: f1(yC + 34) + 'px' });   // +34: chừa dấu nặng (CẢM ƠN BẠN)
      vua(moi, 42, 1600); css(moi, { top: f1(yC + 66) + 'px' });
      YN = Math.round(Math.min(860, yC + 66 + 70 + 34));
      const wN = 440, gap = 30; XN = Math.round((W - (wN + 3 * 104 + 3 * gap)) / 2);
      XT = XN + wN + gap; XC = XT + 104 + gap; XS = XC + 104 + gap;
      css(nut, { left: XN + 'px', top: YN + 'px', width: wN + 'px' });
      css(song, { left: XN + 'px', top: YN + 'px', width: wN + 'px', height: '104px' });
      css(thich, { left: XT + 'px', top: YN + 'px' }); css(chuong, { left: XC + 'px', top: YN + 'px' }); css(chiase, { left: XS + 'px', top: YN + 'px' });
      css(nThich, { left: (XT - 28) + 'px', top: (YN + 112) + 'px' }); css(nCs, { left: (XS - 28) + 'px', top: (YN + 112) + 'px' }); css(nCh, { left: (XC - 28) + 'px', top: (YN + 112) + 'px' });
    },
    ve(t) {
      const on = t >= C.tu - .02; show(CT, on); if (!on) return;
      toi.style.opacity = P(t, C.tu, .6, E.ioS).toFixed(3);
      if (kenh) { const a = P(t, C.tu + .1, .5, E.outB); kenh.style.opacity = P(t, C.tu + .1, .25).toFixed(3); kenh.style.transform = `translateY(${f1((1 - a) * -24)}px)`; }
      dongCau.forEach((x, i) => { const f = P(t, C.tu + .15 + i * .12, .6, E.outE); x.style.transform = `translateY(${((1 - f) * 105).toFixed(1)}%)`; });
      lc.forEach((c, i) => { const f = P(t, C.tu + .6 + i * .15, .45, E.outB); c.style.opacity = P(t, C.tu + .6 + i * .15, .2).toFixed(3); c.style.transform = `scale(${(.6 + .4 * f).toFixed(3)})`; });
      const tc = C.luc_cam_on ?? C.tu + 1.2;
      const ec = P(t, tc, .32, E.outC);
      camTx.style.opacity = P(t, tc - .02, .08).toFixed(3); camTx.style.transform = `scale(${(1.25 - .25 * ec).toFixed(4)})`;
      vach.style.transform = `scaleX(${P(t, tc + .15, .4, E.outE).toFixed(3)})`;
      { const a = P(t, tc + .3, .45); moi.style.opacity = a.toFixed(3); moi.style.transform = `translateY(${f1((1 - a) * 18)}px)`; }
      const n = P(t, tc + .6, .55, E.outB);
      [nut, thich, chuong, chiase, nThich, nCs, nCh].forEach(x => { x.style.opacity = P(t, tc + .6, .3).toFixed(3); x.style.transform = `translateY(${((1 - n) * 40).toFixed(1)}px)`; });
      // nút đăng ký: bóng quét + sóng lan trước khi bấm; bấm → xám "ĐÃ ĐĂNG KÝ" + chuông lắc
      const da = t >= C.luc_bam;
      nut.classList.toggle('da', da);
      nutTx.textContent = da ? C.nut_da : C.nut;
      nutIc.style.display = da ? 'inline-flex' : 'none';
      const chg = da && t >= C.luc_chuong;
      chuong.style.background = chg ? 'var(--nhan)' : 'rgba(255,255,255,.16)'; chuong.style.color = chg ? '#07302B' : '#fff';
      if (chg) { const r = clamp((t - C.luc_chuong) / .8); chuong.style.transform += ` rotate(${(Math.sin(r * Math.PI * 5) * 22 * (1 - r)).toFixed(1)}deg)`; }
      const q = ((t - tc - .9) % 1.4 + 1.4) % 1.4 / 1.4;
      quet.style.left = (-160 + q * 680).toFixed(1) + 'px'; show(quet, !da && t > tc + .9);
      const sq = ((t - tc - .9) % 1.1 + 1.1) % 1.1 / 1.1;
      show(song, !da && t > tc + .9); song.style.opacity = ((1 - sq) * .8).toFixed(3); song.style.transform = `scale(${(1 + sq * .2).toFixed(3)}, ${(1 + sq * .6).toFixed(3)})`;
      const ep = da ? 1 - .06 * Math.sin(clamp((t - C.luc_bam) / .25) * Math.PI) : 1;
      nut.style.transform += ` scale(${ep.toFixed(3)})`;
      const th = t >= C.luc_thich;
      thich.style.background = th ? '#3EA6FF' : 'rgba(255,255,255,.16)';
      const tp = th ? 1 + .25 * Math.sin(clamp((t - C.luc_thich) / .35) * Math.PI) : 1;
      thich.style.transform += ` scale(${tp.toFixed(3)})`;
      tims.forEach((h, i) => {
        const r = clamp((t - C.luc_thich - i * .07) / 1.1);
        show(h, th && r > 0 && r < 1);
        const ang = -90 + (i - 2.5) * 22;
        h.style.left = (XT + 32 + Math.cos(ang * Math.PI / 180) * 120 * r).toFixed(1) + 'px';
        h.style.top = (YN + 30 + Math.sin(ang * Math.PI / 180) * 160 * r).toFixed(1) + 'px';
        h.style.opacity = (1 - r).toFixed(3); h.style.transform = `scale(${(.6 + .6 * r).toFixed(3)})`;
      });
      // tay: vào → bấm Đăng ký → sang bấm Thích → ra
      const p1 = [XN + 300, YN + 52], p2 = [XT + 52, YN + 52], p0 = [XN + 520, 1200], p3 = [XT + 260, 1220];
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
  const fams = ['900 40px BC', '900 40px BCI', '800 40px BCE', '600 40px MSI', '700 40px MSI', '500 40px BVP', '600 40px BVP', '700 40px BVP',
    '800 40px BVP', '900 40px BVP', '700 40px MS'];
  await Promise.all(fams.map(f => document.fonts.load(f, 'ÀẢÃẠăâđêôơư ỂẤỮ Việt Nam 0123')));
  await document.fonts.ready;
  hatNhieu();
  // đo chữ cần phần tử ĐANG HIỆN (display:none → bề rộng 0): bật tạm lúc init rồi ẩn lại
  for (const g of DH) { show(g.el, true); g.init && g.init(); show(g.el, false); }
  if (CTA) { show(CT, true); CTA.init(); show(CT, false); }
  // mặt nạ chữ: đệm theo CỠ CHỮ THẬT bên trong (em của .mask là cỡ chữ cha ~16 px → đệm 5 px cắt mất dấu nặng / dấu hỏi:
  // "VỊNH HẠ LONG" ra "VINH HA LONG", soát 14/11/2026). Lề âm bằng đệm → bố cục không đổi.
  for (const m of document.querySelectorAll('.mask')) {
    let fs = 0; for (const c of m.querySelectorAll('*')) fs = Math.max(fs, parseFloat(getComputedStyle(c).fontSize) || 0);
    if (!fs) continue;
    const tr = f1(fs * .26), du = f1(fs * .36), ng = f1(fs * .05);
    css(m, { padding: `${tr}px ${ng}px ${du}px`, margin: `-${tr}px -${ng}px -${du}px` });
  }
})();
window.__seek = async (t) => {
  DS.length = 0; KHUNG_SO++;
  veMau(t);
  ghepCanh(t);
  for (const g of DH) g.ve(t);
  veSub(t);
  CTA && CTA.ve(t);
  if (DS.length) await Promise.all(DS.map(i => i.decode().catch(() => { })));
  if (CHO.length) await Promise.all(CHO.splice(0));          // ô ảnh vệ tinh của khung này
  for (const f of VE_SAU.splice(0)) f();
  donAnhO();
  return true;
};
window.__bao_cao = () => {
  const o = [];
  const vis = el => { let e = el; while (e && e !== stage) { const s = getComputedStyle(e); if (s.display === 'none' || +s.opacity < .5) return false; e = e.parentElement; } return true; };
  for (const h of HOP) if (vis(h.el)) { const r = h.el.getBoundingClientRect(); o.push({ loai: h.d.loai, id: h.d.id, x: r.left, y: r.top, w: r.width, h: r.height }); }
  if (subBox.length && +SUB.style.opacity > .5) for (const l of subBox) { const b = l.getBoundingClientRect(); o.push({ loai: 'sub', id: 'sub', x: b.left, y: b.top, w: b.width, h: b.height }); }
  return o;
};
