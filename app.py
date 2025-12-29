import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Memuat environment variables
load_dotenv()

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VBA Project Evaluator", page_icon="📝", layout="wide")

# --- CUSTOM CSS (DIPERBAIKI) ---
# Menggunakan satu baris atau memastikan tidak ada indentasi liar
st.markdown("<style>.report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; color: black; }</style>", unsafe_allow_index=True)

# --- FUNGSI UTAMA PENILAIAN ---
def evaluate_summary(api_key, model_name, soal, summary):
    try:
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "VBA Evaluator App"
            }
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Anda adalah instruktur IT senior. Berikan penilaian kritis, jujur, dan objektif."),
            ("user", "Bandingkan RINGKASAN MATERI dengan KRITERIA SOAL.\n\nSOAL:\n{soal}\n\nRINGKASAN MATERI:\n{summary}\n\nBerikan skor 0-100, analisis kriteria dalam tabel, dan rekomendasi.")
        ])

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"soal": soal, "summary": summary})
    except Exception as e:
        return f"Terjadi Kesalahan: {str(e)}"

# --- INTERFACE STREAMLIT ---
st.title("🤖 AI VBA Project Grader")

with st.sidebar:
    st.header("Konfigurasi API")
    api_key = st.text_input("OpenRouter API Key:", type="password")
    model_choice = st.selectbox("Pilih Model AI:", [
        "google/gemini-flash-1.5-8b",
        "meta-llama/llama-3.1-8b-instruct",
        "openai/gpt-3.5-turbo"
    ])

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Penilaian")
    soal_input = st.text_input("Kriteria Soal:", value="Membuat form input data")
    summary_input = st.text_area("Summary Materi:", height=400)
    analyze_btn = st.button("🚀 Jalankan Analisis")

with col2:
    st.subheader("📊 Hasil Evaluasi")
    if analyze_btn:
        if not api_key:
            st.error("Masukkan API Key!")
        elif not summary_input:
            st.warning("Masukkan materi!")
        else:
            with st.spinner("AI sedang menganalisis..."):
                hasil = evaluate_summary(api_key, model_choice, soal_input, summary_input)
                # Menampilkan hasil di dalam div dengan class CSS yang sudah didefinisikan
                st.markdown(f'<div class="report-card">{hasil}</div>', unsafe_allow_index=True)
