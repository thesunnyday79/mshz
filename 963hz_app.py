import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(
    page_title="963 Hz · Angelic Piano Healing",
    page_icon="🎹",
    layout="centered",
)

SR = 44100

# ── Scale: 963 Hz base, just-intonation ratios (ethereal/angelic) ──
BASE = 963.0
SCALE = [
    BASE/4,       # 0: 240.75
    BASE*9/32,    # 1: 270.84
    BASE*5/16,    # 2: 300.94
    BASE/2,       # 3: 481.5
    BASE*9/16,    # 4: 541.69
    BASE*5/8,     # 5: 601.88
    BASE*3/4,     # 6: 722.25
    BASE,         # 7: 963
    BASE*9/8,     # 8: 1083.4
    BASE*5/4,     # 9: 1203.75
    BASE*3/2,     # 10: 1444.5
    BASE*2,       # 11: 1926
]

MELODY_PATTERNS = [
    [(7,2.5),(6,2.0),(5,2.5),(4,3.0),(3,4.0)],
    [(3,2.0),(4,2.0),(5,2.5),(7,3.0),(8,2.5),(7,4.5)],
    [(7,3.0),(8,2.0),(7,2.5),(6,2.0),(7,4.0)],
    [(10,2.0),(9,1.5),(8,2.0),(7,2.5),(6,3.0),(5,4.0)],
    [(4,2.5),(5,2.0),(7,3.0),(6,2.5),(4,4.5)],
    [(8,2.0),(9,1.5),(10,2.5),(8,2.0),(7,4.0)],
    [(7,3.5),(8,2.0),(9,2.5),(8,3.0),(7,4.5)],
    [(5,2.0),(6,1.5),(7,2.0),(8,1.5),(9,3.5)],
]

def piano_note(freq, duration, velocity=0.6):
    n = int(SR * duration)
    if n == 0:
        return np.zeros(1)
    t = np.linspace(0, duration, n, endpoint=False)
    tone = (
        np.sin(2*np.pi*freq*1*t) * 1.00 +
        np.sin(2*np.pi*freq*2*t) * 0.50 +
        np.sin(2*np.pi*freq*3*t) * 0.22 +
        np.sin(2*np.pi*freq*4*t) * 0.10 +
        np.sin(2*np.pi*freq*5*t) * 0.05 +
        np.sin(2*np.pi*freq*6*t) * 0.025
    )
    atk = max(1, int(0.008 * SR))
    env = np.zeros(n)
    env[:atk] = np.linspace(0, 1, atk)
    rest = n - atk
    if rest > 0:
        env[atk:] = np.exp(-3.2 * np.linspace(0, duration, rest))
    return tone * env * velocity

def soft_pad(f, dur, detune=0.0025):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    out = np.zeros(n)
    for d, w in zip([-0.004, -0.002, 0, 0.002, 0.004],
                    [0.45,   0.75,   1.0, 0.75,  0.45]):
        out += np.sin(2*np.pi*f*(1+d)*t) * w
    out += np.sin(2*np.pi*f*2*t) * 0.10
    out += np.sin(2*np.pi*f*3*t) * 0.04
    return out / (np.max(np.abs(out)) + 1e-9)

def reverb_vec(sig, decay=0.50, delays_ms=(30, 62, 105, 165, 240)):
    out = sig.astype(np.float64).copy()
    d = decay
    for ms in delays_ms:
        nd = int(ms * SR / 1000)
        if nd < len(sig):
            ref = np.zeros(len(sig), dtype=np.float64)
            ref[nd:] = sig[:-nd] * d
            out += ref
            d *= 0.48
    return out

def generate_music(duration_sec, style, piano_vol, pad_vol, bell_on, reverb_strength):
    n = int(duration_sec * SR)
    out = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(42)

    # ── 1. Ambient pad background ──────────────────────────────────────────────
    pad_config = {
        "Piano + Ambient Pad":  [BASE/2, BASE, BASE*3/2],
        "Piano + Deep Bass":    [BASE/4, BASE/2, BASE],
        "Piano Solo (Pure)":    [BASE],
        "Piano + Bell Choir":   [BASE/2, BASE],
        "Deep Meditation":      [BASE/4, BASE/2, BASE, BASE*3/2],
    }
    t_arr = np.linspace(0, duration_sec, n, endpoint=False)
    for k, f in enumerate(pad_config.get(style, [BASE/2, BASE])):
        layer = soft_pad(f, duration_sec) * (pad_vol * 0.15 / (k+1))
        layer *= 0.85 + 0.15 * np.sin(2*np.pi*0.04*t_arr + k*1.4)
        out += layer

    # ── 2. Piano melody (right hand) ───────────────────────────────────────────
    melody_lo, melody_hi = 4, 10
    if style == "Deep Meditation":
        melody_lo, melody_hi = 3, 8
    elif style == "Piano Solo (Pure)":
        melody_lo, melody_hi = 5, 11

    t_cur = float(rng.uniform(2.5, 5.0))
    while t_cur < duration_sec - 10:
        pat = MELODY_PATTERNS[int(rng.integers(0, len(MELODY_PATTERNS)))]
        offset = int(rng.integers(-1, 2))
        note_t = t_cur
        for si, nd in pat:
            idx = max(0, min(len(SCALE)-1, si + offset))
            freq = SCALE[idx]
            vel = float(rng.uniform(0.40, 0.72))
            note = piano_note(freq, nd, vel)
            pos = int(note_t * SR)
            end = min(pos + len(note), n)
            if pos < n:
                out[pos:end] += note[:end-pos] * piano_vol * 0.55
            note_t += nd * 0.82  # slight legato overlap
        t_cur = note_t + float(rng.uniform(1.8, 4.5))

    # ── 3. Bass notes (left hand) ──────────────────────────────────────────────
    bass_t = float(rng.uniform(3.0, 7.0))
    bass_pool = [SCALE[0], SCALE[1], SCALE[2], SCALE[3]]
    while bass_t < duration_sec - 6:
        bf = float(rng.choice(bass_pool))
        bd = float(rng.uniform(3.5, 6.0))
        bn = piano_note(bf, bd, float(rng.uniform(0.25, 0.45)))
        pos = int(bass_t * SR)
        end = min(pos + len(bn), n)
        if pos < n:
            out[pos:end] += bn[:end-pos] * piano_vol * 0.42
        bass_t += float(rng.uniform(7.0, 14.0))

    # ── 4. Crystal bell chimes ─────────────────────────────────────────────────
    if bell_on:
        bell_t = float(rng.uniform(6, 12))
        while bell_t < duration_sec - 4:
            bf = SCALE[int(rng.integers(7, 12))]
            bd = float(rng.uniform(2.5, 4.5))
            bn_n = int(bd * SR)
            bt = np.linspace(0, bd, bn_n, endpoint=False)
            bell = (
                np.sin(2*np.pi*bf*bt)       * 0.55 +
                np.sin(2*np.pi*bf*2.756*bt) * 0.20 * np.exp(-5.0*bt) +
                np.sin(2*np.pi*bf*5.404*bt) * 0.08 * np.exp(-8.0*bt)
            ) * np.exp(-2.5*bt)
            pos = int(bell_t * SR)
            end = min(pos + bn_n, n)
            if pos < n:
                out[pos:end] += bell[:end-pos] * float(rng.uniform(0.07, 0.13))
            bell_t += float(rng.uniform(10, 22))

    # ── 5. Reverb ──────────────────────────────────────────────────────────────
    rev_decay = 0.38 + reverb_strength * 0.28
    rev_delays = (28, 60, 100, 160, 230, 320) if reverb_strength > 0.6 else (30, 65, 115)
    out = reverb_vec(out, decay=rev_decay, delays_ms=rev_delays)

    # ── 6. Fade & normalize ────────────────────────────────────────────────────
    fade = min(int(7 * SR), n // 4)
    out[:fade]  *= np.linspace(0.0, 1.0, fade)
    out[-fade:] *= np.linspace(1.0, 0.0, fade)
    pk = np.max(np.abs(out))
    if pk > 0:
        out = out / pk * 0.88

    pcm = (out * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("🎹 963 Hz — Angelic Piano Healing")
st.markdown("*Nhạc piano chữa lành · Jesus Christ Frequency · Thư giãn · Ngủ sâu · Giảm stress*")
st.divider()

STYLES = {
    "Piano + Ambient Pad":  "🎹 Piano giai điệu + nền pad mềm mại — êm dịu nhất, phù hợp thư giãn & ngủ",
    "Piano + Deep Bass":    "🎹 Piano + bass sâu 963 Hz — grounding, chữa lành sâu thẳm",
    "Piano Solo (Pure)":    "🎹 Piano thuần — giai điệu rõ ràng, trong trẻo, thiền định",
    "Piano + Bell Choir":   "🎹 Piano + chuông thiên thần — thánh thót, tâm linh",
    "Deep Meditation":      "🧘 Thiền sâu — nhịp chậm, tần số thấp, thả lỏng hoàn toàn",
}

style = st.selectbox("🎵 Phong cách âm nhạc", list(STYLES.keys()))
st.info(STYLES[style])

col1, col2 = st.columns(2)
with col1:
    duration_min = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1)
with col2:
    reverb_strength = st.slider("🏛 Reverb (độ vang)", 0.1, 1.0, 0.7, 0.05,
                                help="Cao = vang như nhà thờ, thấp = phòng nhỏ ấm áp")

col3, col4 = st.columns(2)
with col3:
    piano_vol = st.slider("🎹 Âm lượng Piano", 0.1, 1.0, 0.85, 0.05)
with col4:
    pad_vol = st.slider("🌊 Âm lượng Pad nền", 0.0, 1.0, 0.7, 0.05)

bell_on = st.toggle("🔔 Chuông thiên thần (Crystal Bells)", value=True)

st.divider()

if st.button("✦ TẠO NHẠC PIANO CHỮA LÀNH ✦", use_container_width=True):
    dur_sec = duration_min * 60
    with st.spinner(f"Đang soạn nhạc piano {duration_min} phút... 🎹"):
        audio_bytes = generate_music(
            duration_sec=dur_sec,
            style=style,
            piano_vol=piano_vol,
            pad_vol=pad_vol,
            bell_on=bell_on,
            reverb_strength=reverb_strength,
        )
    mb = len(audio_bytes) / (1024 * 1024)
    st.success(f"✦ Hoàn thành · {duration_min} phút · {style} · {mb:.1f} MB")
    st.audio(audio_bytes, format="audio/wav")
    fname = style.lower().replace(" ", "_").replace("+","").replace("(","").replace(")","").replace("__","_").strip("_")
    st.download_button(
        label="⬇ Tải Xuống File WAV",
        data=audio_bytes,
        file_name=f"963hz_piano_{fname}_{duration_min}min.wav",
        mime="audio/wav",
        use_container_width=True,
    )

st.divider()
st.caption("🎹 963 Hz · Solfeggio Frequency of God · Piano Angelic Healing · *Be still, and know that I am God* — Psalm 46:10")
