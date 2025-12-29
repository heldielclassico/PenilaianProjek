import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

st.set_page_config(page_title="VBA Summary Evaluator", page_icon="📋")

def get_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

st.title("📋 Summary & Evaluasi Proyek VBA")
st.markdown("Dapatkan ringkasan kesesuaian materi video dengan cepat.")

with st.sidebar:
    api_key = st.text_input("OpenAI API Key:", type="password")
    st.divider()
    st.info("Mode: Summary Evaluator")

# Area Soal/Referensi
soal_input = st.text_area("✍️ Referensi Soal/Tugas:", height=150)

tab_otomatis, tab_manual = st.tabs(["🌐 Link YouTube", "📄 Tempel Transkrip"])

with tab_otomatis:
    url_input = st.text_input("URL Video:")

with tab_manual:
    manual_transcript = st.text_area("Tempel Transkrip:")

if st.button("Buat Summary"):
    if not api_key:
        st.error("Masukkan API Key!")
    else:
        materi = manual_transcript if manual_transcript.strip() else ""
        if not materi and url_input:
            v_id = get_video_id(url_input)
            try:
                t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['id', 'en'])
                materi = " ".join([t['text'] for t in t_list])
            except:
                st.warning("Gagal ambil otomatis. Gunakan metode tempel manual.")

        if materi:
            with st.spinner("Menyusun ringkasan..."):
                try:
                    openai.api_key = api_key
                    # Prompt fokus ke Summary
                    prompt = f"Buat ringkasan eksekutif (Summary) materi VBA ini berdasarkan soal: {soal_input}. Materi: {materi[:5000]}. Berikan skor % kesesuaian, tabel kriteria, dan kesimpulan singkat."
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    st.subheader("📊 Hasil Summary")
                    st.markdown("---")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error AI: {e}")
