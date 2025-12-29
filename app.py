import streamlit as st
import openai

# Konfigurasi Halaman
st.set_page_config(page_title="AI Project Grader", page_icon="🎓")

# Judul dan Deskripsi
st.title("🎓 Penilai Kesesuaian Proyek VBA")
st.markdown("""
Aplikasi ini menilai seberapa sesuai isi **Summary/Deskripsi Video** dengan **Soal** yang diberikan menggunakan AI.
""")

# Input API Key di Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API Key:", type="password")
    st.info("Aplikasi ini akan menganalisis teks secara semantik untuk menentukan skor.")

# Layout Kolom
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Data")
    # Input Soal
    soal_input = st.text_input("Masukkan Soal/Kriteria:", value="Membuat form input data")
    
    # Input Teks Summary (Deskripsi Materi)
    materi_input = st.text_area("Masukkan Summary/Deskripsi Video:", height=400, placeholder="Tempel deskripsi video di sini...")

with col2:
    st.subheader("📊 Hasil Penilaian AI")
    
    if st.button("Mulai Penilaian"):
        if not api_key:
            st.error("Mohon masukkan API Key terlebih dahulu!")
        elif not materi_input:
            st.error("Mohon masukkan teks summary video!")
        else:
            with st.spinner("Sedang menghitung skor..."):
                try:
                    openai.api_key = api_key
                    
                    # Prompt Instruksi ke AI
                    prompt = f"""
                    Anda adalah dosen penguji pemrograman VBA. 
                    Tugas Anda adalah menilai sejauh mana MATERI DESKRIPSI VIDEO memenuhi kriteria SOAL.

                    SOAL: 
                    {soal_input}

                    MATERI DESKRIPSI VIDEO:
                    {materi_input}

                    Berikan penilaian dengan format berikut:
                    1. SKOR PERSENTASE: (Berikan angka 0-100% berdasarkan relevansi lurus)
                    2. ANALISIS: (Jelaskan bagian mana di materi yang membuktikan kriteria soal terpenuhi)
                    3. BUKTI TEKSTUAL: (Kutip kalimat dari materi yang mendukung penilaian Anda)
                    4. KESIMPULAN: (Apakah kriteria soal benar-benar tercapai?)
                    """

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "Anda adalah asisten akademik yang objektif dan teliti."},
                                  {"role": "user", "content": prompt}],
                        temperature=0
                    )

                    # Menampilkan Hasil
                    st.success("Penilaian Selesai!")
                    st.markdown("---")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")
    else:
        st.write("Silakan klik tombol 'Mulai Penilaian' untuk melihat hasil.")

# Footer
st.markdown("---")
st.caption("Aplikasi Penilai Otomatis Berbasis GPT-3.5")
