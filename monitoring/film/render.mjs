// Renders film.html frame by frame in Chromium (GPU canvas) and pipes the frames to ffmpeg (NVENC).
// Needs Playwright, an NVIDIA GPU, and Python with imageio_ffmpeg (for the ffmpeg binary).
//   node render.mjs stills <outDir> <scale> [seconds...]
//   node render.mjs video <out.mp4> <scale> [firstFrame] [lastFrame]
import { spawn } from 'node:child_process'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { createRequire } from 'node:module'
import os from 'node:os'

const here = dirname(fileURLToPath(import.meta.url))
// Playwright is resolved from PLAYWRIGHT_FROM (a folder that has it installed) or from this folder.
const require = createRequire(join(process.env.PLAYWRIGHT_FROM || here, 'package.json'))
const { chromium } = require('playwright')
const [mode, out, scaleArg, ...rest] = process.argv.slice(2)
const scale = Number(scaleArg || 1)
const JPEG = process.env.FMT === 'jpeg'
try { os.setPriority(process.pid, os.constants.priority.PRIORITY_BELOW_NORMAL) } catch {}

function ffmpegPath() {
  return new Promise((ok, fail) => {
    const p = spawn('python', ['-c', 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'])
    let s = ''
    p.stdout.on('data', (d) => { s += d })
    p.on('close', (code) => (code ? fail(new Error('imageio_ffmpeg not found')) : ok(s.trim())))
  })
}

const browser = await chromium.launch({
  channel: process.env.PW_CHANNEL || undefined,
  args: ['--enable-gpu', '--use-angle=d3d11', '--enable-gpu-rasterization', '--ignore-gpu-blocklist',
    '--force_high_performance_gpu', '--renderer-process-limit=1', '--allow-file-access-from-files', '--force-device-scale-factor=1'],
})
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })
page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message) })
await page.goto(pathToFileURL(join(here, 'film.html')).href + `?scale=${scale}`)
await page.evaluate(() => window.ready)
const { FPS, DURATION } = await page.evaluate(() => window.FILM)
const frame = (i, type, q) => page.evaluate(([n, ty, qq]) => { window.render(n); return document.getElementById('c').toDataURL(ty, qq).split(',')[1] }, [i, type, q])

if (mode === 'bench') {
  for (const sc of ['render', 'image/png', 'image/jpeg']) {
    const ms = await page.evaluate(async (ty) => { const t0 = performance.now(); for (let i = 600; i < 610; i++) { window.render(i); if (ty !== 'render') document.getElementById('c').toDataURL(ty, 0.97); else document.getElementById('c').getContext('2d').getImageData(0, 0, 1, 1) } return (performance.now() - t0) / 10 }, sc)
    console.log(sc, ms.toFixed(0), 'ms')
  }
} else if (mode === 'stills') {
  mkdirSync(out, { recursive: true })
  for (const s of rest.map(Number)) {
    writeFileSync(join(out, `t${s.toFixed(2).padStart(6, '0')}.png`), Buffer.from(await frame(Math.round(s * FPS), 'image/png'), 'base64'))
  }
} else {
  const total = Math.round(FPS * DURATION)
  const first = Number(rest[0] || 0), last = Number(rest[1] || total)
  const ff = spawn(await ffmpegPath(), [
    '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', JPEG ? 'mjpeg' : 'png', '-i', '-',
    '-vf', `scale=1080:1920:flags=lanczos,format=yuv420p`,
    '-c:v', 'h264_nvenc', '-preset', 'p7', '-tune', 'hq', '-rc', 'vbr', '-cq', '15', '-b:v', '0', '-maxrate', '40M', '-bufsize', '80M',
    '-spatial-aq', '1', '-temporal-aq', '1', '-aq-strength', '10', '-bf', '3', '-g', '120', '-profile:v', 'high',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', resolve(out),
  ], { stdio: ['pipe', 'inherit', 'inherit'] })
  try { os.setPriority(ff.pid, os.constants.priority.PRIORITY_BELOW_NORMAL) } catch {}
  const done = new Promise((ok) => ff.on('close', ok))
  const t0 = Date.now()
  for (let i = first; i < last; i++) {
    const png = Buffer.from(await frame(i, JPEG ? 'image/jpeg' : 'image/png', 0.97), 'base64')
    if (!ff.stdin.write(png)) await new Promise((ok) => ff.stdin.once('drain', ok))
    if (i % 120 === 0) process.stderr.write(`frame ${i}/${last} ${((Date.now() - t0) / 1000).toFixed(0)}s\n`)
  }
  ff.stdin.end()
  await done
}
await browser.close()
