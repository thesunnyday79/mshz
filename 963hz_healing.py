import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(page_title="963 Hz · Angelic Healing Music", page_icon="✦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Cinzel:wght@400;500&display=swap');
:root{--bg0:#070a12;--gold:#c8a96e;--gold2:#e8d5a3;--silver:#a8b8d4;--glow:rgba(200,169,110,0.25);--cream:#f0e8d8;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg0)!important;color:var(--cream)!important;}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse 80% 40% at 50% -10%,rgba(140,100,40,0.18) 0%,transparent 70%),var(--bg0)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"]{display:none!important;}
.halo{width:160px;height:160px;margin:0 auto 1.2rem;border-radius:50%;background:radial-gradient(circle,rgba(200,169,110,0.15) 0%,transparent 70%);border:1px solid rgba(200,169,110,0.25);display:flex;align-items:center;justify-content:center;animation:halo-pulse 4s ease-in-out infinite;position:relative;}
.halo::before,.halo::after{content:'';position:absolute;border-radius:50%;border:1px solid rgba(200,169,110,0.1);animation:ring-expand 4s ease-out infinite;}
.halo::before{width:200px;height:200px;animation-delay:0s;}
.halo::after{width:240px;height:240px;animation-delay:1.8s;}
@keyframes halo-pulse{0%,100%{box-shadow:0 0 30px rgba(200,169,110,0.12);}50%{box-shadow:0 0 55px rgba(200,169,110,0.32);}}
@keyframes ring-expand{0%{opacity:0.4;transform:scale(0.95);}100%{opacity:0;transform:scale(1.3);}}
.halo-num{font-family:'Cinzel',serif;font-size:2rem;font-weight:500;color:var(--gold);text-shadow:0 0 20px var(--glow);line-height:1;}
.halo-hz{font-family:'Cinzel',serif;font-size:0.7rem;color:var(--gold2);letter-spacing:0.35em;text-align:center;}
h1.title{font-family:'Cinzel',serif;font-weight:400;font-size:clamp(1rem,4vw,1.6rem);color:var(--gold2);text-align:center;letter-spacing:0.15em;text-shadow:0 0 22px var(--glow);margin:0 0 0.25rem;}
.sub{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.05rem;color:var(--silver);text-align:center;letter-spacing:0.07em;margin-bottom:1.6rem;}
.card{background:rgba(255,255,255,0.03);border:1px solid rgba(200,169,110,0.15);border-radius:6px;padding:1rem 1.2rem;margin-bottom:0.8rem;}
.card-title{font-family:'Cinzel',serif;font-size:0.65rem;color:var(--gold);letter-spacing:0.25em;opacity:0.8;margin-bottom:0.7rem;text-transform:uppercase;}
label{font-family:'Cormorant Garamond',serif!important;font-size:1rem!important;color:var(--cream)!important;}
.stButton>button{width:100%;font-family:'Cinzel',serif!important;font-size:0.85rem!important;letter-spacing:0.15em!important;background:linear-gradient(135deg,rgba(200,169,110,0.12),rgba(200,169,110,0.06))!important;color:var(--gold2)!important;border:1px solid rgba(200,169,110,0.4)!important;border-radius:3px!important;padding:0.75rem!important;}
[data-testid="stAlert"]{background:rgba(200,169,110,0.07)!important;border:1px solid rgba(200,169,110,0.25)!important;font-family:'Cormorant Garamond',serif!important;color:var(--cream)!important;}
audio{width:100%;margin-top:0.5rem;}
.footer{text-align:center;margin-top:2rem;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:0.88rem;color:rgba(200,169,110,0.35);letter-spacing:0.1em;}
.sep{color:rgba(200,169,110,0.3);text-align:center;font-size:1.1rem;margin:1rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="halo"><div><div class="halo-num">963</div><div class="halo-hz">H Z</div></div></div>
<h1 class="title">ANGELIC HEALING MUSIC</h1>
<div class="sub">Jesus Christ Frequency · Divine Consciousness · Deep Healing</div>
""", unsafe_allow_html=True)

SR = 44100

def soft_pad(f, dur, detune=0.003, harmonics=4):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    out = np.zeros(n)
    for i in range(-2, 3):
        df = f * (1 + i * detune)
        out += np.sin(2 * np.pi * df * t) * (0.7 ** abs(i))
    rng = np.random.default_rng(int(f))
    for h in range(2, harmonics + 1):
        ph = rng.uniform(0, 2 * np.pi)
        out += np.sin(2 * np.pi * f * h * t + ph) * (0.18 / h)
    return out / (np.max(np.abs(out)) + 1e-9)

def tremolo(sig, rate=0.08, depth=0.08):
    t = np.linspace(0, len(sig) / SR, len(sig), endpoint=False)
    return sig * (1 - depth + depth * np.sin(2 * np.pi * rate * t))

def reverb_vec(sig, decay=0.55, delays_ms=(30, 60, 100, 150)):
    out = sig.astype(np.float64).copy()
    d = decay
    for ms in delays_ms:
        nd = int(ms * SR / 1000)
        if nd < len(sig):
            r = np.zeros_like(out)
            r[nd:] = sig[:-nd] * d
            out += r
            d *= 0.50
    return out

def chorus_vec(sig, depth_ms=9, rate=0.22):
    n = len(sig)
    t = np.arange(n, dtype=np.float64) / SR
    ds = depth_ms * SR / 1000
    lfo = ds * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    indices = np.clip(np.arange(n, dtype=np.float64) - lfo, 0, n - 1)
    i0 = indices.astype(int)
    frac = indices - i0
    i1 = np.minimum(i0 + 1, n - 1)
    delayed = sig[i0] * (1 - frac) + sig[i1] * frac
    return (sig + delayed * 0.65) / 1.65

def gen_bell(f, dur=2.5):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.exp(-3.0 * t)
    return (np.sin(2*np.pi*f*t)*0.55 +
            np.sin(2*np.pi*f*2.756*t)*0.25*np.exp(-4.5*t) +
            np.sin(2*np.pi*f*5.41*t)*0.12*np.exp(-7.0*t)) * env

def slow_fade(sig, fade_sec=6.0):
    f = min(int(fade_sec * SR), len(sig) // 4)
    sig = sig.copy()
    sig[:f] *= np.linspace(0, 1, f)
    sig[-f:] *= np.linspace(1, 0, f)
    return sig

CHORD_TABLE = {
    "Pure 963 Hz":          [963],
    "Divine Peaceful":      [481.5, 963, 1444.5, 1926],
    "Christ Consciousness": [321.0, 642.0, 963, 963*1.333],
    "Deep Sleep":           [240.75, 481.5, 963],
    "Stress Relief":        [321.0, 963, 963*1.2, 963*1.5],
}

def generate_healing_music(duration_sec, preset, bell_density, reverb_depth, bass_vol):
    rng = np.random.default_rng(42)
    n = duration_sec * SR
    out = np.zeros(n, dtype=np.float64)

    # 1. Root drone
    drone = soft_pad(963, duration_sec, detune=0.0022, harmonics=5)
    out += tremolo(drone, rate=0.07, depth=0.08) * 0.30

    # 2. Chord layers
    for i, f in enumerate(CHORD_TABLE.get(preset, [963])):
        layer = soft_pad(f, duration_sec, detune=0.002 + i*0.001, harmonics=3)
        out += tremolo(layer, rate=0.06 + i*0.018, depth=0.09) * (0.17 / (i+1))

    # 3. Bass pulse
    if bass_vol > 0:
        t = np.linspace(0, duration_sec, n, endpoint=False)
        bass = np.sin(2*np.pi*(963/4)*t) + np.sin(2*np.pi*(963/4)*1.5*t)*0.28
        swell = np.abs(np.sin(np.linspace(0, duration_sec*0.10*np.pi, n)))
        out += bass * swell * bass_vol * 0.20

    # 4. Bells
    bell_freqs_set = [963, 963*1.25, 963*1.5, 963*2, 481.5, 1926]
    avg_gap = max(4.0, 22.0 - bell_density * 18.0)
    t_cur = float(rng.uniform(2.0, 5.0))
    while t_cur < duration_sec - 3.5:
        bf = float(rng.choice(bell_freqs_set))
        bell = gen_bell(bf, float(rng.uniform(2.0, 3.2)))
        pos = int(t_cur * SR)
        end = min(pos + len(bell), n)
        out[pos:end] += bell[:end-pos] * float(rng.uniform(0.07, 0.15))
        t_cur += float(rng.exponential(avg_gap))

    # 5. High shimmer
    shimmer = soft_pad(963*4, duration_sec, detune=0.006, harmonics=2)
    shimmer_env = np.abs(np.sin(np.linspace(0, duration_sec*0.04*np.pi, n)))*0.4 + 0.6
    out += shimmer * shimmer_env * 0.033

    # 6. FX
    out = chorus_vec(out)
    rev_delays = (25, 55, 90, 140, 200) if reverb_depth > 0.6 else (28, 65, 110)
    out = reverb_vec(out, decay=0.42 + reverb_depth*0.32, delays_ms=rev_delays)

    # 7. Finalize
    out = slow_fade(out, fade_sec=min(8.0, duration_sec*0.06))
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.88

    pcm = (out * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    return buf.getvalue()

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">✦ Chọn Preset Chữa Lành</div>', unsafe_allow_html=True)
preset = st.selectbox("preset", list(CHORD_TABLE.keys()), label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

PRESET_DESC = {
    "Pure 963 Hz":          "✦ Tần số thuần khiết 963 Hz — kết nối nguồn sáng thiêng liêng",
    "Divine Peaceful":      "✦ Hòa âm bình an — trải nghiệm sự tĩnh lặng tuyệt đối",
    "Christ Consciousness": "✦ Ý thức Kitô — mở rộng tâm thức, yêu thương vô điều kiện",
    "Deep Sleep":           "✦ Ngủ sâu — sóng âm nhẹ nhàng đưa vào giấc ngủ thiên thần",
    "Stress Relief":        "✦ Giảm stress — hòa âm giải phóng lo âu, mang lại bình tĩnh",
}
st.info(PRESET_DESC.get(preset, ""))

st.markdown('<div class="card"><div class="card-title">⚙ Tuỳ Chỉnh</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: duration_min = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1)
with c2: bell_density = st.slider("🔔 Mật độ chuông thiên thần", 0.0, 1.0, 0.4, 0.1)
c3, c4 = st.columns(2)
with c3: reverb_depth = st.slider("🌊 Độ vang không gian", 0.1, 1.0, 0.65, 0.05)
with c4: bass_vol = st.slider("🎵 Bass chữa lành", 0.0, 1.0, 0.5, 0.1)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="sep">✦ ✦ ✦</div>', unsafe_allow_html=True)

if st.button("✦  TẠO NHẠC CHỮA LÀNH  ✦"):
    dur_sec = duration_min * 60
    with st.spinner("Đang tạo nhạc chữa lành... ✦"):
        audio_bytes = generate_healing_music(dur_sec, preset, bell_density, reverb_depth, bass_vol)
    mb = len(audio_bytes) / (1024*1024)
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
    ✦ &nbsp; Be still, and know that I am God &nbsp; ✦<br>
    <span style="font-size:0.75rem;opacity:0.6;">963 Hz · Solfeggio Frequency · Angelic Healing Music</span>
</div>
""", unsafe_allow_html=True)
