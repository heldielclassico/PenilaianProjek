import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# --- KONFIGURASI ---
st.set_page_config(page_title="VBA Evaluator Pro", page_icon="📋")

def get_video_id(url):
    """Fungsi ekstraksi ID video yang lebih kuat"""
    if not url:
        return None
    
    # Regex untuk menangani berbagai format link YouTube
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", # Link standar & embed
        r"(?:be\/)([0-9A-Za-z_-]{11}).*",  # Link pendek (youtu.be)
        r"(?:shorts\/)([0-9A-Za-z_-]{11}).*" # Link YouTube Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return str(match.group(1)) # Memastikan output adalah string
    return None

def fetch_transcript(video_id):
    """Mengambil transkrip dengan penanganan error string"""
    try:
        # Menampilkan transkrip yang tersedia untuk debugging di console
        transcript_list = YouTubeTranscriptApi.list_transcripts(str(video_id))
        
        # Mencoba mencari bahasa Indonesia atau Inggris (Manual atau Otomatis)
        try:
            transcript = transcript_list.find_transcript(['id', 'en'])
        except:
            transcript = transcript_list.find_generated_transcript(['id', 'en'])
            
        data = transcript.fetch()
        return " ".join([t['text'] for t in data])
    except Exception as e:
        return f"ERROR_TRANSCRIPT: {str(e)}"

# --- INTERFACE ---
st.title("🤖 Penilai Proyek VBA")
st.markdown("Aplikasi akan membandingkan isi video dengan kriteria soal Anda.")

with st.sidebar:
    api_key = st.text_input("OpenAI API Key:", type="password")
    st.divider()
    st.caption("Pastikan video memiliki Subtitle/CC.")

col1, col2 = st.columns(2)

with col1:
    url_input = st.text_input("Masukkan Link YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    soal_input = st.text_area("Kriteria Soal/Referensi:", height=200, placeholder="1. Cara buat loop\n2. Cara koneksi DB...")

if st.button("Mulai Analisis"):
    if not api_key or not url_input or not soal_input:
        st.warning("Harap lengkapi semua input!")
    else:
        v_id = get_video_id(url_input)
        
        if v_id:
            with st.spinner("Mengekstrak materi video..."):
                transkrip = fetch_transcript(v_id)
                
                if "ERROR_TRANSCRIPT" in transkrip:
                    st.error(f"Gagal mengambil teks: {transkrip.replace('ERROR_TRANSCRIPT:', '')}")
                    st.info("Saran: Gunakan video lain yang memiliki tombol CC (Closed Captions).")
                else:
                    with st.spinner("AI sedang menilai..."):
                        try:
                            openai.api_key = api_key
                            prompt = f"""
                            Anda adalah penguji coding VBA. Bandingkan materi video dengan kriteria berikut.
                            
                            KRITERIA SOAL:
                            {soal_input}
                            
                            TRANSKRIP VIDEO:
                            {transkrip[:4000]}
                            
                            Berikan skor persentase kesesuaian (0-100%) dan jelaskan poin mana yang kurang.
                            """
                            
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "user", "content": prompt}]
                            )
                            
                            with col2:
                                st.success("Analisis Selesai!")
                                st.markdown("### Laporan Penilaian")
                                st.write(response.choices[0].message.content)
                                
                        except Exception as e:
                            st.error(f"Kesalahan AI: {str(e)}")
        else:
            st.error("Link YouTube tidak dikenali. Pastikan link benar.")
