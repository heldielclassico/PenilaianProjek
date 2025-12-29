import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

st.set_page_config(page_title="VBA Evaluator Plus", page_icon="📝")

st.title("📝 Penilai Materi VBA Berbasis Soal")
st.markdown("Aplikasi ini akan membandingkan isi video dengan soal/referensi yang Anda berikan.")

# Sidebar untuk API Key
api_key = st.sidebar.text_input("Masukkan OpenAI API Key", type="password")

# Input Link YouTube
video_url = st.text_input("Link Video YouTube:")

# Input Soal atau Kriteria Referensi
soal_referensi = st.text_area(
    "Masukkan Soal atau Kriteria Referensi Penilaian:",
    placeholder="Contoh: Soal 1: Membuat UserForm input data. Soal 2: Koneksi ke database Excel. Soal 3: Tombol hapus data."
)

def get_video_id(url):
    video_id_match = re.search(r"(?<=v=)[^&#]+", url)
    video_id_match = video_id_match or re.search(r"(?<=be/)[^&#]+", url)
    return video_id_match.group(0) if video_id_match else None

if st.button("Analisis Berdasarkan Soal"):
    if not api_key or not video_url or not soal_referensi:
        st.warning("Mohon lengkapi API Key, Link YouTube, dan Soal Referensi!")
    else:
        video_id = get_video_id(video_url)
        with st.spinner('Mengevaluasi kesesuaian video dengan soal...'):
            try:
                # 1. Ambil Transkrip
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['id', 'en'])
                text = " ".join([t['text'] for t in transcript_list])
                
                # 2. Prompt AI dengan Referensi Soal
                openai.api_key = api_key
                prompt = f"""
                Anda adalah penguji kompetensi VBA. 
                Tugas Anda adalah menilai apakah video tutorial ini menjawab soal/kriteria berikut:
                
                SOAL/REFERENSI:
                {soal_referensi}
                
                TRANSKRIP VIDEO:
                {text[:4000]}
                
                BERIKAN HASIL DALAM FORMAT:
                1. Analisis Per Soal: (Sebutkan soal mana yang terjawab dan mana yang tidak)
                2. Skor Persentase Kesesuaian: (0-100% berdasarkan seberapa banyak soal yang tercover)
                3. Kejelasan Penjelasan: (Nilai 1-10 beserta alasannya)
                4. Kesimpulan: (Apakah video ini layak dijadikan referensi untuk menjawab soal di atas?)
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 3. Tampilkan Hasil
                st.success("Analisis Selesai!")
                st.markdown("### 📊 Hasil Evaluasi")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
