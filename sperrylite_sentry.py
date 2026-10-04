"""Sperrylite Sentry — neon tower-lite arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if not PLAY or RECORD:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/SPERRYLITE_SENTRY_ElbowOS.mp4")
random.seed(19)
INK, COBALT = (10, 8, 16), (64, 118, 255)
COPPER, EMBER = (255, 132, 48), (255, 206, 110)
BONE, MINT, ROSE = (236, 226, 208), (92, 230, 176), (255, 92, 122)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if (PLAY and not RECORD) else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Sperrylite Sentry")
        self.font = pygame.font.SysFont("dejavusans", 62, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = self.score = self.spawn = 0
        self.cores, self.sel = 5, 1
        self.cd = [0, 0, 0]
        self.tx, self.ty = [200, 540, 880], 1460
        self.aim = [-1.3, -1.57, -1.85]
        self.moths, self.bolts, self.sparks = [], [], []
        self.stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(90)]
        for i in range(7):
            self.spawn_moth(-80 - i * 110)

    def spawn_moth(self, y=None):
        self.moths.append({
            "x": random.randint(100, W - 100),
            "y": -50 if y is None else y,
            "vy": random.uniform(5.4, 9.2),
            "ph": random.random() * 6.28,
            "amp": random.choice([0, 40, 70]),
            "hue": random.choice([COPPER, COBALT, EMBER, ROSE, MINT]),
            "r": random.randint(22, 36),
        })

    def nearest(self, i):
        best, bd = None, 1e9
        for m in self.moths:
            if m["y"] > self.ty + 10:
                continue
            d = math.hypot(m["x"] - self.tx[i], m["y"] - self.ty)
            if d < bd and d < 1000:
                best, bd = m, d
        return best

    def fire(self, i):
        if self.cd[i] > 0:
            return
        m = self.nearest(i)
        if not m:
            return
        ang = math.atan2(m["y"] - (self.ty - 90), m["x"] - self.tx[i])
        self.aim[i] = ang
        self.cd[i] = 6
        self.bolts.append({"x": self.tx[i], "y": self.ty - 90, "a": ang, "life": 5})
        if math.hypot(m["x"] - self.tx[i], m["y"] - self.ty) < 900:
            self.score += 25
            self.sparks.append({"x": m["x"], "y": m["y"], "life": 14, "c": m["hue"]})
            self.moths.remove(m)

    def step(self, auto=False):
        self.t += 1
        self.spawn += 1
        if self.spawn > 16:
            self.spawn = 0
            self.spawn_moth()
        for i in range(3):
            self.cd[i] = max(0, self.cd[i] - 1)
        if auto and self.moths:
            low = max(self.moths, key=lambda m: m["y"])
            self.sel = min(range(3), key=lambda i: abs(self.tx[i] - low["x"]))
            if self.t % 3 == 0:
                self.fire(self.sel)
            if self.t % 9 == 0:
                self.fire((self.sel + 1) % 3)
        for m in self.moths:
            m["y"] += m["vy"]
            m["x"] += math.sin(self.t * 0.09 + m["ph"]) * (m["amp"] * 0.045)
            m["x"] = max(48, min(W - 48, m["x"]))
        for m in [m for m in self.moths if m["y"] > 1690]:
            self.cores = max(0, self.cores - 1)
            self.sparks.append({"x": m["x"], "y": 1660, "life": 10, "c": ROSE})
            self.moths.remove(m)
        self.bolts = [b for b in self.bolts if b.update({"life": b["life"] - 1}) or b["life"] > 0]
        self.sparks = [s for s in self.sparks if s.update({"life": s["life"] - 1}) or s["life"] > 0]

    def moth(self, surf, m):
        x, y, r = int(m["x"]), int(m["y"]), m["r"]
        flap = math.sin(self.t * 0.45 + m["ph"]) * 12
        pygame.draw.polygon(surf, m["hue"], [(x, y - r), (x + r + 10, y + flap), (x, y + 8), (x - r - 10, y - flap)])
        pygame.draw.circle(surf, BONE, (x, y), 7)
        pygame.draw.circle(surf, INK, (x - 3, y - 1), 2)

    def tower(self, surf, i):
        x, y = self.tx[i], self.ty
        hot = i == self.sel
        col = COPPER if hot else COBALT
        pygame.draw.polygon(surf, (40, 22, 18) if hot else (18, 24, 48), [(x - 70, y + 40), (x + 70, y + 40), (x + 40, y - 10), (x - 40, y - 10)])
        pygame.draw.polygon(surf, col, [(x, y - 130), (x + 38, y), (x - 38, y)])
        pygame.draw.polygon(surf, EMBER if hot else BONE, [(x, y - 130), (x + 14, y - 46), (x - 14, y - 46)])
        ang = self.aim[i]
        pygame.draw.line(surf, EMBER, (x, y - 90), (x + math.cos(ang) * 54, y - 90 + math.sin(ang) * 54), 7)
        pygame.draw.circle(surf, BONE, (x, y - 90), 11)
        if hot:
            pygame.draw.circle(surf, COPPER, (x, y - 24), 52, 3)

    def draw(self, surf):
        surf.fill(INK)
        for y in range(0, H, 10):
            k = int(22 + 14 * math.sin(y * 0.008 + self.t * 0.03))
            pygame.draw.line(surf, (k + 10, max(0, k // 3), 36), (0, y), (W, y))
        for x, y, r in self.stars:
            pygame.draw.circle(surf, BONE, (x, int((y + self.t * r * 2) % H)), r)
        pygame.draw.rect(surf, (26, 16, 20), (0, 1624, W, 296))
        pygame.draw.line(surf, COPPER, (40, 1624), (W - 40, 1624), 5)
        for i in range(9):
            pygame.draw.line(surf, (110, 48, 28), (60 + i * 120, 1640), (90 + i * 120, 1880), 4)
        for m in self.moths:
            self.moth(surf, m)
        for b in self.bolts:
            x2 = b["x"] + math.cos(b["a"]) * 860
            y2 = b["y"] + math.sin(b["a"]) * 860
            pygame.draw.line(surf, (140, 54, 18), (b["x"], b["y"]), (x2, y2), 12)
            pygame.draw.line(surf, EMBER, (b["x"], b["y"]), (x2, y2), 3)
        for s in self.sparks:
            rr = s["life"] + 5
            pygame.draw.circle(surf, s["c"], (int(s["x"]), int(s["y"])), rr, 3)
            pygame.draw.circle(surf, BONE, (int(s["x"]), int(s["y"])), max(2, rr // 3))
        for i in range(3):
            self.tower(surf, i)
        title = self.font.render("SPERRYLITE SENTRY", True, EMBER)
        surf.blit(title, title.get_rect(center=(W // 2, 88)))
        sub = self.small.render("TOWER-LITE   ·   PYTHON 3", True, COBALT)
        surf.blit(sub, sub.get_rect(center=(W // 2, 158)))
        sc = self.font.render(f"{self.score:04d}", True, BONE)
        surf.blit(sc, sc.get_rect(center=(W // 2, 248)))
        cores = self.small.render("VAULT  " + "● " * self.cores + "○ " * (5 - self.cores), True, MINT)
        surf.blit(cores, cores.get_rect(center=(W // 2, 322)))
        hint = self.tiny.render("A / D  switch sentry     SPACE  beam", True, (190, 168, 146))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 128)))
        tag = self.small.render("x.com/ElbowOS", True, COPPER)
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 68)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_a, pygame.K_LEFT):
                        self.sel = (self.sel - 1) % 3
                    if ev.key in (pygame.K_d, pygame.K_RIGHT):
                        self.sel = (self.sel + 1) % 3
                    if ev.key == pygame.K_SPACE:
                        self.fire(self.sel)
                    if ev.key == pygame.K_r:
                        self.reset()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.fire(self.sel)
            self.step(False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(True)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        alt = "/home/workdir/artifacts/SPERRYLITE_SENTRY_ElbowOS.mp4"
        if os.path.abspath(alt) != os.path.abspath(OUT):
            os.makedirs(os.path.dirname(alt), exist_ok=True)
            subprocess.check_call(["cp", OUT, alt])
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    g.play_interactive() if (PLAY and not RECORD) else g.record()


if __name__ == "__main__":
    main()
