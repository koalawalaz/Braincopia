"""
The logo is a PNG, so there is no pen path to animate. Recover one: take the
white marks, thin them to a single-pixel skeleton (Zhang-Suen), then walk the
skeleton into ordered polylines. Those become SVG strokes that can be drawn
with stroke-dashoffset, which is what makes the loader look hand-made rather
than wiped.
"""
from PIL import Image
import json, math

SIZE = 384
im = Image.open('assets/logo.png').convert('RGBA').resize((SIZE, SIZE), Image.LANCZOS)
px = im.load()

# white marks only: bright and opaque
g = [[1 if (px[x, y][3] > 140 and (px[x, y][0] + px[x, y][1] + px[x, y][2]) / 3 > 165) else 0
      for x in range(SIZE)] for y in range(SIZE)]
print('mark pixels:', sum(map(sum, g)))

def neighbours(g, x, y):
    return [g[y-1][x], g[y-1][x+1], g[y][x+1], g[y+1][x+1],
            g[y+1][x], g[y+1][x-1], g[y][x-1], g[y-1][x-1]]   # P2..P9 clockwise

def transitions(n):
    n2 = n + n[:1]
    return sum(1 for i in range(8) if n2[i] == 0 and n2[i+1] == 1)

def thin(g):
    changed = True
    rounds = 0
    while changed:
        changed = False
        for step in (0, 1):
            drop = []
            for y in range(1, SIZE-1):
                row = g[y]
                for x in range(1, SIZE-1):
                    if not row[x]:
                        continue
                    n = neighbours(g, x, y)
                    b = sum(n)
                    if not (2 <= b <= 6):        continue
                    if transitions(n) != 1:      continue
                    P2,P3,P4,P5,P6,P7,P8,P9 = n
                    if step == 0:
                        if P2*P4*P6: continue
                        if P4*P6*P8: continue
                    else:
                        if P2*P4*P8: continue
                        if P2*P6*P8: continue
                    drop.append((x, y))
            if drop:
                changed = True
                for x, y in drop: g[y][x] = 0
        rounds += 1
    print('thinning rounds:', rounds)
    return g

g = thin(g)
pts = {(x, y) for y in range(SIZE) for x in range(SIZE) if g[y][x]}
print('skeleton pixels:', len(pts))

N8 = [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]
def nb(p):
    x, y = p
    return [(x+dx, y+dy) for dx, dy in N8 if (x+dx, y+dy) in pts]

def walk(start, used):
    """Follow the skeleton from a pixel, always stepping to an unused neighbour."""
    line = [start]; used.add(start); cur = start
    while True:
        nxt = [q for q in nb(cur) if q not in used]
        if not nxt: break
        # prefer carrying straight on, so a junction does not fold the line back
        if len(line) > 1:
            dx, dy = cur[0]-line[-2][0], cur[1]-line[-2][1]
            nxt.sort(key=lambda q: -((q[0]-cur[0])*dx + (q[1]-cur[1])*dy))
        cur = nxt[0]; used.add(cur); line.append(cur)
    return line

used = set()
lines = []
for p in sorted(pts, key=lambda p: (p[1], p[0])):        # endpoints first
    if p not in used and len(nb(p)) == 1:
        lines.append(walk(p, used))
for p in sorted(pts, key=lambda p: (p[1], p[0])):        # then closed loops
    if p not in used:
        lines.append(walk(p, used))

def rdp(line, eps):
    if len(line) < 3: return line
    (x1, y1), (x2, y2) = line[0], line[-1]
    dx, dy = x2-x1, y2-y1
    n = math.hypot(dx, dy) or 1
    worst, wi = 0, 0
    for i in range(1, len(line)-1):
        x, y = line[i]
        d = abs(dy*x - dx*y + x2*y1 - y2*x1) / n
        if d > worst: worst, wi = d, i
    if worst <= eps: return [line[0], line[-1]]
    return rdp(line[:wi+1], eps)[:-1] + rdp(line[wi:], eps)

lines = [l for l in lines if len(l) >= 8]
lines = [rdp(l, 1.1) for l in lines]
lines.sort(key=len, reverse=True)
print('strokes:', len(lines), '| points:', sum(len(l) for l in lines))

k = 100.0 / SIZE
def d(line):
    p = ['M%.2f %.2f' % (line[0][0]*k, line[0][1]*k)]
    for x, y in line[1:]:
        p.append('L%.2f %.2f' % (x*k, y*k))
    return ' '.join(p)

paths = [d(l) for l in lines]
json.dump(paths, open('/tmp/claude-0/-home-user-Braincopia/b8f13ae9-c582-5ccb-a510-c69a879832e7/scratchpad/paths.json','w'))
print('longest 3 path lengths (pts):', [len(l) for l in lines[:3]])
