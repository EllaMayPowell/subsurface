import importlib, sys, time, threading
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from pyo import Server, Sine, Pattern

# ---------- Audio server ----------
# If you get choppy audio, try buffersize=512; if silent, see the device tips below.
s = Server(sr=48000, buffersize=256, nchnls=2, duplex=0).boot().start()

# ---------- Musical clock ----------
class Clock:
    def __init__(self, bpm=120.0):
        self.set_bpm(bpm)
        self.start_time = time.monotonic()
    def set_bpm(self, bpm):
        self.bpm = float(bpm)
        self.sec_per_beat = 60.0 / self.bpm
    def now(self):
        return time.monotonic() - self.start_time

clock = Clock(130)

# ---------- Tiny audio helpers ----------
def sine(freq=220, dur_beats=0.25, amp=0.08):
    dur = dur_beats * clock.sec_per_beat
    tone = Sine(freq=freq, mul=amp).out()
    def stop(): tone.stop()
    Pattern(stop, time=dur).play()

# ---------- Live loop system ----------
class LiveLoop:
    def __init__(self, name, every_beats):
        self.name = name
        self.period_beats = every_beats
        self.is_running = False
        self._pat = None
        self.func = None
    def _tick(self):
        try:
            if self.func: self.func()
        except Exception as e:
            print(f"[{self.name}] error: {e}", file=sys.stderr)
    def start(self):
        if self.is_running: return
        self.is_running = True
        period_sec = float(self.period_beats) * clock.sec_per_beat
        self._pat = Pattern(self._tick, time=period_sec).play()
    def stop(self):
        self.is_running = False
        if self._pat:
            try: self._pat.stop()
            except Exception: pass
            self._pat = None

LOOPS = {}

def every(spec):
    if isinstance(spec, (int, float)): return float(spec)
    return float(Fraction(spec))

def live_loop(name, every_beats="1"):
    beats = every(every_beats)
    loop = LOOPS.get(name) or LiveLoop(name, beats)
    loop.period_beats = beats
    LOOPS[name] = loop
    def decorator(fn):
        loop.func = fn
        return fn
    return decorator

def start_all():
    for lp in LOOPS.values(): lp.start()

def stop_all():
    for lp in LOOPS.values(): lp.stop()

# ---------- Hot reloader ----------
USER_FILE = Path("user_code.py")
_last_mtime = None
_user_mod: ModuleType | None = None

def load_user_code():
    global _user_mod, _last_mtime
    try:
        if USER_FILE.exists():
            mtime = USER_FILE.stat().st_mtime
            if _last_mtime is None or mtime > _last_mtime:
                _last_mtime = mtime
                stop_all()
                if _user_mod and "user_code" in sys.modules:
                    del sys.modules["user_code"]
                _user_mod = importlib.import_module("user_code")
                start_all()
                print(f"[engine] loaded {USER_FILE.name}")
    except Exception as e:
        print(f"[engine] load error: {e}", file=sys.stderr)

def watch_thread():
    while True:
        load_user_code()
        time.sleep(0.2)

threading.Thread(target=watch_thread, daemon=True).start()

print("[engine] running. Edit user_code.py to live-code. Ctrl+C to quit.")
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    stop_all()
    s.stop(); s.shutdown()
