import streamlit as st
import numpy as np
import io
import wave

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="963 Hz · Angelic Healing Music",
    page_icon="✦",
    layout="centered",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Cinzel:wght@400;500&display=swap');

:root {
    --bg0: #070a12;
    --bg1: #0d1220;
    --gold: #c8a96e;
    --gold2: #e8d5a3;
    --silver: #a8b8d4;
    --glow: rgba(200,169,110,0.25);
    --glowb: rgba(140,170,220,0.2);
    --cream: #f0e8d8;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg0) !important;
    color: var(--cream) !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(140,100,40,0.18) 0%, transparent 70%),
        radial-gradient(ellipse 60% 60% at 80% 80%, rgba(60,80,140,0.12) 0%, transparent 60%),
        var(--bg0) !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display:none !important; }

/* Stars animation */
.stars-wrap {
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events:none; z-index:0; overflow:hidden;
}
.star {
    position:absolute; border-radius:50%;
    background: white; opacity:0;
    animation: twinkle var(--d,4s) var(--delay,0s) infinite ease-in-out;
}
@keyframes twinkle {
    0%,100%{opacity:0; transform:scale(0.8);}
    50%{opacity:var(--op,0.7); transform:scale(1.2);}
}

/* Layout */
.main-wrap { position:relative; z-index:1; padding: 2rem 0.5rem; }

.halo {
    width: 180px; height: 180px;
    margin: 0 auto 1.5rem;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(200,169,110,0.15) 0%, transparent 70%);
    border: 1px solid rgba(200,169,110,0.25);
    display: flex; align-items:center; justify-content:center;
    position: relative;
    animation: halo-pulse 4s ease-in-out infinite;
}
.halo::before, .halo::after {
    content:''; position:absolute; border-radius:50%;
    border: 1px solid rgba(200,169,110,0.12);
    animation: ring-expand 4s ease-out infinite;
}
.halo::before { width:220px; height:220px; animation-delay:0s; }
.halo::after  { width:260px; height:260px; animation-delay:1.5s; }
@keyframes halo-pulse {
    0%,100%{box-shadow:0 0 30px rgba(200,169,110,0.15);}
    50%{box-shadow:0 0 60px rgba(200,169,110,0.35);}
}
@keyframes ring-expand {
    0%{opacity:0.5; transform:scale(0.95);}
    100%{opacity:0; transform:scale(1.3);}
}
.halo-num {
    font-family:'Cinzel',serif; font-size:2.2rem; font-weight:500;
    color:var(--gold); text-shadow:0 0 20px var(--glow);
    line-height:1;
}
.halo-hz { font-family:'Cinzel',serif; font-size:0.8rem; color:var(--gold2); letter-spacing:0.3em; }

h1.title {
    font-family:'Cinzel',serif; font-weight:400; font-size:clamp(1.1rem,4vw,1.8rem);
    color:var(--gold2); text-align:center; letter-spacing:0.15em;
    text-shadow:0 0 25px var(--glow); margin:0 0 0.3rem;
}
.sub {
    font-family:'Cormorant Garamond',serif; font-style:italic;
    font-size:1.05rem; color:var(--silver); text-align:center;
    letter-spacing:0.08em; margin-bottom:2rem;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(200,169,110,0.15);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family:'Cinzel',serif; font-size:0.7rem;
    color:var(--gold); letter-spacing:0.25em; opacity:0.8;
    margin-bottom:0.8rem; text-transform:uppercase;
}

/* Streamlit widget overrides */
label { font-family:'Cormorant Garamond',serif !important; font-size:1rem !important; color:var(--cream) !important; }
[data-testid="stSlider"] { padding: 0.3rem 0; }
.stButton>button {
    width:100%; margin-top:0.5rem;
    font-family:'Cinzel',serif !important; font-size:0.85rem !important;
    letter-spacing:0.15em !important;
    background: linear-gradient(135deg, rgba(200,169,110,0.12), rgba(200,169,110,0.06)) !important;
    color:var(--gold2) !important; border:1px solid rgba(200,169,110,0.4) !important;
    border-radius:3px !important; padding:0.75rem !important;
    transition:all 0.4s ease !important;
}
.stButton>button:hover {
    background:rgba(200,169,110,0.18) !important;
    box-shadow:0 0 25px rgba(200,169,110,0.3) !important;
}
[data-testid="stAlert"] {
    background:rgba(200,169,110,0.07) !important;
    border:1px solid rgba(200,169,110,0.25) !important;
    font-family:'Cormorant Garamond',serif !important;
    font-size:1rem !important; color:var(--cream) !important;
}
audio { width:100%; margin-top:0.5rem; }
[data-testid="stSelectbox"]>div>div {
    background:rgba(255,255,255,0.04) !important;
    border-color:rgba(200,169,110,0.25) !important;
    color:var(--cream) !important;
    font-family:'Cormorant Garamond',serif !important;
}

.footer {
    text-align:center; margin-top:3rem;
    font-family:'Cormorant Garamond',serif; font-style:italic;
    font-size:0.9rem; color:rgba(200,169,110,0.35); letter-spacing:0.1em;
}
.sep { color:rgba(200,169,110,0.3); text-align:center; font-size:1.2rem; margin:1.5rem 0; }
</style>

<div class="stars-wrap" id="stars"></div>
<script>
(function(){
    const w=document.getElementById('stars'); if(!w) return;
    for(let i=0;i<80;i++){
        const s=document.createElement('div'); s.className='star';
        const sz=Math.random()*2+0.5;
        s.style.cssText=`width:${sz}px;height:${sz}px;
          top:${Math.random()*100}%;left:${Math.random()*100}%;
          --d:${3+Math.random()*5}s;--delay:${Math.random()*6}s;
          --op:${0.3+Math.random()*0.6}`;
        w.appendChild(s);
    }
})();
</script>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-wrap">
<div class="halo">
    <div>
        <div class="halo-num">963</div>
        <div class="halo-hz">H Z</div>
    </div>
</div>
<h1 class="title">ANGELIC HEALING MUSIC</h1>
<div class="sub">Jesus Christ Frequency · Divine Consciousness · Deep Healing</div>
""", unsafe_allow_html=True)


# ── Audio Engine ───────────────────────────────────────────────────────────────
SR = 44100

def adsr(n, a=0.01, d=0.05, s=0.8, r=0.15):
    env = np.ones(n) * s
    ai = int(a * n); di = int(d * n); ri = int(r * n)
    if ai > 0: env[:ai] = np.linspace(0, 1, ai)
    if di > 0: env[ai:ai+di] = np.linspace(1, s, di)
    if ri > 0: env[-ri:] = np.linspace(s, 0, ri)
    return env

def sine(f, dur, sr=SR, phase=0.0):
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    return np.sin(2 * np.pi * f * t + phase)

def soft_pad(f, dur, sr=SR, detune=0.003, harmonics=4):
    """Lush pad: multiple detuned sines + harmonics — mềm như synth pad"""
    n = int(sr * dur)
    out = np.zeros(n)
    for i in range(-2, 3):
        df = f * (1 + i * detune)
        wave = sine(df, dur, sr)
        out += wave * (0.7 ** abs(i))
    for h in range(2, harmonics + 1):
        amp = 0.18 / h
        out += sine(f * h, dur, sr, phase=np.random.uniform(0, 2*np.pi)) * amp
    return out / np.max(np.abs(out) + 1e-9)

def tremolo(sig, rate=0.15, depth=0.12, sr=SR):
    t = np.linspace(0, len(sig)/sr, len(sig), endpoint=False)
    return sig * (1 - depth + depth * np.sin(2 * np.pi * rate * t))

def reverb_simple(sig, decay=0.6, delays_ms=(30, 60, 100, 150)):
    out = sig.copy().astype(np.float64)
    for d_ms in delays_ms:
        d = int(d_ms * SR / 1000)
        if d < len(sig):
            buf = np.zeros_like(sig)
            buf[d:] = sig[:-d] * decay
            out += buf
            decay *= 0.55
    return out

def slow_fade(sig, fade_sec=6.0, sr=SR):
    f = int(fade_sec * sr)
    f = min(f, len(sig) // 3)
    sig[:f] *= np.linspace(0, 1, f)
    sig[-f:] *= np.linspace(1, 0, f)
    return sig

def gen_bell(f, dur=2.5, sr=SR):
    """Angelic bell chime"""
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    env = np.exp(-3 * t)
    tone = (np.sin(2*np.pi*f*t) * 0.5 +
            np.sin(2*np.pi*f*2.756*t) * 0.25 * np.exp(-4*t) +
            np.sin(2*np.pi*f*5.41*t)  * 0.12 * np.exp(-6*t))
    return tone * env

def chorus(sig, sr=SR, depth_ms=8, rate=0.3):
    """Chorus effect for angelic width"""
    n = len(sig)
    t = np.linspace(0, n/sr, n, endpoint=False)
    depth = int(depth_ms * sr / 1000)
    lfo = ((np.sin(2*np.pi*rate*t) + 1) / 2 * depth).astype(int)
    out = np.zeros(n)
    for i in range(n):
        idx = i - lfo[i]
        if 0 <= idx < n:
            out[i] = sig[idx]
    return (sig + out * 0.7) / 1.7

def generate_healing_music(
    duration_sec: int,
    preset: str,
    bell_density: float,
    reverb_depth: float,
    bass_vol: float,
) -> bytes:
    rng = np.random.default_rng(42)
    n = duration_sec * SR
    out = np.zeros(n, dtype=np.float64)

    # ── 1. Root 963 Hz Drone (soul of the music) ──────────────────────────────
    drone = soft_pad(963, duration_sec, detune=0.0025, harmonics=5)
    drone = tremolo(drone, rate=0.08, depth=0.08)
    drone_vol = 0.30
    out += drone * drone_vol

    # ── 2. Sacred chord — angelic harmony above/below 963 Hz ─────────────────
    # 963 Hz fits in B♭ / A# scale. Build angelic chord cluster.
    chord_freqs = {
        "Pure 963 Hz": [963, 963*1.25, 963*1.5],
        "Divine Peaceful": [481.5, 963, 963*1.5, 963*2],
        "Christ Consciousness": [321, 642, 963, 963*1.333],
        "Deep Sleep": [240.75, 481.5, 963],
        "Stress Relief": [321, 963, 963*1.2, 963*1.5],
    }
    freqs = chord_freqs.get(preset, [963])
    for i, f in enumerate(freqs):
        vol = 0.18 / (i + 1)
        layer = soft_pad(f, duration_sec, detune=0.002 + i*0.001, harmonics=3)
        layer = tremolo(layer, rate=0.06 + i*0.02, depth=0.10)
        out += layer * vol

    # ── 3. Sub-bass healing pulse (low rumble, grounding) ────────────────────
    if bass_vol > 0:
        bass_f = 963 / 4  # 240.75 Hz, deep
        bass = sine(bass_f, duration_sec)
        bass += sine(bass_f * 1.5, duration_sec) * 0.3
        bass = tremolo(bass, rate=0.04, depth=0.15)
        # slow swell envelope
        swell = np.abs(np.sin(np.linspace(0, duration_sec * 0.12 * np.pi, n)))
        out += bass * swell * bass_vol * 0.22

    # ── 4. Angelic bells sprinkled randomly ───────────────────────────────────
    bell_freqs_set = [963, 963*1.25, 963*1.5, 963*2, 481.5, 1926]
    avg_gap = max(4.0, 20.0 - bell_density * 16)  # density 0-1 → gap 20s-4s
    t_cursor = rng.uniform(2, 6)
    while t_cursor < duration_sec - 3:
        bf = rng.choice(bell_freqs_set)
        bell = gen_bell(bf, dur=rng.uniform(2.0, 3.5))
        bvol = rng.uniform(0.06, 0.14)
        pos = int(t_cursor * SR)
        end = min(pos + len(bell), n)
        out[pos:end] += bell[:end-pos] * bvol
        t_cursor += rng.exponential(avg_gap)

    # ── 5. Soft shimmer — very high frequency air / celestial sparkle ─────────
    shimmer_f = 963 * 4  # 3852 Hz
    shimmer = soft_pad(shimmer_f, duration_sec, detune=0.005, harmonics=2)
    shimmer_env = np.abs(np.sin(np.linspace(0, duration_sec * 0.05 * np.pi, n))) * 0.5 + 0.5
    out += shimmer * shimmer_env * 0.04

    # ── 6. Chorus + Reverb ────────────────────────────────────────────────────
    out = chorus(out, depth_ms=10, rate=0.18)

    rev_delays = (25, 55, 90, 140, 210) if reverb_depth > 0.6 else (30, 70, 120)
    rev_decay  = 0.45 + reverb_depth * 0.35
    out = reverb_simple(out, decay=rev_decay, delays_ms=rev_delays)

    # ── 7. Master fade & normalize ────────────────────────────────────────────
    out = slow_fade(out, fade_sec=min(8.0, duration_sec * 0.06))
    peak = np.max(np.abs(out)) + 1e-9
    out = out / peak * 0.88  # headroom

    # ── 8. Encode WAV ─────────────────────────────────────────────────────────
    pcm = (out * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ── Controls UI ────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">✦ Chọn Preset Chữa Lành</div>', unsafe_allow_html=True)
preset = st.selectbox("", [
    "Pure 963 Hz",
    "Divine Peaceful",
    "Christ Consciousness",
    "Deep Sleep",
    "Stress Relief",
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

preset_desc = {
    "Pure 963 Hz": "✦ Tần số thuần khiết 963 Hz — kết nối với nguồn sáng thiêng liêng",
    "Divine Peaceful": "✦ Hòa âm bình an — trải nghiệm sự tĩnh lặng tuyệt đối",
    "Christ Consciousness": "✦ Ý thức Kitô — mở rộng tâm thức, yêu thương vô điều kiện",
    "Deep Sleep": "✦ Ngủ sâu — sóng âm nhẹ nhàng đưa vào giấc ngủ thiên thần",
    "Stress Relief": "✦ Giảm stress — hòa âm giải phóng lo âu, mang lại bình tĩnh",
}
st.info(preset_desc.get(preset, ""))

st.markdown('<div class="card"><div class="card-title">⚙ Tuỳ Chỉnh Âm Thanh</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    duration_min = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1)
with col2:
    bell_density = st.slider("🔔 Mật độ tiếng chuông", 0.0, 1.0, 0.4, 0.1)

col3, col4 = st.columns(2)
with col3:
    reverb_depth = st.slider("🌊 Độ vang (Reverb)", 0.1, 1.0, 0.65, 0.05)
with col4:
    bass_vol = st.slider("🎵 Bass healing", 0.0, 1.0, 0.5, 0.1)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="sep">✦ ✦ ✦</div>', unsafe_allow_html=True)

# ── Generate ───────────────────────────────────────────────────────────────────
if st.button("✦  TẠO NHẠC CHỮA LÀNH  ✦"):
    dur_sec = duration_min * 60
    with st.spinner("Đang tạo nhạc chữa lành... vui lòng đợi ✦"):
        audio_bytes = generate_healing_music(
            duration_sec=dur_sec,
            preset=preset,
            bell_density=bell_density,
            reverb_depth=reverb_depth,
            bass_vol=bass_vol,
        )
    mb = len(audio_bytes) / (1024 * 1024)
    st.success(f"✦ Hoàn thành · {duration_min} phút · {preset} · {mb:.1f} MB")
    st.audio(audio_bytes, format="audio/wav")
    st.download_button(
        "⬇  Tải Xuống WAV",
        data=audio_bytes,
        file_name=f"963hz_{preset.lower().replace(' ','_')}_{duration_min}min.wav",
        mime="audio/wav",
        use_container_width=True,
    )

st.markdown("""
<div class="footer">
    ✦ &nbsp; Be still, and know that I am God &nbsp; ✦ <br>
    <span style="font-size:0.75rem; opacity:0.6;">963 Hz · Solfeggio Frequency · Angelic Healing Music</span>
</div>
</div>
""", unsafe_allow_html=True)
