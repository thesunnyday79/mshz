import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(
    page_title="432Hz · Healing Worship Music",
    page_icon="✝",
    layout="centered",
)

# ══════════════════════════════════════════════════════
#  MUSIC ENGINE — 432Hz tuned, real chord progressions
# ══════════════════════════════════════════════════════
SR = 44100
TUNE = 432.0 / 440.0  # 432Hz tuning ratio

def note_freq(midi):
    """MIDI note → frequency at 432Hz tuning"""
    return 440.0 * (2 ** ((midi - 69) / 12)) * TUNE

# ── Chord progressions per preset (I-V-vi-IV in each key) ──
PRESETS = {
    "✝ Deep Healing Worship (A major · 52 BPM)": {
        "key": "A_major", "bpm": 52, "rain": True, "base_vol": 0.55,
        "prog": [(69,73,76),(76,80,83),(78,81,85),(74,78,81)],  # A-E-F#m-D
        "melody": [69,71,73,76,78,80],  # A B C# E F# G#
        "desc": "Peace and surrender in God's presence. Soft grand piano + rain texture + 1111Hz healing undertone.",
    },
    "🌧 Rainy Morning Prayer (D major · 48 BPM)": {
        "key": "D_major", "bpm": 48, "rain": True, "base_vol": 0.50,
        "prog": [(62,66,69),(69,73,76),(71,74,78),(67,71,74)],  # D-A-Bm-G
        "melody": [62,64,66,69,71,74],  # D E F# A B D
        "desc": "Quiet prayer on a rainy morning. Warm chord progressions, delicate high notes, angelic pads.",
    },
    "✝ Time Alone With God (G major · 45 BPM)": {
        "key": "G_major", "bpm": 45, "rain": False, "base_vol": 0.48,
        "prog": [(67,71,74),(74,78,81),(76,79,83),(72,76,79)],  # G-D-Em-C
        "melody": [67,69,71,74,76,79],  # G A B D E G
        "desc": "Minimalist & reverent. Deep resonant bass notes, tender melody, choir-like pads. Stillness.",
    },
    "✨ Jesus Presence Healing (E major · 50 BPM)": {
        "key": "E_major", "bpm": 50, "rain": False, "base_vol": 0.52,
        "prog": [(64,68,71),(71,75,78),(73,76,80),(69,73,76)],  # E-B-C#m-A
        "melody": [64,66,68,71,73,76],  # E F# G# B C# E
        "desc": "Cinematic & intimate. Emotional piano flowing at 50 BPM, glowing pads, spacious sound design.",
    },
    "🌤 Trust In God's Care (C major · 54 BPM)": {
        "key": "C_major", "bpm": 54, "rain": False, "base_vol": 0.56,
        "prog": [(60,64,67),(67,71,74),(69,72,76),(65,69,72)],  # C-G-Am-F
        "melody": [60,62,64,67,69,72],  # C D E G A C
        "desc": "Peace, trust, surrender. Warm I-V-vi-IV progression, loop-ready, ideal for 3-hour worship sessions.",
    },
}

# ── Piano synthesis (432Hz tuned, realistic envelope) ──
def piano_note(freq, dur, vel=0.65, bright=0.85):
    n = int(SR * dur)
    if n < 2: return np.zeros(2)
    t = np.linspace(0, dur, n, endpoint=False)
    atk_env = np.exp(-7 * t)
    tone = (
        np.sin(2*np.pi*freq*1*t) * 1.000 +
        np.sin(2*np.pi*freq*2*t) * (0.52 * bright) +
        np.sin(2*np.pi*freq*3*t) * (0.26 * bright * (1 + 0.35*atk_env)) +
        np.sin(2*np.pi*freq*4*t) * (0.13 * bright * atk_env) +
        np.sin(2*np.pi*freq*5*t) * (0.06 * bright * atk_env) +
        np.sin(2*np.pi*freq*6*t) * (0.03 * atk_env)
    )
    atk_n = max(1, int(0.007 * SR))
    env = np.zeros(n)
    env[:atk_n] = np.linspace(0, 1, atk_n)
    rest = n - atk_n
    if rest > 0:
        s1 = int(rest * 0.14)
        s2 = rest - s1
        if s1 > 0: env[atk_n:atk_n+s1] = np.linspace(1.0, 0.70, s1)
        if s2 > 0: env[atk_n+s1:] = 0.70 * np.exp(-2.0 * np.linspace(0, dur*0.85, s2))
    return tone * env * vel

# ── Chord pad (choir/string hybrid, warm & wide) ──
def chord_pad(midi_notes, dur, vol=0.16):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    out = np.zeros(n)
    for midi in midi_notes:
        f = note_freq(midi)
        for d, w in zip([-0.0035,-0.0015,0.0,0.0015,0.0035],
                        [0.45, 0.80, 1.00, 0.80, 0.45]):
            out += np.sin(2*np.pi*f*(1+d)*t) * w * vol * 0.28
        out += np.sin(2*np.pi*f*2*t) * vol * 0.055
    swell_n = min(int(SR*2.5), n//3)
    swell = np.ones(n)
    swell[:swell_n] = np.linspace(0, 1, swell_n)
    swell[-swell_n:] *= np.linspace(1, 0.35, swell_n)
    return out * swell

# ── Bass piano note (left hand, grounding) ──
def bass_note(freq, dur, vel=0.40):
    n = int(SR * dur)
    if n < 2: return np.zeros(2)
    t = np.linspace(0, dur, n, endpoint=False)
    tone = (np.sin(2*np.pi*freq*t) * 1.0 +
            np.sin(2*np.pi*freq*2*t) * 0.35 +
            np.sin(2*np.pi*freq*3*t) * 0.12)
    atk_n = max(1, int(0.010*SR))
    env = np.zeros(n)
    env[:atk_n] = np.linspace(0,1,atk_n)
    rest = n-atk_n
    if rest > 0: env[atk_n:] = np.exp(-1.6*np.linspace(0,dur,rest))
    return tone * env * vel

# ── 1111Hz healing undertone (felt more than heard) ──
def healing_undertone(dur, vol=0.016):
    n = int(SR*dur)
    t = np.linspace(0, dur, n, endpoint=False)
    tone = np.sin(2*np.pi*1111.0*t)
    tone *= 0.82 + 0.18*np.sin(2*np.pi*0.07*t)  # slow breath
    return tone * vol

# ── Rain texture (filtered noise + drips) ──
def rain_texture(dur, vol=0.038):
    n = int(SR*dur)
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, n)
    kernel = np.ones(90)/90
    filtered = np.convolve(noise, kernel, mode='same')
    drip_times = rng.integers(0, n, size=max(1, n//700))
    for dt in drip_times:
        dl = int(0.014*SR)
        if dt + dl < n:
            td = np.linspace(0,1,dl)
            filtered[dt:dt+dl] += np.sin(2*np.pi*580*td)*np.exp(-9*td)*0.5
    filtered = filtered/(np.max(np.abs(filtered))+1e-9)
    fade_n = min(int(SR*4), n//4)
    filtered[:fade_n] *= np.linspace(0,1,fade_n)
    return filtered * vol

# ── Reverb (hall reverb, vectorized) ──
def reverb_hall(sig, strength=0.65):
    decay = 0.40 + strength * 0.30
    delays = (30,65,108,172,255,360) if strength > 0.6 else (32,68,115)
    out = sig.astype(np.float64).copy()
    d = decay
    for ms in delays:
        nd = int(ms*SR/1000)
        if nd < len(sig):
            ref = np.zeros(len(sig))
            ref[nd:] = sig[:-nd]*d
            out += ref; d *= 0.45
    return out

# ── Intensity arc: maps section time → volume multiplier ──
def intensity_arc(t_arr, dur, arc_type="worship"):
    # Mimics Lyria 3 timestamp intensity: low→build→peak→resolve
    x = t_arr / dur
    if arc_type == "worship":
        # 0.1→0.2→0.35→0.1 (peaceful, never loud)
        arc = np.where(x < 0.2, 0.10 + x*0.5,
              np.where(x < 0.55, 0.20 + (x-0.2)*0.43,
              np.where(x < 0.80, 0.35 - (x-0.55)*0.80,
                                 0.15 - (x-0.80)*0.5)))
    elif arc_type == "minimalist":
        arc = np.where(x < 0.25, 0.05 + x*0.6,
              np.where(x < 0.65, 0.20,
                                 0.20 - (x-0.65)*0.57))
    else:
        arc = 0.25 * np.ones_like(x)
    return np.clip(arc, 0.05, 0.40)

# ══════════════════════════════════════════════════════
#  MAIN GENERATOR
# ══════════════════════════════════════════════════════
def generate_music(preset_cfg, duration_sec, reverb_strength, rain_vol, bell_on, piano_expression):
    rng = np.random.default_rng(42)
    n = int(duration_sec * SR)
    out = np.zeros(n, dtype=np.float64)
    t_arr = np.linspace(0, duration_sec, n, endpoint=False)

    bpm        = preset_cfg["bpm"]
    prog       = preset_cfg["prog"]
    melody_set = preset_cfg["melody"]
    has_rain   = preset_cfg["rain"]
    arc_type   = "minimalist" if "God" in list(PRESETS.keys())[2] else "worship"

    beat_dur  = 60.0 / bpm
    chord_dur = beat_dur * 4          # one chord per bar (4 beats)

    # ── Intensity arc ────────────────────────────────
    arc = intensity_arc(t_arr, duration_sec)

    # ── 1. Chord pads (I-V-vi-IV cycling) ─────────────
    t_c = 0.0; ci = 0
    while t_c < duration_sec - chord_dur * 0.5:
        chord = prog[ci % len(prog)]
        cd = chord_dur + beat_dur * 0.5  # slight overlap for legato
        pad = chord_pad(chord, min(cd, duration_sec - t_c + 1))
        pos = int(t_c*SR); end = min(pos+len(pad), n)
        arc_vol = float(np.mean(arc[pos:min(pos+len(pad),n)])) if pos < n else 0.15
        out[pos:end] += pad[:end-pos] * (arc_vol / 0.25)
        t_c += chord_dur; ci += 1

    # ── 2. Piano melody (right hand) ─────────────────
    note_t = beat_dur * float(rng.uniform(1.5, 3.0))
    phrase_len = 5 + int(rng.integers(0, 3))  # notes per phrase
    while note_t < duration_sec - beat_dur * 3:
        # Choose melody note — prefer stepwise motion
        mid = melody_set[int(rng.integers(0, len(melody_set)))]
        nd  = float(rng.choice([beat_dur, beat_dur*1.5, beat_dur*2.0, beat_dur*2.5]))
        vel = float(rng.uniform(0.38, 0.62)) * piano_expression
        note = piano_note(note_freq(mid), nd, vel)
        pos  = int(note_t*SR); end = min(pos+len(note), n)
        if pos < n:
            arc_v = float(arc[min(pos, n-1)])
            out[pos:end] += note[:end-pos] * (arc_v / 0.20) * 0.60
        note_t += nd * 0.86  # legato overlap
        # phrase gap
        if int(rng.integers(0, phrase_len)) == 0:
            note_t += beat_dur * float(rng.uniform(2.0, 4.5))

    # ── 3. Bass notes (left hand — root of each chord) ──
    t_b = beat_dur * float(rng.uniform(0.5, 1.5))
    bi  = 0
    while t_b < duration_sec - beat_dur * 2:
        root_midi = prog[bi % len(prog)][0] - 12  # one octave lower
        bd = beat_dur * float(rng.choice([3.0, 4.0, 5.0]))
        bn = bass_note(note_freq(root_midi), min(bd, duration_sec - t_b))
        pos = int(t_b*SR); end = min(pos+len(bn), n)
        if pos < n:
            arc_v = float(arc[min(pos, n-1)])
            out[pos:end] += bn[:end-pos] * (arc_v/0.22) * 0.42
        t_b += beat_dur * float(rng.choice([3.5, 4.0, 4.5, 6.0])); bi += 1

    # ── 4. Crystal bell accents ───────────────────────
    if bell_on:
        bell_t = beat_dur * float(rng.uniform(4, 8))
        while bell_t < duration_sec - 4:
            mid_b = melody_set[int(rng.integers(0, len(melody_set)))] + 12
            f_b   = note_freq(mid_b)
            bd_s  = float(rng.uniform(2.5, 4.0))
            bn_n  = int(bd_s*SR)
            bt    = np.linspace(0, bd_s, bn_n, endpoint=False)
            bell  = (np.sin(2*np.pi*f_b*bt)*0.55 +
                     np.sin(2*np.pi*f_b*2.756*bt)*0.20*np.exp(-5*bt) +
                     np.sin(2*np.pi*f_b*5.40*bt)*0.08*np.exp(-8*bt)) * np.exp(-2.6*bt)
            pos   = int(bell_t*SR); end = min(pos+bn_n, n)
            if pos < n:
                arc_v = float(arc[min(pos,n-1)])
                out[pos:end] += bell[:end-pos] * float(rng.uniform(0.06,0.12)) * (arc_v/0.20)
            bell_t += beat_dur * float(rng.uniform(6, 14))

    # ── 5. 1111Hz healing undertone ───────────────────
    out += healing_undertone(duration_sec)

    # ── 6. Rain texture ───────────────────────────────
    if has_rain and rain_vol > 0:
        out += rain_texture(duration_sec, vol=rain_vol * 0.06)

    # ── 7. Hall reverb ────────────────────────────────
    out = reverb_hall(out, strength=reverb_strength)

    # ── 8. Slow fade in/out ───────────────────────────
    fade = min(int(8*SR), n//4)
    out[:fade]  *= np.linspace(0.0, 1.0, fade)
    out[-fade:] *= np.linspace(1.0, 0.0, fade)

    # ── 9. Normalize ─────────────────────────────────
    pk = np.max(np.abs(out))
    if pk > 0: out = out/pk * 0.88

    pcm = (out * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ══════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════
st.title("✝ 432Hz · Healing Worship Music")
st.markdown("*Piano chữa lành · 432Hz tuning · 1111Hz undertone · Christian Worship · Deep Prayer*")
st.divider()

preset_name = st.selectbox("🎹 Chọn preset", list(PRESETS.keys()))
cfg = PRESETS[preset_name]
st.info(f"**{cfg['key'].replace('_',' ')} · {cfg['bpm']} BPM**  \n{cfg['desc']}")

st.divider()

col1, col2 = st.columns(2)
with col1:
    duration_min = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1)
with col2:
    reverb_strength = st.slider("🏛 Reverb — Cathedral Hall", 0.2, 1.0, 0.72, 0.04,
        help="0.2 = phòng ấm · 1.0 = nhà thờ rộng")

col3, col4 = st.columns(2)
with col3:
    piano_expression = st.slider("🎹 Piano Expression", 0.5, 1.5, 1.0, 0.05,
        help="Cao = mạnh hơn, nhiều cảm xúc hơn")
with col4:
    rain_vol = st.slider("🌧 Rain Texture", 0.0, 1.0, 0.6 if cfg["rain"] else 0.0, 0.05,
        help="0 = không có mưa · 1.0 = mưa đầy")

col5, col6 = st.columns(2)
with col5:
    bell_on = st.toggle("🔔 Crystal Bell Chimes", value=True)
with col6:
    st.metric("🎵 Key & Tuning", f"{cfg['key'].replace('_',' ')} · 432Hz")

st.divider()

# Show structure preview
with st.expander("📋 Xem cấu trúc bài (Intensity Arc)"):
    bpm = cfg['bpm']
    bd  = 60/bpm
    st.markdown(f"""
**{preset_name}**  
Tuning: 432Hz · BPM: {bpm} · Beat duration: {bd:.2f}s · 1 chord per {bd*4:.1f}s

| Section | Thời gian | Nội dung | Intensity |
|---|---|---|---|
| Intro | 0:00 – 0:{int(duration_min*60*0.12):02d} | Pad + bass note đầu tiên | 0.5–1/10 |
| Theme A | 0:{int(duration_min*60*0.12):02d} – {duration_min//3}:{int((duration_min*60*0.35)%60):02d} | Piano melody + chord pads | 2–3/10 |
| Build | {duration_min//3}:{int((duration_min*60*0.35)%60):02d} – {int(duration_min*0.65)}:{int((duration_min*60*0.65)%60):02d} | Peak — pads swell + bells | 3–3.5/10 |
| Resolution | {int(duration_min*0.65)}:{int((duration_min*60*0.65)%60):02d} – {duration_min}:00 | Strip back, fade | 1–1.5/10 |
""")

if st.button("✦ TẠO NHẠC CHỮA LÀNH 432Hz ✦", use_container_width=True):
    dur_sec = duration_min * 60
    with st.spinner(f"Đang soạn nhạc {preset_name} · {duration_min} phút ✝"):
        audio_bytes = generate_music(
            preset_cfg      = cfg,
            duration_sec    = dur_sec,
            reverb_strength = reverb_strength,
            rain_vol        = rain_vol,
            bell_on         = bell_on,
            piano_expression= piano_expression,
        )
    mb = len(audio_bytes) / (1024*1024)
    st.success(f"✦ Hoàn thành · {duration_min} phút · {cfg['key'].replace('_',' ')} · 432Hz · {mb:.1f} MB")
    st.audio(audio_bytes, format="audio/wav")
    fname = preset_name.split("(")[0].strip().replace(" ","_").replace("✝","").replace("🌧","").replace("✨","").replace("🌤","").strip("_").lower()
    st.download_button(
        "⬇ Tải Xuống WAV",
        data=audio_bytes,
        file_name=f"432hz_{fname}_{duration_min}min.wav",
        mime="audio/wav",
        use_container_width=True,
    )

st.divider()
st.caption("✝ 432Hz Sacred Tuning · 1111Hz Healing Undertone · I–V–vi–IV Worship Progressions · *Be still, and know that I am God* — Psalm 46:10")
