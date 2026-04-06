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

# FIX 1: O(n) moving average instead of O(n*k) np.convolve
def fast_lp(x, k):
    """Fast lowpass via cumsum — replaces np.convolve"""
    k = max(1, int(k))
    cs = np.cumsum(np.concatenate(([0.0], x.astype(np.float64))))
    out = (cs[k:] - cs[:-k]) / float(k)
    # pad to original length
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
#  TAB 1 — WORSHIP / HEALING PIANO
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
    filtered = fast_lp(noise, int(SR*0.002))          # FIX: use fast_lp
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
        rm=prog[bi%len(prog)][0]-12
        bd=beat*float(rng.choice(np.array([3.0,4.0,5.0])))
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
#  TAB 2 — OCEAN MUSIC FOR SLEEP
# ══════════════════════════════════════════════════════════════════
OCEAN_PRESETS = {
    "🌊 Deep Ocean Sleep — 432Hz Theta": {
        "wave_period":9.0,"wind":0.12,"depth":"deep",
        "piano":True,"bpm":44,
        "prog":[(60,64,67),(67,71,74),(69,72,76),(65,69,72)],
        "melody":[60,62,64,67,69],
        "desc":"Deep ocean rumble + slow 432Hz piano 44 BPM. Dành cho ngủ sâu & thiền.",
    },
    "🏖 Gentle Beach Waves — Morning Calm": {
        "wave_period":6.5,"wind":0.06,"depth":"shallow",
        "piano":True,"bpm":48,
        "prog":[(67,71,74),(74,78,81),(76,79,83),(72,76,79)],
        "melody":[67,69,71,74,76],
        "desc":"Sóng biển nhẹ nhàng + piano buổi sáng G major. Thức dậy bình an, giảm lo âu.",
    },
    "🌙 Midnight Ocean — Pure Nature Sleep": {
        "wave_period":11.0,"wind":0.18,"depth":"deep",
        "piano":False,"bpm":42,
        "prog":[],"melody":[],
        "desc":"Chỉ tiếng sóng đêm khuya + gió biển. Thuần thiên nhiên, không nhạc.",
    },
    "🐋 Underwater Meditation — Whale & Depth": {
        "wave_period":13.0,"wind":0.05,"depth":"underwater",
        "piano":False,"bpm":40,
        "prog":[],"melody":[],
        "desc":"Âm thanh đáy đại dương + whale song analog + áp suất nước sâu.",
    },
    "🌅 Sunset Cove — Piano & Ocean Blend": {
        "wave_period":7.5,"wind":0.09,"depth":"shallow",
        "piano":True,"bpm":46,
        "prog":[(62,66,69),(69,73,76),(71,74,78),(67,71,74)],
        "melody":[62,64,66,69,71],
        "desc":"Hoàng hôn bên bờ biển. Piano D major 46 BPM + sóng chiều tà. Chữa lành cảm xúc.",
    },
}

# FIX 2: ocean_waves uses fast_lp instead of np.convolve
def ocean_waves(dur, wave_period=8.0, depth="shallow", wind_vol=0.10, ocean_vol=0.70):
    n = int(SR * dur)
    rng = np.random.default_rng(99)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = rng.normal(0, 1, n).astype(np.float64)

    deep = fast_lp(noise, int(SR*0.014)) * 0.60
    mid  = (fast_lp(noise, int(SR*0.0025)) - deep) * 0.30
    hiss = (noise - fast_lp(noise, int(SR*0.0004))) * 0.10
    raw  = deep + mid + hiss

    phase = (t % wave_period) / wave_period
    wave_env = np.sin(np.pi * phase)**2 * 0.65 + 0.35
    phase2 = (t % (wave_period * 0.55)) / (wave_period * 0.55)
    wave_env += np.sin(np.pi * phase2)**2 * 0.20
    ocean = raw * wave_env

    if depth == "deep":
        ocean = fast_lp(ocean, int(SR*0.006)) * 1.3
    elif depth == "underwater":
        ocean = fast_lp(ocean, int(SR*0.020)) * 1.6
        whomp = 0.12 + 0.04*np.sin(2*np.pi*0.007*t)
        ocean *= 0.7 + 0.3*np.sin(2*np.pi*whomp*t)

    ocean = ocean / (np.max(np.abs(ocean)) + 1e-9)

    if wind_vol > 0:
        wind_noise = rng.normal(0, 1, n).astype(np.float64)
        wind = fast_lp(wind_noise, int(SR*0.001))
        wind_sw = 0.6 + 0.4*np.sin(2*np.pi*0.022*t + 1.2)
        wind = wind / (np.max(np.abs(wind))+1e-9) * wind_sw
        ocean = ocean*ocean_vol + wind*wind_vol
    else:
        ocean = ocean * ocean_vol

    return ocean

# FIX 3: whale_song division safe
def whale_song(dur, vol=0.10):
    n = int(SR * dur)
    rng = np.random.default_rng(55)
    t = np.linspace(0, dur, n, endpoint=False)
    out = np.zeros(n)
    t_w = float(rng.uniform(5, 12))
    while t_w < dur - 10:
        call_dur = float(rng.uniform(4, 9))
        cn = int(call_dur * SR)
        ct = np.linspace(0, call_dur, cn, endpoint=False)
        f_sw = 65 + 35*np.sin(np.pi*ct/call_dur) + 8*np.sin(2*np.pi*0.8*ct)
        phase = np.cumsum(2*np.pi*f_sw/SR)
        call = (np.sin(phase)*0.6 + np.sin(phase*2)*0.25) * (np.sin(np.pi*ct/call_dur)**0.6)
        pos = int(t_w*SR); end = min(pos+cn, n)
        out[pos:end] += call[:end-pos] * float(rng.uniform(0.7, 1.0))
        t_w += call_dur + float(rng.uniform(8, 20))
    pk = np.max(np.abs(out))
    if pk > 0.001:
        out = out / pk
    return out * vol

def underwater_ambient(dur, vol=0.08):
    n = int(SR*dur); t = np.linspace(0, dur, n, endpoint=False)
    f_d = 48 + 6*np.sin(2*np.pi*0.018*t) + 3*np.sin(2*np.pi*0.007*t)
    phase = np.cumsum(2*np.pi*f_d/SR)
    tone = (np.sin(phase)*0.55 + np.sin(phase*2)*0.28 + np.sin(phase*3)*0.12)
    swell = 0.50 + 0.50*np.abs(np.sin(2*np.pi*0.012*t))
    return tone * swell * vol

def ocean_piano(dur, cfg):
    if not cfg.get("piano") or not cfg.get("prog"):
        return np.zeros(int(SR*dur))
    rng = np.random.default_rng(33)
    n = int(SR*dur); out = np.zeros(n, dtype=np.float64)
    bpm=cfg["bpm"]; beat=60.0/bpm; chord_dur=beat*6
    prog=cfg["prog"]; mel=cfg["melody"]

    t_c=beat*float(rng.uniform(3,6)); ci=0
    while t_c < dur-chord_dur*0.5:
        cd = min(chord_dur+beat, dur-t_c+1)
        pad = chord_pad(prog[ci%len(prog)], cd, vol=0.10)
        pos=int(t_c*SR); end=min(pos+len(pad), n)
        out[pos:end] += pad[:end-pos] * 0.55
        t_c += chord_dur; ci += 1

    nt = beat*float(rng.uniform(4, 8))
    while nt < dur-beat*4:
        mid=mel[int(rng.integers(0, len(mel)))]
        nd=float(rng.choice(np.array([beat*2, beat*3, beat*4])))
        vel=float(rng.uniform(0.28, 0.48))
        note=piano_note(note_freq(mid), nd, vel, bright=0.70)
        pos=int(nt*SR); end=min(pos+len(note), n)
        if pos < n:
            out[pos:end] += note[:end-pos] * 0.50
        nt += nd*0.90 + beat*float(rng.uniform(2.5, 6.0))

    return out

def generate_ocean(cfg, duration_sec, ocean_vol, wind_vol, piano_vol,
                   whale_on, reverb_strength):
    n = int(duration_sec * SR); out = np.zeros(n, dtype=np.float64)

    ocean = ocean_waves(duration_sec,
                        wave_period=cfg["wave_period"],
                        depth=cfg["depth"],
                        wind_vol=wind_vol * cfg["wind"],
                        ocean_vol=ocean_vol * 0.85)
    out[:len(ocean)] += ocean[:n]

    if cfg["depth"] == "underwater":
        out += underwater_ambient(duration_sec)[:n]
    if whale_on:
        out += whale_song(duration_sec)[:n]

    if cfg["piano"] and piano_vol > 0:
        pn = ocean_piano(duration_sec, cfg)
        out += pn[:n] * piano_vol

    t = np.linspace(0, duration_sec, n, endpoint=False)
    out += np.sin(2*np.pi*963.0*t) * (0.80+0.20*np.sin(2*np.pi*0.05*t)) * 0.010

    out = reverb_hall(out, strength=min(reverb_strength, 0.55))
    out = slow_fade(out, fade_sec=10.0)
    out = normalize(out)
    return to_wav(out)


# ══════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════
st.title("🎵 432Hz · Healing Music Generator")
st.markdown("*Worship Piano · Ocean Sleep · 432Hz Sacred Tuning · 1111Hz Undertone*")
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
        bpm=cfg_w['bpm']; bd=round(60/bpm,2)
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
            file_name=f"432hz_{fname}_{dur_w}min.wav", mime="audio/wav",
            use_container_width=True, key="dl_w")

    st.caption("✝ 432Hz · 1111Hz Healing · I–V–vi–IV Worship · *Be still, and know that I am God* — Ps 46:10")

# ─── TAB 2 ───────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🌊 Ocean Music for Sleep")
    st.markdown("*Tiếng sóng biển chữa lành · Ngủ sâu · Thư giãn · Thiền định*")

    # FIX 4: cap ocean duration to avoid OOM on Streamlit Cloud
    MAX_OCEAN_MIN = 30

    o_name = st.selectbox("🌊 Chọn cảnh biển", list(OCEAN_PRESETS.keys()), key="op")
    cfg_o  = OCEAN_PRESETS[o_name]
    st.info(cfg_o["desc"])

    c5,c6 = st.columns(2)
    with c5: dur_o   = st.slider("⏱ Thời lượng (phút)", 1, MAX_OCEAN_MIN, 10, 1, key="dur_o",
                                  help=f"Tối đa {MAX_OCEAN_MIN} phút cho ocean (tối ưu RAM)")
    with c6: ocean_v = st.slider("🌊 Âm lượng sóng", 0.3, 1.0, 0.80, 0.05, key="ocv")

    c7,c8 = st.columns(2)
    with c7: wind_v  = st.slider("💨 Gió biển", 0.0, 1.0, 0.5, 0.05, key="wv")
    with c8:
        # FIX 5: removed disabled= parameter, use conditional logic instead
        if cfg_o["piano"]:
            piano_v = st.slider("🎹 Piano", 0.0, 1.0, 0.55, 0.05, key="pv")
        else:
            st.info("🎹 Preset này không có piano (pure nature)")
            piano_v = 0.0

    c9,c10 = st.columns(2)
    with c9:  whale_on = st.toggle("🐋 Whale Song / Underwater", value=True, key="whale")
    with c10: rev_o    = st.slider("🔊 Reverb", 0.1, 0.8, 0.35, 0.05, key="rev_o")

    with st.expander("📋 Chi tiết âm thanh"):
        st.markdown(f"""
| Layer | Chi tiết |
|---|---|
| 🌊 Ocean waves | Wave period: **{cfg_o['wave_period']}s** · Depth: **{cfg_o['depth']}** |
| 💨 Wind | Base intensity: **{int(cfg_o['wind']*100)}%** |
| 🎹 Piano | **{"Có · " + str(cfg_o.get("bpm","")) + " BPM" if cfg_o["piano"] else "Không (pure nature)"}** |
| 🐋 Whale | Whale calls + underwater pressure tones |
| ✨ Undertone | 963Hz healing frequency (rất nhẹ) |
""")

    if st.button("🌊 TẠO NHẠC BIỂN CHO GIẤC NGỦ 🌊", use_container_width=True, key="btn_o"):
        with st.spinner(f"Đang tạo {o_name} · {dur_o} phút 🌊"):
            audio_o = generate_ocean(cfg_o, dur_o*60, ocean_v, wind_v, piano_v,
                                     whale_on, rev_o)
        mb = len(audio_o)/(1024*1024)
        st.success(f"🌊 Hoàn thành · {dur_o} phút · {mb:.1f} MB")
        st.audio(audio_o, format="audio/wav")
        fname2 = ''.join(c for c in o_name.split("—")[0] if c.isalnum() or c==' ').strip().replace(' ','_').lower()
        st.download_button("⬇ Tải WAV", audio_o,
            file_name=f"ocean_{fname2}_{dur_o}min.wav", mime="audio/wav",
            use_container_width=True, key="dl_o")

    st.caption("🌊 Ocean · Whale Song · 963Hz · Nature Sleep Sounds · *The sea is his, and he made it* — Ps 95:5")
