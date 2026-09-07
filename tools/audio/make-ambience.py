"""
An original ambient bed: falling water over a slow drone, with bells that
arrive off the grid. Written from scratch so nothing here is anyone else's
recording. Loops seamlessly: every modulation completes a whole number of
cycles across the piece, and the tail crossfades into the head.
"""
import math, random, struct, wave, subprocess, os

SR   = 44100
SECS = 48
N    = SR * SECS
XF   = int(SR * 3.0)          # crossfade length
random.seed(7)

buf = [0.0] * N

# ---- water: noise pushed through two one-pole lowpasses, breathing ---------
lp1 = lp2 = 0.0
hp_prev_in = hp_prev_out = 0.0
for i in range(N):
    t = i / SR
    n = random.uniform(-1, 1)
    # cutoff wanders slowly; 3 whole cycles over the loop so the seam matches
    k = 0.10 + 0.055 * math.sin(2 * math.pi * 3 * t / SECS)
    lp1 += k * (n - lp1)
    lp2 += k * (lp1 - lp2)
    # a gentle highpass keeps it from turning into mud
    hp = 0.94 * (hp_prev_out + lp2 - hp_prev_in)
    hp_prev_in, hp_prev_out = lp2, hp
    swell = 0.72 + 0.28 * math.sin(2 * math.pi * 2 * t / SECS + 1.1)
    buf[i] = hp * 0.42 * swell

# ---- drone: a low root and its fifth, slightly detuned so they beat --------
for f, amp, det in ((55.0, 0.16, 0.0), (82.5, 0.10, 0.31), (110.0, 0.055, -0.19)):
    for i in range(N):
        t = i / SR
        trem = 0.80 + 0.20 * math.sin(2 * math.pi * 1 * t / SECS + f)
        buf[i] += amp * trem * math.sin(2 * math.pi * (f + det) * t)

# ---- bells: a pentatonic set, struck at intervals that never line up -------
NOTES = [440.0, 523.25, 587.33, 659.25, 880.0]
t = 2.0
while t < SECS - 6:
    f = random.choice(NOTES)
    start = int(t * SR)
    dur = int(SR * random.uniform(3.5, 5.5))
    peak = random.uniform(0.05, 0.085)
    for j in range(dur):
        i = start + j
        if i >= N: break
        env = math.exp(-3.1 * j / dur)
        buf[i] += peak * env * (math.sin(2 * math.pi * f * j / SR)
                                + 0.30 * math.sin(2 * math.pi * f * 2.01 * j / SR))
    t += random.uniform(4.5, 8.0)

# ---- seamless seam: fold the tail back over the head ----------------------
for j in range(XF):
    a = j / XF
    head = buf[j]
    tail = buf[N - XF + j]
    buf[j] = head * a + tail * (1 - a)
out = buf[:N - XF]

# ---- fit, soft-clip, write ------------------------------------------------
peak = max(abs(v) for v in out)
gain = 0.80 / peak
frames = bytearray()
for v in out:
    v = math.tanh(v * gain * 1.05)
    frames += struct.pack('<h', int(max(-1.0, min(1.0, v)) * 32767))

wav = '/tmp/ambience.wav'
with wave.open(wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(bytes(frames))
print('wav %.1fs, %.0f KB' % (len(out) / SR, os.path.getsize(wav) / 1024))

FF = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
mp3 = 'assets/audio/ambience.mp3'
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', wav,
                '-c:a', 'libmp3lame', '-b:a', '96k', '-ac', '1', mp3], check=True)
print('mp3 %.0f KB' % (os.path.getsize(mp3) / 1024))
