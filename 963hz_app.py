import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(
    page_title="432Hz · Healing Music",
    page_icon="🌊",
    layout="centered",
)

# ══════════════════════════════════════════════════════════════════
#  SHARED ENGINE
# ══════════════════════════════════════════════════════════════════
SR   = 44100
TUNE = 432.0 / 440.0

def note_freq(midi):
    return 440.0 * (2 ** ((midi - 69) / 12)) * TUNE

def fast_lp(x, k):
    """O(n) lowpass via cumsum — replaces np.convolve"""
    k = max(1, int(k))
    cs = np.cumsum(np.concatenate(([0.0], x.astype(np.float64))))
    out = (cs[k:] - cs[:-k]) / float(k)
    pad = len(x) - len(out)
    if pad > 0:
        out = np.concatenate((out, np.full(pad, out[-1] if len(out) else 0.0)))
    return out[:len(x)]

def reverb_hall(sig, strength=0.65):
    decay  = 0.38 + strength * 0.28
    delays = (30, 65, 108, 172, 255) if strength > 0.5 else (32, 70, 120)
    out = sig.astype(np.float64).copy()
    d = decay
    for ms in delays:
        nd = int(ms * SR / 1000)
        if nd < len(sig):
            ref = np.zeros(len(sig))
            ref[nd:] = sig[:-nd] * d
            out += ref; d *= 0.46
    return out

def slow_fade(sig, fade_sec=8.0):
    n = len(sig); f = min(int(fade_sec * SR), n // 4)
    sig = sig.copy()
    sig[:f]  *= np.linspace(0.0, 1.0, f)
    sig[-f:] *= np.linspace(1.0, 0.0, f)
    return sig

def normalize(sig, peak=0.88):
    pk = np.max(np.abs(sig))
    return sig / (pk + 1e-9) * peak

def to_wav(sig):
    pcm = (sig * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════
#  TAB 1 — WORSHIP / HEALING PIANO (giữ nguyên)
# ══════════════════════════════════════════════════════════════════
WORSHIP_PRESETS = {
    "✝ Deep Healing Worship (A major · 52 BPM)": {
        "key":"A_major","bpm":52,"rain":True,
        "prog":[(69,73,76),(76,80,83),(78,81,85),(74,78,81)],
        "melody":[69,71,73,76,78,80],
        "desc":"Peace & surrender in God's presence. Grand piano + rain + 1111Hz healing undertone.",
    },
    "🌧 Rainy Morning Prayer (D major · 48 BPM)": {
        "key":"D_major","bpm":48,"rain":True,
        "prog":[(62,66,69),(69,73,76),(71,74,78),(67,71,74)],
        "melody":[62,64,66,69,71,74],
        "desc":"Quiet prayer on a rainy morning. Warm chords, delicate high notes, angelic pads.",
    },
    "✝ Time Alone With God (G major · 45 BPM)": {
        "key":"G_major","bpm":45,"rain":False,
        "prog":[(67,71,74),(74,78,81),(76,79,83),(72,76,79)],
        "melody":[67,69,71,74,76,79],
        "desc":"Minimalist & reverent. Deep resonant bass, tender melody, choir-like pads. Stillness.",
    },
    "✨ Jesus Presence Healing (E major · 50 BPM)": {
        "key":"E_major","bpm":50,"rain":False,
        "prog":[(64,68,71),(71,75,78),(73,76,80),(69,73,76)],
        "melody":[64,66,68,71,73,76],
        "desc":"Cinematic & intimate. Emotional piano 50 BPM, glowing pads, spacious sound design.",
    },
    "🌤 Trust In God's Care (C major · 54 BPM)": {
        "key":"C_major","bpm":54,"rain":False,
        "prog":[(60,64,67),(67,71,74),(69,72,76),(65,69,72)],
        "melody":[60,62,64,67,69,72],
        "desc":"Peace, trust, surrender. I–V–vi–IV loop, ideal for 3-hour worship sessions.",
    },
}

def piano_note(freq, dur, vel=0.65, bright=0.85):
    n = int(SR * dur)
    if n < 2: return np.zeros(2)
    t = np.linspace(0, dur, n, endpoint=False)
    ae = np.exp(-7 * t)
    tone = (np.sin(2*np.pi*freq*1*t)*1.000 +
            np.sin(2*np.pi*freq*2*t)*(0.52*bright) +
            np.sin(2*np.pi*freq*3*t)*(0.26*bright*(1+0.35*ae)) +
            np.sin(2*np.pi*freq*4*t)*(0.13*bright*ae) +
            np.sin(2*np.pi*freq*5*t)*(0.06*bright*ae) +
            np.sin(2*np.pi*freq*6*t)*(0.03*ae))
    atk = max(1, int(0.007*SR))
    env = np.zeros(n); env[:atk] = np.linspace(0, 1, atk)
    rest = n - atk
    if rest > 0:
        s1 = int(rest*0.14); s2 = rest-s1
        if s1 > 0: env[atk:atk+s1] = np.linspace(1.0, 0.70, s1)
        if s2 > 0: env[atk+s1:] = 0.70 * np.exp(-2.0*np.linspace(0, dur*0.85, s2))
    return tone * env * vel

def chord_pad(midi_notes, dur, vol=0.16):
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False); out = np.zeros(n)
    for midi in midi_notes:
        f = note_freq(midi)
        for d, w in zip([-0.0035,-0.0015,0.0,0.0015,0.0035],
                        [0.45, 0.80, 1.00, 0.80, 0.45]):
            out += np.sin(2*np.pi*f*(1+d)*t) * w * vol * 0.28
        out += np.sin(2*np.pi*f*2*t) * vol * 0.055
    sn = min(int(SR*2.5), n//3); sw = np.ones(n)
    sw[:sn] = np.linspace(0, 1, sn); sw[-sn:] *= np.linspace(1, 0.35, sn)
    return out * sw

def bass_note(freq, dur, vel=0.40):
    n = int(SR*dur)
    if n < 2: return np.zeros(2)
    t = np.linspace(0, dur, n, endpoint=False)
    tone = (np.sin(2*np.pi*freq*t)*1.0 + np.sin(2*np.pi*freq*2*t)*0.35 +
            np.sin(2*np.pi*freq*3*t)*0.12)
    atk = max(1, int(0.010*SR)); env = np.zeros(n); env[:atk] = np.linspace(0,1,atk)
    rest = n-atk
    if rest > 0: env[atk:] = np.exp(-1.6*np.linspace(0, dur, rest))
    return tone * env * vel

def healing_undertone(dur, vol=0.016):
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False)
    return np.sin(2*np.pi*1111.0*t) * (0.82+0.18*np.sin(2*np.pi*0.07*t)) * vol

def rain_texture(dur, vol=0.038):
    n = int(SR*dur); rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, n)
    filtered = fast_lp(noise, int(SR*0.002))
    for dt in rng.integers(0, n, size=max(1, n//700)):
        dl = int(0.014*SR)
        if dt+dl < n:
            td = np.linspace(0, 1, dl)
            filtered[dt:dt+dl] += np.sin(2*np.pi*580*td)*np.exp(-9*td)*0.5
    filtered = filtered / (np.max(np.abs(filtered))+1e-9)
    fn = min(int(SR*4), n//4); filtered[:fn] *= np.linspace(0,1,fn)
    return filtered * vol

def intensity_arc(n, dur):
    x = np.linspace(0, 1, n)
    arc = np.where(x < 0.20, 0.10+x*0.50,
          np.where(x < 0.55, 0.20+(x-0.20)*0.43,
          np.where(x < 0.80, 0.35-(x-0.55)*0.80,
                              0.15-(x-0.80)*0.50)))
    return np.clip(arc, 0.05, 0.40)

def generate_worship(cfg, duration_sec, reverb_strength, rain_vol, bell_on, piano_expression):
    rng = np.random.default_rng(42)
    n = int(duration_sec*SR); out = np.zeros(n, dtype=np.float64)
    bpm=cfg["bpm"]; prog=cfg["prog"]; mel=cfg["melody"]
    beat=60.0/bpm; chord_dur=beat*4
    arc = intensity_arc(n, duration_sec)

    t_c=0.0; ci=0
    while t_c < duration_sec-chord_dur*0.5:
        chord=prog[ci%len(prog)]; cd=min(chord_dur+beat*0.5, duration_sec-t_c+1)
        pad=chord_pad(chord, cd)
        pos=int(t_c*SR); end=min(pos+len(pad), n)
        av=float(np.mean(arc[pos:min(pos+len(pad),n)])) if pos < n else 0.15
        out[pos:end] += pad[:end-pos] * (av/0.25)
        t_c += chord_dur; ci += 1

    nt=beat*float(rng.uniform(1.5,3.0)); pl=5+int(rng.integers(0,3))
    while nt < duration_sec-beat*3:
        mid=mel[int(rng.integers(0,len(mel)))]
        nd=float(rng.choice(np.array([beat,beat*1.5,beat*2.0,beat*2.5])))
        vel=float(rng.uniform(0.38,0.62))*piano_expression
        note=piano_note(note_freq(mid), nd, vel)
        pos=int(nt*SR); end=min(pos+len(note), n)
        if pos < n:
            av=float(arc[min(pos,n-1)])
            out[pos:end] += note[:end-pos] * (av/0.20) * 0.60
        nt += nd*0.86
        if int(rng.integers(0,pl)) == 0:
            nt += beat*float(rng.uniform(2.0,4.5))

    t_b=beat*float(rng.uniform(0.5,1.5)); bi=0
    while t_b < duration_sec-beat*2:
        rm=prog[bi%len(prog)][0]-12; bd=beat*float(rng.choice(np.array([3.0,4.0,5.0])))
        bn=bass_note(note_freq(rm), min(bd, duration_sec-t_b))
        pos=int(t_b*SR); end=min(pos+len(bn), n)
        if pos < n:
            av=float(arc[min(pos,n-1)])
            out[pos:end] += bn[:end-pos] * (av/0.22) * 0.42
        t_b += beat*float(rng.choice(np.array([3.5,4.0,4.5,6.0]))); bi += 1

    if bell_on:
        bt=beat*float(rng.uniform(4,8))
        while bt < duration_sec-4:
            fb=note_freq(mel[int(rng.integers(0,len(mel)))]+12)
            bds=float(rng.uniform(2.5,4.0)); bnn=int(bds*SR)
            btt=np.linspace(0,bds,bnn,endpoint=False)
            bell=(np.sin(2*np.pi*fb*btt)*0.55 +
                  np.sin(2*np.pi*fb*2.756*btt)*0.20*np.exp(-5*btt) +
                  np.sin(2*np.pi*fb*5.40*btt)*0.08*np.exp(-8*btt))*np.exp(-2.6*btt)
            pos=int(bt*SR); end=min(pos+bnn, n)
            if pos < n:
                av=float(arc[min(pos,n-1)])
                out[pos:end] += bell[:end-pos]*float(rng.uniform(0.06,0.12))*(av/0.20)
            bt += beat*float(rng.uniform(6,14))

    out += healing_undertone(duration_sec)
    if cfg["rain"] and rain_vol > 0:
        out += rain_texture(duration_sec, vol=rain_vol*0.06)
    out = reverb_hall(out, strength=reverb_strength)
    out = slow_fade(out); out = normalize(out)
    return to_wav(out)


# ══════════════════════════════════════════════════════════════════
#  TAB 2 — OCEAN MUSIC FOR SLEEP (rebuilt from prompt)
#  "deep sleep ocean ambience · slow gentle waves · deep calming pads
#   warm atmospheric drones · very slow tempo · peaceful night beach
#   soothing low frequency tones · minimal melody · 432hz ambient"
# ══════════════════════════════════════════════════════════════════

OCEAN_PRESETS = {
    "🌊 Deep Sleep Ocean — Night Beach (432Hz)": {
        "wave_period": 12.0, "scene": "night_beach",
        "drone_root": 54.0,
        "pad_freqs": [54.0, 81.0, 108.0, 162.0],
        "piano": False,
        "desc": "Bãi biển đêm khuya. Sóng chậm 12s · drone trầm ấm · pad sâu · 432Hz. Thiết kế để ngủ nhanh.",
    },
    "🌙 Midnight Deep Ocean — Low Drone Sleep": {
        "wave_period": 15.0, "scene": "deep_ocean",
        "drone_root": 40.5,
        "pad_freqs": [40.5, 60.75, 81.0, 121.5],
        "piano": False,
        "desc": "Đại dương khuya sâu thẳm. Sóng rất chậm 15s · drone cực trầm · không gian rộng lớn.",
    },
    "🏖 Gentle Beach — Soft Piano & Waves": {
        "wave_period": 9.0, "scene": "beach",
        "drone_root": 64.5,
        "pad_freqs": [64.5, 96.75, 129.0, 193.5],
        "piano": True,
        "melody_midi": [60, 62, 64, 67, 69],
        "bpm": 40,
        "desc": "Bờ biển lúc bình minh. Sóng nhẹ 9s · piano thưa thớt D major · drone ấm · thư giãn.",
    },
    "🐋 Underwater World — Whale & Depth": {
        "wave_period": 18.0, "scene": "underwater",
        "drone_root": 36.0,
        "pad_freqs": [36.0, 54.0, 72.0, 108.0],
        "piano": False,
        "desc": "Thế giới dưới nước. Áp suất sâu · whale song · drone siêu trầm · thiền định sâu.",
    },
    "🌅 Sunset Cove — Warm Ocean Ambient": {
        "wave_period": 10.5, "scene": "sunset",
        "drone_root": 48.0,
        "pad_freqs": [48.0, 72.0, 96.0, 144.0],
        "piano": True,
        "melody_midi": [67, 69, 71, 74, 76],
        "bpm": 38,
        "desc": "Vịnh hoàng hôn. Sóng êm 10s · piano G major rất thưa · drone hoàng kim · chữa lành cảm xúc.",
    },
}

# ── Ocean waves — slow, deep, immersive ──────────────────────────
def ocean_slow(dur, wave_period=12.0, scene="night_beach"):
    n = int(SR*dur); rng = np.random.default_rng(77)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = rng.normal(0, 1, n).astype(np.float64)

    # Three spectral layers
    body = fast_lp(noise, int(SR*0.018)) * 0.65   # deep rumble
    surf = (fast_lp(noise, int(SR*0.003)) -
            fast_lp(noise, int(SR*0.016))) * 0.25  # wave break
    hiss = (noise - fast_lp(noise, int(SR*0.0005))) * 0.08  # foam/air

    if scene == "deep_ocean" or scene == "underwater":
        # Heavier bass, less hiss
        body *= 1.40; surf *= 0.70; hiss *= 0.30
    elif scene == "beach" or scene == "sunset":
        # Slightly brighter
        body *= 0.90; surf *= 1.10; hiss *= 1.10

    raw = body + surf + hiss

    # Slow wave envelope — smooth sin^2, never silent
    env_main  = np.sin(np.pi * ((t % wave_period) / wave_period))**2
    env_micro = np.sin(np.pi * ((t % (wave_period*0.63)) / (wave_period*0.63)))**2 * 0.18
    wave_env  = env_main * 0.58 + env_micro + 0.42   # floor 42% always present

    # Extra long swell (simulate tide)
    tide = 0.85 + 0.15*np.sin(2*np.pi*(1/120.0)*t)
    ocean = raw * wave_env * tide

    # Underwater: add pressure whomp
    if scene == "underwater":
        ocean = fast_lp(ocean, int(SR*0.025)) * 1.5
        whomp = 0.75 + 0.25*np.sin(2*np.pi*0.06*t)
        ocean *= whomp

    return ocean / (np.max(np.abs(ocean)) + 1e-9)

# ── Warm atmospheric drone — low pitch, organic drift ────────────
def warm_drone(dur, root_hz=54.0, vol=0.22):
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False)
    # Organic frequency drift (subtle detuning over time)
    drift = 1 + 0.0018*np.sin(2*np.pi*0.006*t) + 0.0009*np.sin(2*np.pi*0.011*t)
    f1=root_hz; f2=root_hz*1.5; f3=root_hz*2.0; f4=root_hz*3.0
    tone = (
        np.sin(2*np.pi*f1*drift*t) * 0.50 +
        np.sin(2*np.pi*f2*drift*t) * 0.28 +
        np.sin(2*np.pi*f3*drift*t) * 0.14 +
        np.sin(2*np.pi*f4*drift*t) * 0.06 +
        # Sub-harmonic (half freq) — felt more than heard
        np.sin(2*np.pi*(f1*0.5)*t)  * 0.08
    )
    # Very slow breath — 28s swell cycle
    swell = 0.52 + 0.48*np.sin(2*np.pi*(1/28.0)*t + 0.8)
    return tone * swell * vol

# ── Deep calming pad — detuned choir layers ───────────────────────
def deep_pad_layer(dur, freqs, vol=0.14):
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False)
    out = np.zeros(n)
    for f in freqs:
        for d, w in zip([-0.005,-0.002,0.0,0.002,0.005],
                        [0.35,  0.72,  1.0, 0.72, 0.35]):
            out += np.sin(2*np.pi*f*(1+d)*t) * w * vol * 0.22
        out += np.sin(2*np.pi*f*2*t) * vol * 0.045
    # Slow 22s swell + gentle modulation
    swell_n = min(int(SR*10), n//3); sw = np.ones(n)
    sw[:swell_n] = np.linspace(0, 1, swell_n)
    sw[-swell_n:] *= np.linspace(1, 0, swell_n)
    sw *= 0.72 + 0.28*np.sin(2*np.pi*(1/22.0)*t + 1.3)
    return out * sw

# ── Low frequency healing tones (432Hz foundation) ───────────────
def healing_low_freq(dur, root=54.0, vol=0.12):
    """432Hz / 8 = 54Hz base · harmonic stack · felt not heard"""
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False)
    tone = (
        np.sin(2*np.pi*root*t)      * 0.45 +  # deep ground
        np.sin(2*np.pi*root*2*t)    * 0.28 +  # octave
        np.sin(2*np.pi*root*4*t)    * 0.15 +  # 2nd octave (432Hz if root=108)
        np.sin(2*np.pi*432.0*t)     * 0.08 +  # 432Hz tone
        np.sin(2*np.pi*963.0*t)     * 0.04    # 963Hz healing whisper
    )
    tone *= 0.78 + 0.22*np.sin(2*np.pi*(1/18.0)*t)
    return tone * vol

# ── Whale song (analog synthesis) ────────────────────────────────
def whale_song(dur, vol=0.10):
    n = int(SR*dur); rng = np.random.default_rng(55); out = np.zeros(n)
    t_w = float(rng.uniform(8, 18))
    while t_w < dur - 12:
        cd  = float(rng.uniform(5, 10)); cn = int(cd*SR)
        ct  = np.linspace(0, cd, cn, endpoint=False)
        # Sweeping whale frequency 50-120Hz
        f_sw = 58 + 42*np.sin(np.pi*ct/cd) + 10*np.sin(2*np.pi*0.7*ct)
        phase = np.cumsum(2*np.pi*f_sw/SR)
        call = (np.sin(phase)*0.55 + np.sin(phase*2)*0.28 + np.sin(phase*3)*0.10)
        call *= np.sin(np.pi*ct/cd)**0.5 * float(rng.uniform(0.65, 1.0))
        pos=int(t_w*SR); end=min(pos+cn, n)
        out[pos:end] += call[:end-pos]
        t_w += cd + float(rng.uniform(10, 25))
    pk = np.max(np.abs(out))
    return (out/pk if pk > 0.001 else out) * vol

# ── Night ambient texture (minimal air/wind) ──────────────────────
def night_air(dur, vol=0.022):
    n = int(SR*dur); rng = np.random.default_rng(13)
    noise = rng.normal(0, 1, n).astype(np.float64)
    band = fast_lp(noise, int(SR*0.0008)) - fast_lp(noise, int(SR*0.003))
    t = np.linspace(0, dur, n, endpoint=False)
    band *= 0.25 + 0.75*np.abs(np.sin(2*np.pi*(1/38.0)*t))
    return band / (np.max(np.abs(band))+1e-9) * vol

# ── Minimal sleep piano (very sparse — breathes with ocean) ───────
def sleep_piano(dur, melody_midi, bpm=40):
    rng = np.random.default_rng(88)
    n = int(SR*dur); out = np.zeros(n, dtype=np.float64)
    beat = 60.0/bpm

    nt = beat * float(rng.uniform(6, 12))
    while nt < dur - beat*5:
        mid = melody_midi[int(rng.integers(0, len(melody_midi)))]
        nd  = float(rng.choice(np.array([beat*3, beat*4, beat*5, beat*6])))
        vel = float(rng.uniform(0.22, 0.40))  # very soft
        freq = note_freq(mid)
        nn   = int(nd*SR)
        if nn < 2: continue
        tt   = np.linspace(0, nd, nn, endpoint=False)
        ae   = np.exp(-3.5*tt)
        tone = (np.sin(2*np.pi*freq*tt)*1.0 +
                np.sin(2*np.pi*freq*2*tt)*0.30*ae +
                np.sin(2*np.pi*freq*3*tt)*0.10*ae)
        atk  = max(1, int(0.012*SR)); env = np.zeros(nn)
        env[:atk] = np.linspace(0,1,atk)
        rest = nn-atk
        if rest > 0: env[atk:] = np.exp(-0.9*np.linspace(0,nd,rest))
        note = tone*env*vel
        pos=int(nt*SR); end=min(pos+nn, n)
        if pos < n: out[pos:end] += note[:end-pos] * 0.48
        # Large gap between notes — silence is part of the music
        nt += nd + beat*float(rng.uniform(4.0, 9.0))

    return out

# ── MAIN OCEAN GENERATOR ─────────────────────────────────────────
def generate_ocean(cfg, duration_sec,
                   ocean_vol, drone_vol, pad_vol,
                   whale_on, piano_vol, reverb_str):
    n   = int(duration_sec * SR)
    out = np.zeros(n, dtype=np.float64)

    # 1. Slow gentle ocean waves (foundation)
    waves = ocean_slow(duration_sec,
                       wave_period=cfg["wave_period"],
                       scene=cfg["scene"])
    out += waves * ocean_vol * 0.80

    # 2. Warm atmospheric drone (low pitch center)
    drone = warm_drone(duration_sec, root_hz=cfg["drone_root"], vol=0.24)
    out += drone * drone_vol

    # 3. Deep calming pads (harmonic blanket)
    pad = deep_pad_layer(duration_sec, freqs=cfg["pad_freqs"], vol=0.16)
    out += pad * pad_vol

    # 4. Low frequency healing tones (432Hz foundation)
    out += healing_low_freq(duration_sec, root=cfg["drone_root"], vol=0.13)

    # 5. Whale / underwater (optional)
    if whale_on:
        out += whale_song(duration_sec, vol=0.09)

    # 6. Minimal piano (optional, very sparse)
    if cfg.get("piano") and piano_vol > 0:
        mel  = cfg.get("melody_midi", [60, 64, 67])
        bpm  = cfg.get("bpm", 40)
        pn   = sleep_piano(duration_sec, mel, bpm)
        out += pn * piano_vol * 0.80

    # 7. Night air texture
    out += night_air(duration_sec, vol=0.022)

    # 8. Deep reverb (cave/ocean space)
    out = reverb_hall(out, strength=reverb_str)

    # 9. Very long fade (10s in/out — sleep music needs gradual)
    out = slow_fade(out, fade_sec=12.0)
    out = normalize(out)
    return to_wav(out)


# ══════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════
st.title("🎵 432Hz · Healing Music Generator")
st.markdown("*Worship Piano · Ocean Deep Sleep · 432Hz Tuning · Low Frequency Healing*")
st.divider()

tab1, tab2 = st.tabs(["✝ Worship & Healing Piano", "🌊 Ocean Music for Sleep"])

# ─── TAB 1 ───────────────────────────────────────────────────────
with tab1:
    st.markdown("#### ✝ 432Hz Worship & Healing Piano")

    p_name = st.selectbox("🎹 Chọn preset", list(WORSHIP_PRESETS.keys()), key="wp")
    cfg_w  = WORSHIP_PRESETS[p_name]
    st.info(f"**{cfg_w['key'].replace('_',' ')} · {cfg_w['bpm']} BPM**  \n{cfg_w['desc']}")

    c1,c2 = st.columns(2)
    with c1: dur_w  = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1, key="dur_w")
    with c2: rev_w  = st.slider("🏛 Cathedral Reverb", 0.2, 1.0, 0.72, 0.04, key="rev_w")
    c3,c4 = st.columns(2)
    with c3: pexp   = st.slider("🎹 Piano Expression", 0.5, 1.5, 1.0, 0.05, key="pexp")
    with c4: rain_w = st.slider("🌧 Rain Texture", 0.0, 1.0,
                                 0.6 if cfg_w["rain"] else 0.0, 0.05, key="rain_w")
    bell_w = st.toggle("🔔 Crystal Bell Chimes", value=True, key="bell_w")

    with st.expander("📋 Cấu trúc bài"):
        bpm=cfg_w['bpm']; bd=round(60/bpm, 2)
        st.markdown(f"""
**Tuning:** 432Hz · **BPM:** {bpm} · **Beat:** {bd}s · **1 chord per** {round(bd*4,1)}s

| Section | Nội dung | Intensity |
|---|---|---|
| Intro (0–12%) | Pad + bass đầu tiên | 0.5–1/10 |
| Theme A (12–35%) | Piano melody + chord pads | 2–3/10 |
| Build (35–65%) | Peak — pads swell + bells | 3–3.5/10 |
| Resolution (65–100%) | Strip back, fade | 1–1.5/10 |
""")

    if st.button("✦ TẠO NHẠC WORSHIP 432Hz ✦", use_container_width=True, key="btn_w"):
        with st.spinner(f"Đang soạn {p_name} · {dur_w} phút ✝"):
            audio_w = generate_worship(cfg_w, dur_w*60, rev_w, rain_w, bell_w, pexp)
        mb = len(audio_w)/(1024*1024)
        st.success(f"✦ Hoàn thành · {dur_w} phút · {cfg_w['key'].replace('_',' ')} · {mb:.1f} MB")
        st.audio(audio_w, format="audio/wav")
        fname = ''.join(c for c in p_name.split("(")[0] if c.isalnum() or c==' ').strip().replace(' ','_').lower()
        st.download_button("⬇ Tải WAV", audio_w,
            file_name=f"432hz_{fname}_{dur_w}min.wav",
            mime="audio/wav", use_container_width=True, key="dl_w")

    st.caption("✝ 432Hz · 1111Hz Healing · I–V–vi–IV · *Be still, and know that I am God* — Ps 46:10")

# ─── TAB 2 ───────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🌊 Ocean Music for Deep Sleep")
    st.markdown(
        "*Slow gentle waves · Deep calming pads · Warm atmospheric drones · "
        "Low frequency healing · 432Hz ambient · Thiết kế để ngủ nhanh*"
    )

    o_name = st.selectbox("🌊 Chọn cảnh biển", list(OCEAN_PRESETS.keys()), key="op")
    cfg_o  = OCEAN_PRESETS[o_name]
    st.info(cfg_o["desc"])

    c5,c6 = st.columns(2)
    with c5:
        dur_o = st.slider("⏱ Thời lượng (phút)", 1, 30, 10, 1, key="dur_o",
                          help="Tối đa 30 phút để tối ưu RAM")
    with c6:
        ocean_v = st.slider("🌊 Sóng biển", 0.2, 1.0, 0.75, 0.05, key="ocv",
                            help="Âm lượng tiếng sóng")

    c7,c8 = st.columns(2)
    with c7:
        drone_v = st.slider("🎵 Drone trầm ấm", 0.2, 1.0, 0.80, 0.05, key="dv",
                            help="Atmospheric drone — linh hồn của ambient sleep")
    with c8:
        pad_v   = st.slider("☁ Deep calming pads", 0.2, 1.0, 0.75, 0.05, key="pv",
                            help="Choir/string pad chìm sâu")

    c9,c10 = st.columns(2)
    with c9:
        rev_o   = st.slider("🔊 Reverb không gian", 0.2, 0.9, 0.60, 0.05, key="rev_o",
                            help="0.2 = phòng nhỏ · 0.9 = đại dương rộng")
    with c10:
        whale_on = st.toggle("🐋 Whale Song", value=True, key="whale")

    if cfg_o.get("piano"):
        piano_v = st.slider(
            f"🎹 Minimal Piano ({cfg_o.get('bpm',40)} BPM · rất thưa)",
            0.0, 1.0, 0.45, 0.05, key="piano_v"
        )
    else:
        piano_v = 0.0
        st.caption("🎹 Preset này pure nature — không có piano")

    with st.expander("📋 Chi tiết âm thanh & layers"):
        st.markdown(f"""
| Layer | Thông số | Vai trò |
|---|---|---|
| 🌊 Ocean waves | Wave period: **{cfg_o['wave_period']}s** · Scene: **{cfg_o['scene']}** | Nền thiên nhiên |
| 🎵 Warm drone | Root: **{cfg_o['drone_root']}Hz** + 5th + octave | Trung tâm cảm xúc |
| ☁ Deep pads | **{len(cfg_o['pad_freqs'])} harmonic layers** | Blanket âm thanh |
| ✨ Low freq | **54Hz → 432Hz → 963Hz** stack | Healing tones |
| 🐋 Whale | Analog synthesis sweep | Depth & mystery |
| 🎹 Piano | {"Minimal · " + str(cfg_o.get("bpm","")) + " BPM · rất thưa" if cfg_o.get("piano") else "Không (pure nature)"} | Melody tối giản |
| 🌬 Night air | Band-filtered ambient texture | Không gian đêm |
""")

    if st.button("🌊  TẠO NHẠC BIỂN CHO GIẤC NGỦ SÂU  🌊",
                 use_container_width=True, key="btn_o"):
        with st.spinner(f"Đang tạo {o_name} · {dur_o} phút 🌊"):
            audio_o = generate_ocean(
                cfg=cfg_o, duration_sec=dur_o*60,
                ocean_vol=ocean_v, drone_vol=drone_v,
                pad_vol=pad_v, whale_on=whale_on,
                piano_vol=piano_v, reverb_str=rev_o,
            )
        mb = len(audio_o)/(1024*1024)
        st.success(f"🌊 Hoàn thành · {dur_o} phút · {mb:.1f} MB")
        st.audio(audio_o, format="audio/wav")
        fname2 = ''.join(c for c in o_name.split("—")[0]
                         if c.isalnum() or c==' ').strip().replace(' ','_').lower()
        st.download_button("⬇ Tải WAV", audio_o,
            file_name=f"ocean_sleep_{fname2}_{dur_o}min.wav",
            mime="audio/wav", use_container_width=True, key="dl_o")

    st.caption(
        "🌊 432Hz · Deep Sleep Ocean · Warm Drones · Low Frequency Healing · "
        "*The sea is his, and he made it* — Ps 95:5"
    )
