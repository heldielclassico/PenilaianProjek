import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VBA Project Evaluator", page_icon="💻", layout="wide")

# --- STYLE CSS CUSTOM ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_index=True)

# --- FUNGSI HELPER ---
def get_video_id(url):
    """Mengekstrak ID video dari berbagai format link YouTube"""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """Mengambil transkrip dengan fallback bahasa"""
    try:
        # Mencoba ambil bahasa Indonesia, jika tidak ada ambil Inggris
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['id', 'en'])
        return " ".join([t['text'] for t in transcript_list])
    except Exception:
        return None

# --- UI UTAMA ---
st.title("🚀 Penilai Proyek VBA (YouTube Analyzer)")
st.subheader("Menilai kesesuaian materi video dengan standar soal Anda")

with st.sidebar:
    st.header("Konfigurasi")
    api_key = st.text_input("Masukkan OpenAI API Key:", type="password")
    st.info("""
    **Tips:** Gunakan video yang memiliki Subtitle/CC agar transkrip bisa dibaca oleh sistem.
    """)

col1, col2 = st.columns([1, 1])

with col1:
    yt_url = st.text_input("Link Video YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    soal_ref = st.text_area(
        "Masukkan Soal/Kriteria Referensi:", 
        height=250,
        placeholder="Contoh:\n1. Harus menjelaskan cara membuat UserForm\n2. Harus ada coding koneksi database\n3. Penjelasan variabel harus detail"
    )

# --- LOGIKA ANALISIS ---
if st.button("Mulai Penilaian"):
    if not api_key:
        st.error("❌ Mohon isi API Key OpenAI di sidebar!")
    elif not yt_url or not soal_ref:
        st.error("❌ Mohon isi Link YouTube dan Soal Referensi!")
    else:
        v_id = get_video_id(yt_url)
        
        if v_id:
            with st.spinner('Memproses video...'):
                # 1. Ambil Transkrip
                full_text = fetch_transcript(v_id)
                
                if not full_text:
                    st.error("⚠️ Transkrip tidak ditemukan untuk video ini. Silakan cari video lain yang memiliki fitur Caption (CC).")
                else:
                    # 2. Kirim ke OpenAI
                    try:
                        openai.api_key = api_key
                        
                        prompt_system = "Anda adalah instruktur senior pemrograman VBA dan Excel Macro."
                        prompt_user = f"""
                        Tugas: Nilailah transkrip video tutorial berikut berdasarkan SOAL REFERENSI yang diberikan.
                        
                        SOAL REFERENSI:
                        {soal_ref}
                        
                        TRANSKRIP VIDEO:
                        {full_text[:4500]} 
                        
                        Berikan laporan evaluasi dengan format:
                        - **Skor Kesesuaian Keseluruhan**: [0-100]%
                        - **Analisis Poin demi Poin**: (Apakah setiap butir soal terjawab di video?)
                        - **Kejelasan Teknis**: (Nilai kejelasan penjelasan coding VBA-nya)
                        - **Kekurangan**: (Apa yang tidak dijelaskan padahal ada di soal?)
                        - **Kesimpulan Akhir**: (Layak atau tidak untuk referensi proyek)
                        """
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo", # atau gpt-4 jika ingin lebih akurat
                            messages=[
                                {"role": "system", "content": prompt_system},
                                {"role": "user", "content": prompt_user}
                            ],
                            temperature=0.7
                        )
                        
                        # 3. Tampilkan Hasil di Col2
                        with col2:
                            st.success("✅ Analisis Berhasil!")
                            st.markdown("### 📋 Hasil Laporan Penilaian")
                            st.markdown("---")
                            st.write(response.choices[0].message.content)
                            
                    except Exception as e:
                        st.error(f"Terjadi kesalahan AI: {str(e)}")
        else:
            st.error("❌ Link YouTube tidak valid!")

# --- FOOTER ---
st.markdown("---")
st.caption("Aplikasi ini menggunakan integrasi YouTube Transcript API dan OpenAI GPT.")
