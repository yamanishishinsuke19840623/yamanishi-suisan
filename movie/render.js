// brand-movie.html を MP4 に書き出す（Playwrightで全フレームを撮り、Web Audio の音と合わせて ffmpeg で結合）
// 使い方: node movie/render.js [--vertical] [--frames 0,60,120] [--out movie/brand-movie-16x9.mp4]
//   PLAYWRIGHT=/path/to/playwright  FFMPEG=/path/to/ffmpeg
//   FONTS_VIA_CURL=1  … ブラウザからGoogle Fontsに直接つながらない環境では curl で取得
const { spawn, execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, args = process.argv.slice(2);
const opt = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const vertical = args.includes('--vertical'), stills = opt('--frames');
const out = path.resolve(opt('--out') || path.join(root, vertical ? 'brand-movie-9x16.mp4' : 'brand-movie-16x9.mp4'));
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const MIME = { '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
(async () => {
  await new Promise(r => server.listen(0, r));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: vertical ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 } });
  if (process.env.FONTS_VIA_CURL) {
    const ua = await page.evaluate(() => navigator.userAgent.replace('Headless', ''));
    await page.route(/fonts\.(googleapis|gstatic)\.com/, route => {
      const u = route.request().url(), body = execFileSync('curl', ['-sSL', '-A', ua, u], { maxBuffer: 64 << 20 });
      route.fulfill({ body, contentType: u.includes('googleapis') ? 'text/css' : 'font/woff2', headers: { 'Access-Control-Allow-Origin': '*' } });
    });
  }
  await page.goto(`http://127.0.0.1:${server.address().port}/brand-movie.html${vertical ? '?format=vertical' : ''}`, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.__movie.ready);
  const grab = t => page.evaluate(t => { window.__movie.render(t); return document.getElementById('cv').toDataURL('image/jpeg', .95).split(',')[1]; }, t);
  if (stills) {
    for (const f of stills.split(',').map(Number)) {
      const file = path.join(path.dirname(out), `frame-${vertical ? 'v' : 'h'}-${String(f).padStart(3, '0')}.jpg`);
      fs.writeFileSync(file, Buffer.from(await grab(f / 30), 'base64')); console.log(file);
    }
  } else {
    const { DUR, FPS } = await page.evaluate(() => ({ DUR: window.__movie.DUR, FPS: window.__movie.FPS }));
    const wav = out.replace(/\.mp4$/, '.wav');
    fs.writeFileSync(wav, Buffer.from(await page.evaluate(() => window.__movie.renderAudioWav()), 'base64'));
    const ff = spawn(process.env.FFMPEG || 'ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', wav,
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-maxrate', '4M', '-bufsize', '8M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const total = Math.round(DUR * FPS);
    for (let f = 0; f < total; f++) {
      const buf = Buffer.from(await grab(f / FPS), 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 60 === 0) process.stderr.write(`frame ${f}/${total}\n`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); fs.unlinkSync(wav); console.log(out);
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
