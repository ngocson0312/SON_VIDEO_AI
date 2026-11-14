// render.mjs — dựng khung từ trang HTML bằng Chrome headless qua DevTools Protocol.
// Không cần gói npm: dùng WebSocket có sẵn của Node >= 22 + Chrome / Edge đã cài trên máy.
//
// Trang HTML phải có:  window.__ready  (Promise)  và  window.__seek(t) -> Promise  (vẽ đúng khung ở giây t)
//
// Cách gọi:
//   node render.mjs --html <file.html> --out <ra.mp4> --fps 30 --tu 0 --den 35.8 [--crf 17] [--luong 3]
//   node render.mjs --html <file.html> --anh <thư mục> --times 1.2,3.4,...      (chụp khung lẻ ra .jpg)
//   node render.mjs --html <file.html> --report <ra.json> --times 1.2,3.4,...   (đo hộp chữ để tự kiểm)
//   node render.mjs --html <file.html> --khung <thư mục> --tu 0 --n 270 --fps 30 [--luong 3]   (xuất chuỗi ảnh 00001.jpg… — cảnh 3D làm footage)
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';

const W = +(process.env.DLN_W || 1920), H = +(process.env.DLN_H || 1080);

function args() {
  const a = process.argv.slice(2), o = {};
  for (let i = 0; i < a.length; i++) {
    if (a[i].startsWith('--')) { const k = a[i].slice(2); const v = (a[i + 1] && !a[i + 1].startsWith('--')) ? a[++i] : true; o[k] = v; }
  }
  return o;
}

function timChrome() {
  const env = process.env.DLN_CHROME || process.env.DLV_CHROME;
  const ung = [env,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe'),
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];
  for (const p of ung) if (p && fs.existsSync(p)) return p;
  throw new Error('⛔ Không tìm thấy Chrome / Edge. Cài Chrome hoặc đặt biến DLV_CHROME=<đường dẫn chrome.exe>');
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function moChrome() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dln-chrome-'));
  const proc = spawn(timChrome(), [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${dir}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--mute-audio',
    '--allow-file-access-from-files', '--disable-background-timer-throttling',
    '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
    '--force-device-scale-factor=1', `--window-size=${W},${H}`, '--font-render-hinting=none',
    '--disable-extensions', '--disable-features=Translate,MediaRouter',
    '--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--enable-unsafe-swiftshader', '--use-angle=default', 'about:blank'], { stdio: 'ignore' });
  const f = path.join(dir, 'DevToolsActivePort');
  for (let i = 0; i < 300 && !fs.existsSync(f); i++) await sleep(50);
  let port = 0;
  // Chrome đang ghi DevToolsActivePort → đọc có thể EBUSY (14/11/2026: đoạn 3 lỗi, Chrome sót làm node treo 15 phút) → thử lại;
  // hỏng hẳn thì GIẾT cả cây Chrome trước khi báo lỗi
  const giet = () => { try { if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(proc.pid), '/T', '/F'], { stdio: 'ignore' }); else proc.kill(); } catch { } };
  for (let i = 0; i < 160; i++) { let s = ''; try { s = fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n')[0] : ''; } catch { } if (s) { port = +s; break; } await sleep(50); }
  if (!port) { giet(); throw new Error('⛔ Chrome không mở cổng DevTools'); }
  let ds = [];
  for (let i = 0; i < 100; i++) { try { ds = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { } if (ds.find(d => d.type === 'page')) break; await sleep(50); }
  const page = ds.find(d => d.type === 'page');
  if (!page) { giet(); throw new Error('⛔ Chrome không mở được trang (DevTools)'); }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0; const cho = new Map(), nghe = new Map();
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && cho.has(m.id)) { const { r, j } = cho.get(m.id); cho.delete(m.id); m.error ? j(new Error(m.error.message)) : r(m.result); }
    else if (m.method && nghe.has(m.method)) { for (const fn of nghe.get(m.method)) fn(m.params); }
  };
  const send = (method, params = {}) => new Promise((r, j) => { const i = ++id; cho.set(i, { r, j }); ws.send(JSON.stringify({ id: i, method, params })); });
  const on = (m, fn) => { if (!nghe.has(m)) nghe.set(m, []); nghe.get(m).push(fn); };
  // Windows: proc.kill() chỉ giết tiến trình Chrome chính, tiến trình con còn giữ ống → node treo sau khi dựng xong (14/11/2026) → giết cả cây
  const dong = () => { try { ws.close(); } catch { } try { if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(proc.pid), '/T', '/F'], { stdio: 'ignore' }); else proc.kill(); } catch { } setTimeout(() => { try { fs.rmSync(dir, { recursive: true, force: true }); } catch { } }, 800); };
  return { send, on, dong };
}

async function moTrang(cdp, html) {
  const { send, on } = cdp;
  const loi = [];
  on('Runtime.exceptionThrown', p => loi.push(p.exceptionDetails?.exception?.description || p.exceptionDetails?.text));
  on('Runtime.consoleAPICalled', p => { if (p.type === 'error') loi.push(p.args.map(a => a.value ?? a.description).join(' ')); });
  await send('Runtime.enable'); await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 1 } });
  const xong = new Promise(r => on('Page.loadEventFired', r));
  await send('Page.navigate', { url: pathToFileURL(path.resolve(html)).href });
  await xong;
  const r = await send('Runtime.evaluate', { expression: 'window.__ready ? window.__ready.then(()=>"ok") : "khong_co_ready"', awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error('⛔ Trang lỗi khi nạp: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
  if (loi.length) console.error('⚠ Lỗi trong trang:', loi.slice(0, 5).join(' | '));
  return loi;
}

async function seek(cdp, t) {
  const r = await cdp.send('Runtime.evaluate', { expression: `window.__seek(${t.toFixed(4)})`, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(`⛔ __seek(${t}) lỗi: ` + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
  return r.result?.value;
}
async function chup(cdp, q = 95) {
  const r = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: q, fromSurface: true });
  return Buffer.from(r.data, 'base64');
}

async function renderDoan(html, tu, n, fps, ghi, nhan, q = 95) {
  const cdp = await moChrome();
  try {
    await moTrang(cdp, html);
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      await seek(cdp, tu + i / fps);
      await ghi(await chup(cdp, q));
      if (nhan && (i % 60 === 59 || i === n - 1)) {
        const s = (Date.now() - t0) / 1000; process.stdout.write(`  ${nhan}: ${i + 1}/${n} khung (${((i + 1) / s).toFixed(1)} khung/s)\n`);
      }
    }
  } finally { cdp.dong(); }
}

function ffmpegGhi(out, fps, crf) {
  const p = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', String(crf), '-pix_fmt', 'yuv420p', '-r', String(fps),
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const ghi = buf => new Promise(r => { if (!p.stdin.write(buf)) p.stdin.once('drain', r); else r(); });
  const xong = () => new Promise((r, j) => { p.on('close', c => c === 0 ? r() : j(new Error('ffmpeg mã hoá lỗi ' + c))); p.stdin.end(); });
  const huy = () => new Promise(r => { p.on('close', r); try { p.stdin.destroy(); } catch { } try { p.kill(); } catch { } });
  return { ghi, xong, huy };
}

async function main() {
  const o = args();
  if (!o.html) throw new Error('thiếu --html');
  const fps = +(o.fps || 30);
  if (o.times) {
    const ts = String(o.times).split(',').map(Number).filter(x => !isNaN(x));
    const cdp = await moChrome();
    try {
      await moTrang(cdp, o.html);
      const bao = [];
      if (o.anh) fs.mkdirSync(o.anh, { recursive: true });
      for (const t of ts) {
        const v = await seek(cdp, t);
        if (o.anh) fs.writeFileSync(path.join(o.anh, `k_${t.toFixed(2)}.jpg`), await chup(cdp, 92));
        if (o.report) {
          const r = await cdp.send('Runtime.evaluate', { expression: 'window.__bao_cao ? window.__bao_cao() : []', returnByValue: true });
          bao.push({ t, hop: r.result.value, seek: v });
        }
      }
      if (o.report) fs.writeFileSync(o.report, JSON.stringify(bao, null, 1));
    } finally { cdp.dong(); }
    return;
  }
  if (o.khung) {                       // chuỗi ảnh: mỗi luồng Chrome 1 đoạn, ghi thẳng 00001.jpg…
    const tu = +(o.tu || 0), N = +o.n, luong = Math.max(1, Math.min(+(o.luong || 3), 6)), q = +(o.q || 93);
    fs.mkdirSync(o.khung, { recursive: true });
    const per = Math.ceil(N / luong), viec = [];
    for (let k = 0; k < luong; k++) {
      const a = k * per, n = Math.min(per, N - a); if (n <= 0) break;
      viec.push((async () => {
        await sleep(600 * k);
        for (let lan = 1; ; lan++) {
          let i = 0;
          const ghi = async buf => { fs.writeFileSync(path.join(o.khung, String(a + (++i)).padStart(5, '0') + '.jpg'), buf); };
          try { await renderDoan(o.html, tu + a / fps, n, fps, ghi, `3D ${k + 1}/${luong}`, q); return; }
          catch (e) { if (lan >= 3) throw e; console.error(`⚠ đoạn 3D ${k + 1} lỗi (${e.message}) — thử lại lần ${lan + 1}`); await sleep(1500 * lan); }
        }
      })());
    }
    await Promise.all(viec); return;
  }
  const tu = +(o.tu || 0), den = +o.den;
  const N = Math.round((den - tu) * fps);
  const luong = Math.max(1, Math.min(+(o.luong || 3), 6));
  const crf = +(o.crf || 17);
  if (luong === 1 || N < 90) {
    const f = ffmpegGhi(o.out, fps, crf);
    await renderDoan(o.html, tu, N, fps, f.ghi, 'dựng');
    await f.xong(); return;
  }
  // chia đoạn cho nhiều Chrome chạy song song, mỗi đoạn mã hoá riêng rồi nối bằng copy (vẫn chỉ mã hoá 1 lần)
  const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(o.out)), '_doan_'));
  const per = Math.ceil(N / luong); const doan = [];
  for (let k = 0; k < luong; k++) {
    const a = k * per, n = Math.min(per, N - a); if (n <= 0) break;
    const f = path.join(tmp, `d${k}.mp4`);
    doan.push({ f, p: (async () => {      // mỗi đoạn tự thử lại tối đa 3 lần (Chrome thỉnh thoảng mở hụt khi chạy song song)
      await sleep(600 * k);
      for (let lan = 1; ; lan++) {
        const g = ffmpegGhi(f, fps, crf);
        try { await renderDoan(o.html, tu + a / fps, n, fps, g.ghi, `đoạn ${k + 1}/${luong}`); await g.xong(); return; }
        catch (e) { await g.huy(); if (lan >= 3) throw e; console.error(`⚠ đoạn ${k + 1} lỗi (${e.message}) — thử lại lần ${lan + 1}`); await sleep(1500 * lan); }
      }
    })() });
  }
  await Promise.all(doan.map(d => d.p));
  const ds = path.join(tmp, 'ds.txt');
  fs.writeFileSync(ds, doan.map(d => `file '${d.f.replace(/\\/g, '/')}'`).join('\n'));
  await new Promise((r, j) => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', ds, '-c', 'copy', o.out], { stdio: 'inherit' })
    .on('close', c => c === 0 ? r() : j(new Error('ffmpeg nối đoạn lỗi'))));
  fs.rmSync(tmp, { recursive: true, force: true });
}

main().then(() => setTimeout(() => process.exit(0), 1200), e => { console.error(e.message || e); process.exit(1); });   // xong là thoát, không chờ Chrome sót
