/* bds3d_3d.js — CẢNH 3D công trình đặt trên ảnh vệ tinh thật (Three.js r149) cho skill bds_model_3d.
 * Nạp SAU three.min.js và bds3d.js. Mỗi __seek(t): vẽ khung WebGL ở giây t (camera, vòng, chú thích bám công trình…)
 * rồi gọi __seek cũ của bds3d.js để vẽ chữ 2 tầng đè lên. Mọi thứ là hàm thuần của t (tua tới đâu ra đúng hình đó).
 *
 * window.M3 (do scripts/mo_hinh_3d.py lập):
 *   nen:   [{url, nua_m}]                       lớp ảnh vệ tinh vuông quanh gốc, GẦN → XA (x = Đông, z = Nam, mét thật)
 *   ct:    {xoay, thap:[…], de:[…], khoi:[…], khu:{rong,sau}, cay_quanh, mau:{…}}   mô hình tham số (xem references/mo_hinh_3d.md)
 *   cam:   [{t, nhin:[x,y,z], goc, nghieng, xa, fov}]                      khoá camera, giây tuyệt đối
 *   vong:  [{tu, den, x, z, r}]   chu_thich: [{tu, den, diem:[x,y,z], chu, phu, ben}]   logo: {tu, den, diem, url|chu, phu}
 *   dia_danh: [{tu, den, chu, diem:[x,y,z]}]   tia: [{tu, den}]   nang: {goc, cao}   troi: {dinh, giua, chan}
 */
(() => {
'use strict';
const M = window.M3, T3 = window.THREE;
if (!M || !T3) { console.error('bds3d_3d: thiếu M3 hoặc THREE'); return; }
const W = 1080, H = 1920, D2R = Math.PI / 180;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const outC = u => 1 - Math.pow(1 - u, 3), inOutS = u => -(Math.cos(Math.PI * u) - 1) / 2;
const P = (t, a, d, e = outC) => e(clamp((t - a) / d));
function rng(seed) { let s = 0; for (const c of String(seed)) s = (s * 31 + c.charCodeAt(0)) >>> 0; s = s || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const CT = M.ct || {};
// buổi: ngày (mặc định, khớp ảnh vệ tinh) | hoang_hon (nắng thấp ấm, cửa sổ sáng) | dem (trời xanh đêm, cửa sổ sáng nhiều)
const BUOI = ({
  ngay: { bloom: .18, nguong: .92 },
  hoang_hon: { troi: { dinh: '#3e5276', giua: '#c4ab9a', chan: '#ecd5bd' }, cao: 16, nang: [0xffcc9c, 1.0], hemi: [0xffe6cc, 0x4a4652, .6], dat: '#b5a892', den: .3, bloom: .4, nguong: .78 },
  // chạng vạng / giờ xanh — kiểu ảnh phối cảnh chung cư hay dùng nhất: trời xanh thẫm, mặt kính tối phản chiếu trời, viền LED + đèn ấm toả sáng
  chang_vang: { troi: { dinh: '#122039', giua: '#2a4672', chan: '#7a8db0' }, cao: 10, nang: [0xb4c2e6, .3], hemi: [0xa3b6e2, 0x2a2d36, .66], dat: '#6c7894', den: .13,
                bloom: .6, nguong: .6, phan_chieu: .55, dat_pc: '#30343f', nen: '#7a86a2' },
  dem: { troi: { dinh: '#0b1022', giua: '#1d2a48', chan: '#3a4a6a' }, cao: 30, nang: [0x9fb6ff, .25], hemi: [0x8aa0d0, 0x202430, .42], dat: '#5a6274', den: .62, bloom: .65, nguong: .55, phan_chieu: .5, dat_pc: '#22252e', nen: '#525c76' },
})[M.buoi || 'ngay'] || {};
const MAU = Object.assign({
  kinh: '#f3f6fa', kinh2: '#d5deea', san: '#8d9bb0', khung: '#b7c1cf', mai: '#6f7782',
  de: '#2a221d', de_lam: '#4a3a30', den: '#d99b4c', vien: '#d6b15c', vuon: '#2a2621', ho: '#41c3d8', san_thuong: '#9fa39d',
  den_cua: BUOI.den || 0,
}, CT.mau || {});

/* ---------------- khung vẽ ---------------- */
const stage = document.getElementById('stage');
for (const id of ['nen', 'toi_tren']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }
document.body.style.background = '#000'; stage.style.background = 'transparent';
const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
cv.style.cssText = `position:absolute;left:0;top:0;width:${W}px;height:${H}px;filter:${M.loc || 'saturate(.9) contrast(1.05) brightness(.97)'}`;
document.body.insertBefore(cv, stage);
const st = document.createElement('style');
st.textContent = `
#ov3d{position:absolute;inset:0;pointer-events:none;font-family:BVP,sans-serif}
#ov3d .vig{position:absolute;inset:0;background:radial-gradient(130% 85% at 50% 52%,rgba(0,0,0,0) 58%,rgba(0,0,0,.34) 100%)}
#ov3d .tia{position:absolute;left:-40%;right:-40%;top:-30%;height:120%;transform-origin:50% 0;
  background:repeating-conic-gradient(from 180deg at 50% 0,rgba(255,250,235,0) 0deg,rgba(255,250,235,.07) 2.2deg,rgba(255,250,235,0) 4.6deg,rgba(255,250,235,0) 9deg);
  -webkit-mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.7) 45%,transparent 85%);mix-blend-mode:screen}
#ov3d .ct{position:absolute;left:0;top:0;width:0;height:0}
#ov3d .ct .dot{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:0 0 0 4px rgba(255,255,255,.25),0 0 14px rgba(255,255,255,.7)}
#ov3d .ct .ln{position:absolute;top:-1.5px;height:3px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.45);border-radius:2px}
#ov3d .ct .tx{position:absolute;white-space:nowrap;line-height:1}
#ov3d .ct .c1{font-weight:800;font-size:46px;letter-spacing:-.01em;text-shadow:0 2px 10px rgba(0,0,0,.55),0 1px 2px rgba(0,0,0,.5)}
#ov3d .ct .c2{font-weight:400;font-size:27px;margin-top:9px;color:rgba(255,255,255,.88);text-shadow:0 1px 6px rgba(0,0,0,.6)}
#ov3d .logo{position:absolute;left:0;top:0;transform-origin:50% 100%}
#ov3d .logo .the{position:relative;display:flex;align-items:center;gap:16px;padding:20px 34px;border-radius:16px;
  background:linear-gradient(135deg,rgba(221,168,82,.93),rgba(176,118,44,.9));border:1.5px solid rgba(255,232,178,.75);
  box-shadow:0 14px 40px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.35)}
#ov3d .logo .the:after{content:"";position:absolute;left:50%;bottom:-15px;margin-left:-15px;border:15px solid transparent;border-bottom:0;border-top-color:rgba(184,124,48,.92)}
#ov3d .logo img{height:76px;display:block}
#ov3d .logo .l1{font-weight:800;font-size:34px;color:#fff;letter-spacing:.04em;text-transform:uppercase;text-shadow:0 1px 3px rgba(90,50,0,.5)}
#ov3d .logo .l2{font-weight:500;font-size:20px;color:rgba(255,248,230,.92);letter-spacing:.12em;text-transform:uppercase;margin-top:6px}
#ov3d .tag{position:absolute;left:0;top:0;padding:9px 18px;border-radius:9px;background:rgba(20,26,34,.55);border:1px solid rgba(255,255,255,.35);
  font-weight:800;font-size:25px;letter-spacing:.07em;text-transform:uppercase;white-space:nowrap;box-shadow:0 6px 20px rgba(0,0,0,.35);transform-origin:50% 100%}
`;
document.head.appendChild(st);
const ov = document.createElement('div'); ov.id = 'ov3d';
stage.insertBefore(ov, stage.firstChild ? stage.firstChild.nextSibling : null);
const mk = (cls, parent, html) => { const e = document.createElement('div'); e.className = cls; if (html != null) e.innerHTML = html; parent.appendChild(e); return e; };
const vig = mk('vig', ov);

/* ---------------- Three ---------------- */
const R = new T3.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
R.setPixelRatio(1); R.setSize(W, H, false);
// HẬU KỲ (giống ảnh chụp / render thật, hết lấp lánh): cảnh vẽ vào bộ đệm ×ssaa (siêu mẫu khử răng cưa cả trong texture),
// rồi 1 lượt: gộp siêu mẫu + NHOÈ THEO ĐỘ SÂU (xa / sát camera mờ như ống kính, chân trời mờ sương — chỗ ảnh vệ tinh xa hay nhấp nháy)
// + TOẢ SÁNG (đèn cửa, viền LED, vương miện có quầng). M.hau_ky = {dof, mo_xa, mo_gan, bloom, nguong} — false = tắt.
// Mờ GẦN để nhẹ (mo_gan ~1): mờ gần mạnh = hiệu ứng tilt-shift → công trình trông như MÔ HÌNH ĐỒ CHƠI.
const SS = clamp(Math.round(+M.ssaa || 2), 1, 3);
const HK = M.hau_ky === false ? null : Object.assign({ dof: 1, mo_xa: 4.5, mo_gan: 1.2, bloom: BUOI.bloom ?? .35, nguong: BUOI.nguong ?? .8 }, M.hau_ky || {});
const RT = new T3.WebGLRenderTarget(W * SS, H * SS, { depthBuffer: true, minFilter: T3.LinearFilter, magFilter: T3.LinearFilter, generateMipmaps: false });
RT.depthTexture = new T3.DepthTexture(W * SS, H * SS); RT.depthTexture.type = T3.UnsignedIntType;
const PQ = new T3.Scene(), PC = new T3.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const PM = new T3.ShaderMaterial({
  depthTest: false, depthWrite: false,
  uniforms: { tC: { value: RT.texture }, tD: { value: RT.depthTexture }, uN: { value: 2 }, uF: { value: 1e5 }, uFoc: { value: 600 },
    uPx: { value: new T3.Vector2(1 / W, 1 / H) }, uDof: { value: HK ? HK.dof : 0 }, uXa: { value: HK ? HK.mo_xa : 0 }, uGan: { value: HK ? HK.mo_gan : 0 },
    uBl: { value: HK ? HK.bloom : 0 }, uNg: { value: HK ? HK.nguong : 1 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `
uniform sampler2D tC, tD; uniform float uN, uF, uFoc, uDof, uXa, uGan, uBl, uNg; uniform vec2 uPx; varying vec2 vUv;
float kc(vec2 uv){ float d = texture2D(tD, uv).x; return -(uN * uF) / ((uF - uN) * d - uF); }
float coc(float k){ float f = (k - uFoc) / k; return uDof * (uXa * smoothstep(.25, .92, f) + uGan * smoothstep(.5, 1.6, -f)); }
void main(){
  vec3 c0 = texture2D(tC, vUv).rgb;                 // lấy mẫu song tuyến giữa khối SS×SS = gộp siêu mẫu
  vec3 c = c0;
  if (uDof > 0.0) {
    float r = coc(kc(vUv));
    if (r > .45) {
      vec3 s = c0; float w = 1.0;
      for (int i = 1; i < 24; i++) {
        float fi = float(i), rr = r * sqrt(fi / 23.0), a = fi * 2.39996;
        vec2 o = vec2(cos(a), sin(a)) * rr * uPx;
        float rt = coc(kc(vUv + o));
        float wi = smoothstep(rr - .8, rr + .2, rt);      // điểm nét (nhà gần tiêu cự) không loang ra nền mờ
        s += texture2D(tC, vUv + o).rgb * wi; w += wi;
      }
      c = mix(c0, s / w, smoothstep(.45, 1.4, r));
    }
  }
  if (uBl > 0.0) {                                    // toả sáng: gom phần sáng vượt ngưỡng quanh điểm (bán kính 2–20 px)
    vec3 b = vec3(0.0);
    for (int i = 0; i < 16; i++) {
      float fi = float(i), rr = 2.0 + 18.0 * sqrt((fi + .5) / 16.0), a = fi * 2.39996 + .7;
      vec3 t = texture2D(tC, vUv + vec2(cos(a), sin(a)) * rr * uPx).rgb;
      float l = max(max(t.r, t.g), t.b);
      b += t * (max(l - uNg, 0.0) / max(l, 1e-3)) * (1.0 - rr / 22.0);
    }
    c += b * (uBl / 6.0);
  }
  gl_FragColor = vec4(c, 1.0);
}` });
PQ.add(new T3.Mesh(new T3.PlaneGeometry(2, 2), PM));
R.shadowMap.enabled = true; R.shadowMap.type = T3.PCFSoftShadowMap; R.shadowMap.autoUpdate = true;
const S = new T3.Scene();
const TROI = Object.assign({ dinh: '#26343f', giua: '#8f9ca5', chan: '#b9c1c5' }, BUOI.troi || {}, M.troi || {});
S.fog = new T3.Fog(new T3.Color(TROI.chan), 900, 9000);
const cam = new T3.PerspectiveCamera(32, W / H, 2, 160000);

// bầu trời: nửa cầu tô dải màu theo độ cao hướng nhìn
const sky = new T3.Mesh(new T3.SphereGeometry(120000, 48, 24), new T3.ShaderMaterial({
  side: T3.BackSide, depthWrite: false, fog: false,
  uniforms: { cTop: { value: new T3.Color(TROI.dinh) }, cMid: { value: new T3.Color(TROI.giua) }, cHor: { value: new T3.Color(TROI.chan) } },
  vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform vec3 cTop, cMid, cHor; varying vec3 vP; void main(){ float y = max(vP.y, 0.0); vec3 c = mix(cHor, cMid, smoothstep(0.0, 0.12, y)); c = mix(c, cTop, smoothstep(0.12, 0.55, y)); gl_FragColor = vec4(c, 1.0); }',
}));
sky.renderOrder = -100; S.add(sky);

// môi trường PHẢN CHIẾU cho mặt kính: trời theo buổi + dải phố xa ở chân trời (lấm tấm đèn khi chiều tối) + đất tối bên dưới
// → kính đổi sắc theo góc nhìn như kính thật, không còn "mảng màu phẳng" giả
const ENV = (() => {
  const N = 256, mk = ve => { const c = document.createElement('canvas'); c.width = c.height = N; ve(c.getContext('2d')); return c; };
  const dat = BUOI.dat_pc || '#4d4f4c';
  const ben = k => mk(g => {
    const gr = g.createLinearGradient(0, 0, 0, N);
    gr.addColorStop(0, TROI.dinh); gr.addColorStop(.34, TROI.giua); gr.addColorStop(.49, TROI.chan); gr.addColorStop(.5, mau(dat, .05)); gr.addColorStop(1, mau(dat, -.1));
    g.fillStyle = gr; g.fillRect(0, 0, N, N);
    const r = rng('env' + k);
    for (let x = 0; x < N; x += 2 + r() * 5) { const h = 2 + r() * r() * 20; g.fillStyle = mau(dat, -.05 + r() * .06); g.fillRect(x, N * .5 - h, 2 + r() * 6, h); }
    if ((BUOI.den || 0) > .1) for (let i = 0; i < 260; i++) { const y = N * (.52 + .46 * r() * r()); g.fillStyle = `rgba(255,${190 + r() * 50 | 0},${120 + r() * 80 | 0},${(.25 + r() * .5).toFixed(2)})`; g.fillRect(r() * N, y, 1.4, 1.4); }
    if ((BUOI.den || 0) > .1) for (let i = 0; i < 110; i++) { g.fillStyle = `rgba(255,${200 + r() * 45 | 0},${140 + r() * 70 | 0},${(.45 + r() * .55).toFixed(2)})`; g.fillRect(r() * N, N * .5 - r() * 16, 1.6, 1.6); }
  });
  const t = new T3.CubeTexture([ben(0), ben(1), mk(g => { g.fillStyle = TROI.dinh; g.fillRect(0, 0, N, N); }), mk(g => { g.fillStyle = mau(dat, -.1); g.fillRect(0, 0, N, N); }), ben(2), ben(3)]);
  t.needsUpdate = true; return t;
})();
// tối dần về chân tường (giả che sáng môi trường / AO): khối nhà "đứng" trên đất thay vì dán lên ảnh
function aoChan(m) {
  m.onBeforeCompile = s => {
    s.vertexShader = 'varying float vWY;\n' + s.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n  vWY = (modelMatrix * vec4(transformed, 1.0)).y;');
    s.fragmentShader = 'varying float vWY;\n' + s.fragmentShader.replace('#include <color_fragment>', '#include <color_fragment>\n  diffuseColor.rgb *= mix(.5, 1.0, smoothstep(0.0, 26.0, vWY)) * mix(.93, 1.0, smoothstep(26.0, 90.0, vWY));');
  };
  m.customProgramCacheKey = () => 'aoChan';
  return m;
}

// ánh sáng
const NANG = Object.assign({ goc: 32, cao: BUOI.cao ?? 55 }, M.nang || {});          // goc như camera: 0 = từ phía Nam (VN: nắng chủ yếu phía Nam)
S.add(new T3.HemisphereLight(...(BUOI.hemi || [0xe4ecf6, 0x6a675a, .78])));
const sun = new T3.DirectionalLight(...(BUOI.nang || [0xfff3df, .92]));
{
  const a = NANG.goc * D2R, e = NANG.cao * D2R;
  sun.position.set(Math.sin(a) * Math.cos(e) * 900, Math.sin(e) * 900, Math.cos(a) * Math.cos(e) * 900);
  sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096);
  const c = sun.shadow.camera, r = M.bong_r || 260; c.left = -r; c.right = r; c.top = r; c.bottom = -r; c.near = 50; c.far = 2400;
  sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.6;
  S.add(sun, sun.target);
}

/* ---------------- mặt đất: ảnh vệ tinh nhiều lớp ---------------- */
const loader = new T3.TextureLoader();
const cho = [];
const maxAniso = R.capabilities.getMaxAnisotropy();
window.__m3_info = { webgl2: R.capabilities.isWebGL2, aniso: maxAniso, maxTex: R.capabilities.maxTextureSize, samples: R.capabilities.maxSamples, ratio: R.getPixelRatio() };
function canvasTex(w, h, ve, lap = false) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; ve(c.getContext('2d'), w, h);
  const t = new T3.CanvasTexture(c); t.anisotropy = maxAniso;
  if (lap) t.wrapS = t.wrapT = T3.RepeatWrapping;
  return t;
}
const mepMo = canvasTex(256, 256, (g, w, h) => {      // alphaMap: mờ dần ở 18 % mép ngoài
  const im = g.createImageData(w, h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const d = Math.min(x, w - 1 - x, y, h - 1 - y) / (w / 2), a = clamp(d / .36); const v = Math.round(255 * a * a * (3 - 2 * a));
    const i = (y * w + x) * 4; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255;
  }
  g.putImageData(im, 0, 0);
});
const NEN = M.nen || [];
NEN.forEach((L, i) => {
  const xa = i === NEN.length - 1;
  const mat = new T3.MeshBasicMaterial({ color: new T3.Color(M.mau_dat || BUOI.dat || '#d9d9d9'), transparent: !xa, alphaMap: xa ? null : mepMo, depthWrite: false });
  cho.push(loader.loadAsync(L.url).then(tx => { tx.anisotropy = maxAniso; mat.map = tx; mat.needsUpdate = true; })
    .catch(() => { mat.color.set('#5b6157'); console.warn('bds3d_3d: không nạp được ' + L.url); }));
  const g = new T3.PlaneGeometry(2 * L.nua_m, 2 * L.nua_m); g.rotateX(-Math.PI / 2);
  const m = new T3.Mesh(g, mat); m.renderOrder = -50 - i; S.add(m);
});
// lớp hứng bóng
{
  const r = (M.bong_r || 260) * 1.3, g = new T3.PlaneGeometry(2 * r, 2 * r); g.rotateX(-Math.PI / 2);
  const m = new T3.Mesh(g, new T3.ShadowMaterial({ opacity: M.bong_dam ?? .42, depthWrite: false })); m.position.y = .05; m.receiveShadow = true; m.renderOrder = -20; S.add(m);
}

/* ---------------- mô hình công trình ---------------- */
const G0 = new T3.Group(); G0.position.set(CT.x || 0, 0, CT.z || 0); G0.rotation.y = -(CT.xoay || 0) * D2R; S.add(G0);
const CHAN = [];                                   // chân công trình (nhóm + rộng/sâu) — cây sân vườn né ra
const lam = (c, o = {}) => new T3.MeshLambertMaterial(Object.assign({ color: new T3.Color(c) }, o));
function hop(w, h, d, mat, x, y, z, parent, bong = true) {
  const m = new T3.Mesh(new T3.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); m.castShadow = bong; m.receiveShadow = true; parent.add(m); return m;
}
function mau(hex, k) { const c = new T3.Color(hex); c.offsetHSL(0, 0, k); return '#' + c.getHexString(); }

// mặt kính: ô lặp 8 bước cột × 12 tầng (12 tầng để ô đèn sáng không lặp thành cột thấy rõ)
const NB = 8, NF = 12, BW = 56, FH = 44;
// ô cửa sáng đèn (den_cua = tỉ lệ 0–1, nửa bước cột / tầng): vẽ ấm trên map + sáng trên emissiveMap
const oDen = MT => { const r = rng('den' + (CT.seed || '')), L = []; if (MT.den_cua > 0) for (let f = 0; f < NF; f++) for (let b = 0; b < NB; b++) for (const h of [0, 1]) if (r() < MT.den_cua) L.push([b * BW + h * BW / 2 + 2, f * FH + 3, BW / 2 - 4, FH * .76 - 5]); return L; };
const veLuoi = (g, mauLuoi, bong) => {               // lưới khung mặt đứng: lam đứng dày so le + khung ngang mỗi 4 tầng
  g.fillStyle = mauLuoi;
  for (const b of [0, 3, 5]) g.fillRect(b * BW, 0, 10, NF * FH);
  for (let f = 0; f < NF; f += 4) g.fillRect(0, f * FH + FH * .76 - 2, NB * BW, 9);   // khung ngang mỗi 4 tầng
  if (bong) { g.fillStyle = 'rgba(0,0,0,.18)'; for (const b of [0, 3, 5]) g.fillRect(b * BW + 10, 0, 2, NF * FH); }
};
// kiểu mặt `mat: "can_ho"` (chung cư kính tối như ảnh phối cảnh): mỗi bước cột 1 ô cửa có đố giữa, lan can mảnh,
// đèn ấm NHIỀU MỨC sáng (có ô kéo rèm chỉ sáng nửa dưới), lưới mảnh `luoi_min` mỗi cột + mỗi tầng (khung đồng / trắng)
const oCanHo = MT => { const r = rng('ch' + (CT.seed || '')), L = [];
  for (let f = 0; f < NF; f++) for (let b = 0; b < NB; b++) { const sang = r() < (MT.den_cua || 0) ? .3 + .7 * r() : 0; L.push([b, f, sang, r() < .3 ? .5 + .35 * r() : 1, r()]); }
  return L; };
const hexNhan = (c, k) => '#' + new T3.Color(c).multiplyScalar(k).getHexString();
function veCanHo(g, MT, phat) {
  const W_ = NB * BW, H_ = NF * FH, nen = phat ? hexNhan(MT.phat || '#3a4656', .3) : MT.san;
  g.fillStyle = nen; g.fillRect(0, 0, W_, H_);
  for (const [b, f, sang, rem, q] of oCanHo(MT)) {
    const x = b * BW + 5, y = f * FH + 4, w = BW - 10, h = FH * .72, yr = y + h * (1 - rem);
    if (phat) { if (sang > 0) { g.fillStyle = hexNhan(MT.den_mau || '#ffc37a', sang); g.fillRect(x + 2, yr, w - 4, h * rem); } continue; }
    const k = (q - .5) * .05, gr = g.createLinearGradient(0, y, 0, y + h);
    gr.addColorStop(0, mau(MT.kinh, k + .03)); gr.addColorStop(1, mau(MT.kinh2, k)); g.fillStyle = gr; g.fillRect(x, y, w, h);
    if (sang > 0) {
      const gl = g.createLinearGradient(0, yr, 0, y + h); gl.addColorStop(0, '#ffe8bd'); gl.addColorStop(1, MT.den_mau || '#e9a65e');
      g.globalAlpha = .35 + .65 * sang; g.fillStyle = gl; g.fillRect(x + 2, yr, w - 4, h * rem); g.globalAlpha = 1;
    }
    g.fillStyle = MT.khung; g.fillRect(x + w / 2 - 1, y, 2, h);
    g.globalAlpha = .6; g.fillStyle = MT.mep || '#8a8d92'; g.fillRect(x - 3, y + h + 5, w + 6, 2); g.globalAlpha = 1;
  }
  if (MT.luoi_min) {
    const c = phat ? (MT.luoi_den > 0 ? hexNhan(MT.luoi_min, MT.luoi_den * .7) : null) : MT.luoi_min;
    if (c) { g.fillStyle = c; for (let b = 0; b <= NB; b++) g.fillRect(b * BW - 1.5, 0, 3, H_); for (let f = 0; f <= NF; f++) g.fillRect(0, f * FH - 1, W_, 2.5); }
  }
  if (MT.luoi) veLuoi(g, phat ? (MT.luoi_den > 0 ? hexNhan(MT.luoi, MT.luoi_den) : nen) : MT.luoi, !phat);
}
const mkTexKinh = MT => MT.mat === 'can_ho' ? canvasTex(NB * BW, NF * FH, g => veCanHo(g, MT, false), true) : canvasTex(NB * BW, NF * FH, (g) => {
  const r = rng('kinh' + (CT.seed || ''));
  for (let f = 0; f < NF; f++) for (let b = 0; b < NB; b++) {
    const x = b * BW, y = f * FH, k = (r() - .5) * .06 - (r() < .14 ? .07 : 0);
    const gr = g.createLinearGradient(0, y, 0, y + FH);
    gr.addColorStop(0, mau(MT.kinh, k + .02)); gr.addColorStop(.75, mau(MT.kinh2, k)); gr.addColorStop(1, mau(MT.kinh2, k - .03));
    g.fillStyle = gr; g.fillRect(x, y, BW, FH);
    g.fillStyle = MT.san; g.fillRect(x, y + FH * .76, BW, FH * .24);                   // dải sàn / lan can
    g.fillStyle = MT.mep || '#fbfcfd'; g.fillRect(x, y + FH * .76, BW, 3);             // mép ban công sáng
    g.fillStyle = 'rgba(40,50,64,.18)'; g.fillRect(x, y + FH - 2, BW, 2);
    g.fillStyle = MT.khung; g.fillRect(x, y, 2, FH * .76); g.fillRect(x + BW / 2, y, 1, FH * .76);
  }
  for (const [x, y, w, h] of oDen(MT)) {
    const gr = g.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, '#ffe2ae'); gr.addColorStop(1, MT.den_mau || '#f0a95c');
    g.fillStyle = gr; g.fillRect(x, y, w, h);
  }
  if (MT.luoi) veLuoi(g, MT.luoi, true);
}, true);
const mkTexDen = MT => MT.mat === 'can_ho' ? canvasTex(NB * BW, NF * FH, g => veCanHo(g, MT, true), true) : canvasTex(NB * BW, NF * FH, (g) => {    // emissiveMap: nền = ánh tự phát cũ (phat × 0,3), ô đèn sáng ấm
  const c = new T3.Color(MT.phat || '#3a4656').multiplyScalar(.3);
  g.fillStyle = '#' + c.getHexString(); g.fillRect(0, 0, NB * BW, NF * FH);
  g.fillStyle = MT.den_mau || '#ffc37a'; for (const [x, y, w, h] of oDen(MT)) g.fillRect(x, y, w, h);
  if (MT.luoi) veLuoi(g, MT.luoi_den > 0 ? '#' + new T3.Color(MT.luoi).multiplyScalar(MT.luoi_den).getHexString() : '#' + c.getHexString(), false);
}, true);
// mặt nạ PHẢN CHIẾU (specularMap): trắng = kính phản chiếu trời, đen = khung / tường / ô đang sáng đèn
const mkTexPhan = MT => canvasTex(NB * BW, NF * FH, g => {
  g.fillStyle = '#000'; g.fillRect(0, 0, NB * BW, NF * FH);
  if (MT.mat === 'can_ho') {
    for (const [b, f, sang, rem] of oCanHo(MT)) {
      const x = b * BW + 5, y = f * FH + 4, w = BW - 10, h = FH * .72;
      g.fillStyle = '#fff'; g.fillRect(x, y, w, h);
      if (sang > 0) { g.fillStyle = '#262626'; g.fillRect(x + 2, y + h * (1 - rem), w - 4, h * rem); }
      g.fillStyle = '#000'; g.fillRect(x + w / 2 - 1, y, 2, h);
    }
  } else {
    g.fillStyle = '#fff'; for (let f = 0; f < NF; f++) g.fillRect(0, f * FH, NB * BW, FH * .76);
    g.fillStyle = '#000'; for (let b = 0; b < NB; b++) { g.fillRect(b * BW, 0, 2, NF * FH); g.fillRect(b * BW + BW / 2, 0, 1, NF * FH); }
    g.fillStyle = '#262626'; for (const [x, y, w, h] of oDen(MT)) g.fillRect(x, y, w, h);
  }
  if (MT.luoi) veLuoi(g, '#000', false);
}, true);
// tường hồi (2 mặt ngắn của tháp hộp): vách đặc màu `tuong_hoi`, giữa có 1 cột cửa hẹp, vạch sàn mờ — kiểu đầu hồi chung cư VN
const mkTexHoi = MT => canvasTex(96, NF * FH, (g, w) => {
  const r = rng('hoi' + (CT.seed || ''));
  g.fillStyle = MT.tuong_hoi; g.fillRect(0, 0, w, NF * FH);
  for (let f = 0; f < NF; f++) {
    const y = f * FH; g.fillStyle = 'rgba(0,0,0,.07)'; g.fillRect(0, y + FH - 2, w, 2);
    const sang = MT.den_cua > 0 && r() < MT.den_cua; g.fillStyle = sang ? (MT.den_mau || '#f0a95c') : mau(MT.kinh2, -.02); g.fillRect(w * .42, y + 6, w * .16, FH * .62);
  }
  g.fillStyle = 'rgba(255,255,255,.12)'; g.fillRect(0, 0, 3, NF * FH); g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(w - 3, 0, 3, NF * FH);
}, true);
const texKinh = mkTexKinh(MAU);
// bảng màu riêng từng tháp (T.mau ghi đè MAU): texture kính, đèn cửa, chỉ vàng, vương miện theo bộ màu đó
const _boMau = {};
function boMau(T) {
  const MT = T && T.mau ? Object.assign({}, MAU, T.mau) : MAU, k = JSON.stringify(MT);
  return _boMau[k] || (_boMau[k] = {
    MT, texKinh: MT === MAU ? texKinh : mkTexKinh(MT), texDen: (MT.den_cua > 0 || MT.luoi_den > 0) ? mkTexDen(MT) : null,
    texHoi: MT.tuong_hoi ? mkTexHoi(MT) : null,
    texPhan: (MT.phan_chieu ?? BUOI.phan_chieu ?? .38) > 0 ? mkTexPhan(MT) : null, phan: MT.phan_chieu ?? BUOI.phan_chieu ?? .38,
    matVien: lam(MT.vien, { emissive: new T3.Color(MT.vien), emissiveIntensity: .28 }),
  });
}
// mặt đế: lam đứng nâu + cửa sáng ấm, ô lặp 8 cột × 2 tầng
const texDe = canvasTex(8 * 48, 2 * 64, (g) => {
  const r = rng('de' + (CT.seed || ''));
  g.fillStyle = MAU.de; g.fillRect(0, 0, 384, 128);
  for (let f = 0; f < 2; f++) for (let b = 0; b < 8; b++) {
    const x = b * 48, y = f * 64;
    if (r() < .46) {
      const gr = g.createLinearGradient(0, y + 8, 0, y + 56); gr.addColorStop(0, mau(MAU.den, .08)); gr.addColorStop(1, mau(MAU.den, -.12));
      g.fillStyle = gr; g.fillRect(x + 4, y + 10, 40, 44);
    } else { g.fillStyle = '#1c1714'; g.fillRect(x + 4, y + 10, 40, 44); }
    g.fillStyle = MAU.de_lam; for (let k = 0; k < 5; k++) g.fillRect(x + 3 + k * 9.5, y + 8, 3, 48);
    g.fillStyle = '#17110e'; g.fillRect(x, y + 56, 48, 8);
  }
}, true);
const texVuon = canvasTex(256, 64, (g) => {
  const r = rng('vuon');
  g.fillStyle = MAU.vuon; g.fillRect(0, 0, 256, 64);
  for (let i = 0; i < 26; i++) { g.fillStyle = `rgba(242,180,94,${.55 + r() * .4})`; g.fillRect(r() * 250, 12 + r() * 26, 4 + r() * 5, 10 + r() * 10); }
  for (let i = 0; i < 70; i++) { g.fillStyle = ['#355f2e', '#4a7a36', '#2c4f28'][i % 3]; g.beginPath(); g.arc(r() * 256, 50 + r() * 12, 4 + r() * 7, 0, 7); g.fill(); }
}, true);
const texMai = (song, seed, MT = MAU) => canvasTex(512, 160, (g, w, h) => {         // vương miện lưới xám, mép trên lượn sóng
  const r = rng(seed);
  const top = u => song ? h * (.04 + .3 * (1 - (.5 + .5 * Math.cos(2 * Math.PI * u)))) : h * .06;
  g.fillStyle = MT.mai;
  g.beginPath(); g.moveTo(0, h);
  for (let x = 0; x <= w; x += 4) g.lineTo(x, top(x / w));
  g.lineTo(w, h); g.closePath(); g.save(); g.clip();
  g.fillStyle = 'rgba(176,186,198,.5)'; g.fillRect(0, 0, w, h);                // kính mờ phía sau lưới
  g.fillStyle = MT.mai; for (let x = 0; x < w; x += 12) g.fillRect(x, 0, 3, h);
  for (const y of [.5, .97]) g.fillRect(0, h * y - 3, w, 6);
  g.restore();
  g.strokeStyle = mau(MT.mai, -.1); g.lineWidth = 6; g.beginPath();
  for (let x = 0; x <= w; x += 4) { const y = top(x / w) + 3; x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
});
const texHo = canvasTex(256, 256, (g, w, h) => {
  const r = rng('ho');
  const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, mau(MAU.ho, .1)); gr.addColorStop(1, mau(MAU.ho, -.06));
  g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(255,255,255,.28)'; g.lineWidth = 2;
  for (let i = 0; i < 40; i++) { g.beginPath(); const x = r() * w, y = r() * h; g.moveTo(x, y); g.bezierCurveTo(x + 20, y - 10, x + 30, y + 12, x + 50, y); g.stroke(); }
  g.strokeStyle = '#f3f5f2'; g.lineWidth = 10; g.strokeRect(5, 5, w - 10, h - 10);
});
function matMat(tex, wm, nf, bw, seed, phat, den, B) {   // wm/nf/bw = null: geometry đã có UV theo ô (đa giác) → repeat 1
  const t = tex.clone(); t.needsUpdate = true; if (wm != null) t.repeat.set(wm / (NB * bw), nf / NF); const r = rng(seed); t.offset.set(Math.floor(r() * NB) / NB, Math.floor(r() * NF / 4) * 4 / NF);
  const ban = (x) => { const e = x.clone(); e.needsUpdate = true; e.repeat.copy(t.repeat); e.offset.copy(t.offset); return e; };
  const o = den ? { map: t, emissive: new T3.Color('#ffffff'), emissiveMap: ban(den), emissiveIntensity: 1 } : { map: t, emissive: new T3.Color(phat || '#3a4656'), emissiveIntensity: .3 };
  if (B && B.texPhan) Object.assign(o, { envMap: ENV, combine: T3.MixOperation, reflectivity: B.phan, specularMap: ban(B.texPhan) });
  return aoChan(lam('#f4f6f9', o));
}
const matSan = lam('#b9bcbb'), matVien = lam(MAU.vien, { emissive: new T3.Color(MAU.vien), emissiveIntensity: .28 });
const matCot = lam('#e6e9ec'), matSanh = lam('#3b4654', { emissive: new T3.Color('#4a3a22'), emissiveIntensity: .4 });
const matVuon = (wm, h) => { const t = texVuon.clone(); t.needsUpdate = true; t.repeat.set(wm / 30, 1); return lam('#ffffff', { map: t, emissive: new T3.Color('#ffffff'), emissiveMap: t, emissiveIntensity: .55 }); };

/* ---- tháp mọi hình: tròn / elip, bo góc, đa giác tự do (chữ L, U, tam giác, cánh cung…) + lùi tầng ---- */
function chanDaGiac(T) {                 // đa giác chân tháp (toạ độ trong tháp, mét) hoặc null = hộp chữ nhật
  const w = +T.rong || 30, d = +T.sau || 30, h = T.hinh || 'chu_nhat';
  if (h === 'da_giac' && Array.isArray(T.diem) && T.diem.length >= 3) return T.diem.map(p => [+p[0], +p[1]]);
  if (h === 'tron') { const n = 56, P = []; for (let k = 0; k < n; k++) { const a = 2 * Math.PI * k / n; P.push([Math.cos(a) * w / 2, Math.sin(a) * d / 2]); } return P; }
  if (h === 'bo_goc') {
    const r = Math.min(T.bo ?? Math.min(w, d) * .22, w / 2 - .01, d / 2 - .01), P = [];
    for (const [cx, cz, a0] of [[w / 2 - r, d / 2 - r, 0], [-w / 2 + r, d / 2 - r, 90], [-w / 2 + r, -d / 2 + r, 180], [w / 2 - r, -d / 2 + r, 270]])
      for (let k = 0; k <= 6; k++) { const a = (a0 + k * 15) * D2R; P.push([cx + Math.cos(a) * r, cz + Math.sin(a) * r]); }
    return P;
  }
  if (T.lui) return [[w / 2, d / 2], [-w / 2, d / 2], [-w / 2, -d / 2], [w / 2, -d / 2]];
  return null;
}
const hopBao = P => { let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9; for (const [x, z] of P) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); } return { x0, x1, z0, z1, w: x1 - x0, d: z1 - z0 }; };
const trongDG = (P, x, z) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, zi] = P[i], [xj, zj] = P[j]; if ((zi > z) !== (zj > z) && x < (xj - xi) * (z - zi) / (zj - zi) + xi) c = !c; } return c; };
function tuongGeo(P, y0, y1, uDen, vDen, muot) {   // vách quanh đa giác, UV liền theo chu vi (u = m / uDen, v = m / vDen)
  const n = P.length; let A = 0;
  for (let i = 0; i < n; i++) { const [x1, z1] = P[i], [x2, z2] = P[(i + 1) % n]; A += x1 * z2 - x2 * z1; }
  const sg = A > 0 ? 1 : -1, NO = [];
  for (let i = 0; i < n; i++) { const [x1, z1] = P[i], [x2, z2] = P[(i + 1) % n], L = Math.hypot(x2 - x1, z2 - z1) || 1; NO.push([sg * (z2 - z1) / L, -sg * (x2 - x1) / L]); }
  const tb = (a, b) => { const x = a[0] + b[0], z = a[1] + b[1], l = Math.hypot(x, z) || 1; return a[0] * b[0] + a[1] * b[1] > .86 ? [x / l, z / l] : a; };
  const pos = [], nor = [], uv = []; let s = 0;
  for (let i = 0; i < n; i++) {
    const a = P[i], b = P[(i + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const nA = muot ? tb(NO[i], NO[(i - 1 + n) % n]) : NO[i], nB = muot ? tb(NO[i], NO[(i + 1) % n]) : NO[i];
    const A0 = [a, y0, nA, s], B0 = [b, y0, nB, s + L], B1 = [b, y1, nB, s + L], A1 = [a, y1, nA, s];
    const tri = sg > 0 ? [A0, B1, B0, A0, A1, B1] : [A0, B0, B1, A0, B1, A1];
    for (const [p, y, nn, ss] of tri) { pos.push(p[0], y, p[1]); nor.push(nn[0], 0, nn[1]); uv.push(ss / uDen, (y - y0) / vDen); }
    s += L;
  }
  const g = new T3.BufferGeometry();
  g.setAttribute('position', new T3.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new T3.Float32BufferAttribute(nor, 3)); g.setAttribute('uv', new T3.Float32BufferAttribute(uv, 2));
  return g;
}
function phienGeo(P, y, day) {           // tấm phẳng theo đa giác (nắp sàn / mái / vành), dày `day` m (0 = mặt phẳng)
  const sh = new T3.Shape(); P.forEach(([x, z], k) => k ? sh.lineTo(x, -z) : sh.moveTo(x, -z));
  const g = day > 0 ? new T3.ExtrudeGeometry(sh, { depth: day, bevelEnabled: false }) : new T3.ShapeGeometry(sh);
  g.rotateX(-Math.PI / 2); g.translate(0, y, 0); return g;
}
const mesh = (g, m, parent, bong = true) => { const o = new T3.Mesh(g, m); o.castShadow = bong; o.receiveShadow = true; parent.add(o); return o; };
const texMaiLap = (song, seed, MT) => { const t = texMai(song, seed, MT); t.wrapS = T3.RepeatWrapping; t.needsUpdate = true; return t; };
function matMaiTop(MT, tex) {
  const o = { map: tex, alphaTest: .5, side: T3.DoubleSide, transparent: false };
  if (MT.mai_den) Object.assign(o, { emissive: new T3.Color(MT.mai_den), emissiveMap: tex, emissiveIntensity: .95 });   // vương miện phát sáng
  return lam('#ffffff', o);
}
function thapDa(T, i, G, B, P0) {
  const fh = T.cao_tang || 3.3, N = T.tang | 0, y0 = T.chan || 0, bw = T.buoc_cot || 3.6, muot = (T.hinh === 'tron');
  const bb = hopBao(P0), kt = Math.max(6, Math.min(bb.w, bb.d));
  const lui = (T.lui || []).map(o => [o.tu | 0, +o.co || 1]).filter(o => o[0] > 0 && o[0] < N).sort((a, b) => a[0] - b[0]);
  const coAt = f => lui.reduce((s, [t, c]) => f >= t ? s * c : s, 1);
  const sc = (P, s) => P.map(([x, z]) => [x * s, z * s]);
  const vu = [...new Set((T.vuon || []).map(v => v | 0))].filter(v => v > 0 && v < N - 2).sort((a, b) => a - b);
  const cat = new Set([0, N]); vu.forEach(v => { cat.add(v); cat.add(v + 2); }); lui.forEach(([t]) => cat.add(t));
  const cs = [...cat].filter(c => c >= 0 && c <= N).sort((a, b) => a - b);
  for (let k = 0; k < cs.length - 1; k++) {
    const a = cs[k], b = cs[k + 1], s = coAt(a), ya = y0 + a * fh, yb = y0 + b * fh, P = sc(P0, s);
    if (vu.some(v => a >= v && b <= v + 2)) {
      const t = texVuon.clone(); t.needsUpdate = true;
      mesh(tuongGeo(sc(P0, s * (1 - 2.6 / kt)), ya, yb, 30, yb - ya, muot), lam('#ffffff', { map: t, emissive: new T3.Color('#ffffff'), emissiveMap: t, emissiveIntensity: .55 }), G);
      mesh(phienGeo(sc(P0, s * (1 + .5 / kt)), ya, .55), B.matVien, G);
      mesh(phienGeo(sc(P0, s * (1 + .5 / kt)), yb - .55, .55), B.matVien, G);
    } else {
      mesh(tuongGeo(P, ya, yb, NB * bw, NF * fh, muot), matMat(B.texKinh, null, null, null, `${i}p${a}`, B.MT.phat, B.texDen, B), G);
    }
    mesh(phienGeo(P, yb, 0), matSan, G, false);
  }
  if (y0 > 0) {                                                   // chân cột + sảnh
    const Pl = sc(P0, .62); mesh(tuongGeo(Pl, 0, y0, 8, y0, muot), matSanh, G); mesh(phienGeo(Pl, y0 - .05, 0), matSan, G, false);
    let s = 0; const n = P0.length, buoc = 7.5;
    for (let e = 0; e < n; e++) {
      const a = P0[e], b = P0[(e + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      for (; s <= L; s += buoc) { const u = s / (L || 1); hop(1.2, y0, 1.2, matCot, (a[0] + (b[0] - a[0]) * u) * .97, y0 / 2, (a[1] + (b[1] - a[1]) * u) * .97, G); }
      s -= L;
    }
  }
  const sT = coAt(N), Pt = sc(P0, sT), yt = y0 + N * fh;          // mái + hộp kỹ thuật + vương miện
  mesh(phienGeo(Pt, yt, .7), lam(B.MT.mai_tren || '#b5babd'), G);
  const r = rng('mai' + i);
  for (let k = 0, thu = 0; k < 4 && thu < 40; thu++) {
    const x = (bb.x0 + bb.w * (.25 + .5 * r())) * sT, z = (bb.z0 + bb.d * (.25 + .5 * r())) * sT;
    if (!trongDG(Pt, x, z)) continue;
    hop(3 + r() * 5, 2 + r() * 2.5, 3 + r() * 5, lam('#8a9097'), x, yt + 1.5, z, G); k++;
  }
  const ch = T.mai_cao ?? 2.4 * fh;
  if (ch > 0) mesh(tuongGeo(sc(Pt, 1 + .3 / kt), yt, yt + ch, 24, ch, muot), matMaiTop(B.MT, texMaiLap((T.mai || 'song') === 'song', 'm' + i, B.MT)), G);
}

// MẶT ĐỨNG ẢNH THẬT (`anh_mat` của tháp — texture nắn phẳng từ ảnh phối cảnh bằng run.py mat-anh): phủ trọn mặt dài từ chân tới đỉnh,
// ảnh đã có ánh sáng sẵn nên phần lớn là tự phát (`anh_phat`), chỉ 1 phần nhận nắng để mặt khuất vẫn sẫm hơn mặt đón nắng
const _texAnh = {};
function texAnh(u) {
  if (_texAnh[u]) return _texAnh[u];
  const t = new T3.Texture(); t.anisotropy = maxAniso; _texAnh[u] = t;
  cho.push(loader.loadAsync(u).then(x => { t.image = x.image; t.needsUpdate = true; }).catch(() => console.warn('bds3d_3d: không nạp được mặt ảnh ' + u)));
  return t;
}
const matAnh = (T, u) => { const t = texAnh(u || T.anh_mat_url), k = T.anh_phat ?? .6, c = T.anh_sang ?? .4;
  return aoChan(lam(new T3.Color(c, c, c), { map: t, emissive: new T3.Color('#ffffff'), emissiveMap: t, emissiveIntensity: k })); };
function thap(T, i) {
  const G = new T3.Group(); G.position.set(T.x || 0, T.cao_nen || 0, T.z || 0); G.rotation.y = -(T.xoay || 0) * D2R; G0.add(G);
  const B = boMau(T), P0 = chanDaGiac(T);
  if (P0) { const bb = hopBao(P0); CHAN.push({ G, w: bb.w, d: bb.d }); thapDa(T, i, G, B, P0); return G; }
  const fh = T.cao_tang || 3.3, N = T.tang | 0, w = T.rong, d = T.sau, y0 = T.chan || 0, bw = T.buoc_cot || 3.6;
  const matVien = B.matVien;
  CHAN.push({ G, w, d });
  const vu = T.anh_mat_url ? [] : [...new Set((T.vuon || []).map(v => v | 0))].filter(v => v > 0 && v < N - 2).sort((a, b) => a - b);
  let f = 0; const seg = [];
  for (const v of vu) { if (v > f) seg.push([f, v, 'k']); seg.push([v, v + 2, 'v']); f = v + 2; }
  if (f < N) seg.push([f, N, 'k']);
  for (const [a, b, k] of seg) {
    const h = (b - a) * fh, yc = y0 + a * fh + h / 2;
    if (k === 'k') {
      let mx = matMat(B.texKinh, d, b - a, bw, `${i}x${a}`, B.MT.phat, B.texDen, B), mz = matMat(B.texKinh, w, b - a, bw, `${i}z${a}`, B.MT.phat, B.texDen, B);
      if (B.texHoi) {                                             // tường hồi ở 2 mặt ngắn
        const t = B.texHoi.clone(); t.needsUpdate = true; t.repeat.set(1, (b - a) / NF);
        const mh = aoChan(lam('#ffffff', { map: t, emissive: new T3.Color(B.MT.phat || '#3a4656'), emissiveIntensity: .3 }));
        if (d <= w) mx = mh; else mz = mh;
      }
      if (T.anh_mat_url) { const ma = matAnh(T); if (d <= w) mz = ma; else mx = ma; }
      if (T.anh_hoi_url) { const mh2 = matAnh(T, T.anh_hoi_url); if (d <= w) mx = mh2; else mz = mh2; }   // tường hồi ảnh thật
      hop(w, h, d, [mx, mx, matSan, matSan, mz, mz], 0, yc, 0, G);
    } else {
      const mv = matVuon(Math.max(w, d), h);
      hop(w - 2.6, h, d - 2.6, [mv, mv, matSan, matSan, mv, mv], 0, yc, 0, G);
      hop(w + .5, .55, d + .5, matVien, 0, y0 + a * fh + .28, 0, G);
      hop(w + .5, .55, d + .5, matVien, 0, y0 + b * fh - .28, 0, G);
    }
  }
  // chân cột + sảnh
  if (y0 > 0) {
    hop(w * .62, y0, d * .62, matSanh, 0, y0 / 2, 0, G);
    const nx = Math.max(2, Math.round(w / 7.5)), nz = Math.max(2, Math.round(d / 7.5));
    for (let a = 0; a <= nx; a++) for (const s of [-1, 1]) hop(1.2, y0, 1.2, matCot, -w / 2 + .6 + a * (w - 1.2) / nx, y0 / 2, s * (d / 2 - .6), G);
    for (let a = 1; a < nz; a++) for (const s of [-1, 1]) hop(1.2, y0, 1.2, matCot, s * (w / 2 - .6), y0 / 2, -d / 2 + .6 + a * (d - 1.2) / nz, G);
  }
  // mái + vương miện
  const yt = y0 + N * fh;
  hop(w, .7, d, lam(B.MT.mai_tren || '#b5babd'), 0, yt + .35, 0, G);
  const r = rng('mai' + i);
  for (let k = 0; k < 4; k++) hop(3 + r() * 5, 2 + r() * 2.5, 3 + r() * 5, lam('#8a9097'), (r() - .5) * w * .5, yt + 1.5, (r() - .5) * d * .5, G);
  const ch = T.mai_cao ?? 2.4 * fh, song = (T.mai || 'song') === 'song';
  if (ch > 0) {
    const mt = matMaiTop(B.MT, texMai(song, 'm' + i, B.MT)), mt2 = matMaiTop(B.MT, texMai(song, 'n' + i, B.MT));
    const mat_ = (ww, m) => { const p = new T3.Mesh(new T3.PlaneGeometry(ww, ch), m); p.castShadow = true; return p; };
    const yc = yt + ch / 2;
    let p = mat_(w + .3, mt); p.position.set(0, yc, d / 2 + .15); G.add(p);
    p = mat_(w + .3, mt); p.position.set(0, yc, -d / 2 - .15); p.rotation.y = Math.PI; G.add(p);
    p = mat_(d + .3, mt2); p.position.set(w / 2 + .15, yc, 0); p.rotation.y = Math.PI / 2; G.add(p);
    p = mat_(d + .3, mt2); p.position.set(-w / 2 - .15, yc, 0); p.rotation.y = -Math.PI / 2; G.add(p);
  }
  // tầng đỉnh sáng đèn (vương miện ấm dưới viền mái) — `mau.den_dinh`
  if (B.MT.den_dinh && !T.anh_mat_url) {
    const c = new T3.Color(B.MT.den_dinh), nd = B.MT.den_dinh_tang ?? 1;
    hop(w + .12, fh * nd - .25, d + .12, lam('#ffffff', { color: c.clone().multiplyScalar(.55), emissive: c, emissiveIntensity: .8 }), 0, yt - fh * nd / 2, 0, G, false);
  }
  // khung viền module nổi (`vien`): 2 trụ góc bọc kín đầu hồi + `giua` trụ chia module + vành đỉnh — kiểu "khung tranh" đồng / trắng
  const V = T.vien;
  if (V) {
    const vr = +V.rong || 2.2, vn = V.noi ?? .45, hp = V.dinh ?? 3.2, giua = V.giua | 0, cm = V.mau || B.MT.tuong_hoi || '#e8e7e2';
    const mv = aoChan(lam(cm, { emissive: new T3.Color(cm), emissiveIntensity: V.phat ?? .14 }));
    const H_ = yt + hp, dai = w >= d, L = dai ? w : d, S = dai ? d : w;
    const cot = (u, rr, m = mv) => dai ? hop(rr, H_, S + 2 * vn, m, u, H_ / 2, 0, G) : hop(S + 2 * vn, H_, rr, m, 0, H_ / 2, u, G);
    // trụ góc bọc kín đầu hồi → có `anh_hoi` thì dán ảnh tường hồi thật lên MẶT NGOÀI trụ (không thì ảnh hồi bị trụ che mất)
    // không có ảnh hồi thì mặt ngoài trụ góc mang texture tường hồi (dải cửa giữa từng tầng) thay vì mảng màu trơn trông như khối nhựa
    let mHoi = T.anh_hoi_url ? matAnh(T, T.anh_hoi_url) : null;
    if (!mHoi && B.texHoi) {
      const t = B.texHoi.clone(); t.needsUpdate = true; t.repeat.set(1, H_ / fh / NF);
      mHoi = aoChan(lam('#ffffff', { map: t, emissive: new T3.Color('#ffffff'), emissiveMap: t, emissiveIntensity: V.phat ?? .14 }));
    }
    for (const sg of [-1, 1]) {
      let m = mv;
      if (mHoi) { m = [mv, mv, mv, mv, mv, mv]; m[dai ? (sg > 0 ? 0 : 1) : (sg > 0 ? 4 : 5)] = mHoi; }
      cot(sg * (L / 2 - vr / 2 + vn / 2), vr + vn, m);
    }
    if (!T.anh_mat_url) for (let k = 1; k <= giua; k++) cot(-L / 2 + L * k / (giua + 1), vr);
    const yp = yt + hp / 2, dv = vr * .7;
    for (const sg of [-1, 1]) {
      if (dai) hop(w + 2 * vn, hp, dv, mv, 0, yp, sg * (d / 2 + vn - dv / 2), G);
      else hop(dv, hp, d + 2 * vn, mv, sg * (w / 2 + vn - dv / 2), yp, 0, G);
    }
    CHAN[CHAN.length - 1].w = w + 2 * vn; CHAN[CHAN.length - 1].d = d + 2 * vn;
  }
  return G;
}

const CAY = { n: 0, list: [] };
function cauDua(parent, x, y, z, h, seed) {           // cây dừa / cọ thấp đa giác
  const r = rng(seed), G = new T3.Group(); G.position.set(x, y, z); parent.add(G);
  const than = new T3.Mesh(new T3.CylinderGeometry(.16, .26, h, 5), lam('#6e5a45')); than.position.y = h / 2; than.castShadow = true; G.add(than);
  const la = lam(['#3e6e37', '#4b7d3c', '#356231'][Math.floor(r() * 3)], { side: T3.DoubleSide });
  for (let k = 0; k < 7; k++) {
    const g = new T3.PlaneGeometry(.9, 3.6); g.translate(0, 1.8, 0);
    const m = new T3.Mesh(g, la); m.position.y = h; m.rotation.order = 'YXZ'; m.rotation.y = k * 2 * Math.PI / 7 + r(); m.rotation.x = 1.05 + r() * .35; m.castShadow = true; G.add(m);
  }
}
function de(Dz, i) {
  const G = new T3.Group(); G.position.set(Dz.x || 0, Dz.cao_nen || 0, Dz.z || 0); G.rotation.y = -(Dz.xoay || 0) * D2R; G0.add(G);
  const w = Dz.rong, d = Dz.sau, h = Dz.cao || 4.5 * (Dz.tang || 3);
  CHAN.push({ G, w, d });
  const mk_ = wm => { const t = texDe.clone(); t.needsUpdate = true; t.repeat.set(wm / 26, h / 9); return aoChan(lam('#ffffff', { map: t, emissive: new T3.Color('#2a1a0c'), emissiveIntensity: .35 })); };
  const mx = mk_(d), mz = mk_(w);
  hop(w, h, d, [mx, mx, lam(MAU.san_thuong), matSan, mz, mz], 0, h / 2, 0, G);
  hop(w + .7, .8, d + .7, MAU.vien_de ? lam(MAU.vien_de, { emissive: new T3.Color(MAU.vien_de), emissiveIntensity: .2 }) : matVien, 0, h + .2, 0, G);   // mép đỉnh đế
  hop(w + .3, .35, d + .3, matVien, 0, h * .34, 0, G, false);                        // chỉ vàng thân đế
  if (Dz.ho_boi) {
    const B = Dz.ho_boi, g = new T3.PlaneGeometry(B.rong, B.sau); g.rotateX(-Math.PI / 2);
    const m = new T3.Mesh(g, new T3.MeshLambertMaterial({ map: texHo, emissive: new T3.Color(MAU.ho), emissiveIntensity: .25 })); m.position.set(B.x || 0, h + .66, B.z || 0); m.receiveShadow = true; G.add(m);
  }
  const r = rng('de' + i), nc = Dz.cay ?? Math.round((w + d) / 9);
  for (let k = 0; k < nc; k++) {
    const s = r() * 2 * (w + d); let x, z;
    if (s < w) { x = -w / 2 + s; z = -d / 2 + 1.6; } else if (s < w + d) { x = w / 2 - 1.6; z = -d / 2 + s - w; } else if (s < 2 * w + d) { x = w / 2 - (s - w - d); z = d / 2 - 1.6; } else { x = -w / 2 + 1.6; z = d / 2 - (s - 2 * w - d); }
    cauDua(G, x, h + .6, z, 4 + r() * 3, 'c' + i + k);
  }
}
// khối tự do: nhà phố / biệt thự / khối thấp (kieu kinh | de | tuong; mai phang | ngoi)
const texTuong = canvasTex(4 * 56, 2 * 50, (g) => {
  const r = rng('tuong' + (CT.seed || ''));
  g.fillStyle = MAU.tuong || '#ece8df'; g.fillRect(0, 0, 224, 100);
  for (let f = 0; f < 2; f++) for (let b = 0; b < 4; b++) {
    const x = b * 56, y = f * 50;
    g.fillStyle = r() < .3 ? '#d9a35a' : '#3a4350'; g.fillRect(x + 12, y + 10, 32, 28);
    g.fillStyle = 'rgba(255,255,255,.55)'; g.fillRect(x + 12, y + 10, 32, 3);
    g.fillStyle = '#c9c3b7'; g.fillRect(x, y + 44, 56, 6);
  }
}, true);
function khoi(K, i) {
  const G = new T3.Group(); G.position.set(K.x || 0, K.cao_nen || 0, K.z || 0); G.rotation.y = -(K.xoay || 0) * D2R; G0.add(G);
  const w = K.rong, d = K.sau, h = K.cao || 3.6 * (K.tang || 3), kieu = K.kieu || 'tuong';
  CHAN.push({ G, w, d });
  let mx, mz;
  if (kieu === 'kinh') { const nf = Math.max(1, Math.round(h / 3.3)); mx = matMat(texKinh, d, nf, 3.6, 'k' + i + 'x'); mz = matMat(texKinh, w, nf, 3.6, 'k' + i + 'z'); }
  else {
    const tx = kieu === 'de' ? texDe : texTuong, sx = kieu === 'de' ? 26 : 14, sy = kieu === 'de' ? 9 : 7.2;
    const mm = wm => { const t = tx.clone(); t.needsUpdate = true; t.repeat.set(wm / sx, h / sy); return lam('#ffffff', { map: t, emissive: new T3.Color(kieu === 'de' ? '#2a1a0c' : '#3a3630'), emissiveIntensity: .3 }); };
    mx = mm(d); mz = mm(w);
  }
  const top = lam(K.mau_mai || MAU.san_thuong);
  hop(w, h, d, [mx, mx, top, matSan, mz, mz], 0, h / 2, 0, G);
  if (K.mai === 'ngoi') {                                       // mái dốc 2 phía dọc cạnh dài
    const dai = Math.max(w, d), ngan = Math.min(w, d), cao = ngan * .32;
    const sh = new T3.Shape(); sh.moveTo(-ngan / 2 - .5, 0); sh.lineTo(ngan / 2 + .5, 0); sh.lineTo(0, cao); sh.closePath();
    const g = new T3.ExtrudeGeometry(sh, { depth: dai + .8, bevelEnabled: false }); g.translate(0, 0, -(dai + .8) / 2);
    const m = new T3.Mesh(g, lam(K.mau_ngoi || '#a8513a')); m.position.y = h; if (w > d) m.rotation.y = Math.PI / 2; m.castShadow = true; m.receiveShadow = true; G.add(m);
  } else if (kieu !== 'de') hop(w + .4, .5, d + .4, lam('#d8d4cb'), 0, h + .25, 0, G);
}
(CT.de || []).forEach(de);
(CT.thap || []).forEach(thap);
(CT.khoi || []).forEach(khoi);

/* ---------------- mặt đất trong khu: hồ bơi, sân thể thao, đường dạo, sân lát, cầu đi bộ trên cao ----------------
   Toạ độ MÔ HÌNH (như tháp: gốc vi_tri, xoay theo `xoay`). NE = vùng cây sân vườn phải né.
   Vật liệu phẳng để transparent: lớp cỏ san_vuon là transparent → luôn vẽ SAU mọi vật đục, sẽ phủ mất sân nếu sân đục. */
const NE = [];
{
  const texSanTT = (k) => canvasTex(512, 256, (g, w, h) => {
    const M_ = { tennis: ['#3f7a5e', '#3a6fa0', .65, .6], bong_ro: ['#7a4a3a', '#c06a3c', .78, .72], pickleball: ['#2f6b55', '#3b7fb5', .55, .55], bong_da: ['#3f8a46', '#4b9a52', .9, .86] }[k] || ['#3f7a5e', '#3a6fa0', .65, .6];
    g.fillStyle = M_[0]; g.fillRect(0, 0, w, h);
    const iw = w * M_[2], ih = h * M_[3], x0 = (w - iw) / 2, y0 = (h - ih) / 2;
    g.fillStyle = M_[1]; g.fillRect(x0, y0, iw, ih);
    g.strokeStyle = '#f4f4ef'; g.lineWidth = 4; g.strokeRect(x0, y0, iw, ih);
    g.beginPath(); g.moveTo(w / 2, y0); g.lineTo(w / 2, y0 + ih);
    if (k === 'bong_ro' || k === 'bong_da') { g.moveTo(w / 2 + ih * .18, h / 2); g.arc(w / 2, h / 2, ih * .18, 0, 7); }
    else { g.moveTo(x0 + iw * .23, y0 + ih * .12); g.lineTo(x0 + iw * .23, y0 + ih * .88); g.moveTo(x0 + iw * .77, y0 + ih * .12); g.lineTo(x0 + iw * .77, y0 + ih * .88);
           g.moveTo(x0 + iw * .23, h / 2); g.lineTo(x0 + iw * .77, h / 2); g.moveTo(x0, y0 + ih * .12); g.lineTo(x0 + iw, y0 + ih * .12); g.moveTo(x0, y0 + ih * .88); g.lineTo(x0 + iw, y0 + ih * .88); }
    g.stroke();
  });
  const texGach = canvasTex(256, 256, (g, w, h) => {
    const r = rng('gach'); g.fillStyle = '#cfc7b8'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 32) { g.fillStyle = `rgba(${150 + r() * 40 | 0},${140 + r() * 40 | 0},${125 + r() * 35 | 0},.35)`; g.fillRect(x + 1, y + 1, 30, 30); }
    g.strokeStyle = 'rgba(120,110,95,.35)'; g.lineWidth = 1.5; for (let k = 0; k <= w; k += 32) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, h); g.moveTo(0, k); g.lineTo(w, k); g.stroke(); }
  }, true);
  const phang = (P, mat, y, ro) => { const m = new T3.Mesh(phienGeo(P, y, 0), mat); m.receiveShadow = true; m.renderOrder = ro; G0.add(m); return m; };
  const chuNhat = (o, w, d) => { const a = -(o.xoay || 0) * D2R, c = Math.cos(a), s = Math.sin(a), x = o.x || 0, z = o.z || 0;
    return [[w / 2, d / 2], [-w / 2, d / 2], [-w / 2, -d / 2], [w / 2, -d / 2]].map(([u, v]) => [x + u * c + v * s, z - u * s + v * c]); };
  const daGiacCua = (o, w, d) => (Array.isArray(o.diem) && o.diem.length >= 3) ? o.diem.map(p => [+p[0], +p[1]]) : chuNhat(o, +o.rong || w, +o.sau || d);
  const no = (P, k) => { const cx = P.reduce((s, p) => s + p[0], 0) / P.length, cz = P.reduce((s, p) => s + p[1], 0) / P.length;
    return P.map(([x, z]) => { const dx = x - cx, dz = z - cz, l = Math.hypot(dx, dz) || 1; return [x + dx / l * k, z + dz / l * k]; }); };
  const daiGeo = (L, rong, y) => {            // dải theo đường gấp khúc (đường dạo / mặt cầu), UV dọc theo chiều dài
    const pos = [], uv = []; let s = 0;
    for (let i = 0; i < L.length - 1; i++) {
      const [x1, z1] = L[i], [x2, z2] = L[i + 1], l = Math.hypot(x2 - x1, z2 - z1) || 1, nx = -(z2 - z1) / l * rong / 2, nz = (x2 - x1) / l * rong / 2;
      const q = [[x1 - nx, z1 - nz, s, 0], [x2 - nx, z2 - nz, s + l, 0], [x2 + nx, z2 + nz, s + l, 1], [x1 - nx, z1 - nz, s, 0], [x2 + nx, z2 + nz, s + l, 1], [x1 + nx, z1 + nz, s, 1]];
      const up = (x2 - x1) * (z1 + nz - z1) - (z2 - z1) * (x1 + nx - x1) < 0;      // mặt hướng lên
      const thu = up ? q : [q[0], q[2], q[1], q[3], q[5], q[4]];
      for (const [x, z, u, v] of thu) { pos.push(x, y, z); uv.push(u / 8, v); }
      s += l;
    }
    const g = new T3.BufferGeometry(); g.setAttribute('position', new T3.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new T3.Float32BufferAttribute(uv, 2)); g.computeVertexNormals(); return g;
  };
  (CT.mat_dat || []).forEach((o, i) => {
    const loai = o.loai || 'san';
    if (loai === 'ho') {                      // hồ bơi: sàn đá quanh + mặt nước
      const P = daGiacCua(o, 25, 12), ve = o.ve ?? 2.5;
      phang(no(P, ve), lam(o.mau_ve || '#d9d3c5'), .05, -27);
      const t = texHo.clone(); t.needsUpdate = true;
      phang(P, new T3.MeshLambertMaterial({ map: t, emissive: new T3.Color(MAU.ho), emissiveIntensity: .25, transparent: true, depthWrite: false }), .07, -26);
      NE.push({ P: no(P, ve + 1) });
    } else if (loai === 'san_tt') {           // sân thể thao (tennis / bong_ro / pickleball / bong_da)
      const k = o.kieu || 'tennis', S_ = { tennis: [36, 18], bong_ro: [32, 19], pickleball: [20, 10], bong_da: [42, 25] }[k] || [36, 18];
      const P = chuNhat(o, +o.rong || S_[0], +o.sau || S_[1]);
      const g = phienGeo(P, .06, 0); const bb = hopBao(P);
      // UV theo trục sân (bỏ UV mặc định của Shape)
      const a = -(o.xoay || 0) * D2R, c = Math.cos(a), s = Math.sin(a), pa = g.attributes.position, uv = [];
      for (let j = 0; j < pa.count; j++) { const dx = pa.getX(j) - (o.x || 0), dz = pa.getZ(j) - (o.z || 0); uv.push((dx * c - dz * s) / (+o.rong || S_[0]) + .5, (dx * s + dz * c) / (+o.sau || S_[1]) + .5); }
      g.setAttribute('uv', new T3.Float32BufferAttribute(uv, 2));
      const m = new T3.Mesh(g, new T3.MeshLambertMaterial({ map: texSanTT(k), transparent: true, depthWrite: false })); m.receiveShadow = true; m.renderOrder = -26; G0.add(m);
      NE.push({ P: no(P, 1.5) }); void bb;
    } else if (loai === 'san') {              // sân lát / quảng trường
      const P = daGiacCua(o, 30, 20), t = texGach.clone(); t.needsUpdate = true; t.repeat.set(1 / 12, 1 / 12);
      phang(P, new T3.MeshLambertMaterial({ map: t, color: new T3.Color(o.mau || '#ffffff'), transparent: true, depthWrite: false }), .05, -27);
      NE.push({ P: no(P, 1) });
    } else if (loai === 'duong' || loai === 'cau_tren_cao') {
      const L = (o.diem || []).map(p => [+p[0], +p[1]]); if (L.length < 2) return;
      const rong = +o.rong || (loai === 'duong' ? 3 : 3.2);
      if (loai === 'duong') {
        const t = texGach.clone(); t.needsUpdate = true;
        const m = new T3.Mesh(daiGeo(L, rong, .055), new T3.MeshLambertMaterial({ map: t, color: new T3.Color(o.mau || '#efe6d4'), transparent: true, depthWrite: false }));
        m.receiveShadow = true; m.renderOrder = -26; G0.add(m); NE.push({ L, r: rong / 2 + 1 });
      } else {                                // cầu đi bộ trên tán cây: mặt cầu + lan can + cột
        const cao = +o.cao || 7, matD = lam(o.mau || '#d9cdb6'), matL = lam('#eef0ee'), matC = lam('#9a9488');
        mesh(daiGeo(L, rong, cao), matD, G0); mesh(daiGeo(L, rong, cao - .45), matC, G0, false);
        for (let k = 0; k < L.length - 1; k++) {
          const [x1, z1] = L[k], [x2, z2] = L[k + 1], l = Math.hypot(x2 - x1, z2 - z1), goc = Math.atan2(z2 - z1, x2 - x1), nx = -(z2 - z1) / l, nz = (x2 - x1) / l;
          for (const sd of [-1, 1]) { const m = hop(l, 1.1, .12, matL, (x1 + x2) / 2 + nx * sd * rong / 2, cao + .55, (z1 + z2) / 2 + nz * sd * rong / 2, G0); m.rotation.y = -goc; }
          for (let u = 0; u <= l; u += 9) { const c = new T3.Mesh(new T3.CylinderGeometry(.32, .38, cao, 8), matC); c.position.set(x1 + (x2 - x1) * u / l, cao / 2, z1 + (z2 - z1) * u / l); c.castShadow = true; G0.add(c); }
          const nut = new T3.Mesh(new T3.CylinderGeometry(rong / 2, rong / 2, .45, 16), matD); nut.position.set(x2, cao - .2, z2); G0.add(nut);
        }
      }
    }
  });
}

// cây (sprite tán tròn + bóng mềm) — dùng cho cây quanh khu đất và cây trong sân vườn
let _cay = null;
function trongCay(parent, x, z, rr, k) {
  if (!_cay) {
    const texCay = k => canvasTex(128, 128, (g, w, h) => {          // tán cây: khối tối + hàng trăm chùm lá nhỏ, sáng phía trên-trái
      const q = rng('tan' + k), C = [];
      for (let i = 0; i < 8; i++) { const a = q() * 6.28, rr = q() * 22; C.push([64 + Math.cos(a) * rr, 68 + Math.sin(a) * rr * .8, 17 + q() * 14]); }
      g.fillStyle = ['#29431f', '#253f1d', '#2e4a22'][k % 3];
      for (const [x, y, R] of C) { g.beginPath(); g.arc(x, y, R, 0, 7); g.fill(); }
      const trong = (x, y) => C.some(([cx, cy, R]) => (x - cx) ** 2 + (y - cy) ** 2 < R * R * .92);
      const T_ = [[42, 70, 34], [52, 82, 40], [38, 66, 30]][k % 3], S_ = [[118, 160, 82], [128, 168, 88], [104, 150, 76]][k % 3];
      for (let i = 0; i < 420; i++) {
        const x = 8 + q() * 112, y = 8 + q() * 112; if (!trong(x, y)) continue;
        const l = Math.max(0, Math.min(1, .55 - (x - 64) / 150 - (y - 64) / 110 + (q() - .5) * .5)), r = 2 + q() * 3.6;
        g.fillStyle = `rgba(${T_.map((c, j) => Math.round(c + (S_[j] - c) * l)).join(',')},.9)`;
        g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
      }
    });
    const bongTex = canvasTex(64, 64, (g) => { const gr = g.createRadialGradient(32, 32, 2, 32, 32, 31); gr.addColorStop(0, 'rgba(0,0,0,.55)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); });
    const bg = new T3.PlaneGeometry(1, 1); bg.rotateX(-Math.PI / 2);
    _cay = { mats: [0, 1, 2].map(texCay).map(t => new T3.SpriteMaterial({ map: t, alphaTest: .25, fog: true, color: new T3.Color(BUOI.nen || '#ffffff') })), bg,
             bm: new T3.MeshBasicMaterial({ map: bongTex, transparent: true, depthWrite: false }) };
  }
  const sp = new T3.Sprite(_cay.mats[k % 3]); sp.position.set(x, rr * 1.05 + 1.5, z); sp.scale.set(rr * 2.3, rr * 2.3, 1); parent.add(sp);
  const b = new T3.Mesh(_cay.bg, _cay.bm); b.position.set(x + 1.2, .08, z + 1.2); b.scale.set(rr * 2.4, 1, rr * 2.4); b.renderOrder = -15; parent.add(b);
}
{
  const n = CT.cay_quanh ?? 70, K = CT.khu || { rong: 120, sau: 110 }, r = rng('cay' + (CT.seed || ''));
  for (let k = 0; k < n; k++) {
    const s = r() * 2 * (K.rong + K.sau); let x, z; const j = (r() - .5) * 6;
    if (s < K.rong) { x = -K.rong / 2 + s; z = -K.sau / 2 + j; } else if (s < K.rong + K.sau) { x = K.rong / 2 + j; z = -K.sau / 2 + s - K.rong; }
    else if (s < 2 * K.rong + K.sau) { x = K.rong / 2 - (s - K.rong - K.sau); z = K.sau / 2 + j; } else { x = -K.rong / 2 + j; z = K.sau / 2 - (s - 2 * K.rong - K.sau); }
    trongCay(G0, x, z, 2.6 + r() * 2.6, k);
  }
  if (CT.khu && CT.khu.toi !== 0) {                         // nền lô đất sẫm nhẹ
    const g = new T3.PlaneGeometry(K.rong, K.sau); g.rotateX(-Math.PI / 2);
    const m = new T3.Mesh(g, new T3.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: CT.khu.toi ?? .3, depthWrite: false }));
    m.position.y = .03; m.renderOrder = -30; G0.add(m);
  }
}
// sân vườn: đa giác cỏ phủ lên công trường trên ảnh vệ tinh + cây rải bên trong (né chân công trình).
// Toạ độ CẢNH (gốc vi_tri, x Đông, z Nam), KHÔNG xoay theo công trình — vẽ thẳng theo ranh đất.
{
  const SV = CT.san_vuon || [];
  if (SV.length) {
    S.updateMatrixWorld(true);
    const texCo = canvasTex(256, 256, (g, w, h) => {
      const r = rng('co');
      g.fillStyle = '#5a7843'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 1400; i++) {
        const R = 1.5 + r() * 7; g.fillStyle = ['rgba(78,112,56,.3)', 'rgba(112,140,74,.26)', 'rgba(62,92,46,.32)', 'rgba(140,146,110,.14)'][i % 4];
        g.beginPath(); g.arc(r() * w, r() * h, R, 0, 7); g.fill();
      }
    }, true);
    const trong = (P, x, z) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, zi] = P[i], [xj, zj] = P[j]; if ((zi > z) !== (zj > z) && x < (xj - xi) * (z - zi) / (zj - zi) + xi) c = !c; } return c; };
    const v = new T3.Vector3();
    const dDoan = (x, z, [x1, z1], [x2, z2]) => { const dx = x2 - x1, dz = z2 - z1, l2 = dx * dx + dz * dz || 1, u = Math.max(0, Math.min(1, ((x - x1) * dx + (z - z1) * dz) / l2)); return Math.hypot(x - x1 - u * dx, z - z1 - u * dz); };
    const duoiNha = (x, z, le) => CHAN.some(C => { v.set(x, 0, z); C.G.worldToLocal(v); return Math.abs(v.x) < C.w / 2 + le && Math.abs(v.z) < C.d / 2 + le; })
      || (NE.length && (v.set(x, 0, z), G0.worldToLocal(v), NE.some(e => e.P ? trongDG(e.P, v.x, v.z) : e.L.some((p, k) => k && dDoan(v.x, v.z, e.L[k - 1], p) < e.r))));
    SV.forEach((V, i) => {
      const P = (V.diem || []).filter(p => Array.isArray(p) && p.length >= 2).map(p => [+p[0], +p[1]]);
      if (P.length < 3) return;
      const sh = new T3.Shape(); P.forEach(([x, z], k) => k ? sh.lineTo(x, -z) : sh.moveTo(x, -z));
      const g = new T3.ShapeGeometry(sh); g.rotateX(-Math.PI / 2);
      const t = texCo.clone(); t.needsUpdate = true; t.repeat.set(1 / 36, 1 / 36);
      const m = new T3.Mesh(g, new T3.MeshBasicMaterial({ map: t, color: new T3.Color(V.mau || '#ffffff').multiply(new T3.Color(BUOI.nen || '#ffffff')), transparent: true, opacity: V.dam ?? .94, depthWrite: false }));
      m.position.y = .04; m.renderOrder = -28; S.add(m);
      let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9; for (const [x, z] of P) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
      let dt = 0; for (let a = 0, b = P.length - 1; a < P.length; b = a++) dt += (P[b][0] - P[a][0]) * (P[b][1] + P[a][1]); dt = Math.abs(dt / 2);
      const n = V.cay ?? Math.round(dt / 260), r = rng('sv' + i + (CT.seed || ''));
      for (let k = 0, thu = 0; k < n && thu < n * 30; thu++) {
        const x = x0 + r() * (x1 - x0), z = z0 + r() * (z1 - z0);
        if (!trong(P, x, z) || duoiNha(x, z, 3)) continue;
        trongCay(S, x, z, 2.2 + r() * 2.8, k); k++;
      }
    });
  }
}

/* ---------------- vòng vàng trên mặt đất ---------------- */
const VONG = (M.vong || []).map(V => {
  const g = new T3.RingGeometry(.985, 1, 160); g.rotateX(-Math.PI / 2);
  const m = new T3.Mesh(g, new T3.MeshBasicMaterial({ color: new T3.Color(V.mau || '#f3d23c'), transparent: true, opacity: 0, depthWrite: false, fog: false }));
  m.position.set(V.x || 0, .4, V.z || 0); m.renderOrder = -10; S.add(m);
  const dg = new T3.CircleGeometry(1, 24); dg.rotateX(-Math.PI / 2);
  const dot = new T3.Mesh(dg, new T3.MeshBasicMaterial({ color: new T3.Color(V.mau || '#f3d23c'), transparent: true, opacity: 0, depthWrite: false, fog: false }));
  dot.renderOrder = -9; S.add(dot);
  return { V, m, dot };
});
function veVong(t) {
  for (const o of VONG) {
    const V = o.V, a = P(t, V.tu, .7), b = 1 - P(t, V.den - .35, .35, inOutS), on = a * b;
    o.m.visible = o.dot.visible = on > .003;
    const r = V.r * (.82 + .18 * a), w = Math.max(1.2, V.r * .012);
    o.m.scale.set(r, 1, r); o.m.material.opacity = .95 * on;
    const ang = (t - V.tu) * .55 + 1.1;
    o.dot.position.set((V.x || 0) + Math.cos(ang) * r, .45, (V.z || 0) + Math.sin(ang) * r); o.dot.scale.setScalar(w * 1.9); o.dot.material.opacity = on;
  }
}

/* ---------------- đường line sáng CHẠY quanh khu (ranh lô / tuyến đường) ---------------- */
// M.duong_vien: [{tu, den, diem:[[x,z],…] (toạ độ cảnh, x Đông z Nam), kin (khép vòng, mặc định true), rong (m, lõi sáng),
//                 cao (m nổi trên đất), mau, ve (giây vẽ hết vòng), chay (xung sáng chạy dọc, mặc định true), buoc (m giữa 2 xung)}]
const DVIEN = (M.duong_vien || []).filter(o => Array.isArray(o.diem) && o.diem.length >= 2).map((o, i) => {
  const kin = o.kin !== false && o.diem.length >= 3, P = o.diem.map(p => [+p[0], +p[1]]); if (kin) P.push(P[0]);
  const n = P.length, S_ = [0]; for (let k = 1; k < n; k++) S_.push(S_[k - 1] + Math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]));
  const L = S_[n - 1] || 1, rong = +o.rong || 3.2, NG = 3.4;                 // dải = lõi + quầng (NG × lõi)
  const pos = [], aS = [], aV = [], idx = [];
  for (let k = 0; k < n; k++) {
    const a = P[Math.max(0, k - 1)], b = P[Math.min(n - 1, k + 1)];
    let tx = b[0] - a[0], tz = b[1] - a[1];
    if (kin && (k === 0 || k === n - 1)) { const p = P[n - 2], q = P[1]; tx = q[0] - p[0]; tz = q[1] - p[1]; }
    const l = Math.hypot(tx, tz) || 1, nx = -tz / l, nz = tx / l, h = rong * NG / 2;
    for (const sg of [-1, 1]) { pos.push(P[k][0] + nx * h * sg, +o.cao || .7, P[k][1] + nz * h * sg); aS.push(S_[k] / L); aV.push(sg); }
    if (k) { const j = 2 * k; idx.push(j - 2, j - 1, j, j - 1, j + 1, j); }
  }
  const g = new T3.BufferGeometry();
  g.setAttribute('position', new T3.Float32BufferAttribute(pos, 3)); g.setAttribute('aS', new T3.Float32BufferAttribute(aS, 1)); g.setAttribute('aV', new T3.Float32BufferAttribute(aV, 1)); g.setIndex(idx);
  const m = new T3.ShaderMaterial({
    transparent: true, depthWrite: false, blending: T3.AdditiveBlending, side: T3.DoubleSide, fog: false,
    uniforms: { uMau: { value: new T3.Color(o.mau || '#ffd54a') }, uVe: { value: 0 }, uT: { value: 0 }, uOp: { value: 0 }, uL: { value: L }, uLoi: { value: 1 / NG },
      uChay: { value: o.chay === false ? 0 : 1 }, uBuoc: { value: +o.buoc || Math.max(30, L / 7) } },
    vertexShader: 'attribute float aS, aV; varying float vS, vV; void main(){ vS = aS; vV = aV; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: `uniform vec3 uMau; uniform float uVe, uT, uOp, uL, uLoi, uChay, uBuoc; varying float vS, vV;
void main(){
  float v = abs(vV), loi = 1.0 - smoothstep(uLoi * .7, uLoi, v), quang = pow(1.0 - v, 2.2) * .5;
  float hien = 1.0 - smoothstep(uVe - .0015, uVe, vS);
  float dau = exp(-pow((uVe - vS) * uL / 16.0, 2.0)) * step(uVe, .999) * hien;
  float x = fract(vS * uL / uBuoc - uT * .55), chay = uChay * (exp(-pow(x * uBuoc / 9.0, 2.0)) + exp(-pow((1.0 - x) * uBuoc / 9.0, 2.0)));
  vec3 c = uMau * (loi * (.95 + 1.1 * chay) + quang * (.55 + 1.2 * chay)) + vec3(1.0, .97, .9) * (dau * (loi * 1.6 + quang));
  gl_FragColor = vec4(c * hien * uOp, 1.0);
}` });
  const me = new T3.Mesh(g, m); me.renderOrder = -8; me.visible = false; S.add(me);
  return { o, me, m };
});
function veDuongVien(t) {
  for (const D of DVIEN) {
    const o = D.o, a = P(t, o.tu, .3), b = 1 - P(t, o.den - .45, .45, inOutS), on = a * b;
    D.me.visible = on > .003; if (!D.me.visible) continue;
    const U = D.m.uniforms; U.uOp.value = on; U.uT.value = t - o.tu; U.uVe.value = P(t, o.tu, +o.ve || 2.2, inOutS) * 1.002;
  }
}

/* ---------------- camera ---------------- */
const KC =(M.cam || []).slice().sort((a, b) => a.t - b.t);
const camVal = k => [k.nhin[0], k.nhin[1], k.nhin[2], k.goc, k.nghieng, Math.log(k.xa), k.fov || 32];
function camAt(t) {
  if (!KC.length) return camVal({ nhin: [0, 40, 0], goc: 20, nghieng: 32, xa: 600 });
  if (t <= KC[0].t) return camVal(KC[0]);
  if (t >= KC[KC.length - 1].t) return camVal(KC[KC.length - 1]);
  let i = 0; while (KC[i + 1].t <= t) i++;
  const k0 = KC[i - 1], k1 = KC[i], k2 = KC[i + 1], k3 = KC[i + 2];
  const v1 = camVal(k1), v2 = camVal(k2), dt = k2.t - k1.t, u = (t - k1.t) / dt;
  const v0 = k0 ? camVal(k0) : null, v3 = k3 ? camVal(k3) : null;
  const h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
  // Hermite đơn điệu (Fritsch–Carlson): không vọt quá khoá, 2 khoá trùng thì đứng yên, khoá đầu/cuối vận tốc 0
  const tan = (vp, tp, va, ta, vn, tn, j) => {
    if (!vp || !vn) return 0;
    const d0 = (va[j] - vp[j]) / (ta - tp), d1 = (vn[j] - va[j]) / (tn - ta);
    if (d0 * d1 <= 0) return 0;
    const m = (vn[j] - vp[j]) / (tn - tp);
    return Math.sign(m) * Math.min(Math.abs(m), 3 * Math.abs(d0), 3 * Math.abs(d1));
  };
  return v1.map((a, j) => {
    const b = v2[j];
    const m1 = tan(v0, k0 && k0.t, v1, k1.t, v2, k2.t, j) * dt;
    const m2 = tan(v1, k1.t, v2, k2.t, v3, k3 && k3.t, j) * dt;
    return h00 * a + h10 * m1 + h01 * b + h11 * m2;
  });
}
function datCam(t) {
  const [x, y, z, goc, ng, lx, fov] = camAt(t);
  const xa = Math.exp(lx), a = goc * D2R, e = clamp(ng, 2, 89.6) * D2R;
  cam.fov = fov; cam.position.set(x + Math.sin(a) * Math.cos(e) * xa, y + Math.sin(e) * xa, z + Math.cos(a) * Math.cos(e) * xa);
  cam.near = clamp(xa * .03, 2, 40);                   // near theo tầm xa: đủ chính xác độ sâu, hết z-fighting nhấp nháy ở mặt sát nhau
  cam.up.set(0, 1, 0); cam.lookAt(x, y, z); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const hcam = cam.position.y, dd = Math.hypot(cam.position.x - x, cam.position.z - z) + hcam;
  S.fog.near = Math.max(400, dd * 1.25); S.fog.far = Math.max(4000, dd * 9 + hcam * 6);
  sky.position.copy(cam.position);
}

/* ---------------- lớp chữ bám 3D ---------------- */
const v3 = new T3.Vector3();
function chieu(p) {                                   // toạ độ mô hình → px màn hình (null nếu sau lưng camera)
  v3.set(p[0], p[1], p[2]); G0.localToWorld(v3); v3.project(cam);
  if (v3.z > 1 || v3.z < -1) return null;
  return [(v3.x + 1) / 2 * W, (1 - v3.y) / 2 * H];
}
function chieuTheGioi(p) { v3.set(p[0], p[1], p[2]); v3.project(cam); if (v3.z > 1 || v3.z < -1) return null; return [(v3.x + 1) / 2 * W, (1 - v3.y) / 2 * H]; }
const CTH = (M.chu_thich || []).map(c => {
  const e = mk('ct', ov), dot = mk('dot', e), ln = mk('ln', e), tx = mk('tx', e, `<div class="c1">${esc(c.chu)}</div>${c.phu ? `<div class="c2">${esc(c.phu)}</div>` : ''}`);
  e.style.display = 'none'; return { c, e, dot, ln, tx };
});
function veChuThich(t) {
  for (const o of CTH) {
    const c = o.c;
    if (t < c.tu || t > c.den) { o.e.style.display = 'none'; continue; }
    const p = chieu(c.diem); if (!p) { o.e.style.display = 'none'; continue; }
    o.e.style.display = 'block';
    const out = 1 - P(t, c.den - .3, .3, inOutS), L = c.dai || 118, trai = (c.ben || 'trai') === 'trai';
    const a = P(t, c.tu, .28), b = P(t, c.tu + .08, .38), d = P(t, c.tu + .22, .34);
    o.e.style.transform = `translate(${p[0].toFixed(1)}px,${p[1].toFixed(1)}px)`; o.e.style.opacity = out.toFixed(3);
    o.dot.style.transform = `scale(${a.toFixed(3)})`;
    const lw = L * b; o.ln.style.width = lw.toFixed(1) + 'px'; o.ln.style.left = (trai ? -lw : 0).toFixed(1) + 'px';
    const tw = o.tx.offsetWidth;
    o.tx.style.left = (trai ? -L - 14 - tw : L + 14).toFixed(1) + 'px'; o.tx.style.top = (-o.tx.querySelector('.c1').offsetHeight - 6) + 'px';
    o.tx.style.textAlign = trai ? 'right' : 'left';
    o.tx.style.opacity = d.toFixed(3); const bl = (1 - d) * 8; o.tx.style.filter = bl > .05 ? `blur(${bl.toFixed(2)}px)` : 'none';
    o.tx.style.transform = `translateX(${((trai ? 1 : -1) * 18 * (1 - d)).toFixed(1)}px)`;
  }
}
const LOGO = M.logo ? (() => {
  const L = M.logo, e = mk('logo', ov), the = mk('the', e,
    (L.url ? `<img src="${esc(L.url)}">` : '') + (L.chu ? `<div><div class="l1">${esc(L.chu)}</div>${L.phu ? `<div class="l2">${esc(L.phu)}</div>` : ''}</div>` : ''));
  e.style.display = 'none'; return { L, e, the };
})() : null;
function veLogo(t) {
  if (!LOGO) return; const L = LOGO.L;
  if (t < L.tu || t > L.den) { LOGO.e.style.display = 'none'; return; }
  const p = chieu(L.diem || [0, 160, 0]); if (!p) { LOGO.e.style.display = 'none'; return; }
  LOGO.e.style.display = 'block';
  const a = P(t, L.tu, .5), b = 1 - P(t, L.den - .35, .35, inOutS), w = LOGO.e.offsetWidth, h = LOGO.e.offsetHeight;
  LOGO.e.style.transform = `translate(${(p[0] - w / 2).toFixed(1)}px,${(p[1] - h - 18 - 30 * (1 - a)).toFixed(1)}px) scale(${(.86 + .14 * a).toFixed(3)})`;
  LOGO.e.style.opacity = (a * b).toFixed(3); const bl = (1 - a) * 10; LOGO.e.style.filter = bl > .05 ? `blur(${bl.toFixed(2)}px)` : 'none';
}
const TAG = (M.dia_danh || []).map(d => { const e = mk('tag', ov, esc(d.chu)); e.style.display = 'none'; return { d, e }; });
function veTag(t) {
  for (const o of TAG) {
    const d = o.d; if (t < d.tu || t > d.den) { o.e.style.display = 'none'; continue; }
    const p = chieuTheGioi(d.diem); if (!p) { o.e.style.display = 'none'; continue; }
    o.e.style.display = 'block';
    const a = P(t, d.tu, .4), b = 1 - P(t, d.den - .3, .3, inOutS), w = o.e.offsetWidth, h = o.e.offsetHeight;
    o.e.style.transform = `translate(${(p[0] - w / 2).toFixed(1)}px,${(p[1] - h - 10 + 14 * (1 - a)).toFixed(1)}px) scale(${(.9 + .1 * a).toFixed(3)})`;
    o.e.style.opacity = (a * b).toFixed(3);
  }
}
const TIA = (M.tia || []).length ? mk('tia', ov) : null;
function veTia(t) {
  if (!TIA) return; let on = 0;
  for (const s of M.tia) on = Math.max(on, P(t, s.tu, .8, inOutS) * (1 - P(t, s.den - .6, .6, inOutS)) * (t >= s.tu - .01 && t <= s.den + .01));
  TIA.style.opacity = on.toFixed(3); TIA.style.transform = `rotate(${(Math.sin(t * .35) * 3).toFixed(2)}deg)`;
}

/* ---------------- vòng chính ---------------- */
function ve3d(t) {
  datCam(t); veVong(t); veDuongVien(t);
  const U = PM.uniforms; U.uN.value = cam.near; U.uF.value = cam.far; U.uFoc.value = Math.exp(camAt(t)[5]);
  R.setRenderTarget(RT); R.render(S, cam); R.setRenderTarget(null); R.render(PQ, PC);
  veChuThich(t); veLogo(t); veTag(t); veTia(t);
}
const baoCu = window.__bao_cao;
window.__bao_cao = () => {
  const out = baoCu ? baoCu() : [];
  const add = (loai, el, chu) => { if (el.style.display === 'none' || +el.style.opacity < .5) return; const r = el.getBoundingClientRect(); if (r.width > 0) out.push({ loai, chu: chu || el.textContent.trim(), x0: Math.round(r.left), y0: Math.round(r.top), x1: Math.round(r.right), y1: Math.round(r.bottom) }); };
  for (const o of CTH) if (o.e.style.display !== 'none' && +o.e.style.opacity > .5) add('chu_thich_3d', o.tx, o.c.chu);
  if (LOGO) add('logo_3d', LOGO.e, LOGO.L.chu || 'logo');
  for (const o of TAG) add('dia_danh_3d', o.e);
  return out;
};
const seekCu = window.__seek, readyCu = window.__ready;
window.__seek = async t => { ve3d(t); return seekCu(t); };
window.__m3_chieu = (p, t) => { datCam(t); return chieu(p); };
window.__ready = (async () => {
  await readyCu; await Promise.all(cho); await document.fonts.ready;
  await window.__seek(0);
})();
})();
