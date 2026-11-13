/* dulich.js — bộ chạy khung cho skill TuấnJp_Dulich_ManDoc.
 * Nhận window.KH (kế hoạch đã giải giờ bởi scripts/ke_hoach.py), vẽ đúng khung ở giây t qua window.__seek(t).
 * Mọi chuyển động là HÀM THUẦN của t (tua tới đâu cũng ra đúng một hình) — không requestAnimationFrame, không CSS animation.
 */
(() => {
'use strict';
const KH = window.KH;
const FPS = KH.fps || 30, W = 1080, H = 1920;
const stage = document.getElementById('stage');

/* ================= tiện ích ================= */
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const E = {
  lin: u => u,
  inQ: u => u * u,
  inC: u => u * u * u,
  outQ: u => 1 - (1 - u) * (1 - u),
  outC: u => 1 - Math.pow(1 - u, 3),
  outE: u => u >= 1 ? 1 : 1 - Math.pow(2, -10 * u),
  inOutC: u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2,
  inOutS: u => -(Math.cos(Math.PI * u) - 1) / 2,
  outB: u => { const c1 = 1.6, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); },
  drop: u => { if (u < .6) { const v = u / .6; return v * v; } const v = (u - .6) / .4; return 1 - .16 * Math.sin(Math.PI * v) * (1 - v * .5); },
};
const P = (t, a, d, e = E.outC) => e(clamp((t - a) / Math.max(1e-6, d)));
const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || stage).appendChild(e); return e; };
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const setSrc = (img, u, ds) => { if (u && img.dataset.u !== u) { img.dataset.u = u; img.src = u; if (ds) ds.push(img); return true; } return false; };
const pad5 = i => String(i).padStart(5, '0');
const hash01 = n => { let x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const chars = s => Array.from(String(s ?? '').normalize('NFC'));
const words = s => String(s ?? '').trim().split(/\s+/).filter(Boolean);
const NN = KH.ngon_ngu || 'vi';
const KHONG_CACH = ['ja', 'zh', 'th'].includes(NN);
// chữ không phải Latin: chồng font đúng tiếng (Windows có sẵn) — Han của tiếng Trung không mượn nét Nhật và ngược lại
const FONT_NN = {
  ja: ["'Yu Mincho', 'YuMincho', 'MS Mincho', 'Yu Gothic UI', 'Meiryo'", "'Yu Gothic UI', 'Yu Gothic', 'Meiryo'"],
  zh: ["'SimSun', 'Microsoft YaHei', 'Microsoft JhengHei'", "'Microsoft YaHei', 'Microsoft JhengHei'"],
  ko: ["'Batang', 'Malgun Gothic'", "'Malgun Gothic'"],
  th: ["'Leelawadee UI', 'Tahoma'", "'Leelawadee UI', 'Tahoma'"],
  ru: ["'Georgia', 'Times New Roman'", "'Segoe UI', 'Arial'"],
};
if (FONT_NN[NN]) {
  document.documentElement.style.setProperty('--cjk-serif', FONT_NN[NN][0]);
  document.documentElement.style.setProperty('--cjk-sans', FONT_NN[NN][1]);
}
// Nhật / Trung / Hàn / Thái: máy không có font viết tay cho chữ đó → dòng "viết tay" rơi về Gothic: nhỏ lại, không kéo đè lên tít
const PHI_LATIN = ['ja', 'zh', 'ko', 'th'].includes(NN);
if (PHI_LATIN) document.documentElement.classList.add('phi_latin');
const CO_TAY = PHI_LATIN ? .58 : 1;
function show(el, on) { const v = on ? '' : 'none'; if (el.style.display !== v) el.style.display = v; }
function css(el, o) { for (const k in o) { const v = o[k]; if (el.style[k] !== v) el.style[k] = v; } }

/* ================= icon (SVG tự vẽ, nét currentColor) ================= */
const S = (p, extra = '') => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ${extra}>${p}</svg>`;
const IC = {
  ghim: S('<path d="M12 22s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="10" r="2.6"/>'),
  dong_ho: S('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>'),
  lich_su: S('<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v4h4"/><path d="M12 8v4l3 2"/>'),
  sao: S('<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'),
  may_anh: S('<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.6"/>'),
  bat_pho: S('<path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 20h8"/><path d="M14 3l-4 7M18 4l-5 6"/>'),
  ca_phe: S('<path d="M4 9h13v5a6 6 0 0 1-6 6h-1a6 6 0 0 1-6-6z"/><path d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8 3c0 1.5 1.5 1.5 1.5 3M12 3c0 1.5 1.5 1.5 1.5 3"/>'),
  chua: S('<path d="M12 2l3 3H9z"/><path d="M5 9l7-4 7 4z"/><path d="M3 14l9-5 9 5z"/><path d="M6 14v7h12v-7"/><path d="M10 21v-4h4v4"/>'),
  ho: S('<path d="M2 15c2 0 2-1.5 4-1.5S8 15 10 15s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 19.5c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M8 11V6l4-3 4 3v5"/>'),
  thanh_pho: S('<path d="M3 21h18"/><path d="M5 21V9h5v12"/><path d="M10 21V4h6v17"/><path d="M16 21v-9h3v9"/><path d="M12.5 7.5h1M12.5 11h1M12.5 14.5h1M7 12h1M7 15.5h1"/>'),
  la: S('<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15"/><path d="M5 19l8-8"/>'),
  trang: S('<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/>'),
  mat_troi: S('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
  ve: S('<path d="M3 8a2 2 0 0 0 0 4v4h18v-4a2 2 0 0 1 0-4V4H3z" transform="translate(0 2)"/><path d="M14 6v12" stroke-dasharray="2 2"/>'),
  ban_do: S('<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/>'),
  di_bo: S('<circle cx="13" cy="4" r="2"/><path d="M10 21l2-6 3 3v4M9 12l2-4 3 1 2 4 3 1M11 8l-3 2-1 3"/>'),
  may_bay: S('<path d="M21 15l-8-4V5a1.5 1.5 0 0 0-3 0v6l-8 4v2l8-2v4l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-4l8 2z"/>'),
  tich: S('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 'stroke-width="3"'),
  cong: S('<path d="M12 5v14M5 12h14"/>', 'stroke-width="3"'),
  sach: S('<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/><path d="M8 7h7M8 10h5"/>'),
  vuong_mien: S('<path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z"/><path d="M5 21h14"/>'),
  co: S('<path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/>'),
  di_tich: S('<path d="M3 21h18M4 18h16"/><path d="M6 18V10M10 18V10M14 18V10M18 18V10"/><path d="M3 10h18L12 4z"/>'),
  cay: S('<path d="M12 22v-6"/><path d="M12 16a6 6 0 0 0 6-6 6 6 0 0 0-3-5.2A4 4 0 0 0 9 4.8 6 6 0 0 0 6 10a6 6 0 0 0 6 6z"/>'),
  tim: S('<path d="M12 20.5s-8-4.6-8-10.4A4.6 4.6 0 0 1 12 7.3a4.6 4.6 0 0 1 8 2.8c0 5.8-8 10.4-8 10.4z"/>'),
  tim_dac: `<svg viewBox="0 0 24 24"><path d="M12 20.5s-8-4.6-8-10.4A4.6 4.6 0 0 1 12 7.3a4.6 4.6 0 0 1 8 2.8c0 5.8-8 10.4-8 10.4z" fill="#FE2C55" stroke="#FE2C55" stroke-width="2" stroke-linejoin="round"/></svg>`,
  binh_luan: S('<path d="M20 11.5a8 7.5 0 0 1-11.7 6.6L4 19.5l1.4-3.8A7.5 7 0 0 1 4 11.5a8 7.5 0 0 1 16 0z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01" stroke-width="3"/>'),
  chia_se: S('<path d="M14 5l7 7-7 7v-4c-5 0-8.5 1.5-11 5 1-5.5 4-10 11-11z"/>'),
  luu: S('<path d="M6 3h12v18l-6-4.5L6 21z"/>'),
  luu_dac: `<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.5L6 21z" fill="#F4C66A" stroke="#F4C66A" stroke-width="2" stroke-linejoin="round"/></svg>`,
  chuong: S('<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>'),
  nhac: S('<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>'),
  lap_lanh: S('<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>'),
  cau: S('<path d="M2 17h20"/><path d="M3 17c3-6 15-6 18 0"/><path d="M7 13.2V17M12 12v5M17 13.2V17"/>'),
  den_long: S('<path d="M12 2v3"/><path d="M8 5h8"/><path d="M7 8c0-1.7 2.2-3 5-3s5 1.3 5 3v8c0 1.7-2.2 3-5 3s-5-1.3-5-3z"/><path d="M8 19h8M12 19v3M7 12h10"/>'),
  xe_may: S('<circle cx="5.5" cy="17" r="3"/><circle cx="18.5" cy="17" r="3"/><path d="M8.5 17h6l2-6h-5l-3 6"/><path d="M14 8h3l1.5 3"/>'),
  nguoi: S('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'),
  tau: S('<path d="M3 15l2 5h14l2-5z"/><path d="M12 15V3l6 8h-6"/>'),
  nui: S('<path d="M2 20l7-12 4 6 3-4 6 10z"/><path d="M7.5 10.5l1.5 1.5 1.5-1.5"/>'),
  qua_tang: S('<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M3 13h18M12 9v12"/><path d="M12 9c-2-4-6-4-6-1.5S10 9 12 9c2 0 6-.5 6-1.5S14 5 12 9z"/>'),
  ca: S('<path d="M2 12c3-5 9-6.5 14-3l5-3v12l-5-3c-5 3.5-11 2-14-3z"/><circle cx="7.5" cy="11" r=".6" fill="currentColor"/>'),
  cuon: S('<rect x="3" y="8" width="18" height="8" rx="4"/><path d="M8 8v8M13 8v8"/><path d="M5 19h14"/>'),
  lua: S('<path d="M12 22c4 0 7-2.7 7-6.6 0-3.6-2.6-5.9-4.2-8.4-.5 2-1.6 3.2-2.8 3.6C12.5 7 11 4.3 8.5 2.5 8.8 6 5 8.8 5 13.6 5 18.6 8 22 12 22z"/>'),
  hoa: S('<circle cx="12" cy="9" r="2.2"/><path d="M12 6.8a2.6 2.6 0 1 1 2.6-1.8M14.1 9.7a2.6 2.6 0 1 1 .1 3M12 11.2a2.6 2.6 0 1 1-2.2 1.6M9.8 9.3a2.6 2.6 0 1 1-.2-3"/><path d="M12 13v9M12 18c-2 0-3.5-1.2-4-3M12 17c2 0 3.2-1 3.8-2.6"/>'),
  gio: S('<path d="M3 8h11a3 3 0 1 0-3-3"/><path d="M3 12h16a3 3 0 1 1-3 3"/><path d="M3 16h7"/>'),
  bien: S('<path d="M4 11a8 8 0 0 1 16 0z"/><path d="M12 11v6"/><path d="M2 20c2 0 2-1.5 4-1.5S8 20 10 20s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/>'),
  dao: S('<path d="M3 20c3-3 15-3 18 0"/><path d="M12 18c0-5 1-8 3-11"/><path d="M15 7c-2-2-6-2-8 0M15 7c1-3 4-4 6-3M15 7c3-1 6 1 6 4M15 7c-3 0-5 2-5 5"/>'),
  thac: S('<path d="M3 5h18"/><path d="M8 5v10M12 5v12M16 5v10"/><path d="M2 20c2 0 2-1.5 4-1.5S8 20 10 20s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/>'),
  song_nuoc: S('<path d="M2 7c2 0 2-1.5 4-1.5S8 7 10 7s2-1.5 4-1.5S16 7 18 7s2-1.5 4-1.5"/><path d="M2 12.5c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/>'),
  suoi_nong: S('<path d="M2 19c2 0 2-1.5 4-1.5S8 19 10 19s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M8 14c-1-1.5 1-2.5 0-4s1-2.5 0-4M12 14c-1-1.5 1-2.5 0-4s1-2.5 0-4M16 14c-1-1.5 1-2.5 0-4s1-2.5 0-4"/>'),
  hang: S('<path d="M2 20h20"/><path d="M4 20C4 10 8 4 12 4s8 6 8 16"/><path d="M9 20c0-4 1.4-7 3-7s3 3 3 7"/>'),
  ruong: S('<path d="M2 8c4 0 6-2 10-2s6 2 10 2"/><path d="M2 13c4 0 6-2 10-2s6 2 10 2"/><path d="M2 18c4 0 6-2 10-2s6 2 10 2"/><path d="M7 5.6V3.8M12 4.8V3M17 5.6V3.8"/>'),
  leu: S('<path d="M2 20h20"/><path d="M4 20L12 4l8 16"/><path d="M9.5 20L12 14l2.5 6"/>'),
  khach_san: S('<path d="M3 6v14M3 16h18v4M21 16v-3a3 3 0 0 0-3-3h-8v6"/><circle cx="6.5" cy="12" r="2"/>'),
  nha: S('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
  lau_dai: S('<path d="M4 21V8h3v2h2V8h2v2h2V8h2v2h2V8h3v13z"/><path d="M10 21v-5h4v5"/>'),
  cho: S('<path d="M3 9l2-5h14l2 5"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 12v9h14v-9"/><path d="M10 21v-5h4v5"/>'),
  an_uong: S('<path d="M5 3v6a3 3 0 0 0 6 0V3M8 3v18"/><path d="M18 21V3c-2 1-3.5 4-3.5 8H18"/>'),
  do_uong: S('<path d="M4 4h16l-8 9z"/><path d="M12 13v7M8 20h8"/><path d="M15 4l3-2"/>'),
  gia: S('<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5"/>'),
  tien: S('<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1.2-1.7-2-3-2-1.7 0-3 1-3 2.3 0 3 6 1.5 6 4.5 0 1.3-1.3 2.3-3 2.3-1.4 0-2.6-.8-3-2M12 5.5v2M12 16.5v2"/>'),
  tuyet: S('<path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7"/><path d="M9.5 3.5L12 6l2.5-2.5M9.5 20.5L12 18l2.5 2.5"/>'),
  may: S('<path d="M7 18a4 4 0 0 1-.6-8A6 6 0 0 1 18 9a4.5 4.5 0 0 1 0 9z"/>'),
  mua: S('<path d="M7 14a4 4 0 0 1-.6-8A6 6 0 0 1 18 5a4.5 4.5 0 0 1 0 9z"/><path d="M8 17l-1 3M12 17l-1 3M16 17l-1 3"/>'),
  nhiet_do: S('<path d="M10 14V4a2 2 0 0 1 4 0v10a4 4 0 1 1-4 0z"/><path d="M12 9v7"/>'),
  o_to: S('<path d="M3 16h18v-4l-2-5H5l-2 5z"/><path d="M3 12h18"/><circle cx="7" cy="17.5" r="2"/><circle cx="17" cy="17.5" r="2"/>'),
  xe_dap: S('<circle cx="5.5" cy="16" r="3.5"/><circle cx="18.5" cy="16" r="3.5"/><path d="M5.5 16L9 8h7l2.5 8M12 16L9 8M7.5 5h3M16 8l-1-3h2"/>'),
  tau_hoa: S('<rect x="5" y="3" width="14" height="14" rx="3"/><path d="M5 10h14"/><circle cx="9" cy="13.5" r="1"/><circle cx="15" cy="13.5" r="1"/><path d="M8 21l2-4M16 21l-2-4"/>'),
  xe_buyt: S('<rect x="2" y="5" width="20" height="12" rx="2.5"/><path d="M2 11h20M7 5v6M12 5v6M17 5v6"/><circle cx="6.5" cy="18" r="1.8"/><circle cx="17.5" cy="18" r="1.8"/>'),
  cap_treo: S('<path d="M2 4l20 4"/><path d="M12 6v4"/><rect x="6" y="10" width="12" height="10" rx="2"/><path d="M6 14h12"/>'),
  balo: S('<rect x="5" y="6" width="14" height="15" rx="4"/><path d="M9 6V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V6"/><path d="M8 14h8v4H8z"/>'),
  vali: S('<rect x="4" y="7" width="16" height="13" rx="2"/><path d="M9 7V4h6v3"/><path d="M8 7v13M16 7v13"/><path d="M7 22v-2M17 22v-2"/>'),
  la_ban: S('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
  ong_nhom: S('<circle cx="6.5" cy="16" r="3.5"/><circle cx="17.5" cy="16" r="3.5"/><path d="M3 16l2-10h3l1 7M21 16l-2-10h-3l-1 7M9.5 13h5"/>'),
  phao_hoa: S('<circle cx="12" cy="9" r="1.2"/><path d="M12 2v3M12 13v3M5 9h3M16 9h3M7 4l2 2M17 4l-2 2M7 14l2-2M17 14l-2-2"/><path d="M12 18v4"/>'),
  non_la: S('<path d="M2 16L12 4l10 12"/><path d="M2 16c3 2 17 2 20 0"/><path d="M7 10.2h10"/>'),
};
const icon = (n, cls = '') => (IC[n] || IC.lap_lanh).replace('<svg ', `<svg class="${cls}" `);

/* bàn tay bấm (tự vẽ: viền tối hợp khối + ruột trắng) — đầu ngón trỏ tại (39, 4) trong hộp 120×160 */
const TAY_HINH = `<rect x="28" y="3" width="22" height="80" rx="11"/><rect x="48" y="44" width="21" height="46" rx="10.5"/><rect x="66.5" y="50" width="20" height="42" rx="10"/><rect x="84.5" y="58" width="18" height="36" rx="9"/><path d="M27 66 L103 72 L103 116 Q103 146 76 150 L54 150 Q30 147 27 124 Z"/><rect x="9" y="76" width="22" height="50" rx="11" transform="rotate(-36 20 101)"/>`;
const TAY = `<svg viewBox="0 0 120 170" width="170" height="241"><defs><linearGradient id="gtay" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E9E6E1"/></linearGradient></defs>
<g fill="#16161b" stroke="#16161b" stroke-width="8" stroke-linejoin="round">${TAY_HINH}<rect x="44" y="144" width="56" height="22" rx="5"/></g>
<g fill="url(#gtay)">${TAY_HINH}</g>
<rect x="44" y="144" width="56" height="22" rx="5" fill="#F4C66A"/>
<g stroke="#16161b" stroke-width="3" stroke-linecap="round" fill="none"><path d="M58.5 50v12M76.5 56v11M93.5 63v10"/><path d="M33 12q6-4 12 0"/></g></svg>`;
const TAY_DIEM = [39 * 170 / 120, 4 * 241 / 170];

/* ================= footage ================= */
const CANH = KH.canh.map((c, i) => {
  const el = mk('div', 'canh');
  el.style.zIndex = 1;
  const o = { c, el, i };
  if (c.khung === 'the') {
    o.nen = mk('img', 'nen', el); o.nen.src = c.nen; o.nen.dataset.u = c.nen;
    o.the = mk('div', 'the', el); o.img = mk('img', '', o.the); mk('div', 'vien_the', o.the);
    const r = c.aw / c.ah;
    let w = c.the_rong || 960, h = w / r;
    if (h > 1100) { h = 1100; w = h * r; }
    o.tw = w; o.th = h;
    css(o.the, { width: w + 'px', height: h + 'px', left: (540 - w / 2) + 'px', top: (c.the_y - h / 2) + 'px' });
    const s0 = Math.max(w / c.aw, h / c.ah);
    css(o.img, { width: c.aw * s0 + 'px', height: c.ah * s0 + 'px', left: (w - c.aw * s0) / 2 + 'px', top: (h - c.ah * s0) / 2 + 'px' });
  } else {
    o.img = mk('img', '', el);
    if (c.loai === 'anh') { const s0 = Math.max(W / c.aw, H / c.ah); o.bw = c.aw * s0; o.bh = c.ah * s0; }
    else { o.bw = W; o.bh = H; }
    css(o.img, { width: o.bw + 'px', height: o.bh + 'px' });
  }
  return o;
});

function sceneAt(t) { let i = 0; for (let k = 0; k < KH.canh.length; k++) if (KH.canh[k].tu <= t + 1e-6) i = k; return i; }

function kenBurns(o, t) {
  const c = o.c, dur = Math.max(.5, c.den - c.tu), u = clamp((t - c.tu) / dur, 0, 1.25), k = E.inOutS(clamp(u, 0, 1)) * .85 + u * .15;
  const cd = c.chuyen_dong || 'zoom_vao';
  let s = 1.02, x = 0, y = 0;
  const bw = o.bw || W, bh = o.bh || H;
  if (cd === 'zoom_vao') s = 1.0 + .10 * k;
  else if (cd === 'zoom_ra') s = 1.10 - .10 * k;
  else if (cd === 'lia_trai' || cd === 'lia_phai') {
    s = c.loai === 'anh' ? 1.0 : 1.08;
    const X = Math.max(0, (bw * s - W) / 2) * .92; const d = cd === 'lia_trai' ? 1 : -1;
    x = d * lerp(X, -X, k);
  } else if (cd === 'lia_len' || cd === 'lia_xuong') {
    s = c.loai === 'anh' ? 1.0 : 1.08;
    const Y = Math.max(0, (bh * s - H) / 2) * .92; const d = cd === 'lia_len' ? 1 : -1;
    y = d * lerp(Y, -Y, k);
  }
  if (c.loai === 'anh' && c.khung !== 'the' && c.lech_x != null) x += (c.lech_x || 0) * Math.max(0, (bw * s - W) / 2);
  return { s, x, y };
}

function veCanh(o, t, ds) {
  const c = o.c;
  if (c.loai === 'clip') {
    const i = clamp(Math.floor((t - c.tu) * FPS + 1e-4) + 1, 1, c.n);
    setSrc(o.img, c.dir + pad5(i) + '.jpg', ds);
  } else setSrc(o.img, c.anh, ds);
  const kb = kenBurns(o, t);
  if (c.khung === 'the') {
    const u = clamp((t - c.tu) / Math.max(.5, c.den - c.tu), 0, 1.2);
    css(o.img, { transform: `scale(${(1.0 + .08 * u).toFixed(4)})` });
    css(o.nen, { transform: `scale(${(1.06 + .05 * u).toFixed(4)})`, transformOrigin: '50% 50%' });
    const f = Math.sin((t - c.tu) * 2 * Math.PI / 6);
    css(o.the, { transform: `translateY(${(f * 7).toFixed(2)}px) rotate(${(f * .5 - .3).toFixed(3)}deg)` });
  } else {
    const bw = o.bw, bh = o.bh;
    const tx = 540 - bw * kb.s / 2 + kb.x, ty = 960 - bh * kb.s / 2 + kb.y;
    css(o.img, { transform: `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${kb.s.toFixed(4)})` });
  }
}

function veFootage(t, ds) {
  const i = sceneAt(t), cur = CANH[i], prev = CANH[i - 1];
  const vao = cur.c.vao || { kieu: 'cat', dai: 0 };
  const u = vao.dai > 0 ? (t - cur.c.tu) / vao.dai : 1;
  const dang = new Set([cur]);
  let A = { op: 1, tf: '', bl: 0 }, B = null;
  if (prev && u < 1 && vao.kieu !== 'cat') {
    dang.add(prev); B = { op: 1, tf: '', bl: 0 };
    const k = E.inOutC(clamp(u));
    switch (vao.kieu) {
      case 'hoa_tan': A.op = E.inOutS(clamp(u)); break;
      case 'nhoe': A.op = E.inOutS(clamp(u)); A.bl = 16 * (1 - u); B.bl = 16 * u; break;
      case 'lia': { const b = 34 * Math.sin(Math.PI * clamp(u)); B.tf = `translateX(${(-k * W).toFixed(1)}px)`; A.tf = `translateX(${((1 - k) * W).toFixed(1)}px)`; A.bl = B.bl = b; break; }
      case 'lia_doc': { const b = 34 * Math.sin(Math.PI * clamp(u)); B.tf = `translateY(${(-k * H).toFixed(1)}px)`; A.tf = `translateY(${((1 - k) * H).toFixed(1)}px)`; A.bl = B.bl = b; break; }
      case 'truot': { B.tf = `translateY(${(-k * H * .4).toFixed(1)}px) scale(${(1 - .08 * k).toFixed(4)})`; B.op = 1 - .5 * k; A.tf = `translateY(${((1 - k) * H).toFixed(1)}px)`; break; }
      case 'zoom': {
        const uo = clamp(u / .62), ui = clamp((u - .28) / .72);
        B.tf = `scale(${(1 + 1.3 * E.inC(uo)).toFixed(4)})`; B.bl = 26 * uo; B.op = 1 - E.inQ(uo);
        A.tf = `scale(${(1.45 - .45 * E.outC(ui)).toFixed(4)})`; A.bl = 22 * (1 - ui); A.op = clamp((u - .22) / .3);
        break;
      }
      case 'loe': A.op = E.inOutS(clamp(u)); break;
      default: A.op = E.inOutS(clamp(u));
    }
  }
  // CTA: nền nhoè dần
  const cta = KH.cta;
  let blurCta = 0;
  if (cta && t >= cta.tu) blurCta = 16 * P(t, cta.tu, .8, E.inOutS);
  for (const o of CANH) {
    if (!dang.has(o)) { show(o.el, false); continue; }
    show(o.el, true);
    const st = o === cur ? A : B;
    veCanh(o, t, ds);
    const bl = st.bl + blurCta;
    css(o.el, { opacity: st.op.toFixed(3), transform: st.tf || 'none', filter: bl > .3 ? `blur(${bl.toFixed(1)}px)` : 'none', zIndex: o === cur ? 2 : 1 });
  }
}

/* ================= lớp màu ================= */
mk('div', '', stage).id = 'am';
mk('div', '', stage).id = 'toi_tren';
mk('div', '', stage).id = 'toi_duoi';
mk('div', '', stage).id = 'vignette';
const HAT = mk('div', '', stage); HAT.id = 'hat';
(() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d'); const im = g.createImageData(256, 256);
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (hash01(i * .37) - .5) * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  g.putImageData(im, 0, 0); HAT.style.backgroundImage = `url(${cv.toDataURL()})`; })();
const LOE = mk('div', '', stage); LOE.id = 'loe';
const TRANG = mk('div', '', stage); TRANG.id = 'trang_loe';
const MO_CTA = mk('div', '', stage); MO_CTA.id = 'mo_cta';
const LOE_DS = (KH.loe || []).slice();
for (const c of KH.canh) if (c.vao && c.vao.kieu === 'loe') LOE_DS.push({ t: c.tu - c.vao.dai * .35, dai: c.vao.dai * 1.5 });

function veMau(t) {
  const f = Math.floor(t * FPS);
  css(HAT, { backgroundPosition: `${Math.floor(hash01(f) * 256)}px ${Math.floor(hash01(f + 99) * 256)}px` });
  let L = 0, W2 = 0;
  for (const l of LOE_DS) {
    const u = (t - l.t) / l.dai;
    if (u < 0 || u > 1) continue;
    const e = Math.pow(Math.sin(Math.PI * u), 1.4);
    L = Math.max(L, e); W2 = Math.max(W2, Math.pow(Math.sin(Math.PI * clamp((u - .25) / .5)), 3) * .28);
  }
  if (L > .005) {
    const x = 20 + 60 * hash01(Math.floor(t * 2)), dx = (t * 40) % 100;
    css(LOE, { opacity: L.toFixed(3), background: `radial-gradient(circle at ${(x + dx * .3).toFixed(1)}% 22%, rgba(255,186,90,.95), rgba(255,140,60,0) 46%), radial-gradient(circle at ${(90 - dx * .4).toFixed(1)}% 70%, rgba(255,95,120,.7), rgba(255,95,120,0) 40%), radial-gradient(circle at 50% 50%, rgba(255,240,200,.55), rgba(255,240,200,0) 60%)` });
  } else css(LOE, { opacity: '0' });
  css(TRANG, { opacity: W2.toFixed(3) });
}

/* ================= đồ hoạ ================= */
const LOP = mk('div', 'abs'); LOP.style.inset = '0'; LOP.style.zIndex = 20;
const HOP = [];     // hộp chữ để tự kiểm
function hop(el, loai, id, opf) { HOP.push({ el, loai, id, opf }); }
for (const o of CANH) if (o.the) hop(o.the, 'the_canh', o.c.id);   // thẻ ảnh của cảnh: chữ đồ hoạ không được che ảnh

/* bề rộng chữ thật (khối div rộng 1080 nên scrollWidth không dùng được) */
function rong(el) { const r = document.createRange(); r.selectNodeContents(el); const b = r.getBoundingClientRect(); return b.width; }
/* co chữ cho vừa maxW; hai_dong: chữ quá dài (> 1,18 × maxW) thì ngắt 2 dòng cân ở dấu cách rồi mới co */
function vua(el, base, maxW, hai_dong = false, spans = null) {
  el.style.fontSize = base + 'px';
  let w = rong(el);
  if (hai_dong && w > maxW * 1.18 && spans) {
    const sp = spans.filter(x => x.textContent === ' ');
    if (sp.length) {
      const x0 = spans[0].getBoundingClientRect().left;   // dòng tràn khung thì text-align:center dồn về trái — lấy mép ký tự đầu
      let best = sp[0], bd = 1e9;
      for (const x of sp) { const d = Math.abs(x.getBoundingClientRect().left - x0 - w / 2); if (d < bd) { bd = d; best = x; } }
      best.after(document.createElement('br'));
      w = rong(el);
    }
  }
  if (w > maxW) el.style.fontSize = (base * maxW / w) + 'px';
  return parseFloat(el.style.fontSize);
}
function tachChu(parent, text, cls = 'chu') { return chars(text).map(ch => mk('span', cls, parent, esc(ch))); }
function tachTu(parent, text, mask = true) {
  const out = [];
  const ds = KHONG_CACH ? chars(text) : words(text);
  ds.forEach((w, j) => {
    const m = mask ? mk('span', 'mask', parent) : parent;
    out.push(mk('span', 'tu', m, esc(w)));
    if (!KHONG_CACH && j < ds.length - 1) parent.appendChild(document.createTextNode(' '));
  });
  return out;
}
function vaoRa(t, d, vao = .5, ra = .4) { return { v: P(t, d.tu, vao), r: P(t, d.den - ra, ra, E.inC), on: t >= d.tu - .02 && t <= d.den + .02 }; }

const LAM = {};

/* ---- mở đầu ---- */
LAM.mo_dau = d => {
  const el = mk('div', 'md', LOP);
  const tren = d.tren ? mk('div', 'tren', el) : null;
  let g1, g2, trenTxt;
  if (tren) { g1 = mk('span', 'gach', tren); trenTxt = mk('span', '', tren, esc(d.tren)); g2 = mk('span', 'gach p', tren); }
  const chinh = mk('div', 'chinh', el);
  const cs = tachChu(chinh, d.chinh || '');
  const vt = d.viet_tay ? mk('div', 'viet_tay vang_grad', el, esc(d.viet_tay)) : null;
  const duoi = d.duoi ? mk('div', '', el) : null;
  let duoiPill;
  if (duoi) duoiPill = mk('div', 'duoi', duoi, icon('ghim') + `<span>${esc(d.duoi)}</span>`);
  hop(chinh, 'mo_dau', d.id); if (vt) hop(vt, 'mo_dau', d.id);
  const g = {
    el, sau() { // sau khi có font: co chữ cho vừa 980px, đặt tâm theo y
      chinh.style.letterSpacing = '.16em'; vua(chinh, d.co || 230, 990); chinh.style.letterSpacing = '';   // đo ở độ giãn chữ lớn nhất lúc vào
      if (vt) vua(vt, 132 * CO_TAY, 1000);
      el.style.top = ((d.y || 820) - el.offsetHeight / 2) + 'px';
    },
    ve(t) {
      const { r, on } = vaoRa(t, d, .5, .45); show(el, on); if (!on) return;
      const t0 = d.tu;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(-40 * r).toFixed(1)}px)`, filter: r > .01 ? `blur(${(10 * r).toFixed(1)}px)` : 'none' });
      if (tren) {
        const k = P(t, t0, .9);
        css(trenTxt, { opacity: k.toFixed(3), letterSpacing: lerp(.95, .5, k).toFixed(3) + 'em' });
        const kg = P(t, t0 + .15, .7); css(g1, { width: (120 * kg) + 'px' }); css(g2, { width: (120 * kg) + 'px' });
      }
      const ks = P(t, t0 + .25, 1.4);
      css(chinh, { letterSpacing: lerp(.16, .02, ks).toFixed(3) + 'em' });
      cs.forEach((s, i) => {
        const a = t0 + .25 + i * .055, k = P(t, a, .8, E.outC);
        const sh = clamp((t - (t0 + 1.25) - i * .05) / .55);
        css(s, { opacity: clamp(k * 1.6).toFixed(3), transform: `translateY(${((1 - k) * 70).toFixed(1)}px) scale(${(1.22 - .22 * k).toFixed(3)})`,
          filter: k < .99 ? `blur(${((1 - k) * 14).toFixed(1)}px)` : 'none', backgroundPosition: `${(100 - sh * 100).toFixed(1)}% 0` });
      });
      if (vt) { const k = P(t, t0 + .95, 1.0, E.inOutS); css(vt, { clipPath: `inset(-20% ${(100 - 100 * k).toFixed(1)}% -30% -5%)`, opacity: clamp(k * 3).toFixed(3) }); }
      if (duoiPill) { const k = P(t, t0 + 1.5, .5); css(duoiPill, { opacity: k.toFixed(3), transform: `translateY(${(20 * (1 - k)).toFixed(1)}px)` }); }
    },
  };
  return g;
};

/* ---- từ khoá bật theo lời ---- */
LAM.tu_khoa = d => {
  const el = mk('div', 'tk', LOP);
  const ms = (d.muc || []).map(m => {
    const r = mk('div', 'muc' + (m.kieu === 'tay' ? ' tay' : ''), el);
    const s = mk('span', m.kieu === 'tay' ? 'vang_grad' : '', r, esc(m.chu));
    const gch = m.kieu === 'tay' ? null : mk('span', 'gach', r);
    hop(s, 'tu_khoa', d.id);
    return { m, r, s, gch };
  });
  return {
    el, sau() {
      for (const o of ms) if (o.s.scrollWidth > 980) o.s.style.fontSize = (parseFloat(getComputedStyle(o.s).fontSize) * 980 / o.s.scrollWidth) + 'px';
      el.style.top = ((d.y || 800) - el.offsetHeight / 2) + 'px';
    },
    ve(t) {
      const { r, on } = vaoRa(t, d, .3, .4); show(el, on); if (!on) return;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(-30 * r).toFixed(1)}px)` });
      for (const o of ms) {
        const a = o.m.luc_abs, k = P(t, a - .04, .42, E.outB), k2 = P(t, a - .04, .3);
        css(o.s, { opacity: clamp(k2 * 1.4).toFixed(3), transform: `scale(${(1.35 - .35 * k).toFixed(3)})`, filter: k2 < .99 ? `blur(${((1 - k2) * 12).toFixed(1)}px)` : 'drop-shadow(0 8px 24px rgba(0,0,0,.6))' });
        if (o.gch) css(o.gch, { width: (Math.min(o.s.offsetWidth * .55, 420) * P(t, a + .15, .45)).toFixed(1) + 'px' });
      }
    },
  };
};

/* ---- chương ---- */
LAM.chuong = d => {
  const el = mk('div', 'ch', LOP);
  const nhan = d.nhan ? mk('div', 'nhan', el, esc(d.nhan)) : null;
  const sw = d.so ? mk('div', 'so_wrap', el) : null;
  let so1, so2;
  if (sw) { so1 = mk('div', 'so vien', sw, esc(d.so)); so2 = mk('div', 'so dac', sw, esc(d.so)); }
  const ten = mk('div', 'ten bong', el);
  const tws = tachTu(ten, d.ten || '');
  const gach = mk('div', 'gach', el);
  const phu = d.phu ? mk('div', 'phu', el, esc(d.phu)) : null;
  hop(ten, 'chuong', d.id); if (phu) hop(phu, 'chuong', d.id); if (sw) hop(sw, 'chuong', d.id);
  return {
    el, sau() {
      el.style.top = (d.y || 300) + 'px';
      let fs = 92; ten.style.fontSize = fs + 'px';
      for (let k = 0; k < 8 && (ten.offsetHeight > fs * 1.02 * 2.2 || ten.scrollWidth > 945); k++) { fs *= .9; ten.style.fontSize = fs + 'px'; }
      if (phu && phu.scrollWidth > 940) phu.style.fontSize = (66 * 940 / phu.scrollWidth) + 'px';
    },
    ve(t) {
      const { r, on } = vaoRa(t, d, .5, .4); show(el, on); if (!on) return;
      const t0 = d.tu;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateX(${(-70 * r).toFixed(1)}px)` });
      if (nhan) { const k = P(t, t0, .7); css(nhan, { opacity: k.toFixed(3), letterSpacing: lerp(.8, .42, k).toFixed(3) + 'em' }); }
      if (sw) {
        const k = P(t, t0 + .05, .5); css(so1, { opacity: k.toFixed(3), transform: `translateX(${(-50 * (1 - k)).toFixed(1)}px)` });
        const kf = P(t, t0 + .4, .8, E.inOutS); css(so2, { clipPath: `inset(${(100 - 100 * kf).toFixed(1)}% -5% -5% -5%)`, transform: `translateX(${(-50 * (1 - k)).toFixed(1)}px)` });
      }
      tws.forEach((w, j) => { const k = P(t, t0 + .3 + j * .09, .6, E.outC); css(w, { transform: `translateY(${((1 - k) * 110).toFixed(1)}%)` }); });
      css(gach, { width: (260 * P(t, t0 + .6, .6)).toFixed(1) + 'px' });
      if (phu) { const k = P(t, t0 + .85, .9, E.inOutS); css(phu, { clipPath: `inset(-20% ${(100 - 100 * k).toFixed(1)}% -30% -5%)` }); }
    },
  };
};

/* ---- tiêu đề đoạn ---- */
LAM.tieu_de = d => {
  const el = mk('div', 'td', LOP);
  const dan = d.dan ? mk('div', 'dan bong', el, esc(d.dan)) : null;
  const khoa = mk('div', 'khoa' + (d.mau === 'trang' ? ' trang' : ''), el);
  const cs = tachChu(khoa, d.khoa || '');
  const vt = d.viet_tay ? mk('div', 'viet_tay', el, esc(d.viet_tay)) : null;
  hop(khoa, 'tieu_de', d.id); if (vt) hop(vt, 'tieu_de', d.id);
  return {
    el, sau() {
      vua(khoa, d.co || 132, 980, true, cs);
      if (dan) vua(dan, 32, 1000);
      if (vt) vua(vt, 118 * CO_TAY, 1000);
      el.style.top = ((d.y || 760) - el.offsetHeight / 2) + 'px';
    },
    ve(t) {
      const { r, on } = vaoRa(t, d, .5, .4); show(el, on); if (!on) return;
      const t0 = d.tu;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(-36 * r).toFixed(1)}px)`, filter: r > .01 ? `blur(${(8 * r).toFixed(1)}px)` : 'none' });
      if (dan) { const k = P(t, t0, .8); css(dan, { opacity: k.toFixed(3), letterSpacing: lerp(.8, .4, k).toFixed(3) + 'em' }); }
      cs.forEach((s, i) => { const k = P(t, t0 + .15 + i * .04, .65); css(s, { opacity: clamp(k * 1.6).toFixed(3), transform: `translateY(${((1 - k) * 60).toFixed(1)}px)`, filter: k < .99 ? `blur(${((1 - k) * 10).toFixed(1)}px)` : 'none' }); });
      if (vt) { const k = P(t, t0 + .7, .9, E.inOutS); css(vt, { clipPath: `inset(-20% ${(100 - 100 * k).toFixed(1)}% -30% -5%)` }); }
    },
  };
};

/* ---- ghim địa điểm ---- */
LAM.ghim = d => {
  const el = mk('div', 'gh', LOP);
  const vong = mk('div', 'vien_vong', el);
  const the = mk('div', 'the', el);
  mk('div', 'ten', the, esc(d.ten)); if (d.phu) mk('div', 'phu', the, esc(d.phu));
  const tron = mk('div', 'tron', el, icon('ghim')); tron.style.color = '#2A1C06';
  hop(the, 'ghim', d.id);
  return {
    el, sau() { el.style.top = (d.y || (d.vi_tri === 'duoi' ? 1175 : 214)) + 'px'; },
    ve(t) {
      const { r, on } = vaoRa(t, d, .5, .4); show(el, on); if (!on) return;
      const t0 = d.tu;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateX(${(-40 * r).toFixed(1)}px)` });
      const k = P(t, t0, .6, E.drop); css(tron, { transform: `translateY(${(-170 * (1 - k)).toFixed(1)}px)`, opacity: clamp(P(t, t0, .2) * 1.2).toFixed(3) });
      const kc = P(t, t0 + .38, .55, E.outC); css(the, { clipPath: `inset(-10% ${(100 - 100 * kc).toFixed(1)}% -10% 0)` });
      const pr = ((t - t0 - .5) % 2.2 + 2.2) % 2.2 / .95;
      if (t > t0 + .5 && pr <= 1) css(vong, { opacity: (.9 * (1 - pr)).toFixed(3), transform: `scale(${(1 + 1.2 * E.outC(pr)).toFixed(3)})` }); else css(vong, { opacity: '0' });
    },
  };
};

/* ---- chip thông tin ---- */
LAM.chip = d => {
  const el = mk('div', 'cp', LOP);
  const cs = (d.muc || []).map((m, i) => {
    const c = mk('div', 'c', el);
    const ic = mk('div', 'ic', c, icon(m.icon)); ic.style.color = '#2A1C06';
    mk('div', 't', c, esc(m.chu));
    hop(c, 'chip', d.id);
    return { c, ic, a: m.luc_abs != null ? m.luc_abs : d.tu + i * .2 };
  });
  return {
    el, sau() { el.style.top = (d.y != null ? d.y : 1292 - el.offsetHeight) + 'px'; },   // mặc định: đáy chip 1292 px, ngay trên sub
    ve(t) {
      const { r, on } = vaoRa(t, d, .4, .35); show(el, on); if (!on) return;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(20 * r).toFixed(1)}px)` });
      for (const o of cs) { const k = P(t, o.a, .5, E.outB), k2 = P(t, o.a, .25); css(o.c, { opacity: k2.toFixed(3), transform: `scale(${(.55 + .45 * k).toFixed(3)})` }); css(o.ic, { transform: `rotate(${(-120 * (1 - k)).toFixed(1)}deg)` }); }
    },
  };
};

/* ---- số lớn đếm lên ---- */
const fmtSo = (x, nn) => { const s = String(Math.round(x)); const sep = ['vi', 'de', 'id', 'es', 'it', 'pt', 'ru', 'fr'].includes(nn) ? (nn === 'fr' || nn === 'ru' ? ' ' : '.') : ','; return s.replace(/\B(?=(\d{3})+(?!\d))/g, sep); };
LAM.so_lon = d => {
  const el = mk('div', 'sl', LOP);
  const tt = d.tien_to ? mk('div', 'tien_to', el, esc(d.tien_to)) : null;
  const hang = mk('div', 'hang', el);
  const so = mk('span', 'so', hang, fmtSo(d.so, NN));
  const ht = d.hau_to ? mk('span', 'hau_to', hang, esc(d.hau_to)) : null;
  const nh = d.nhan ? mk('div', 'nhan', el, esc(d.nhan)) : null;
  hop(hang, 'so_lon', d.id); if (nh) hop(nh, 'so_lon', d.id);
  return {
    el, sau() {
      so.textContent = fmtSo(d.so, NN);
      const wh = rong(so) + (ht ? rong(ht) + 10 : 0);
      if (wh > 980) { const k = 980 / wh; so.style.fontSize = (270 * k) + 'px'; if (ht) ht.style.fontSize = (150 * k) + 'px'; }
      if (nh) vua(nh, 120 * CO_TAY, 1000);
      el.style.top = ((d.y || 800) - el.offsetHeight / 2) + 'px';
    },
    ve(t) {
      const { r, on } = vaoRa(t, d, .4, .4); show(el, on); if (!on) return;
      const t0 = d.tu, td = d.dem_tu != null ? d.dem_tu : t0 + .15, dd = d.dem_dai || 1.4;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(-30 * r).toFixed(1)}px)` });
      if (tt) { const k = P(t, t0, .6); css(tt, { opacity: k.toFixed(3), letterSpacing: lerp(.8, .4, k).toFixed(3) + 'em' }); }
      const kd = P(t, td, dd, E.outC); so.textContent = fmtSo(d.so * kd, NN);
      const ka = P(t, t0, .45); css(so, { opacity: ka.toFixed(3) });
      const kb = P(t, td + dd - .05, .45, E.outB); css(hang, { transform: `scale(${(1.0 + .06 * Math.sin(Math.PI * clamp((t - td - dd + .05) / .45)) * (1 - kb * 0)).toFixed(4)})` });
      if (ht) { const k = P(t, td + dd - .1, .45, E.outB); css(ht, { opacity: clamp(k * 2).toFixed(3), transform: `scale(${(.4 + .6 * k).toFixed(3)})`, display: 'inline-block' }); }
      if (nh) { const k = P(t, td + dd + .05, .9, E.inOutS); css(nh, { clipPath: `inset(-20% ${(100 - 100 * k).toFixed(1)}% -30% -5%)` }); }
    },
  };
};

/* ---- thẻ ảnh polaroid ---- */
LAM.the_anh = d => {
  const el = mk('div', 'ta', LOP);
  mk('div', 'bang_dinh', el);
  const kh = mk('div', 'khung', el);
  const im = mk('img', '', kh); im.src = d.anh_url;
  const s0 = Math.max(600 / d.aw, 450 / d.ah);
  css(im, { width: d.aw * s0 + 'px', height: d.ah * s0 + 'px', marginLeft: -d.aw * s0 / 2 + 'px', marginTop: -d.ah * s0 / 2 + 'px' });
  const cap = d.chu_thich ? mk('div', 'cap', el, esc(d.chu_thich)) : null;
  if (!cap) el.style.paddingBottom = '20px';
  hop(el, 'the_anh', d.id);
  return {
    el, sau() {
      if (cap && cap.scrollWidth > 600) cap.style.fontSize = (50 * 600 / cap.scrollWidth) + 'px';
      el.style.left = ((d.x || 540) - 320) + 'px'; el.style.top = ((d.y || 800) - el.offsetHeight / 2) + 'px';
    },
    ve(t) {
      const on = t >= d.tu - .02 && t <= d.den + .02; show(el, on); if (!on) return;
      const t0 = d.tu, g = d.goc != null ? d.goc : -4;
      const k = P(t, t0, .65, E.outB), ka = P(t, t0, .3), kr = P(t, d.den - .45, .45, E.inC);
      const f = Math.sin((t - t0) * 2 * Math.PI / 5);
      css(el, { opacity: (ka * (1 - kr)).toFixed(3),
        transform: `translate(${(kr * 760).toFixed(1)}px, ${(-280 * (1 - k) + f * 6).toFixed(1)}px) rotate(${(g - 14 * (1 - k) + 14 * kr + f * .6).toFixed(2)}deg) scale(${(1.18 - .18 * k).toFixed(3)})` });
      css(im, { transform: `scale(${(1.04 + .1 * clamp((t - t0) / Math.max(1, d.den - t0))).toFixed(4)})` });
    },
  };
};

/* ---- liệt kê ---- */
LAM.liet_ke = d => {
  const el = mk('div', 'lk', LOP);
  const dan = d.dan ? mk('div', 'dan', el, esc(d.dan)) : null;
  const tieu = d.tieu ? mk('div', 'tieu', el, esc(d.tieu)) : null;
  const ds = (d.muc || []).map((m, i) => {
    const r = mk('div', 'dong', el);
    const ic = mk('div', 'ic', r, icon(m.icon)); ic.style.color = '#2A1C06';
    const tx = mk('div', 't', r, esc(m.chu) + (m.phu ? `<span class="phu">${esc(m.phu)}</span>` : ''));
    const ti = mk('div', 'tich', r, icon('tich')); ti.style.color = '#F4C66A';
    return { r, ic, tx, ti, a: m.luc_abs != null ? m.luc_abs : d.tu + .5 + i * .4 };
  });
  hop(el, 'liet_ke', d.id);
  return {
    el, sau() {
      for (const o of ds) if (o.tx.scrollWidth > o.tx.clientWidth + 2) o.tx.style.fontSize = (48 * o.tx.clientWidth / o.tx.scrollWidth) + 'px';
      el.style.top = (d.y || 300) + 'px';
    },
    ve(t) {
      const { v, r, on } = vaoRa(t, d, .55, .45); show(el, on); if (!on) return;
      css(el, { opacity: (v * (1 - r)).toFixed(3), transform: `translateY(${(40 * (1 - v) - 30 * r).toFixed(1)}px) scale(${(.96 + .04 * v).toFixed(4)})` });
      if (dan) css(dan, { opacity: P(t, d.tu + .1, .5).toFixed(3) });
      if (tieu) { const k = P(t, d.tu + .15, .6); css(tieu, { opacity: k.toFixed(3), transform: `translateY(${(24 * (1 - k)).toFixed(1)}px)` }); }
      for (const o of ds) {
        const k = P(t, o.a - .05, .45), kb = P(t, o.a - .05, .5, E.outB), kt = P(t, o.a + .3, .45, E.outB);
        css(o.r, { opacity: k.toFixed(3), transform: `translateX(${(-50 * (1 - k)).toFixed(1)}px)` });
        css(o.ic, { transform: `scale(${(.3 + .7 * kb).toFixed(3)}) rotate(${(-90 * (1 - kb)).toFixed(1)}deg)` });
        css(o.ti, { transform: `scale(${kt.toFixed(3)})`, opacity: clamp(kt * 2).toFixed(3) });
      }
    },
  };
};

/* ---- trích dẫn ---- */
LAM.trich = d => {
  const el = mk('div', 'tr', LOP);
  const ng = mk('div', 'ngoac', el, '<span>“</span>');
  const noi = mk('div', 'noi', el);
  const ws = tachTu(noi, d.noi || '', false);
  const nguon = d.nguon ? mk('div', 'nguon', el, '— ' + esc(d.nguon)) : null;
  hop(noi, 'trich', d.id);
  return {
    el, sau() { el.style.top = ((d.y || 780) - el.offsetHeight / 2) + 'px'; },
    ve(t) {
      const { r, on } = vaoRa(t, d, .5, .4); show(el, on); if (!on) return;
      const t0 = d.tu;
      css(el, { opacity: (1 - r).toFixed(3), transform: `translateY(${(-30 * r).toFixed(1)}px)` });
      const kq = P(t, t0, .55, E.outB); css(ng, { transform: `scale(${(.3 + .7 * kq).toFixed(3)})`, opacity: clamp(kq * 2).toFixed(3) });
      ws.forEach((w, j) => { const k = P(t, t0 + .25 + j * .07, .5); css(w, { opacity: k.toFixed(3), transform: `translateY(${(26 * (1 - k)).toFixed(1)}px)` }); });
      if (nguon) css(nguon, { opacity: P(t, t0 + .6 + ws.length * .07, .5).toFixed(3) });
    },
  };
};

/* ================= HÀNH TRÌNH: điểm đi → điểm đến · phương tiện · thời gian / khoảng cách =================
   nen: troi (máy bay trên biển mây) · duong (xe chạy, núi + cây lùi) · bien (du thuyền giữa núi đá) ·
        ban_do (bản đồ phố, đường đi vẽ dần) · that (BẢN ĐỒ THẬT: vệ tinh + đường đi thật, mặc định) · canh (chỉ thẻ tuyến, đè lên footage có sẵn — vd clip máy bay của người dùng) */
const md = (a, n) => ((a % n) + n) % n;
const IC_PT = { may_bay: 'may_bay', o_to: 'o_to', xe_may: 'xe_may', xe_buyt: 'xe_buyt', xe_dap: 'xe_dap', tau_hoa: 'tau_hoa', tau_thuy: 'tau', di_bo: 'di_bo', khong: 'ghim' };
let HT_U = 0;
const lap4 = (s, w = 1080) => [-w, 0, w, 2 * w].map(o => `<g transform="translate(${o} 0)">${s}</g>`).join('');
const f1 = x => x.toFixed(1);

function mayTile(seed, n, y0, dy, r0, r1) {        // đám mây = chùm vòng tròn (mỗi vòng tô gradient riêng → phồng 3D) + đáy phẳng
  let s = '';
  for (let i = 0; i < n; i++) {
    const cx = (i + .15 + .7 * hash01(seed + i * 1.7)) * 1080 / n, cy = y0 + (hash01(seed + i * 4.3) - .5) * dy;
    const R = r0 + (r1 - r0) * hash01(seed + i * 2.9), k = 5 + Math.floor(hash01(seed + i * 6.1) * 3);
    for (let j = 0; j < k; j++) {
      const a = j / (k - 1) - .5, r = R * (.5 + .55 * (1 - Math.abs(a) * 1.5) + .2 * hash01(seed + i * 9 + j * 1.3));
      s += `<circle cx="${f1(cx + a * R * 2.4)}" cy="${f1(cy - r * .3)}" r="${f1(Math.max(10, r))}"/>`;
    }
    for (let j = 0; j < 3; j++) s += `<circle cx="${f1(cx + (j - 1) * R * .9)}" cy="${f1(cy + R * .12)}" r="${f1(R * .42)}"/>`;
  }
  return lap4(s);
}
function nuiTile(seed, y, h0, h1, buoc) {           // dãy núi đá vôi: sườn dốc, đỉnh tròn
  let p = `M0 ${y}`, x = 0, i = 0;
  while (x < 1080 - 1) {
    const ww = Math.min(1080 - x, buoc * (.6 + .8 * hash01(seed + i * 3.7))), hh = h0 + (h1 - h0) * hash01(seed + i * 5.3);
    p += ` C${f1(x + ww * .1)} ${f1(y - hh * .85)},${f1(x + ww * .28)} ${f1(y - hh)},${f1(x + ww * .5)} ${f1(y - hh)}`;
    p += ` C${f1(x + ww * .72)} ${f1(y - hh)},${f1(x + ww * .9)} ${f1(y - hh * .85)},${f1(x + ww)} ${y}`;
    x += ww; i++;
  }
  return lap4(`<path d="${p} L1080 ${y + 600} L0 ${y + 600}Z"/>`);
}
function doiTile(seed, y, a0, a1, buoc) {           // đồi thoải
  let p = `M0 ${y}`, x = 0, i = 0;
  while (x < 1080 - 1) {
    const ww = Math.min(1080 - x, buoc * (.7 + .6 * hash01(seed + i * 3.1))), hh = a0 + (a1 - a0) * hash01(seed + i * 4.7);
    p += ` C${f1(x + ww * .3)} ${f1(y - hh)},${f1(x + ww * .7)} ${f1(y - hh)},${f1(x + ww)} ${y}`;
    x += ww; i++;
  }
  return lap4(`<path d="${p} L1080 ${y + 600} L0 ${y + 600}Z"/>`);
}
function phoTile(seed, y, h0, h1, cua) {            // đường chân trời thành phố: khối nhà cao thấp + cửa sổ sáng mờ
  let s = '', x = 0, i = 0;
  while (x < 1080) {
    const w = 46 + 70 * hash01(seed + i * 2.3), h = h0 + (h1 - h0) * Math.pow(hash01(seed + i * 5.9), 1.6);
    s += `<rect x="${f1(x)}" y="${f1(y - h)}" width="${f1(w - 6)}" height="${f1(h + 600)}"/>`;
    if (hash01(seed + i * 8.3) > .72) s += `<rect x="${f1(x + w / 2 - 5)}" y="${f1(y - h - 34)}" width="4" height="36"/>`;
    if (cua) for (let yy = y - h + 16; yy < y - 14; yy += 22) for (let xx = x + 8; xx < x + w - 14; xx += 16)
      if (hash01(xx * .37 + yy * .91 + seed) > .58) s += `<rect x="${f1(xx)}" y="${f1(yy)}" width="6" height="9" fill="${cua}"/>`;
    x += w; i++;
  }
  return lap4(s);
}
function cayTile(seed, y) {                          // hàng cây ven đường
  let s = '';
  for (let i = 0; i < 16; i++) {
    const x = i * 67.5 + hash01(seed + i) * 30, r = 22 + 26 * hash01(seed + i * 2.3);
    s += `<rect x="${f1(x - 4)}" y="${f1(y - r * .6)}" width="8" height="${f1(r * .6 + 4)}" fill="#26331f"/><circle cx="${f1(x)}" cy="${f1(y - r * 1.1)}" r="${f1(r)}"/><circle cx="${f1(x + r * .55)}" cy="${f1(y - r * .8)}" r="${f1(r * .7)}"/>`;
  }
  return lap4(s);
}
function coTile(seed) {                              // tiền cảnh: cỏ + cọc tiêu ven đường (lướt nhanh)
  let s = '';
  for (let i = 0; i < 9; i++) {
    const x = i * 120 + hash01(seed + i) * 60, h = 26 + 40 * hash01(seed + i * 3.1);
    s += `<path d="M${f1(x)} 1300 q6 ${f1(-h)} 14 ${f1(-h * 1.1)} q-2 ${f1(h * .6)} 6 ${f1(h * 1.1)} q8 ${f1(-h * .9)} 18 ${f1(-h)} q-4 ${f1(h * .7)} 2 ${f1(h)}Z" fill="#2f4a28"/>`;
  }
  for (let i = 0; i < 2; i++) { const x = 160 + i * 540; s += `<rect x="${x}" y="1262" width="16" height="64" rx="3" fill="#ECE7DC"/><rect x="${x}" y="1272" width="16" height="12" fill="#D8433B"/>`; }
  return lap4(s);
}
function vachTile(ray) {
  let s = '';
  if (ray) for (let i = 0; i < 18; i++) s += `<rect x="${i * 60}" y="1218" width="26" height="16" rx="3" fill="#4a3b2e"/>`;
  else for (let i = 0; i < 6; i++) s += `<rect x="${i * 180}" y="1168" width="96" height="10" rx="5" fill="#F2EFE6"/>`;
  return lap4(s);
}
function songTile(seed) {                            // gợn sóng: hàng xa nhỏ + chậm, hàng gần to + nhanh (mỗi hàng 1 nhóm)
  const hang = [];
  for (let k = 0; k < 7; k++) {
    const y = 1030 + k * k * 18 + k * 30, a = 2 + k * 2.2, L = 60 + k * 26;
    let s = '';
    for (let i = 0; i < 1080 / L + 1; i++) {
      if (hash01(seed + k * 31 + i) < .45) continue;
      const x = i * L + hash01(seed + i * 7 + k) * L * .4;
      s += `<path d="M${f1(x)} ${y} q${f1(L * .25)} ${f1(-a)} ${f1(L * .5)} 0 t${f1(L * .5)} 0" fill="none" stroke="rgba(255,255,255,${(.10 + k * .035).toFixed(3)})" stroke-width="${f1(1.5 + k * .7)}" stroke-linecap="round"/>`;
    }
    hang.push({ s: lap4(s), v: 18 + k * k * 9 });
  }
  return hang;
}

/* ---- phương tiện vẽ to (nhìn ngang, mũi sang phải): {w, h, html, banh: [[cx, cy, r]], day (đáy bánh / mớn nước)} ---- */
function xeLon(pt, u) {
  const vanh = (cx, cy, r) => {   // bánh xe: lốp + mâm 5 chấu (xoay được)
    let sp = '';
    for (let k = 0; k < 5; k++) { const a = k * Math.PI * 2 / 5; sp += `<path d="M${cx} ${cy}L${f1(cx + Math.cos(a) * r * .58)} ${f1(cy + Math.sin(a) * r * .58)}" stroke="#5f6770" stroke-width="${f1(r * .12)}" stroke-linecap="round"/>`; }
    return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#14161a"/><g class="banh" data-c="${cx},${cy},${r}"><circle cx="${cx}" cy="${cy}" r="${f1(r * .64)}" fill="url(#mam${u})"/>${sp}<circle cx="${cx}" cy="${cy}" r="${f1(r * .14)}" fill="#2b3036"/></g>`;
  };
  const mam = `<radialGradient id="mam${u}"><stop offset="0" stop-color="#f4f6f8"/><stop offset=".7" stop-color="#a3acb6"/><stop offset="1" stop-color="#5b636c"/></radialGradient>`;
  const kinh = `<linearGradient id="kinh${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a9cbe8"/><stop offset=".45" stop-color="#2d405a"/><stop offset="1" stop-color="#121b28"/></linearGradient>`;
  const vang = `<linearGradient id="vg${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE3A3"/><stop offset=".5" stop-color="#F4C66A"/><stop offset="1" stop-color="#C68A2E"/></linearGradient>`;
  if (pt === 'may_bay') {
    let cs = '';
    for (let x = 236; x < 640; x += 21) if (x < 650 && Math.abs(x - 660) > 24) cs += `<rect x="${x}" y="124" width="10" height="13" rx="4"/>`;
    return { w: 800, h: 260, html: `<defs>${vang}
      <linearGradient id="than${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#eef2f6"/><stop offset="1" stop-color="#aab6c4"/></linearGradient>
      <linearGradient id="canh${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2e7ec"/><stop offset="1" stop-color="#8994a3"/></linearGradient>
      <linearGradient id="dc${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#edf1f5"/><stop offset="1" stop-color="#7d8999"/></linearGradient></defs>
      <path d="M440 110 L536 66 L562 66 L478 114Z" fill="#c4ccd6"/>
      <path d="M162 112 L88 20 L44 20 L80 120Z" fill="url(#vg${u})"/>
      <path d="M112 120 L62 102 L48 104 L86 124Z" fill="#c4ccd6"/>
      <path d="M64 122 L150 108 L640 106 C712 106 758 122 780 146 C772 166 738 180 690 182 L178 182 C134 182 96 166 64 132Z" fill="url(#than${u})"/>
      <path d="M96 150 C120 168 146 182 178 182 L690 182 C730 181 760 170 776 156 C740 166 700 170 660 170 L190 170 C150 170 120 160 96 150Z" fill="#0b1626" opacity=".10"/>
      <path d="M118 150 L700 150 C735 150 760 154 772 158" stroke="url(#vg${u})" stroke-width="7" fill="none"/>
      <path d="M120 160 L690 160" stroke="#C68A2E" stroke-width="2" opacity=".55" fill="none"/>
      <g fill="#22324a">${cs}</g>
      <path d="M712 122 L744 128 C752 132 756 136 758 140 L718 138Z" fill="#1b2638"/>
      <rect x="652" y="116" width="18" height="44" rx="5" fill="none" stroke="#9aa6b4" stroke-width="2"/>
      <rect x="206" y="116" width="18" height="44" rx="5" fill="none" stroke="#9aa6b4" stroke-width="2"/>
      <path d="M152 146 L72 168 L58 166 L106 140Z" fill="url(#canh${u})"/>
      <path d="M430 186 L446 168 L476 168 L470 186Z" fill="#b7c0cb"/>
      <path d="M506 160 L344 244 L302 247 L412 162Z" fill="url(#canh${u})"/>
      <path d="M344 244 L302 247 L306 236 L350 233Z" fill="url(#vg${u})"/>
      <rect x="376" y="184" width="120" height="42" rx="21" fill="url(#dc${u})"/>
      <ellipse cx="494" cy="205" rx="9" ry="20" fill="#1d242e"/><ellipse cx="492" cy="205" rx="4" ry="12" fill="#5d6b7c"/>
      <rect x="362" y="194" width="20" height="22" rx="9" fill="#5d6b7c"/>`, banh: [], day: 250, vet: [[364, 205], [304, 242]] };
  }
  if (pt === 'o_to') return { w: 540, h: 222, day: 214, banh: [[130, 170, 44], [420, 170, 44]], html: `<defs>${mam}${kinh}
      <linearGradient id="than${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff6b6f"/><stop offset=".45" stop-color="#d0263a"/><stop offset="1" stop-color="#76101e"/></linearGradient></defs>
      <ellipse cx="275" cy="214" rx="252" ry="9" fill="#000" opacity=".35"/>
      <path d="M22 158 L22 124 Q24 108 44 104 L118 98 L170 56 Q182 46 204 46 L296 46 Q316 46 332 58 L392 100 L492 108 Q518 112 522 132 L524 158 Q524 168 512 168 L470 168 A50 50 0 0 0 370 168 L180 168 A50 50 0 0 0 80 168 L34 168 Q22 168 22 158Z" fill="url(#than${u})"/>
      <path d="M144 96 L180 62 Q188 55 204 55 L254 55 L254 96Z" fill="url(#kinh${u})"/>
      <path d="M264 55 L298 55 Q312 55 324 64 L366 96 L264 96Z" fill="url(#kinh${u})"/>
      <path d="M46 112 L508 116" stroke="#fff" stroke-opacity=".35" stroke-width="3"/>
      <path d="M392 102 Q450 104 500 110" stroke="#fff" stroke-opacity=".22" stroke-width="2" fill="none"/>
      <path d="M259 100 L259 160 M374 102 Q380 130 372 160 M140 100 L138 160" stroke="#4a0812" stroke-width="2" opacity=".55" fill="none"/>
      <rect x="282" y="116" width="24" height="5" rx="2.5" fill="#3b0710" opacity=".7"/><rect x="168" y="116" width="24" height="5" rx="2.5" fill="#3b0710" opacity=".7"/>
      <path d="M356 90 L382 84 Q388 84 388 90 L386 98 L362 99Z" fill="#9d1a2c"/>
      <path d="M496 114 L520 118 Q524 126 520 128 L498 126Z" fill="#fff6d0"/><rect x="510" y="138" width="14" height="8" rx="3" fill="#3b0710" opacity=".6"/>
      <rect x="22" y="112" width="13" height="16" rx="4" fill="#ff3b3b"/>
      ${vanh(130, 170, 44)}${vanh(420, 170, 44)}` };
  if (pt === 'xe_may') return { w: 400, h: 316, day: 312, banh: [[78, 270, 42], [318, 270, 42]], html: `<defs>${mam}${vang}
      <linearGradient id="than${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3fd0c8"/><stop offset="1" stop-color="#147a76"/></linearGradient>
      <linearGradient id="ao${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4b6fb0"/><stop offset="1" stop-color="#253c6b"/></linearGradient></defs>
      <ellipse cx="200" cy="312" rx="180" ry="7" fill="#000" opacity=".35"/>
      ${vanh(78, 270, 42)}${vanh(318, 270, 42)}
      <path d="M28 252 Q28 206 84 200 L214 196 Q244 196 256 222 L266 252Z" fill="url(#than${u})"/>
      <rect x="150" y="240" width="128" height="16" rx="8" fill="#2a2f36"/>
      <path d="M262 254 L302 132 L326 136 L300 254Z" fill="url(#than${u})"/>
      <path d="M280 240 Q318 206 358 240 L352 248 Q318 224 288 248Z" fill="url(#than${u})"/>
      <rect x="292" y="118" width="48" height="10" rx="5" fill="#22262c" transform="rotate(-8 316 123)"/>
      <circle cx="330" cy="152" r="11" fill="#fff6d0"/>
      <path d="M86 198 Q96 178 150 180 L206 184 Q216 194 204 200 L92 202Z" fill="#23262b"/>
      <path d="M140 188 L226 200 L232 246" stroke="#2d3a55" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M222 248 L258 250" stroke="#16191d" stroke-width="16" stroke-linecap="round"/>
      <path d="M152 188 L178 100" stroke="url(#ao${u})" stroke-width="58" stroke-linecap="round"/>
      <path d="M184 112 L242 140 L302 126" stroke="url(#ao${u})" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="304" cy="126" r="11" fill="#e3ad84"/>
      <circle cx="186" cy="58" r="36" fill="url(#vg${u})"/><path d="M198 44 Q228 50 222 76 L196 74Z" fill="#1d2633"/>` };
  if (pt === 'xe_dap') return { w: 400, h: 324, day: 318, banh: [[80, 256, 62], [300, 256, 62]], html: `<defs>${mam}${vang}
      <linearGradient id="ao${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f08a4b"/><stop offset="1" stop-color="#b6481c"/></linearGradient></defs>
      <ellipse cx="190" cy="318" rx="170" ry="6" fill="#000" opacity=".35"/>
      <circle cx="80" cy="256" r="62" fill="none" stroke="#14161a" stroke-width="9"/><circle cx="300" cy="256" r="62" fill="none" stroke="#14161a" stroke-width="9"/>
      <g class="banh" data-c="80,256,62">${[0, 1, 2, 3, 4, 5].map(k => `<path d="M80 256 l${f1(Math.cos(k * 1.047) * 56)} ${f1(Math.sin(k * 1.047) * 56)}" stroke="#9aa3ad" stroke-width="2.5"/>`).join('')}</g>
      <g class="banh" data-c="300,256,62">${[0, 1, 2, 3, 4, 5].map(k => `<path d="M300 256 l${f1(Math.cos(k * 1.047) * 56)} ${f1(Math.sin(k * 1.047) * 56)}" stroke="#9aa3ad" stroke-width="2.5"/>`).join('')}</g>
      <path d="M80 256 L150 170 L270 170 L300 256 M150 170 L190 256 L270 170 M190 256 L80 256 M260 140 L270 170 M244 136 L282 136 M140 160 L170 160" stroke="url(#vg${u})" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M156 160 L208 210 L196 250" stroke="#2d3a55" stroke-width="24" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M158 160 L196 84" stroke="url(#ao${u})" stroke-width="52" stroke-linecap="round"/>
      <path d="M200 96 L262 138" stroke="url(#ao${u})" stroke-width="20" stroke-linecap="round"/><circle cx="264" cy="138" r="10" fill="#e3ad84"/>
      <circle cx="210" cy="50" r="30" fill="#e3ad84"/><path d="M180 44 Q190 14 226 20 Q244 26 242 46Z" fill="url(#vg${u})"/>` };
  if (pt === 'xe_buyt') {
    let cs = '';
    for (let x = 56; x < 620; x += 82) cs += `<rect x="${x}" y="62" width="70" height="72" rx="10" fill="url(#kinh${u})"/>`;
    return { w: 760, h: 264, day: 258, banh: [[150, 218, 40], [600, 218, 40]], html: `<defs>${mam}${kinh}${vang}
      <linearGradient id="than${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#e3e7ec"/><stop offset="1" stop-color="#a7b0bb"/></linearGradient></defs>
      <ellipse cx="380" cy="258" rx="360" ry="8" fill="#000" opacity=".35"/>
      <path d="M14 214 L14 56 Q14 30 42 30 L690 30 Q722 30 734 58 L752 140 L752 214 Q752 222 742 222 L650 222 A50 50 0 0 0 550 222 L200 222 A50 50 0 0 0 100 222 L24 222 Q14 222 14 214Z" fill="url(#than${u})"/>
      ${cs}<path d="M690 44 Q716 44 724 64 L742 138 L690 138Z" fill="url(#kinh${u})"/>
      <rect x="640" y="62" width="40" height="140" rx="6" fill="none" stroke="#9aa6b4" stroke-width="3"/>
      <path d="M14 160 L752 160" stroke="url(#vg${u})" stroke-width="16"/><path d="M14 176 L752 176" stroke="#C68A2E" stroke-width="3"/>
      <rect x="728" y="186" width="20" height="14" rx="5" fill="#fff6d0"/><rect x="14" y="186" width="12" height="18" rx="4" fill="#ff3b3b"/>
      ${vanh(150, 218, 40)}${vanh(600, 218, 40)}` };
  }
  if (pt === 'tau_hoa') {
    const toa = (x0, w, dau) => {
      let cs = '';
      for (let x = x0 + 26; x < x0 + w - 60; x += 58) cs += `<rect x="${x}" y="70" width="44" height="46" rx="8" fill="url(#kinh${u})"/>`;
      const than = dau ? `<path d="M${x0} 192 L${x0} 52 Q${x0} 36 ${x0 + 16} 36 L${x0 + w - 110} 36 Q${x0 + w - 40} 40 ${x0 + w} 150 L${x0 + w} 192Z" fill="url(#than${u})"/>
        <path d="M${x0 + w - 104} 46 Q${x0 + w - 52} 50 ${x0 + w - 24} 112 L${x0 + w - 104} 112Z" fill="url(#kinh${u})"/>`
        : `<rect x="${x0}" y="36" width="${w}" height="156" rx="16" fill="url(#than${u})"/>`;
      let bx = '';
      for (const c of [x0 + 50, x0 + 96, x0 + w - 96, x0 + w - 50]) bx += vanh(c, 200, 18);
      return than + cs + `<path d="M${x0} 140 L${x0 + w} 140" stroke="url(#vg${u})" stroke-width="12"/>` + bx;
    };
    return { w: 1000, h: 222, day: 218, banh: [], html: `<defs>${mam}${kinh}${vang}
      <linearGradient id="than${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5f7fa"/><stop offset=".7" stop-color="#cfd6de"/><stop offset="1" stop-color="#8f9aa6"/></linearGradient></defs>
      ${toa(0, 300, false)}${toa(310, 300, false)}${toa(620, 380, true)}`, tat_ca_banh: true };
  }
  if (pt === 'tau_thuy') return { w: 640, h: 440, day: 340, banh: [], html: `<defs>
      <linearGradient id="go${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a5f33"/><stop offset="1" stop-color="#3e220f"/></linearGradient>
      <linearGradient id="buom${u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e9874a"/><stop offset="1" stop-color="#8f3a16"/></linearGradient></defs>
      <path d="M300 300 L300 34 M440 296 L440 70 M170 300 L170 96" stroke="#3a2412" stroke-width="7"/>
      <path d="M308 290 Q336 160 312 42 Q388 64 432 78 Q452 190 430 290Z" fill="url(#buom${u})"/>
      <path d="M448 286 Q470 190 450 80 Q510 104 548 124 Q560 210 540 286Z" fill="url(#buom${u})"/>
      <path d="M178 292 Q198 200 180 104 Q236 120 268 134 Q284 214 270 292Z" fill="url(#buom${u})"/>
      ${[0, 1, 2, 3, 4, 5].map(k => `<path d="M${312 + k * 2} ${70 + k * 40} Q372 ${80 + k * 40} ${434 - k} ${86 + k * 40}" stroke="#5a2a10" stroke-width="3" fill="none" opacity=".7"/>`).join('')}
      <rect x="150" y="262" width="330" height="44" rx="8" fill="#c99a62"/><rect x="170" y="272" width="290" height="22" rx="4" fill="#2b1b10"/>
      <path d="M20 300 Q60 296 110 302 L540 298 Q590 294 624 262 L612 324 Q582 372 490 380 L150 384 Q66 380 20 300Z" fill="url(#go${u})"/>
      <path d="M40 316 L604 306" stroke="#f1c27d" stroke-width="5" opacity=".75"/>` };
  return null;
}

/* ---- nền tự vẽ: trả về {el, ve(t, TG, kp)} ---- */
function nenTroi(host, u, d) {
  const n = mk('div', 'htn troi', host);
  mk('div', 'mt', n);
  n.insertAdjacentHTML('beforeend', `<svg width="1080" height="1920"><defs>
      <linearGradient id="mx${u}" x1="0" y1="440" x2="0" y2="620" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f4f7fb"/><stop offset="1" stop-color="#b7c5da"/></linearGradient>
      <linearGradient id="mg${u}" x1="0" y1="1010" x2="0" y2="1235" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#fdf2e8"/><stop offset="1" stop-color="#e6c0a2"/></linearGradient></defs>
    <g class="l1" fill="url(#mx${u})" opacity=".55" style="filter:blur(2px)">${mayTile(11, 4, 560, 160, 40, 72)}</g>
    <g class="l2" fill="url(#mg${u})" opacity=".85">${mayTile(23, 3, 1150, 140, 70, 110)}</g></svg>`);
  const xe = xeLon('may_bay', u), w = 840, k = w / xe.w;
  const hero = mk('div', 'xe', n, `<svg width="${w}" height="${f1(xe.h * k)}" viewBox="0 0 ${xe.w} ${xe.h}">${xe.html}</svg>`);
  const vets = xe.vet.map(([x, y]) => { const v = mk('div', 'vet', hero); css(v, { left: (x * k - 1200) + 'px', top: (y * k - 6) + 'px', width: '1200px' }); return v; });
  n.insertAdjacentHTML('beforeend', `<svg width="1080" height="1920"><defs>
      <linearGradient id="mb${u}" x1="0" y1="1250" x2="0" y2="1530" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f0d4bf"/></linearGradient>
      <linearGradient id="mn${u}" x1="0" y1="1380" x2="0" y2="1920" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f3dcc8"/><stop offset="1" stop-color="#9c8476"/></linearGradient></defs>
    <g class="l3"><rect x="-1080" y="1440" width="4320" height="480" fill="url(#mn${u})"/><g fill="url(#mb${u})">${mayTile(37, 6, 1430, 60, 120, 190)}</g></g>
    <g class="l4" fill="#ffffff" opacity=".42" style="filter:blur(5px)">${mayTile(53, 1, 1080, 200, 150, 190)}</g></svg>`);
  mk('div', 'toi_duoi', n);
  const L = [['.l1', 20], ['.l2', 64], ['.l3', 150], ['.l4', 430]].map(([s, v]) => ({ g: n.querySelector(s), v }));
  return {
    el: n,
    ve(t, TG) {
      for (const o of L) o.g.setAttribute('transform', `translate(${f1(-md(o.v * TG, 1080))} 0)`);
      const kv = E.outC(clamp((TG - .1) / 1.5)), dur = d.den - d.tu;
      const x = 120 + lerp(-1100, 0, kv) + 50 * (TG / dur - .5), y = 840 + 16 * Math.sin(TG * 2 * Math.PI / 3.4);
      css(hero, { transform: `translate(${f1(x)}px, ${f1(y)}px) rotate(${(-5 + 1.4 * Math.sin(TG * 2 * Math.PI / 4.1)).toFixed(2)}deg)` });
      const kl = clamp((TG - .3) / 1.6);
      for (const v of vets) css(v, { transform: `scaleX(${kl.toFixed(3)})`, opacity: (.85 * kl).toFixed(3) });
    },
  };
}
function nenDuong(host, u, d, pt) {
  const n = mk('div', 'htn duong', host), xa = d.canh_xa || 'doi';
  const m = mk('div', 'mt', n); css(m, { left: '300px', top: '930px' });
  const ray = pt === 'tau_hoa';
  n.insertAdjacentHTML('beforeend', `<svg width="1080" height="1920"><defs>
      <linearGradient id="nx${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8098b6"/><stop offset="1" stop-color="#aebdcc"/></linearGradient>
      <linearGradient id="nv${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4d6c84"/><stop offset="1" stop-color="#6c8696"/></linearGradient>
      <linearGradient id="dg${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${ray ? '#6b6155' : '#444a53'}"/><stop offset="1" stop-color="${ray ? '#4a4239' : '#262a30'}"/></linearGradient>
      <linearGradient id="dt${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c4326"/><stop offset=".35" stop-color="#1b2a18"/><stop offset="1" stop-color="#080c07"/></linearGradient></defs>
    <g class="l1" fill="url(#nx${u})" opacity=".85">${xa === 'nui' ? nuiTile(17, 1012, 120, 300, 300) : xa === 'thanh_pho' ? phoTile(17, 1040, 90, 330, 'rgba(255,236,190,.35)') : doiTile(17, 1030, 60, 150, 420)}</g>
    <g class="l2" fill="url(#nv${u})">${xa === 'nui' ? nuiTile(41, 1044, 60, 170, 220) : xa === 'thanh_pho' ? phoTile(41, 1060, 40, 140, null) : doiTile(41, 1052, 30, 80, 300)}</g>
    <g class="l3" fill="#30503a">${cayTile(73, 1064)}</g>
    <rect x="0" y="1058" width="1080" height="40" fill="#3f5e35"/>
    <rect x="0" y="1094" width="1080" height="160" fill="url(#dg${u})"/>
    ${ray ? '<rect x="0" y="1226" width="1080" height="9" fill="#a9b1ba"/>' : '<rect x="0" y="1094" width="1080" height="6" fill="#d9d4c8"/><rect x="0" y="1246" width="1080" height="6" fill="#d9d4c8" opacity=".8"/>'}
    <g class="l4">${vachTile(ray)}</g>
    <rect x="0" y="1252" width="1080" height="668" fill="url(#dt${u})"/>
    <g class="l5">${coTile(91)}</g></svg>`);
  const xe = xeLon(pt, u);
  let hero = null, banh = [], k = 1, top = 0;
  if (xe) {
    const w = { o_to: 600, xe_may: 400, xe_dap: 390, xe_buyt: 780, tau_hoa: 1000 }[pt] || 600;
    k = w / xe.w; top = 1232 - xe.day * k;
    hero = mk('div', 'xe', n, `<svg width="${w}" height="${f1(xe.h * k)}" viewBox="0 0 ${xe.w} ${xe.h}">${xe.html}</svg>`);
    banh = Array.from(hero.querySelectorAll('.banh')).map(g => { const [cx, cy, r] = g.dataset.c.split(',').map(Number); return { g, cx, cy, r }; });
  }
  const VD = 640;   // tốc độ mặt đường px/s
  const L = [['.l1', 12], ['.l2', 40], ['.l3', 150], ['.l4', VD], ['.l5', VD * 1.5]].map(([s, v]) => ({ g: n.querySelector(s), v }));
  return {
    el: n,
    ve(t, TG) {
      for (const o of L) o.g.setAttribute('transform', `translate(${f1(-md(o.v * TG, 1080))} 0)`);
      if (!hero) return;
      const kv = E.outC(clamp((TG - .1) / 1.3)), w = xe.w * k;
      const x = 540 - w / 2 + lerp(-1200, 0, kv) + 26 * Math.sin(TG * .9), y = top + 2.2 * Math.sin(TG * 2 * Math.PI * 3.1) * (pt === 'tau_hoa' ? .4 : 1);
      css(hero, { transform: `translate(${f1(x)}px, ${f1(y)}px)` });
      for (const b of banh) b.g.setAttribute('transform', `rotate(${f1(md(VD * TG / (b.r * k) * 57.2958, 360))} ${b.cx} ${b.cy})`);
    },
  };
}
function nenBien(host, u, d) {
  const n = mk('div', 'htn bien', host);
  const m = mk('div', 'mt', n); css(m, { left: '760px', top: '930px' });
  const hang = songTile(29);
  n.insertAdjacentHTML('beforeend', `<svg width="1080" height="1920"><defs>
      <linearGradient id="nx${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6d7d99"/><stop offset="1" stop-color="#9aa3b3"/></linearGradient>
      <linearGradient id="nv${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34465c"/><stop offset="1" stop-color="#4b5d70"/></linearGradient>
      <linearGradient id="nc${u}" x1="0" y1="1000" x2="0" y2="1920" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#7f97ad"/><stop offset=".3" stop-color="#2f5671"/><stop offset="1" stop-color="#08192a"/></linearGradient>
      <radialGradient id="pc${u}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd59a" stop-opacity=".75"/><stop offset="1" stop-color="#ffd59a" stop-opacity="0"/></radialGradient></defs>
    <g class="l1" fill="url(#nx${u})" opacity=".9">${nuiTile(57, 1004, 140, 330, 260)}</g>
    <rect x="0" y="1000" width="1080" height="920" fill="url(#nc${u})"/>
    <ellipse cx="760" cy="1180" rx="70" ry="190" fill="url(#pc${u})"/>
    <g class="l2" fill="url(#nv${u})">${nuiTile(83, 1016, 90, 250, 330)}</g>
    ${hang.map((h, i) => `<g class="s${i}">${h.s}</g>`).join('')}</svg>`);
  const xe = xeLon('tau_thuy', u), w = 640, k = w / xe.w;
  const hero = mk('div', 'xe', n, `<svg width="${w}" height="${f1(xe.h * k)}" viewBox="0 0 ${xe.w} ${xe.h}">${xe.html}</svg>`);
  const bot = Array.from({ length: 6 }, () => mk('div', 'bot', n));
  mk('div', 'toi_duoi', n);
  const L = [['.l1', 8], ['.l2', 26]].map(([s, v]) => ({ g: n.querySelector(s), v })).concat(hang.map((h, i) => ({ g: n.querySelector('.s' + i), v: h.v })));
  return {
    el: n,
    ve(t, TG) {
      for (const o of L) o.g.setAttribute('transform', `translate(${f1(-md(o.v * TG, 1080))} 0)`);
      const kv = E.outC(clamp((TG - .1) / 1.6));
      const x = 540 - w / 2 + lerp(-1000, 0, kv) + 20 * Math.sin(TG * .7), y = 1188 - xe.day * k + 7 * Math.sin(TG * 2 * Math.PI / 2.6);
      css(hero, { transform: `translate(${f1(x)}px, ${f1(y)}px) rotate(${(1.8 * Math.sin(TG * 2 * Math.PI / 3.1)).toFixed(2)}deg)` });
      bot.forEach((b, i) => {       // bọt nước sau đuôi thuyền trôi về trái, tan dần
        const ph = md(TG * .9 + i / 6, 1);
        css(b, { left: f1(x + 30 - ph * 420) + 'px', top: f1(1176 + i % 3 * 8) + 'px', opacity: (.8 * (1 - ph) * kv).toFixed(3), transform: `scale(${(.6 + ph * 1.6).toFixed(3)}, ${(.6 + ph * .5).toFixed(3)})` });
      });
    },
  };
}
function nenBanDo(host, u, d, pt) {
  const n = mk('div', 'htn ban_do', host);
  const G = 120;
  let s = '';
  for (let gx = -1; gx < 10; gx++) for (let gy = 0; gy < 17; gy++) {
    const x = gx * G, y = gy * G - 20, h = hash01(gx * 13.1 + gy * 7.7 + 3);
    s += `<rect x="${x + 12}" y="${y + 12}" width="${G - 24}" height="${G - 24}" rx="10" fill="${h < .09 ? '#16301f' : '#19202a'}"/>`;
    if (h > .55) s += `<path d="M${x + G / 2} ${y + 14}V${y + G - 14}" stroke="#12171e" stroke-width="5"/>`;
    else if (h > .3) s += `<path d="M${x + 14} ${y + G / 2}H${x + G - 14}" stroke="#12171e" stroke-width="5"/>`;
  }
  for (const yy of [340, 700, 1180, 1540]) s += `<rect x="0" y="${yy - 14}" width="1080" height="28" fill="#28303c"/>`;
  for (const xx of [240, 600, 840]) s += `<rect x="${xx - 14}" y="0" width="28" height="1920" fill="#28303c"/>`;
  const A = [240, 1180], B = [840, 820];
  const ho = (cx, cy) => `<path d="M${cx - 150} ${cy} C${cx - 150} ${cy - 70},${cx - 60} ${cy - 96},${cx + 20} ${cy - 88} C${cx + 110} ${cy - 80},${cx + 160} ${cy - 30},${cx + 140} ${cy + 26} C${cx + 120} ${cy + 80},${cx + 30} ${cy + 92},${cx - 50} ${cy + 84} C${cx - 120} ${cy + 76},${cx - 150} ${cy + 40},${cx - 150} ${cy}Z" fill="#1c4064" stroke="#2d5c88" stroke-width="3"/>`;
  if (d.ho_tai === 'di') s += ho(A[0] + 10, A[1] - 118);
  else s += `<rect x="372" y="972" width="196" height="176" rx="14" fill="#17301f"/>`;
  if (d.ho_tai === 'den') s += ho(B[0] - 150, B[1] - 40);
  else s += `<rect x="626" y="752" width="190" height="156" rx="14" fill="#17301f"/>`;
  const D = `M240 1180 L572 1180 Q600 1180 600 1152 L600 968 Q600 940 628 940 L812 940 Q840 940 840 912 L840 820`;
  n.insertAdjacentHTML('beforeend', `<svg class="bd" width="1080" height="1920"><defs>
      <linearGradient id="rg${u}" x1="0" x2="1"><stop offset="0" stop-color="#FFE3A3"/><stop offset="1" stop-color="#E9AE4B"/></linearGradient></defs>${s}
    <path d="${D}" fill="none" stroke="rgba(244,198,106,.16)" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
    <path class="r_sang" d="${D}" fill="none" stroke="url(#rg${u})" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 10px rgba(244,198,106,.7))"/></svg>`);
  const sang = n.querySelector('.r_sang');
  const cham = mk('div', 'cham', n); css(cham, { left: A[0] + 'px', top: A[1] + 'px' });
  const ghim = mk('div', 'ghim_lon', n, icon('ghim')); css(ghim, { left: (B[0] - 48) + 'px', top: (B[1] - 88) + 'px' });
  const tagA = mk('div', 'tag', n, esc(d.xuat_phat.ten)), tagB = mk('div', 'tag vang', n, esc(d.diem_den.ten));
  const dot = pt === 'khong' ? mk('div', 'dau_sang', n) : mk('div', 'xe_nho', n, `<div class="ic">${icon(IC_PT[pt] || 'ghim')}</div>`);
  mk('div', 'toi_duoi', n);
  let LUT = null, Lr = 0;
  return {
    el: n,
    sau() {
      Lr = sang.getTotalLength(); sang.style.strokeDasharray = Lr; LUT = [];
      for (let i = 0; i <= 160; i++) { const p = sang.getPointAtLength(Lr * i / 160); LUT.push([p.x, p.y]); }
      css(tagA, { left: f1(A[0] - rong(tagA) / 2 - 26) + 'px', top: (A[1] + 34) + 'px' });
      css(tagB, { left: f1(Math.min(1080 - 60 - rong(tagB) - 52, B[0] - rong(tagB) / 2 - 26)) + 'px', top: (B[1] - 176) + 'px' });
    },
    ve(t, TG, kp, kden) {
      css(n, { transform: `scale(${(1.0 + .05 * clamp(TG / Math.max(1, d.den - d.tu))).toFixed(4)})` });
      sang.style.strokeDashoffset = f1(Lr * (1 - kp));
      const p = LUT[Math.round(kp * 160)];
      css(dot, { left: f1(p[0]) + 'px', top: f1(p[1]) + 'px', opacity: (P(t, d.luc_di - .3, .3) * (1 - P(t, d.luc_den - .05, .3))).toFixed(3) });
      const kg = P(t, d.luc_den - .05, .55, E.drop);
      css(ghim, { opacity: clamp(kg * 3).toFixed(3), transform: `translateY(${f1(-110 * (1 - kg))}px)` });
      css(tagA, { opacity: P(t, d.tu + .35, .4).toFixed(3) });
      css(tagB, { opacity: P(t, d.luc_den + .15, .4).toFixed(3), transform: `translateY(${f1(20 * (1 - P(t, d.luc_den + .15, .4)))}px)` });
    },
  };
}

/* ---- nền BẢN ĐỒ THẬT (nen "that"): ảnh vệ tinh Esri + đường đi thật + camera bay (camera từng khung tính sẵn ở ban_do_that.py).
   Ô ảnh nạp theo nhu cầu: __seek chờ ô của khung đó decode xong (CHO) rồi mới vẽ canvas (VE_SAU); ô lâu không dùng thì nhả. ---- */
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
  if (ANH_O.size < 700) return;
  for (const [k, o] of ANH_O) if (KHUNG_SO - o.dung > 40) { o.im.src = ''; ANH_O.delete(k); }
}
const MAY_BAY_TREN = `<svg viewBox="0 0 100 100"><defs><linearGradient id="mbg" x1="0" x2="1"><stop offset="0" stop-color="#E9EDF2"/><stop offset=".5" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D5DBE3"/></linearGradient></defs>
  <path d="M50 2C55 2 57 9 57 17L57 36L95 57L95 66L57 55L56 79L69 89L69 95L50 90L31 95L31 89L44 79L43 55L5 66L5 57L43 36L43 17C43 9 45 2 50 2Z" fill="url(#mbg)" stroke="rgba(30,40,55,.45)" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M50 8V86" stroke="rgba(30,40,55,.18)" stroke-width="2"/><circle cx="50" cy="12" r="3.2" fill="#22324a"/></svg>`;
function nenThat(host, u, d, pt) {
  const n = mk('div', 'htn that', host);
  const bd = d.bd;
  if (!bd || !bd.cam || !bd.cam.length) { console.error('hành trình ' + d.id + ': thiếu bản đồ thật (bd)'); return null; }
  const cv = mk('canvas', 'bd_cv', n); cv.width = 1080; cv.height = 1920;
  const g = cv.getContext('2d'); g.imageSmoothingQuality = 'high';
  mk('div', 'toi_vien', n);
  const R = bd.duong, FY = bd.foc_y || 945;
  const cum = [0];
  for (let i = 1; i < R.length; i++) cum.push(cum[i - 1] + Math.hypot(R[i][0] - R[i - 1][0], R[i][1] - R[i - 1][1]));
  const LT = cum[cum.length - 1] || 1e-9;
  const may = pt === 'may_bay';
  n.insertAdjacentHTML('beforeend', `<svg class="tuyen_bd" width="1080" height="1920"><defs>
      <linearGradient id="rgt${u}" x1="0" x2="1"><stop offset="0" stop-color="#FFE3A3"/><stop offset="1" stop-color="#E9AE4B"/></linearGradient></defs>
    <path class="vien" fill="none" stroke="rgba(6,8,12,.5)" stroke-width="${may ? 0 : 20}" stroke-linecap="round" stroke-linejoin="round"/>
    <path class="mo" fill="none" stroke="${may ? 'rgba(255,255,255,.75)' : 'rgba(255,240,215,.55)'}" stroke-width="${may ? 5 : 8}" stroke-linecap="round" stroke-linejoin="round" ${may ? 'stroke-dasharray="2 16"' : ''}/>
    <path class="sang" fill="none" stroke="url(#rgt${u})" stroke-width="${may ? 9 : 11}" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 10px rgba(244,198,106,.85))"/></svg>`);
  const pVien = n.querySelector('.vien'), pMo = n.querySelector('.mo'), pSang = n.querySelector('.sang');
  // nhãn phụ (quốc gia / thành phố quanh tuyến) — chỉ rõ lúc nhìn toàn tuyến
  const phu = (bd.phu || []).map(([x, y, ten]) => ({ x, y, el: mk('div', 'phu_bd', n, esc(ten)) }));
  const anhDi = d.xuat_phat.anh_url ? mk('div', 'anh_ghim', n, `<img src="${esc(d.xuat_phat.anh_url)}">`) : null;
  const anhDen = d.diem_den.anh_url ? mk('div', 'anh_ghim', n, `<img src="${esc(d.diem_den.anh_url)}">`) : null;
  const songA = mk('div', 'vong_lan', n), cham = mk('div', 'cham', n);
  const dich = mk('div', 'dich', n), vongB = mk('div', 'vong_lan', n);
  const ghim = mk('div', 'ghim_lon', n, icon('ghim'));
  const tagA = mk('div', 'tag', n, esc(d.xuat_phat.ten)), tagB = mk('div', 'tag vang', n, esc(d.diem_den.ten));
  const kcEl = d.thoi_gian && d.khoang_cach ? mk('div', 'kc_bd', n, `${icon('ban_do')}<span>${esc(d.khoang_cach)}</span>`) : null;
  const xe = may ? mk('div', 'mb', n, MAY_BAY_TREN)
    : pt === 'khong' ? mk('div', 'dau_sang', n) : mk('div', 'xe_nho', n, `<div class="ic">${icon(IC_PT[pt] || 'ghim')}</div>`);
  mk('div', 'toi_duoi', n);
  const camTai = t => {
    const f = clamp((t - d.tu) * 30, 0, bd.cam.length - 1), i = Math.floor(f), j = Math.min(bd.cam.length - 1, i + 1), k = f - i;
    const a = bd.cam[i], b = bd.cam[j];
    return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
  };
  const diemTai = kp => {                         // vị trí + hướng trên tuyến (chuẩn hoá Mercator)
    const L = kp * LT;
    let i = 1; while (i < cum.length - 1 && cum[i] < L) i++;
    const a = R[i - 1], b = R[i], s = cum[i] - cum[i - 1], k = s > 0 ? (L - cum[i - 1]) / s : 0;
    let j = i; while (j < R.length - 1 && Math.hypot(R[j][0] - a[0], R[j][1] - a[1]) < LT * .004) j++;
    const q = R[j];
    return { i, x: lerp(a[0], b[0], k), y: lerp(a[1], b[1], k), goc: Math.atan2(q[1] - a[1], q[0] - a[0]) };
  };
  const dat = (el, x, y) => css(el, { left: f1(x) + 'px', top: f1(y) + 'px' });
  const tDen = d.luc_ten_den != null ? d.luc_ten_den : d.luc_den - .35;
  const tDi = d.luc_ten_di != null ? d.luc_ten_di : d.tu + .35;
  let wA = 0, hA = 0, wB = 0, hB = 0, wK = 0;
  return {
    el: n,
    sau() { wA = tagA.offsetWidth; hA = tagA.offsetHeight; wB = tagB.offsetWidth; hB = tagB.offsetHeight; if (kcEl) wK = kcEl.offsetWidth; },
    ve(t, TG, kp) {
      const [fx, fy, z] = camTai(t), sc = 256 * Math.pow(2, z);
      const P2 = (x, y) => [(x - fx) * sc + 540, (y - fy) * sc + FY];
      // ô ảnh: mức lót (−2) rồi mức chính
      const L = Math.max(1, Math.min(18, Math.floor(z + .5))), ve = [];
      for (const lv of [Math.max(1, L - 2), L]) {
        const nn = Math.pow(2, lv), s = 256 * Math.pow(2, z - lv);
        const x0 = Math.floor((fx - 540 / sc) * nn), x1 = Math.floor((fx + 540 / sc) * nn);
        const y0 = Math.max(0, Math.floor((fy - FY / sc) * nn)), y1 = Math.min(nn - 1, Math.floor((fy + (1920 - FY) / sc) * nn));
        for (let tx = x0; tx <= x1; tx++) for (let ty = y0; ty <= y1; ty++) {
          const im = oAnh(bd.tile, lv, md(tx, nn), ty);
          ve.push([im, (tx / nn - fx) * sc + 540, (ty / nn - fy) * sc + FY, s]);
        }
      }
      VE_SAU.push(() => {
        g.fillStyle = '#0d1624'; g.fillRect(0, 0, 1080, 1920);
        for (const [im, x, y, s] of ve) if (im.complete && im.naturalWidth) g.drawImage(im, x - .4, y - .4, s + .8, s + .8);
      });
      // tuyến
      const S = R.map(p => P2(p[0], p[1]));
      const dd = a => a.map((p, i) => (i ? 'L' : 'M') + f1(p[0]) + ' ' + f1(p[1])).join('');
      const full = dd(S);
      const hien = P(t, d.luc_di - .5, .5);
      pVien.setAttribute('d', full); pMo.setAttribute('d', full);
      css(pVien, { opacity: (hien * .9).toFixed(3) }); css(pMo, { opacity: (hien * (may ? .8 : .85)).toFixed(3) });
      const v = diemTai(kp), pv = P2(v.x, v.y);
      pSang.setAttribute('d', kp > 0 ? dd(S.slice(0, v.i).concat([pv])) : '');
      // xe / máy bay
      const kx = P(t, d.luc_di - .3, .35, E.outB), kr = P(t, d.luc_den - .05, .3);
      dat(xe, pv[0], pv[1]);
      css(xe, { opacity: (clamp(kx * 2) * (1 - kr)).toFixed(3) });
      const gd = v.goc * 57.2958;
      if (may) css(xe.firstElementChild, { transform: `rotate(${f1(gd + 90)}deg) scale(${(.5 + .5 * kx).toFixed(3)})` });
      else if (xe.firstElementChild) css(xe.firstElementChild, { transform: `scale(${(.5 + .5 * kx).toFixed(3)})${Math.cos(v.goc) < -.2 && pt !== 'di_bo' ? ' scaleX(-1)' : ''}` });
      // điểm đi
      const pa = S[0], pb = S[S.length - 1];
      dat(cham, pa[0], pa[1]); css(cham, { opacity: P(t, d.tu + .15, .35).toFixed(3) });
      { const pr = md(TG, 1.6) / 1.1; dat(songA, pa[0], pa[1]); css(songA, { opacity: pr <= 1 ? (.9 * (1 - pr)).toFixed(3) : '0', transform: `scale(${(1 + 1.6 * E.outC(Math.min(1, pr))).toFixed(3)})` }); }
      { const k = P(t, tDi, .45), duoi = pa[1] + 34 + hA < 1290;
        dat(tagA, clamp(pa[0] - wA / 2, 40, 1040 - wA), duoi ? pa[1] + 34 : pa[1] - 34 - hA);
        css(tagA, { opacity: (k * (1 - P(t, d.luc_den + .2, .4) * .35)).toFixed(3), transform: `translateY(${f1(14 * (1 - k))}px)` }); }
      // điểm đến: vòng đích (lúc đọc tên) → ghim rơi + vòng lan (lúc tới)
      dat(dich, pb[0], pb[1]); css(dich, { opacity: (P(t, tDen, .4) * (1 - P(t, d.luc_den, .3))).toFixed(3) });
      const kg = P(t, d.luc_den - .05, .55, E.drop);
      css(ghim, { left: f1(pb[0] - 48) + 'px', top: f1(pb[1] - 92) + 'px', opacity: clamp(kg * 3).toFixed(3), transform: `translateY(${f1(-110 * (1 - kg))}px)` });
      { const ub = (t - d.luc_den - .3) / .8; dat(vongB, pb[0], pb[1]);
        css(vongB, ub >= 0 && ub <= 1 ? { opacity: (.9 * (1 - ub)).toFixed(3), transform: `scale(${(1 + 2.4 * E.outC(ub)).toFixed(3)})` } : { opacity: '0' }); }
      { const k = P(t, Math.min(tDen, d.luc_den) + .1, .45), tren = pb[1] - 104 - hB > 600;
        dat(tagB, clamp(pb[0] - wB / 2, 40, 1040 - wB), tren ? pb[1] - 104 - hB : pb[1] + 30);
        css(tagB, { opacity: k.toFixed(3), transform: `translateY(${f1(14 * (1 - k))}px)` }); }
      // ảnh gắn ghim (Resources / bài báo)
      const datAnh = (el, p, k, tren) => {
        if (!el) return;
        const w = 340, h = 236;
        let x = clamp(p[0] - w / 2, 50, 1030 - w), y = p[1] - 76 - h;
        if (tren && y < 590) y = p[1] + 34 + hA + 30;
        if (!tren) { x = p[0] <= 540 ? p[0] + 110 : p[0] - 110 - w; x = clamp(x, 40, 1040 - w); y = clamp(p[1] - 200, 600, 1290 - h); }
        css(el, { left: f1(x) + 'px', top: f1(y) + 'px', opacity: clamp(k * 1.6).toFixed(3), transform: `translateY(${f1(26 * (1 - k))}px) rotate(${tren ? -2.5 : 2.5}deg) scale(${(.85 + .15 * k).toFixed(3)})` });
      };
      datAnh(anhDi, pa, P(t, d.tu + .45, .5, E.outB) * (1 - P(t, d.luc_di + .15, .45)), true);
      datAnh(anhDen, pb, P(t, d.luc_den + .35, .55, E.outB), false);
      // khoảng cách nằm trên đường (lúc đọc số km)
      if (kcEl) {
        const m = diemTai(.5), pm = P2(m.x, m.y), k = P(t, d.luc_kc != null ? d.luc_kc : d.luc_di + .3, .45, E.outB);
        const trong = pm[0] > 60 && pm[0] < 1020 && pm[1] - 112 > 590 && pm[1] < 1260;
        const kh = clamp(k * 2) * (1 - P(t, d.luc_den, .4)) * (trong ? 1 : 0);
        css(kcEl, { left: f1(clamp(pm[0] - wK / 2, 40, 1040 - wK)) + 'px', top: f1(pm[1] - 112) + 'px', opacity: kh.toFixed(3), transform: `translateY(${f1(14 * (1 - k))}px) scale(${(.6 + .4 * k).toFixed(3)})` });
      }
      for (const o of phu) {
        const p = P2(o.x, o.y), w = o.w || (o.w = o.el.offsetWidth || 200);
        // chỉ rõ lúc nhìn toàn tuyến; không ra mép phải, không xuống vùng sub
        const k = clamp(1 - Math.abs(z - (bd.zO || z)) / 1.1) * P(t, d.luc_di + .3, .5) * clamp((1290 - p[1]) / 40) * clamp((p[1] - 600) / 40);
        css(o.el, { left: f1(clamp(p[0] - 11, 30, 1050 - w)) + 'px', top: f1(p[1] - 22) + 'px', opacity: k.toFixed(3) });
      }
    },
  };
}

/* ---- thẻ tuyến: dòng dẫn · điểm đi ⟶ điểm đến (cung vẽ dần + phương tiện chạy) · thời gian / khoảng cách ---- */
function duongCung(nen) {
  if (nen === 'troi') return 'M70 170 Q470 -46 870 170';
  if (nen === 'bien') return 'M70 170 Q270 104 470 150 T870 170';
  return 'M70 170 C300 56, 640 236, 870 170';
}
LAM.hanh_trinh = d => {
  const u = ++HT_U, pt = d.phuong_tien || 'khong', nen = d.nen || 'troi';
  d.luc_di = d.luc_di != null ? d.luc_di : d.tu + .8;
  d.luc_den = d.luc_den != null ? d.luc_den : Math.max(d.luc_di + 1.5, d.den - 1.0);
  const el = mk('div', 'ht', LOP);
  let N = null;
  if (nen === 'troi') N = nenTroi(el, u, d);
  else if (nen === 'duong') N = nenDuong(el, u, d, pt);
  else if (nen === 'bien') N = nenBien(el, u, d);
  else if (nen === 'ban_do') N = nenBanDo(el, u, d, pt);
  else if (nen === 'that') N = nenThat(el, u, d, pt);
  const gon = nen === 'ban_do' || nen === 'that';
  const the = mk('div', 'ht_the' + (gon ? ' gon' : ''), el);
  const dan = mk('div', 'dan', the);
  const g1 = mk('span', 'gach', dan), dt = mk('span', '', dan, esc(d.dan || '')), g2 = mk('span', 'gach p', dan);
  const tuyen = mk('div', 'tuyen', the);
  const tenHtml = o => `<div class="t">${esc(o.ten)}</div>` + (o.phu ? `<div class="p">${esc(o.phu)}</div>` : '');
  let sang = null, songDi = null, xeNho = null, ghimDen = null, vongDen = null, LUT = null, Lc = 0;
  if (!gon) tuyen.innerHTML = `<svg class="cung" width="940" height="230" viewBox="0 0 940 230"><defs><linearGradient id="cv${u}" x1="0" x2="1"><stop offset="0" stop-color="#FFE3A3"/><stop offset="1" stop-color="#E9AE4B"/></linearGradient></defs>
      <path d="${duongCung(nen)}" fill="none" stroke="rgba(255,240,215,.6)" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 17"/>
      <path class="sang" d="${duongCung(nen)}" fill="none" stroke="url(#cv${u})" stroke-width="7" stroke-linecap="round" style="filter:drop-shadow(0 0 8px rgba(244,198,106,.65))"/>
      <circle class="song_di" cx="70" cy="170" r="16" fill="none" stroke="#F4C66A" stroke-width="3"/>
      <circle cx="70" cy="170" r="12" fill="#fff" stroke="#F4C66A" stroke-width="6"/></svg>`;
  const tenDi = mk('div', 'ten di', tuyen, tenHtml(d.xuat_phat));
  if (gon) mk('div', 'mui', tuyen, `<svg viewBox="0 0 80 40" width="80" height="40"><path d="M4 20H70M54 6l16 14-16 14" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>`);
  const tenDen = mk('div', 'ten den', tuyen, tenHtml(d.diem_den));
  if (!gon) {
    sang = tuyen.querySelector('.sang'); songDi = tuyen.querySelector('.song_di');
    xeNho = mk('div', 'xe_nho', tuyen, `<div class="ic">${icon(IC_PT[pt] || 'ghim')}</div>`);
    ghimDen = mk('div', 'ghim_den', tuyen, icon('ghim'));
    vongDen = mk('div', 'vong_den', tuyen);
  }
  // có cả thời gian lẫn khoảng cách: khoảng cách thành nhãn nằm trên đường (hiện lúc đọc tới số km), thời gian là số lớn
  const kcTren = !gon && !!d.thoi_gian && !!d.khoang_cach;
  const kcEl = kcTren ? mk('div', 'kc', tuyen, `${icon('ban_do')}<span>${esc(d.khoang_cach)}</span>`) : null;
  const chinh = d.thoi_gian || d.khoang_cach || '';
  const phu = [d.nhan_tg, d.thoi_gian && d.khoang_cach && !kcTren && nen !== 'that' ? d.khoang_cach : null].filter(Boolean).join(' · ');
  const tg = mk('div', 'tg', the);
  const tgIc = mk('div', 'ic', tg, icon(d.thoi_gian ? 'dong_ho' : 'ban_do'));
  const so = mk('div', 'so vang_grad', tg, esc(chinh));
  const nh = mk('div', 'nhan', tg, `<div class="pt">${esc(d.nhan_pt || '')}</div>` + (phu ? `<div class="ph">${esc(phu)}</div>` : ''));
  hop(the, 'hanh_trinh', d.id);
  const ttg = d.luc_tg != null ? d.luc_tg : d.luc_di + .4;
  const tDi = d.luc_ten_di != null ? d.luc_ten_di : d.tu + .35, tDen = d.luc_ten_den != null ? d.luc_ten_den : d.luc_den - .35;
  return {
    el, sau() {
      el.style.zIndex = 0;
      the.style.top = (d.y != null ? d.y : (gon ? 200 : 180)) + 'px';
      if (N && N.sau) N.sau();
      for (const o of [tenDi, tenDen]) { const t = o.querySelector('.t'); const w = rong(t); const mx = gon ? 380 : 440; if (w > mx) t.style.fontSize = (58 * mx / w) + 'px'; }
      const wt = rong(so) + rong(nh) + 104 + 52; if (wt > 840) so.style.fontSize = (112 * Math.max(.55, (840 - rong(nh) - 156) / rong(so))) + 'px';
      if (sang) {
        Lc = sang.getTotalLength(); sang.style.strokeDasharray = Lc; LUT = [];
        for (let i = 0; i <= 160; i++) { const p = sang.getPointAtLength(Lc * i / 160); LUT.push([p.x, p.y]); }
        if (kcEl) {
          const [x, y] = LUT[80], w = kcEl.offsetWidth, h = kcEl.offsetHeight;
          css(kcEl, { left: f1(x - w / 2) + 'px', top: f1(y - h - 50 >= 8 ? y - h - 50 : y + 52) + 'px' });
        }
      }
    },
    ve(t) {
      const { v, r, on } = vaoRa(t, d, .5, .45); show(el, on); if (!on) return;
      const TG = t - d.tu;
      css(el, { opacity: (v * (1 - r)).toFixed(3) });
      const kp = E.inOutS(clamp((t - d.luc_di) / Math.max(.3, d.luc_den - d.luc_di))), kden = clamp((t - d.luc_den) / .5);
      if (N) { if (nen !== 'ban_do' && nen !== 'that') css(N.el, { transform: `scale(${(1.06 - .06 * E.outC(clamp(TG / 1.2))).toFixed(4)})` }); N.ve(t, TG, kp, kden); }
      const kc = P(t, d.tu + .15, .65, E.outB);
      css(the, { transform: `translateY(${f1(-70 * (1 - kc) - 24 * r)}px)`, opacity: clamp(kc * 1.6).toFixed(3) });
      { const k = P(t, d.tu + .2, .8); css(dt, { opacity: k.toFixed(3), letterSpacing: lerp(.8, .42, k).toFixed(3) + 'em' }); css(g1, { width: f1(90 * k) + 'px' }); css(g2, { width: f1(90 * k) + 'px' }); }
      { const k = P(t, tDi, .5); css(tenDi, { opacity: k.toFixed(3), transform: `translateX(${f1(-34 * (1 - k))}px)` }); }
      { const k = P(t, tDen, .5); css(tenDen, { opacity: k.toFixed(3), transform: `translateX(${f1(34 * (1 - k))}px)` }); }
      if (sang) {
        sang.style.strokeDashoffset = f1(Lc * (1 - kp));
        const i = Math.round(kp * 160), p = LUT[i], q = LUT[Math.min(160, i + 2)], o = LUT[Math.max(0, i - 2)];
        const goc = Math.atan2(q[1] - o[1], q[0] - o[0]) * 57.2958;
        const kx = P(t, d.luc_di - .3, .35, E.outB), kr = P(t, d.luc_den - .05, .3);
        css(xeNho, { left: f1(p[0]) + 'px', top: f1(p[1]) + 'px', opacity: (clamp(kx * 2) * (1 - kr)).toFixed(3), transform: `scale(${(.4 + .6 * kx).toFixed(3)})` });
        css(xeNho.firstChild, { transform: pt === 'may_bay' ? `rotate(${f1(goc + 90)}deg)` : 'none' });
        const kg = P(t, d.luc_den - .05, .55, E.drop);
        css(ghimDen, { opacity: clamp(kg * 3).toFixed(3), transform: `translateY(${f1(-80 * (1 - kg))}px)` });
        const ub = (t - d.luc_den - .3) / .8;
        css(vongDen, ub >= 0 && ub <= 1 ? { opacity: (.9 * (1 - ub)).toFixed(3), transform: `scale(${(1 + 2.4 * E.outC(ub)).toFixed(3)})` } : { opacity: '0' });
        const pr = md(TG, 1.6) / 1.1;
        css(songDi, { opacity: pr <= 1 ? (.9 * (1 - pr)).toFixed(3) : '0', transform: `scale(${(1 + 1.4 * E.outC(Math.min(1, pr))).toFixed(3)})`, transformOrigin: '70px 170px' });
      }
      if (kcEl) {
        const k = P(t, d.luc_kc != null ? d.luc_kc : d.luc_di + .3, .45, E.outB);
        css(kcEl, { opacity: clamp(k * 2).toFixed(3), transform: `translateY(${f1(14 * (1 - k))}px) scale(${(.6 + .4 * k).toFixed(3)})` });
      }
      const kt = P(t, ttg, .6, E.outB);
      css(tg, { opacity: clamp(kt * 2).toFixed(3), transform: `scale(${(.7 + .3 * kt).toFixed(3)})` });
      css(tgIc, { transform: `rotate(${f1(-160 * (1 - kt))}deg)` });
    },
  };
};

const DH = (KH.do_hoa || []).map(d => { const f = LAM[d.loai]; if (!f) { console.error('loại đồ hoạ lạ: ' + d.loai); return null; } const g = f(d); g.d = d; return g; }).filter(Boolean);

/* ================= nguồn ảnh ================= */
const NGUON = mk('div', '', LOP); NGUON.id = 'nguon_anh';
function veNguon(t) {
  const n = (KH.nguon_anh || []).find(x => t >= x.tu && t < x.den);
  if (!n) { css(NGUON, { opacity: '0' }); return; }
  if (NGUON.dataset.k !== n.chu) { NGUON.dataset.k = n.chu; NGUON.textContent = n.chu; }
  css(NGUON, { opacity: (P(t, n.tu, .4) * (1 - P(t, n.den - .3, .3))).toFixed(3) });
}

/* ================= SUB karaoke ================= */
const SUB = mk('div', '', LOP); SUB.id = 'sub'; SUB.style.zIndex = 30;
let subCur = -1, subW = [];
function veSub(t) {
  const L = KH.sub || [];
  let i = -1;
  for (let k = 0; k < L.length; k++) if (t >= L[k].tu && t < L[k].den) { i = k; break; }
  if (i !== subCur) {
    subCur = i; SUB.innerHTML = ''; subW = [];
    if (i >= 0) {
      for (const dong of L[i].dong) {
        const dv = mk('div', 'dong', SUB);
        dong.forEach((w, j) => { const s = mk('span', 'w', dv, esc(w.w)); subW.push({ s, w }); if (!KHONG_CACH && j < dong.length - 1) dv.appendChild(document.createTextNode(' ')); });
        dv.style.whiteSpace = 'nowrap'; const wd = rong(dv); if (wd > 920) dv.style.fontSize = (60 * 920 / wd) + 'px';
      }
      SUB.style.top = (KH.sub_y - SUB.offsetHeight / 2) + 'px';
    }
  }
  if (i < 0) { css(SUB, { opacity: '0' }); return; }
  const c = L[i];
  const k = P(t, c.tu, .16), kr = c.mo_ra ? P(t, c.den - .15, .15, E.inC) : 0;
  css(SUB, { opacity: (k * (1 - kr)).toFixed(3), transform: `translateY(${(16 * (1 - k)).toFixed(1)}px)` });
  for (const o of subW) {
    const dang = t >= o.w.s - .04 && t < Math.max(o.w.e, o.w.s + .12);
    const kp = dang ? P(t, o.w.s - .04, .12) : 0;
    if (dang !== o.s.classList.contains('dang')) o.s.classList.toggle('dang', dang);
    // phồng nhẹ nhưng mỗi bên nở ≤ ~5 px — từ dài (tiếng Anh, Đức…) không lấn khoảng trắng dính sang từ bên cạnh
    if (o.bw === undefined) o.bw = Math.max(1, o.s.offsetWidth);
    const amp = Math.min(.07, 10 / o.bw);
    css(o.s, { transform: dang ? `scale(${(1 + amp * kp).toFixed(3)})` : 'none' });
  }
}
hop(SUB, 'sub', 'sub');

/* ================= CTA ================= */
const C = KH.cta;
let CT = null;
if (C) {
  const el = mk('div', '', LOP); el.id = 'cta'; el.style.zIndex = 25;
  const khoi = mk('div', 'khoi', el);
  const avw = mk('div', 'av_wrap', khoi);
  const vong = mk('div', 'vong_av', avw);
  const av = mk('div', 'av', avw, C.avatar_url ? `<img src="${esc(C.avatar_url)}">` : esc(C.chu_cai || '★'));
  const ten = C.ten ? mk('div', 'ten_kenh', khoi, `<span>${esc(C.ten)}</span>` + `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#20D5EC"/><path d="M7.5 12.5l3 3 6-6.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`) : null;
  const handle = C.handle ? mk('div', 'handle', khoi, esc(C.handle)) : null;
  const tieu = C.tieu_de ? mk('div', 'tieu', khoi, esc(C.tieu_de)) : null;
  const vt = C.viet_tay ? mk('div', 'viet_tay vang_grad', khoi, esc(C.viet_tay)) : null;
  const nh = mk('div', 'nut_hang', khoi);
  const song = mk('div', 'song', nh);
  const nut = mk('div', 'nut', nh);
  const nutTxt = mk('div', '', nut); nutTxt.style.display = 'flex'; nutTxt.style.alignItems = 'center'; nutTxt.style.gap = '16px';
  const NUT0 = icon('cong') + `<span>${esc(C.nut)}</span>`, NUT1 = icon('tich') + `<span>${esc(C.nut_da)}</span>`;
  nutTxt.innerHTML = NUT0; nutTxt.dataset.k = '0';
  const bs = mk('div', 'bong_sang', nut);
  const chuong = mk('div', 'chuong', nh, icon('chuong')); chuong.style.color = '#F4C66A';
  const ih = mk('div', 'icon_hang', el);
  const icons = (C.icon || []).map(k => {
    const w = mk('div', 'ico', ih);
    const o = mk('div', 'o', w, icon(k)); o.style.color = '#fff';
    mk('div', 'n', w, esc((C.nhan_icon || {})[k] || ''));
    return { k, w, o, dac: false };
  });
  const tims = Array.from({ length: 9 }, (_, i) => { const h = mk('div', 'tim_bay', el, IC.tim_dac); return { h, a: i / 9 * Math.PI * 2 + .3, r: 120 + 50 * hash01(i + 3) }; });
  const gon = mk('div', 'gon', el);
  const tay = mk('div', 'tay', el, TAY);
  hop(khoi, 'cta', 'cta'); hop(ih, 'cta', 'cta_icon');
  CT = {
    sau() {
      if (tieu) { tieu.style.whiteSpace = 'nowrap'; vua(tieu, 76, 960); }
      if (vt) { vt.style.whiteSpace = 'nowrap'; vua(vt, 104 * CO_TAY, 1000); }
      const hh = khoi.offsetHeight; const top = Math.max(150, Math.min(300, 1110 - hh));
      khoi.style.top = top + 'px';
      ih.style.top = (top + hh + 40) + 'px';
    },
    ve(t) {
      const t0 = C.tu;
      const on = t >= t0 - .02; show(el, on);
      css(MO_CTA, { opacity: on ? (.92 * P(t, t0, .7)).toFixed(3) : '0' });
      if (!on) return;
      css(el, { opacity: P(t, t0, .35).toFixed(3) });
      const ka = P(t, t0 + .05, .65, E.outB); css(avw, { transform: `scale(${(.3 + .7 * ka).toFixed(3)})`, opacity: clamp(ka * 2).toFixed(3) });
      css(vong, { transform: `rotate(${((t - t0) * 120).toFixed(1)}deg)` });
      if (ten) { const k = P(t, t0 + .35, .5); css(ten, { opacity: k.toFixed(3), transform: `translateY(${(20 * (1 - k)).toFixed(1)}px)` }); }
      if (handle) css(handle, { opacity: P(t, t0 + .45, .5).toFixed(3) });
      if (tieu) { const k = P(t, t0 + .55, .55); css(tieu, { opacity: k.toFixed(3), transform: `translateY(${(26 * (1 - k)).toFixed(1)}px)` }); }
      if (vt) { const k = P(t, t0 + .8, .85, E.inOutS); css(vt, { clipPath: `inset(-20% ${(100 - 100 * k).toFixed(1)}% -30% -5%)` }); }
      // nút theo dõi
      const tb = C.luc_bam, kn = P(t, t0 + .9, .55, E.outB);
      let sc = (.5 + .5 * kn);
      if (t < tb) sc *= 1 + .035 * Math.sin(2 * Math.PI * Math.max(0, t - t0 - 1.4) / 1.1);
      else { const u = t - tb; sc *= u < .1 ? 1 - .1 * (u / .1) : (u < .35 ? .9 + .14 * E.outB(clamp((u - .1) / .25)) : 1.04 - .04 * P(t, tb + .35, .2)); }
      css(nut, { transform: `scale(${sc.toFixed(4)})`, opacity: clamp(kn * 2).toFixed(3) });
      const da = t >= tb + .1;
      if ((nutTxt.dataset.k === '1') !== da) { nutTxt.innerHTML = da ? NUT1 : NUT0; nutTxt.dataset.k = da ? '1' : '0'; nut.classList.toggle('da', da); }
      const ps = ((t - t0 - 1.4) % 1.1 + 1.1) % 1.1 / 1.1;
      if (t > t0 + 1.4 && t < tb) css(song, { opacity: (.8 * (1 - ps)).toFixed(3), transform: `scale(${(1 + .3 * ps).toFixed(3)}, ${(1 + .6 * ps).toFixed(3)})` }); else css(song, { opacity: '0' });
      const pb = ((t - t0 - 1.2) % 1.7 + 1.7) % 1.7 / .7;
      css(bs, { left: (-40 + 160 * clamp(pb)) + '%', opacity: t < tb && pb <= 1 ? '1' : '0' });
      // chuông
      const kc = P(t, tb + .25, .45, E.outB), uc = Math.max(0, t - tb - .35);
      css(chuong, { opacity: clamp(kc * 2).toFixed(3), transform: `scale(${kc.toFixed(3)}) rotate(${(22 * Math.sin(2 * Math.PI * 5 * uc) * Math.exp(-2.4 * uc)).toFixed(2)}deg)` });
      // hàng icon
      icons.forEach((o, i) => {
        const a = tb + .35 + i * .13, k = P(t, a, .5, E.outB);
        css(o.w, { opacity: clamp(k * 2).toFixed(3), transform: `translateY(${(40 * (1 - k)).toFixed(1)}px) scale(${(.5 + .5 * k).toFixed(3)})` });
        const dac = (o.k === 'thich' && t >= C.luc_tim) || (o.k === 'luu' && t >= C.luc_tim + .45);
        if (dac !== o.dac) { o.dac = dac; o.o.innerHTML = dac ? (o.k === 'thich' ? IC.tim_dac : IC.luu_dac) : icon(o.k); }
        const tap = o.k === 'thich' ? C.luc_tim : (o.k === 'luu' ? C.luc_tim + .45 : null);
        if (tap != null && t >= tap) { const u = P(t, tap, .45, E.outB); css(o.o, { transform: `scale(${(1.35 - .35 * u).toFixed(3)})` }); }
        else css(o.o, { transform: 'none' });
      });
      // vị trí đích
      const rn = nut.getBoundingClientRect();
      const pNut = [rn.left + rn.width * .62, rn.top + rn.height * .55];
      const iTim = icons.find(o => o.k === 'thich') || icons[0];
      let pTim = pNut;
      if (iTim) { const r2 = iTim.o.getBoundingClientRect(); pTim = [r2.left + r2.width * .55, r2.top + r2.height * .58]; }
      const pVao = [1010, 1780], pRa = [1150, 1950];
      let p = pVao, s = 1, op = 0;
      const tv = tb - .95, tt = C.luc_tim, tr = tt + .6;
      if (t >= tv) {
        op = P(t, tv, .25);
        if (t < tb) { const k = P(t, tv, .75, E.outC); p = [lerp(pVao[0], pNut[0], k), lerp(pVao[1], pNut[1], k)]; }
        else if (t < tt - .5) p = pNut;
        else if (t < tt) { const k = P(t, tt - .5, .42, E.inOutC); p = [lerp(pNut[0], pTim[0], k), lerp(pNut[1], pTim[1], k)]; }
        else if (t < tr) p = pTim;
        else { const k = P(t, tr, .55, E.inC); p = [lerp(pTim[0], pRa[0], k), lerp(pTim[1], pRa[1], k)]; op = 1 - k; }
        for (const ta of [tb, tt]) { const u = t - ta; if (u >= -.06 && u < .3) s = Math.min(s, u < .06 ? 1 - .14 * clamp((u + .06) / .12) : .86 + .14 * clamp((u - .06) / .24)); }
      }
      css(tay, { opacity: op.toFixed(3), transform: `translate(${(p[0] - TAY_DIEM[0]).toFixed(1)}px, ${(p[1] - TAY_DIEM[1]).toFixed(1)}px) scale(${s.toFixed(3)})` });
      // gợn chạm
      let g = null;
      for (const [ta, pp] of [[tb, pNut], [tt, pTim]]) { const u = (t - ta) / .5; if (u >= 0 && u <= 1) g = [u, pp]; }
      if (g) css(gon, { opacity: (.9 * (1 - g[0])).toFixed(3), left: g[1][0] + 'px', top: g[1][1] + 'px', transform: `scale(${(.4 + 2.6 * E.outC(g[0])).toFixed(3)})` });
      else css(gon, { opacity: '0' });
      // tim bay
      const ub = (t - tt) / .9;
      for (const h of tims) {
        if (ub < 0 || ub > 1) { css(h.h, { opacity: '0' }); continue; }
        const e = E.outC(ub), x = pTim[0] + Math.cos(h.a) * h.r * e - 20, y = pTim[1] + Math.sin(h.a) * h.r * e - 60 * ub - 20;
        css(h.h, { opacity: (1 - ub).toFixed(3), left: x.toFixed(1) + 'px', top: y.toFixed(1) + 'px', transform: `scale(${(.6 + .6 * (1 - ub)).toFixed(3)})` });
      }
    },
  };
}

/* ================= vòng đời ================= */
window.__ready = (async () => {
  await document.fonts.ready;
  const fams = ['PF', 'PFI', 'GV', 'DS', 'BVP', 'MS', 'AN'];
  await Promise.all(fams.flatMap(f => ['400', '700', '900'].map(w => document.fonts.load(`${w} 60px ${f}`, 'AĂÂaăâ').catch(() => null))));
  for (const g of DH) { show(g.el, true); g.sau && g.sau(); show(g.el, false); }
  if (CT) { document.getElementById('cta').style.display = ''; CT.sau(); }
  // nạp sẵn ảnh tĩnh
  const ims = Array.from(document.images).filter(i => i.src);
  await Promise.all(ims.map(i => i.decode().catch(() => null)));
  return true;
})();

window.__seek = async (t) => {
  KHUNG_SO++;
  const ds = [];
  veFootage(t, ds);
  veMau(t);
  for (const g of DH) g.ve(t);
  veNguon(t);
  veSub(t);
  if (CT) CT.ve(t);
  await Promise.all(ds.map(im => im.decode().catch(() => null)));
  if (CHO.length) await Promise.all(CHO.splice(0));          // ô ảnh vệ tinh của khung này (nen that)
  for (const f of VE_SAU.splice(0)) f();
  donAnhO();
  return t;
};

/* hộp phần nhìn thấy thật: hợp các dòng chữ + svg/img/nút (không lấy khối div rộng 1080) */
function hopThat(el) {
  let L = 1e9, T = 1e9, R = -1e9, B = -1e9, co = false;
  const them = rc => { if (rc.width < 1 || rc.height < 1) return; L = Math.min(L, rc.left); T = Math.min(T, rc.top); R = Math.max(R, rc.right); B = Math.max(B, rc.bottom); co = true; };
  const an = n => { for (let e = n; e && e !== el.parentElement; e = e.parentElement) if (e.nodeType === 1 && getComputedStyle(e).display === 'none') return true; return false; };
  const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (!n.textContent.trim() || an(n.parentElement)) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    for (const rc of rg.getClientRects()) them(rc);
  }
  for (const e of el.querySelectorAll('svg, img, .nut, .av, .c, .the, .o')) if (!an(e) && !(e.closest('svg') && e.tagName !== 'svg')) them(e.getBoundingClientRect());
  if (el.matches('.c, .the, .ta, .lk')) them(el.getBoundingClientRect());
  return co ? { left: L, top: T, width: R - L, height: B - T } : null;
}
window.__bao_cao = () => {
  const out = [];
  const visible = el => { for (let e = el; e && e !== stage; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || parseFloat(cs.opacity) < .5) return false; } return true; };
  for (const h of HOP) {
    if (!visible(h.el)) continue;
    const r = hopThat(h.el);
    if (!r || r.width < 2 || r.height < 2) continue;
    out.push({ loai: h.loai, id: h.id, x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) });
  }
  return out;
};
})();
