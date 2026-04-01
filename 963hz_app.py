import streamlit as st
import numpy as np
import io
import wave
import struct
import math

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="963 Hz · Jesus Christ Frequency",
    page_icon="✝",
    layout="centered",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

:root {
    --gold:   #D4AF37;
    --gold2:  #F5D97A;
    --cream:  #FDF6E3;
    --dark:   #0D0A04;
    --deep:   #1A1406;
    --glow:   rgba(212,175,55,0.35);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: var(--cream) !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 50% 0%, #2a1e00 0%, #0D0A04 60%) !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Hero title */
.hero {
    text-align: center;
    padding: 3rem 0 1rem;
}
.hero h1 {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.6rem, 5vw, 3rem);
    font-weight: 900;
    color: var(--gold);
    text-shadow: 0 0 30px var(--glow), 0 0 60px var(--glow);
    letter-spacing: 0.05em;
    margin: 0;
    line-height: 1.2;
}
.hero .freq {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(3rem, 10vw, 6rem);
    font-weight: 700;
    background: linear-gradient(180deg, var(--gold2) 0%, var(--gold) 60%, #8B6914 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block;
    line-height: 1;
    margin: 0.3rem 0;
    filter: drop-shadow(0 0 20px var(--glow));
}
.hero .subtitle {
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: rgba(212,175,55,0.7);
    letter-spacing: 0.15em;
    margin-top: 0.5rem;
}

/* Divider cross */
.cross-divider {
    text-align: center;
    font-size: 1.6rem;
    color: var(--gold);
    opacity: 0.6;
    margin: 1.5rem 0;
    text-shadow: 0 0 10px var(--glow);
}

/* Description box */
.desc-box {
    background: rgba(212,175,55,0.05);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 4px;
    padding: 1.2rem 1.6rem;
    font-family: 'EB Garamond', serif;
    font-size: 1rem;
    line-height: 1.75;
    color: rgba(253,246,227,0.85);
    margin-bottom: 1.5rem;
}
.desc-box strong { color: var(--gold); }

/* Sliders & labels */
label, .stSlider > div, .stSelectbox > div {
    font-family: 'EB Garamond', serif !important;
    color: var(--cream) !important;
    font-size: 1rem !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--gold) !important;
    border-color: var(--gold2) !important;
}
.stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
    color: var(--dark) !important;
    background: var(--gold) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.1em !important;
    background: linear-gradient(135deg, #2a1e00, #1A1406) !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 2px !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 0 15px rgba(212,175,55,0.15) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3d2c00, #2a1e00) !important;
    box-shadow: 0 0 30px rgba(212,175,55,0.4) !important;
    transform: translateY(-1px) !important;
}

/* Audio player */
audio {
    width: 100%;
    filter: sepia(0.3) hue-rotate(10deg);
    margin-top: 0.5rem;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(212,175,55,0.05) !important;
    border-color: rgba(212,175,55,0.3) !important;
    color: var(--cream) !important;
}

/* Info & success */
[data-testid="stAlert"] {
    background: rgba(212,175,55,0.07) !important;
    border-color: rgba(212,175,55,0.3) !important;
    color: var(--cream) !important;
    font-family: 'EB Garamond', serif !important;
}

/* Column labels */
.col-label {
    font-family: 'EB Garamond', serif;
    font-size: 0.85rem;
    color: rgba(212,175,55,0.6);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

/* Footer */
.footer {
    text-align: center;
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 0.85rem;
    color: rgba(212,175,55,0.35);
    margin-top: 3rem;
    padding-bottom: 2rem;
    letter-spacing: 0.1em;
}

/* Waveform tag */
.wave-tag {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.7rem;
    color: rgba(212,175,55,0.5);
    letter-spacing: 0.2em;
    text-align: center;
    margin: 0.3rem 0 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Audio generation ──────────────────────────────────────────────────────────
def generate_tone(
    frequency: float,
    duration: float,
    sample_rate: int,
    waveform: str,
    volume: float,
    fade_duration: float = 2.0,
) -> bytes:
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    if waveform == "Sine (Pure)":
        wave_data = np.sin(2 * np.pi * frequency * t)
    elif waveform == "Sine + 2nd Harmonic":
        wave_data = 0.7 * np.sin(2 * np.pi * frequency * t) + \
                    0.3 * np.sin(2 * np.pi * frequency * 2 * t)
    elif waveform == "Singing Bowl":
        wave_data = (np.sin(2 * np.pi * frequency * t) +
                     0.25 * np.sin(2 * np.pi * frequency * 2.756 * t) * np.exp(-0.3 * t) +
                     0.15 * np.sin(2 * np.pi * frequency * 5.41 * t) * np.exp(-0.6 * t))
    elif waveform == "Binaural (963 + 966 Hz)":
        wave_data = (0.5 * np.sin(2 * np.pi * 963 * t) +
                     0.5 * np.sin(2 * np.pi * 966 * t))
    else:
        wave_data = np.sin(2 * np.pi * frequency * t)

    # Normalise
    wave_data = wave_data / np.max(np.abs(wave_data) + 1e-9)

    # Fade in / fade out
    fade_samples = int(fade_duration * sample_rate)
    fade_in  = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    wave_data[:fade_samples]  *= fade_in
    wave_data[-fade_samples:] *= fade_out

    wave_data *= volume

    # Convert to 16-bit PCM
    pcm = (wave_data * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buffer.getvalue()


# ─── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>The Sacred Frequency</h1>
    <span class="freq">963 Hz</span>
    <div class="subtitle">✦ Jesus Christ Frequency · Frequency of God ✦</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="cross-divider">✝</div>', unsafe_allow_html=True)

st.markdown("""
<div class="desc-box">
    <strong>963 Hz</strong> là tần số Solfeggio cao nhất, được gọi là <strong>Tần Số Của Thượng Đế</strong>
    hay <em>Jesus Christ Frequency</em>. Tần số này được tin là kết nối con người với 
    <strong>ý thức thuần túy</strong>, giác ngộ tâm linh, và nguồn năng lượng vũ trụ.
    Nghe trong không gian yên tĩnh, nhắm mắt và hít thở sâu để cảm nhận sự chữa lành.
</div>
""", unsafe_allow_html=True)

# Controls
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="col-label">⏱ Thời lượng</div>', unsafe_allow_html=True)
    duration = st.slider("duration", 30, 3600, 300, 30,
                         label_visibility="collapsed",
                         format="%d giây")

with col2:
    st.markdown('<div class="col-label">🌊 Dạng sóng</div>', unsafe_allow_html=True)
    waveform = st.selectbox("waveform",
        ["Sine (Pure)", "Sine + 2nd Harmonic", "Singing Bowl", "Binaural (963 + 966 Hz)"],
        label_visibility="collapsed")

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="col-label">🔊 Âm lượng</div>', unsafe_allow_html=True)
    volume = st.slider("volume", 0.1, 1.0, 0.7, 0.05,
                       label_visibility="collapsed",
                       format="%.0f%%")
with col4:
    st.markdown('<div class="col-label">📻 Sample Rate</div>', unsafe_allow_html=True)
    sample_rate = st.selectbox("sample_rate", [44100, 22050, 48000],
                               label_visibility="collapsed")

st.markdown("---")

# Minutes display
mins = duration // 60
secs = duration % 60
time_str = f"{mins} phút {secs} giây" if secs else f"{mins} phút"

if st.button(f"✦ TẠO ÂM THANH 963 Hz · {time_str} ✦"):
    with st.spinner("Đang tạo tần số thiêng liêng..."):
        audio_bytes = generate_tone(
            frequency=963.0,
            duration=float(duration),
            sample_rate=sample_rate,
            waveform=waveform,
            volume=volume * 0.9,
            fade_duration=min(3.0, duration * 0.05),
        )

    size_mb = len(audio_bytes) / (1024 * 1024)
    st.success(f"✅ Đã tạo xong · {time_str} · {waveform} · {size_mb:.1f} MB")
    st.markdown('<div class="wave-tag">〰 963 Hz SACRED SOUND WAVE 〰</div>', unsafe_allow_html=True)

    st.audio(audio_bytes, format="audio/wav")

    st.download_button(
        label="⬇ TẢI XUỐNG FILE WAV",
        data=audio_bytes,
        file_name=f"963hz_{waveform.split()[0].lower()}_{duration}s.wav",
        mime="audio/wav",
        use_container_width=True,
    )

st.markdown("""
<div class="footer">
    "I am the way, the truth, and the life." — John 14:6<br>
    963 Hz · Solfeggio Scale · Frequency of Divine Consciousness
</div>
""", unsafe_allow_html=True)
