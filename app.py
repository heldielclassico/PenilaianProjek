import streamlit as st
import openai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VBA Project Grader (OpenRouter)", page_icon="⚖️")

st.title("⚖️ Penilai Proyek VBA via OpenRouter")
st.markdown("""
Aplikasi ini membandingkan **Summary Materi** dengan **Soal** menggunakan API OpenRouter.
""")

# --- SIDEBAR KONFIGURASI ---
with st.sidebar:
    st.header("Konfigurasi API")
    # Masukkan API Key OpenRouter Anda (biasanya diawali sk-or-v1-...)
    api_key = st.text_input("Masukkan OpenRouter API Key:", type="password")
    
    # Pilihan Model (Beberapa model di OpenRouter gratis atau sangat murah)
    model_choice = st.selectbox("Pilih Model:", [
        "google/gemini-2.0-flash-lite-001", 
        "openai/gpt-3.5-turbo",
        "mistralai/mistral-7b-instruct-v0.1"
    ])
    
    st.info("""
    **Catatan:** Jika menggunakan model gratis dari OpenRouter, pastikan saldo Anda mencukupi atau gunakan model dengan label 'free'.
    """)

# --- INPUT DATA ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Data")
    soal_input = st.text_input("Kriteria Soal:", value="Membuat form input data")
    
    materi_input = st.text_area(
        "Masukkan Summary/Deskripsi Materi:", 
        height=400,
        placeholder="Tempel summary video Anda di sini..."
    )

with col2:
    st.subheader("📊 Hasil Penilaian AI")
    
    if st.button("Mulai Analisis"):
        if not api_key:
            st.error("Silakan masukkan API Key OpenRouter!")
        elif not materi_input:
            st.error("Materi tidak boleh kosong!")
        else:
            with st.spinner("Menghubungi OpenRouter..."):
                try:
                    # Konfigurasi khusus OpenRouter
                    openai.api_key = api_key
                    openai.api_base = "https://openrouter.ai/api/v1"
                    
                    # Header tambahan yang disarankan OpenRouter
                    headers = {
                        "HTTP-Referer": "http://localhost:8501", # Opsional untuk ranking OpenRouter
                        "X-Title": "VBA Project Grader"
                    }

                    prompt = f"""
                    Anda adalah dosen penguji pemrograman. Tugas Anda adalah memberikan penilaian SUMMARY MATERI berdasarkan SOAL yang diberikan.

                    SOAL: 
                    {soal_input}

                    SUMMARY MATERI:
                    {materi_input}

                    Berikan laporan penilaian dalam format:
                    1. SKOR PERSENTASE: (0-100%)
                    2. ANALISIS KESESUAIAN: (Jelaskan butir apa saja yang terpenuhi)
                    3. KEKURANGAN: (Apa yang tidak ada di materi namun diminta di soal)
                    4. KESIMPULAN: (Layak/Tidak Layak)
                    """

                    response = openai.ChatCompletion.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": "Anda adalah asisten penilai akademik yang objektif."},
                            {"role": "user", "content": prompt}
                        ],
                        headers=headers
                    )
                    
                    # Menampilkan Hasil
                    st.success("Analisis Berhasil!")
                    st.markdown("---")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada API: {str(e)}")

st.markdown("---")
st.caption("Powered by OpenRouter API")
