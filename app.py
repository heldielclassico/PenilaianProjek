import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Memuat environment variables dari file .env
load_dotenv()

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VBA Project Evaluator", page_icon="📝", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_index=True)

# --- FUNGSI UTAMA PENILAIAN ---
def evaluate_summary(api_key, model_name, soal, summary):
    try:
        # Konfigurasi LangChain dengan OpenRouter
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "VBA Evaluator App"
            }
        )

        # Template Prompt yang Ketat
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Anda adalah instruktur IT senior yang bertugas menilai tugas proyek VBA. Berikan penilaian kritis, jujur, dan objektif."),
            ("user", """
            Bandingkan RINGKASAN MATERI dengan KRITERIA SOAL berikut:
            
            SOAL:
            {soal}
            
            RINGKASAN MATERI:
            {summary}
            
            Berikan output dalam format Markdown yang rapi:
            # LAPORAN EVALUASI
            - **Persentase Kesesuaian**: [0-100]%
            - **Status Kriteria**: (Gunakan tabel: Kriteria | Terpenuhi | Penjelasan)
            - **Analisis Mendalam**: (Ringkasan singkat mengapa nilai tersebut diberikan)
            - **Rekomendasi**: (Apa yang harus ditambahkan jika ingin mencapai 100%)
            """)
        ])

        # Chain (Alur Kerja LangChain)
        chain = prompt | llm | StrOutputParser()
        
        return chain.invoke({"soal": soal, "summary": summary})

    except Exception as e:
        return f"Terjadi Kesalahan: {str(e)}"

# --- INTERFACE STREAMLIT ---
st.title("🤖 AI VBA Project Grader")
st.caption("Menilai kesesuaian antara deskripsi proyek dengan kriteria soal.")

with st.sidebar:
    st.header("Konfigurasi API")
    # Mengambil key dari .env atau input manual
    env_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key = st.text_input("OpenRouter API Key:", value=env_key, type="password")
    
    model_choice = st.selectbox("Pilih Model AI:", [
        "google/gemini-flash-1.5-8b",
        "meta-llama/llama-3.1-8b-instruct",
        "openai/gpt-3.5-turbo"
    ])
    st.divider()
    st.write("Aplikasi ini menggunakan framework LangChain untuk analisis semantik.")

# Input Form
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Penilaian")
    soal_input = st.text_input("Kriteria Soal (Misal: Membuat form input data):", value="Membuat form input data")
    summary_input = st.text_area("Summary Materi (Paste deskripsi/ringkasan materi):", height=400)
    
    analyze_btn = st.button("🚀 Jalankan Analisis")

with col2:
    st.subheader("📊 Hasil Evaluasi")
    if analyze_btn:
        if not api_key:
            st.error("Masukkan API Key OpenRouter di sidebar!")
        elif not summary_input:
            st.warning("Silakan masukkan summary materi yang akan dinilai.")
        else:
            with st.spinner("AI sedang berpikir..."):
                hasil = evaluate_summary(api_key, model_choice, soal_input, summary_input)
                st.markdown(f'<div class="report-card">{hasil}</div>', unsafe_allow_index=True)
                
                # Opsi Download
                st.download_button("Simpan Laporan", hasil, file_name="laporan_penilaian.md")
