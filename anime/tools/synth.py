# 山西水産「四代の物語」用の和風BGMと効果音を純Pythonで合成する
#   python3 synth.py <cues.json> <out.wav>
# 90BPM / 18小節 = 48秒。琴（Karplus-Strong）・太鼓・締太鼓・尺八風の笛・波
import json, math, random, struct, sys, wave

SR = 44100
BPM = 90
B = 60 / BPM
BAR = 4 * B
DUR = 18 * BAR
N = int(SR * DUR) + SR
L = [0.0] * N
R = [0.0] * N
rng = random.Random(1879)


def add(i, l, r=None):
    if 0 <= i < N:
        L[i] += l
        R[i] += l if r is None else r


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------- instruments ----------------
def koto(t0, midi, g=0.22, pan=0.0, length=1.6, bright=0.5):
    """Karplus-Strong の撥弦。bright が大きいほど硬い音"""
    f = hz(midi); p = max(2, int(SR / f)); s = int(t0 * SR)
    buf = [(rng.random() * 2 - 1) for _ in range(p)]
    lp = 0.0
    for k in range(p):   # 撥の位置による音色
        lp += (buf[k] - lp) * (0.3 + bright * 0.7); buf[k] = lp
    idx = 0; decay = 0.4985 + 0.0012 * min(1, f / 600)
    n1 = int(length * SR)
    for n in range(n1):
        a = buf[idx]; b = buf[(idx + 1) % p]
        v = decay * (a + b)
        buf[idx] = v
        idx = (idx + 1) % p
        env = min(1, n / 40) * (1 if n < n1 - 2000 else (n1 - n) / 2000)
        add(s + n, a * g * env * (1 - pan), a * g * env * (1 + pan))


def shakuhachi(t0, midi, dur, g=0.09, pan=-0.2):
    f = hz(midi); s = int(t0 * SR); ph = 0.0; nlp = 0.0
    for n in range(int(dur * SR)):
        t = n / SR
        env = min(1, t / 0.18) * min(1, (dur - t) / 0.3)
        vib = 1 + 0.008 * min(1, t / 0.6) * math.sin(2 * math.pi * 5.2 * t)
        ph += 2 * math.pi * f * vib / SR
        x = rng.random() * 2 - 1; nlp += (x - nlp) * 0.08
        v = (math.sin(ph) + 0.18 * math.sin(2 * ph) + 0.06 * math.sin(3 * ph)) * env * g + nlp * env * g * 0.9 * (1.2 - min(1, t / 0.4))
        add(s + n, v * (1 - pan), v * (1 + pan))


def taiko(t0, g=0.6, big=False):
    s = int(t0 * SR); ph = 0.0
    dec = 0.55 if big else 0.28
    for n in range(int((dec * 3) * SR)):
        t = n / SR
        ph += 2 * math.pi * (42 + 38 * math.exp(-t / 0.04)) / SR
        v = (math.sin(ph) + 0.25 * math.sin(2.3 * ph)) * math.exp(-t / dec) * g
        add(s + n, v)
    noise(t0, 0.08, g * 0.35, hp=0.2, dec=0.02, lp=0.25)


def shime(t0, g=0.12, pan=0.35):
    s = int(t0 * SR)
    for n in range(int(0.07 * SR)):
        t = n / SR
        v = math.sin(2 * math.pi * 820 * t) * math.exp(-t / 0.018) * g
        add(s + n, v * (1 - pan), v * (1 + pan))
    noise(t0, 0.03, g * 0.6, hp=0.8, dec=0.006, pan=pan)


def noise(t0, dur, g, hp=0.7, dec=0.03, pan=0.0, lp=1.0):
    s = int(t0 * SR); a = b = 0.0
    for n in range(int(dur * SR)):
        t = n / SR
        x = rng.random() * 2 - 1
        a += (x - a) * (1 - hp); y = x - a; b += (y - b) * lp
        v = b * math.exp(-t / dec) * g
        add(s + n, v * (1 - pan), v * (1 + pan))


def sea(t0, dur, g=0.07):
    """ゆっくり寄せては返す波の環境音"""
    s = int(t0 * SR); a = 0.0
    for n in range(int(dur * SR)):
        t = n / SR
        x = rng.random() * 2 - 1
        swell = 0.5 + 0.5 * math.sin(2 * math.pi * t / 3.2 - 1.2)
        a += (x - a) * (0.01 + 0.05 * swell)
        env = min(1, t / 1.0) * min(1, (dur - t) / 1.0)
        v = a * env * g * (0.4 + swell)
        add(s + n, v * (1 - 0.3 * math.sin(t)), v * (1 + 0.3 * math.sin(t)))


# ---------------- music ----------------
# 都節音階（D）: D Eb G A Bb
SCALE = [50, 51, 55, 57, 58, 62, 63, 67, 69, 70, 74, 75, 79, 81, 82, 86]
def deg(i):
    return SCALE[max(0, min(len(SCALE) - 1, i))]

mel = random.Random(147)
# 小節ごとの役割
# 0-1 オープニング / 2-7 初代〜三代 / 8-12 四代・約束（いまの時代：リズム強め）/ 13-14 言葉（静）/ 15-17 エンド
# オープニング: 琴のグリッサンドと笛
for k, i in enumerate(range(5, 13)):
    koto(0.05 + k * 0.06, deg(i), g=0.16, pan=-0.5 + k * 0.12, length=2.2)
taiko(0.0, 0.7, big=True)
shakuhachi(0.8, 74, 2.6)
shakuhachi(3.5, 70, 1.6)
koto(BAR, 62, g=0.2, length=2.5); taiko(BAR, 0.5)
koto(BAR + 2 * B, 67, g=0.16, length=2.0)

cur = 9
for bar in range(2, 17):
    t0 = bar * BAR
    quiet = bar in (13, 14)
    modern = 8 <= bar <= 12
    # 低い琴のドローン（根音）
    root = 50 if bar % 4 in (0, 1) else (55 if bar % 4 == 2 else 57)
    koto(t0, root, g=0.2 if not quiet else 0.14, length=2.6, bright=0.3)
    if not quiet:
        koto(t0 + 2 * B, root + 7, g=0.12, length=1.8, bright=0.3)
    # 旋律（琴）
    rhy = [1, 0, 1, 1, 0, 1, 0, 1] if bar % 2 == 0 else [1, 1, 0, 1, 1, 0, 1, 0]
    if quiet:
        rhy = [1, 0, 0, 0, 1, 0, 0, 0]
    for k in range(8):
        if not rhy[k]:
            continue
        cur = max(5, min(14, cur + mel.choice([-2, -1, -1, 1, 1, 2, 0])))
        if k == 0 and bar % 4 == 0:
            cur = 10
        koto(t0 + k * B / 2, deg(cur), g=0.17, pan=(k - 3.5) * 0.08, length=1.4, bright=0.6)
    # 太鼓
    if quiet:
        if bar == 13:
            shakuhachi(t0 + 0.2, 74, 2.4, g=0.1)
            shakuhachi(t0 + BAR + 0.1, 70, 1.4, g=0.09)
            shakuhachi(t0 + BAR + 1.6, 67, 1.6, g=0.08)
        continue
    taiko(t0, 0.55)
    taiko(t0 + 2.5 * B, 0.35)
    if modern or bar >= 15:
        taiko(t0 + 2 * B, 0.45)
        for k in range(8):
            shime(t0 + k * B / 2 + B / 4, g=0.08 if k % 2 else 0.1)
    else:
        shime(t0 + B, 0.1); shime(t0 + 3 * B, 0.1); shime(t0 + 3.5 * B, 0.07)
    if bar in (2, 3, 4, 5):
        pass

# 海の場面（初代・二代）に波の音
sea(2 * BAR - 0.5, 4 * BAR + 1.0, g=0.08)

# 最後の小節: 太鼓の連打 → 余韻
t0 = 16 * BAR
for k in range(8):
    taiko(t0 + 2 * B + k * B / 4, 0.25 + 0.05 * k)
t0 = 17 * BAR
taiko(t0, 0.9, big=True)
for k, i in enumerate(range(12, 3, -1)):
    koto(t0 + k * 0.05, deg(i), g=0.14, pan=0.5 - k * 0.11, length=2.4)
koto(t0 + 0.6, 50, g=0.22, length=2.2, bright=0.3)
shakuhachi(t0 + 0.3, 74, 2.1, g=0.08)

# ---------------- sound effects ----------------
def sfx_paper(t0, seed):
    r = random.Random(seed); pan = r.uniform(-0.4, 0.4)
    s = int(t0 * SR); a = 0.0; n1 = int(0.16 * SR)
    for n in range(n1):
        u = n / n1; x = rng.random() * 2 - 1
        a += (x - a) * (0.2 + 0.5 * u)
        v = (x - a * 0.6) * math.sin(math.pi * u) ** 1.5 * 0.09
        add(s + n, v * (1 - pan), v * (1 + pan))


def sfx_tile(t0, seed):
    r = random.Random(seed); f = r.uniform(300, 420); s = int(t0 * SR)
    noise(t0, 0.02, 0.09, hp=0.85, dec=0.005)
    for n in range(int(0.08 * SR)):
        t = n / SR
        add(s + n, math.sin(2 * math.pi * f * t) * math.exp(-t / 0.025) * 0.08)


def sfx_pop(t0, seed):
    s = int(t0 * SR); ph = 0
    for n in range(int(0.12 * SR)):
        t = n / SR
        ph += 2 * math.pi * (500 + 700 * t / 0.12) / SR
        add(s + n, math.sin(ph) * math.exp(-t / 0.04) * 0.09)


def sfx_stamp(t0, seed):
    # 落款を押す「トン」
    s = int(t0 * SR); ph = 0
    for n in range(int(0.3 * SR)):
        t = n / SR
        ph += 2 * math.pi * (70 + 90 * math.exp(-t / 0.02)) / SR
        add(s + n, math.sin(ph) * math.exp(-t / 0.07) * 0.4)
    noise(t0, 0.06, 0.18, hp=0.4, dec=0.015, lp=0.4)


def sfx_whoosh(t0, seed):
    s = int(t0 * SR); a = 0.0; n1 = int(0.7 * SR)
    for n in range(n1):
        u = n / n1; x = rng.random() * 2 - 1
        a += (x - a) * (0.02 + 0.3 * math.sin(math.pi * u))
        pan = 0.8 - 1.6 * u
        v = a * math.sin(math.pi * u) ** 2 * 0.3
        add(s + n, v * (1 - pan), v * (1 + pan))


def sfx_brush(t0, seed):
    # 筆が和紙をこする「サーッ」
    s = int(t0 * SR); a = b = 0.0; n1 = int(1.1 * SR)
    for n in range(n1):
        u = n / n1; x = rng.random() * 2 - 1
        a += (x - a) * 0.5; y = x - a; b += (y - b) * 0.25
        env = min(1, u * 8) * (1 - u) ** 1.2 * (0.7 + 0.3 * math.sin(u * 40))
        add(s + n, b * env * 0.08)


def sfx_wave(t0, seed):
    s = int(t0 * SR); a = 0.0; n1 = int(1.6 * SR)
    for n in range(n1):
        u = n / n1; x = rng.random() * 2 - 1
        a += (x - a) * (0.02 + 0.1 * math.sin(math.pi * u))
        add(s + n, a * math.sin(math.pi * u) ** 2 * 0.35)


FX = {'paper': sfx_paper, 'tile': sfx_tile, 'pop': sfx_pop, 'stamp': sfx_stamp, 'whoosh': sfx_whoosh, 'brush': sfx_brush, 'wave': sfx_wave}
cues = json.load(open(sys.argv[1]))
for i, c in enumerate(cues):
    fn = FX.get(c['type'])
    if fn and c['t'] < DUR:
        fn(c['t'], i)

# ---------------- mix ----------------
end = int(DUR * SR)
peak = max(max(abs(x) for x in L[:end]), max(abs(x) for x in R[:end])) or 1
g = 1.8 / peak
out = bytearray()
for i in range(end):
    fade = min(1.0, (end - i) / (0.5 * SR)) * min(1.0, i / (0.02 * SR))
    out += struct.pack('<hh', int(math.tanh(L[i] * g) * 0.9 * fade * 32767), int(math.tanh(R[i] * g) * 0.9 * fade * 32767))
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(out))
print('wrote', sys.argv[2], len(cues), 'cues')
