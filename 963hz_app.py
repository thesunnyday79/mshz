import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(
    page_title="963 Hz Angelic Healing Music",
    page_icon="✦",
    layout="centered",
)

SR = 44100

PRESETS = {
    "✦ Pure 963 Hz — Thuần Khiết":        [963],
    "☁ Divine Peaceful — Bình An":         [481.5, 963, 1444.5],
    "✝ Christ Consciousness — Ý Thức Cao": [321.0, 642.0, 963],
    "🌙 Deep Sleep — Ngủ Sâu":             [240.75, 481.5, 963],
    "🌿 Stress Relief — Giảm Stress":      [321.0, 963, 1155.6],
}

def make_healing_audio(duration_sec, freqs, bell_density, reverb_on, bass_vol):
    n = int(duration_sec * SR)
    t = np.linspace(0, duration_sec, n, endpoint=False)
    out = np.zeros(n, dtype=np.float64)

    # --- Layered soft pads ---
    for k, f in enumerate(freqs):
        vol = 0.22 / (k + 1)
        detunes = [-0.003, -0.001, 0.0, 0.001, 0.003]
        weights = [0.5, 0.75, 1.0, 0.75, 0.5]
        for d, w in zip(detunes, weights):
            out += np.sin(2 * np.pi * f * (1 + d) * t) * vol * w * 0.28
        # 2nd harmonic (soft overtone)
        out += np.sin(2 * np.pi * f * 2 * t) * vol * 0.07
        # 3rd harmonic (very soft)
        out += np.sin(2 * np.pi * f * 3 * t) * vol * 0.03

    # --- Slow tremolo / volume swell ---
    swell = 0.88 + 0.12 * np.sin(2 * np.pi * 0.06 * t)
    out = out * swell

    # --- Sub bass healing pulse ---
    if bass_vol > 0:
        bass_f = 963.0 / 4.0  # 240.75 Hz
        bass = np.sin(2 * np.pi * bass_f * t) * 0.6
        bass += np.sin(2 * np.pi * bass_f * 1.5 * t) * 0.25
        bass_swell = 0.5 + 0.5 * np.abs(np.sin(np.linspace(0, duration_sec * 0.08 * np.pi, n)))
        out += bass * bass_swell * bass_vol * 0.18

    # --- Angelic bell chimes ---
    rng = np.random.default_rng(42)
    if bell_density > 0:
        bell_freqs = [963, 963 * 1.25, 963 * 1.5, 963 * 2, 481.5, 1926.0]
        avg_gap = max(5.0, 25.0 - bell_density * 20.0)
        tc = float(rng.uniform(3.0, 7.0))
        while tc < duration_sec - 4.0:
            bf = float(rng.choice(bell_freqs))
            bell_dur = float(rng.uniform(2.0, 3.5))
            bn = int(bell_dur * SR)
            bt = np.linspace(0, bell_dur, bn, endpoint=False)
            bell = (
                np.sin(2 * np.pi * bf * bt) * 0.55 +
                np.sin(2 * np.pi * bf * 2.756 * bt) * 0.22 * np.exp(-4.0 * bt) +
                np.sin(2 * np.pi * bf * 5.404 * bt) * 0.10 * np.exp(-6.0 * bt)
            ) * np.exp(-2.8 * bt)
            bvol = float(rng.uniform(0.07, 0.14))
            pos = int(tc * SR)
            end = min(pos + bn, n)
            out[pos:end] += bell[:end - pos] * bvol
            tc += float(rng.exponential(avg_gap))

    # --- Simple reverb (vectorized) ---
    if reverb_on:
        delays_ms = [30, 65, 110, 165]
        decay = 0.45
        for ms in delays_ms:
            nd = int(ms * SR / 1000)
            if nd < n:
                ref = np.zeros(n, dtype=np.float64)
                ref[nd:] = out[:-nd] * decay
                out = out + ref
                decay *= 0.52

    # --- High shimmer layer ---
    shimmer_t = np.linspace(0, duration_sec, n, endpoint=False)
    shimmer = np.sin(2 * np.pi * 963 * 4 * shimmer_t) * 0.022
    shimmer_env = 0.6 + 0.4 * np.abs(np.sin(np.linspace(0, duration_sec * 0.03 * np.pi, n)))
    out += shimmer * shimmer_env

    # --- Fade in / out ---
    fade_n = min(int(6.0 * SR), n // 4)
    out[:fade_n] *= np.linspace(0.0, 1.0, fade_n)
    out[-fade_n:] *= np.linspace(1.0, 0.0, fade_n)

    # --- Normalize ---
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.88

    # --- Encode WAV ---
    pcm = (out * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ─── UI ───────────────────────────────────────────────────────────────────────

st.markdown("## ✦ 963 Hz — Angelic Healing Music")
st.markdown("*Jesus Christ Frequency · Divine Consciousness · Deep Healing*")
st.markdown("---")

preset_name = st.selectbox(
    "🎵 Chọn preset âm nhạc chữa lành",
    list(PRESETS.keys()),
)
freqs = PRESETS[preset_name]

col1, col2 = st.columns(2)
with col1:
    duration_min = st.slider("⏱ Thời lượng (phút)", 1, 60, 10, 1)
with col2:
    bell_density = st.slider("🔔 Mật độ chuông thiên thần", 0.0, 1.0, 0.5, 0.1)

col3, col4 = st.columns(2)
with col3:
    reverb_on = st.toggle("🌊 Reverb (không gian rộng)", value=True)
with col4:
    bass_vol = st.slider("🎵 Bass chữa lành", 0.0, 1.0, 0.6, 0.1)

st.markdown("---")

DESCRIPTIONS = {
    "✦ Pure 963 Hz — Thuần Khiết":        "Tần số gốc 963 Hz thuần khiết nhất — kết nối trực tiếp với nguồn sáng thiêng liêng và ý thức vũ trụ.",
    "☁ Divine Peaceful — Bình An":         "Hòa âm thiêng liêng nhiều tầng — mang lại cảm giác bình an tuyệt đối, tĩnh tâm và thư giãn sâu.",
    "✝ Christ Consciousness — Ý Thức Cao": "Chord thiêng liêng 321→642→963 Hz — mở rộng tâm thức, yêu thương vô điều kiện, giác ngộ tâm linh.",
    "🌙 Deep Sleep — Ngủ Sâu":             "Tần số thấp 240→481→963 Hz — nhẹ nhàng đưa não vào trạng thái ngủ sâu delta, phục hồi hoàn toàn.",
    "🌿 Stress Relief — Giảm Stress":      "Hòa âm cân bằng — giải phóng cortisol, làm dịu hệ thần kinh, mang lại bình tĩnh và thư giãn.",
}
st.info(DESCRIPTIONS.get(preset_name, ""))

if st.button("✦ TẠO NHẠC CHỮA LÀNH ✦", use_container_width=True):
    dur_sec = duration_min * 60
    with st.spinner(f"Đang tạo {duration_min} phút nhạc chữa lành 963 Hz..."):
        audio_bytes = make_healing_audio(
            duration_sec=dur_sec,
            freqs=freqs,
            bell_density=bell_density,
            reverb_on=reverb_on,
            bass_vol=bass_vol,
        )
    mb = len(audio_bytes) / (1024 * 1024)
    st.success(f"✦ Hoàn thành! · {duration_min} phút · {mb:.1f} MB")
    st.audio(audio_bytes, format="audio/wav")
    fname = preset_name.split("—")[0].strip().replace(" ", "_").replace("✦","").replace("☁","").replace("✝","").replace("🌙","").replace("🌿","").strip()
    st.download_button(
        label="⬇ Tải Xuống File WAV",
        data=audio_bytes,
        file_name=f"963hz_{fname}_{duration_min}min.wav",
        mime="audio/wav",
        use_container_width=True,
    )

st.markdown("---")
st.caption("✦ 963 Hz · Solfeggio Frequency of God · Angelic Healing Music · *Be still, and know that I am God* — Psalm 46:10")
