# Sperrylite Sentry

Full-colour Python 3 neon tower-lite arcade for [ElbowOS](https://x.com/ElbowOS).

Three copper-and-cobalt spires sit on a vault ridge. Ore-moths drift down the shaft. Switch the hot sentry and fire a beam before a moth cracks the vault line. Not a Nintendo ROM, not an emulator — original geometry and rules.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 sperrylite_sentry.py --play
```

A / D or Left / Right switches the hot sentry. Hold Space to beam. R restarts.

Needs Python 3.10+ and a desktop window (pygame + SDL).

## Record a 9:16 reel

```bash
python3 sperrylite_sentry.py --record
```

Headless path uses `SDL_VIDEODRIVER=dummy`, draws a 1080x1920 surface, and pipes 15 seconds at 30fps to ffmpeg (libx264, yuv420p, CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/167vg0iDDivd7PE9A69au9xwWrmnYjBRL/view?usp=drivesdk
