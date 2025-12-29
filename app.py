import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VBA Project Evaluator", page_icon="📝", layout="wide")

# --- CUSTOM CSS (SUDAH DIPERBAIKI) ---
st.markdown("""
<style>
    .report-card { 
        background-color: #f9f9f9; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #ff4b4b; 
        color: #1e1e1e;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI MENGAMBIL API KEY ---
def get_api_key():
    # Prioritas 1: Ambil dari Streamlit Secrets
    if "OPENROUTER_API_KEY" in st.secrets:
        return st.secrets["OPENROUTER_API_KEY"]
    return None

# --- UI UTAMA ---
st.title("🤖 AI VBA Project Grader")

# Ambil key dari secrets secara otomatis
auto_key = get_api_key()

with st.sidebar:
    st.header("Konfigurasi API")
    # Jika key tidak ada di Secrets, user bisa input manual
    manual_key = st.text_input("OpenRouter API Key:", type="password", help="Kosongkan jika sudah diatur di Secrets")
    
    api_key = manual_key if manual_key else auto_key
    
    model_choice = st.selectbox("Pilih Model AI:", [
        "google/gemini-flash-1.5-8b", 
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3.1-8b-instruct"
    ])
    
    if not api_key:
        st.warning("⚠️ API Key tidak ditemukan. Masukkan di sini atau di Secrets.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Penilaian")
    soal_input = st.text_input("Kriteria Soal:", value="Membuat form input data")
    summary_input = st.text_area("Summary/Deskripsi Materi Video:", height=400)
    
    analyze_btn = st.button("🚀 Jalankan Analisis")

with col2:
    st.subheader("📊 Hasil Evaluasi")
    if analyze_btn:
        if not api_key:
            st.error("Gagal: API Key tidak ditemukan!")
        elif not summary_input:
            st.warning("Gagal: Ringkasan materi kosong!")
        else:
            with st.spinner("AI sedang menganalisis..."):
                try:
                    # Menghubungkan ke OpenRouter menggunakan LangChain
                    llm = ChatOpenAI(
                        model=model_choice,
                        openai_api_key=api_key,
                        openai_api_base="https://openrouter.ai/api/v1",
                        default_headers={
                            "HTTP-Referer": "https://streamlit.io",
                            "X-Title": "VBA Evaluator Pro"
                        }
                    )

                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "Anda adalah instruktur IT senior yang memberikan penilaian objektif."),
                        ("user", "Bandingkan SUMMARY dengan SOAL.\n\nSOAL:\n{soal}\n\nSUMMARY:\n{summary}\n\nBerikan skor dan analisis.")
                    ])

                    chain = prompt | llm | StrOutputParser()
                    hasil = chain.invoke({"soal": soal_input, "summary": summary_input})
                    
                    # Tampilan Hasil (Pastikan parameter ini benar)
                    st.markdown(f'<div class="report-card">{hasil}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan API: {str(e)}")
