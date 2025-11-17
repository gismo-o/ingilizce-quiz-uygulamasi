import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ANİMASYON VE GÖRSEL SKOR İÇİN STİLLER
st.markdown("""
<style>
/* Mevcut Stilleriniz */
.title-block {
    text-align: center;
    border-bottom: 3px solid #e64f4f;
    padding-bottom: 15px;
}
.title-block h1 {
    margin-bottom: 0;
    color: white;
}
.title-block p {
    font-style: italic;
    font-size: 1.2em;
    color: #a0a0a0;
}

/* YANLIŞ CEVAP İÇİN SALLANMA ANİMASYONU */
@keyframes shake {
  0% { transform: translateX(0); }
  25% { transform: translateX(5px); }
  50% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
  100% { transform: translateX(0); }
}
.shake {
  animation: shake 0.5s ease-in-out;
}

/* DOĞRU CEVAP İÇİN VURGU ANİMASYONU */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
.pulse {
  animation: pulse 0.5s ease-in-out;
}

/* DAİRESEL SKOR GÖSTERGESİ İÇİN STİLLER */
.progress-circle-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px 0;
}
.progress-circle {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    background: conic-gradient(#28a745 0deg, #444 0deg); /* Başlangıç değeri */
}
.progress-value {
    font-size: 2em;
    font-weight: bold;
    color: white;
    background-color: #1c1c2e; /* İç arka plan rengi */
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)


# SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="İngilizce Quiz Uygulaması",
    layout="centered"
)

# VERİYİ YÜKLEME
@st.cache_data
def load_data():
    df = pd.read_csv("kelimeler.csv")
    df['ingilizce_v1'] = df['ingilizce_v1'].astype(str)
    df['ingilizce_v2'] = df['ingilizce_v2'].astype(str)
    return df

df = load_data()

# NORMALLEŞTİRME FONKSİYONU
def normalize_answer(text):
    if not isinstance(text, str):
        return ""
    return text.lower().strip().replace(" ", "")

# YAN MENÜ (SIDEBAR) - KELİME LİSTESİ
st.sidebar.header("📚 Kelime Listesi")
st.sidebar.markdown("Aşağıdaki menüden haftalara göre filtreleme yapabilirsiniz.")

haftalar = sorted(df['hafta'].unique())
secilen_hafta = st.sidebar.selectbox(
    "Görüntülemek istediğiniz haftayı seçin:",
    options=["Tümü"] + [str(h) for h in haftalar]
)

if secilen_hafta == "Tümü":
    goruntulenecek_df = df
else:
    goruntulenecek_df = df[df['hafta'] == int(secilen_hafta)]

# GELİŞTİRİLMİŞ TABLO GÖRÜNÜMÜ
st.sidebar.markdown("""
<style>
.sidebar-table {
    width: 100%;
    font-size: 0.9em;
}
.sidebar-table th {
    text-align: left;
    background-color: #333;
    padding: 6px;
}
.sidebar-table td {
    padding: 6px;
    border-bottom: 1px solid #444;
    white-space: normal !important;
    word-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)
table_html = goruntulenecek_df.to_html(index=False, escape=False, classes="sidebar-table")
st.sidebar.markdown(table_html, unsafe_allow_html=True)


# ANA SAYFA - QUIZ MODU
st.markdown("""
<div class="title-block">
    <h1>İNGİLİZCE QUİZ MODU</h1>
    <p>200 Daily Expressions</p>
</div>
""", unsafe_allow_html=True)
st.write("")

# Session state'i başlatma
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False

# Quiz başlamadıysa ayar ekranını göster
if not st.session_state.quiz_started:
    with st.container(border=True):
        st.info("👋 Hoş geldin! Kendini test etmeye başlamak için aşağıdaki ayarlardan quiz olmak istediğin haftaları seç.")
        st.markdown("---")
        st.subheader("⚙️ Quiz Ayarları")
        st.write("")
        secilen_haftalar = st.multiselect(
            label="**1. Adım:** Quiz olmak istediğiniz haftaları seçin:",
            options=haftalar,
            default=haftalar[0] if haftalar else None
        )

        if not secilen_haftalar:
            available_words = 1
            st.warning("Lütfen soru sayısı seçmeden önce en az bir hafta seçin.")
        else:
            filtered_df_for_slider = df[df['hafta'].isin(secilen_haftalar)]
            available_words = len(filtered_df_for_slider)

        question_count = st.slider(
            label="**2. Adım:** Soru sayısını belirleyin:",
            min_value=1,
            max_value=available_words,
            value=min(15, available_words),
            step=1,
            disabled=(not secilen_haftalar)
        )

        st.write("")
        if st.button("Quizi Başlat", type="primary", use_container_width=True):
            if not secilen_haftalar:
                st.warning("Lütfen quiz için en az bir hafta seçin.")
            else:
                filtered_df = df[df['hafta'].isin(secilen_haftalar)]
                if question_count == 0:
                    st.error("Seçtiğiniz haftalarda çalışılacak kelime bulunamadı.")
                else:
                    quiz_df = filtered_df.sample(n=question_count).reset_index(drop=True)
                    st.session_state.quiz_words = quiz_df.to_dict('records')
                    st.session_state.current_quiz_index = 0
                    st.session_state.score = 0
                    st.session_state.incorrect_answers = []
                    st.session_state.quiz_started = True
                    st.session_state.answer_submitted = False
                    st.rerun()

# --- DÜZELTİLMİŞ YAPI: QUIZ BAŞLADIYSA ---
else:
    total_quiz_words = len(st.session_state.quiz_words)
    current_index = st.session_state.current_quiz_index

    # ÖNCE QUIZ'İN BİTİP BİTMEDİĞİNİ KONTROL ET
    if current_index >= total_quiz_words:
        # EĞER BİTTİYSE, SADECE SONUÇ EKRANINI GÖSTER
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center;'>🎉 Quiz Tamamlandı!</h2>", unsafe_allow_html=True)
            
            score = st.session_state.score
            percentage = (score / total_quiz_words) * 100 if total_quiz_words > 0 else 0
            
            if percentage >= 90:
                progress_color = "#28a745"
            elif percentage >= 70:
                progress_color = "#17a2b8"
            else:
                progress_color = "#ffc107"

            progress_bar_html = f"""
            <div class="progress-circle-container">
                <div class="progress-circle" style="background: conic-gradient({progress_color} {percentage * 3.6}deg, #444 0deg);">
                    <div class="progress-value">{score}/{total_quiz_words}</div>
                </div>
            </div>
            """
            st.markdown(progress_bar_html, unsafe_allow_html=True)

            if percentage >= 90:
                st.success("🏆 Mükemmel! Bu haftayı çok iyi öğrenmişsin.")
                st.balloons()
            elif percentage >= 70:
                st.info("👍 Harika gidiyorsun! Birkaç kelimeyi tekrar etmen yeterli.")
            else:
                st.warning("💪 Çalışmaya devam! Yanlış yaptığın kelimeleri gözden geçirebilirsin.")

            fig = go.Figure(go.Bar(
                x=[score, total_quiz_words - score], y=['', ''], orientation='h',
                marker_color=['#28a745', '#dc3545'],
                text=[f"Doğru: {score}", f"Yanlış: {total_quiz_words - score}"],
                textposition='auto'
            ))
            fig.update_layout(
                showlegend=False, barmode='stack',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                height=100, margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

            if st.session_state.incorrect_answers:
                st.write("")
                st.markdown("#### Gözden Geçirmen Gerekenler:")
                incorrect_df = pd.DataFrame(st.session_state.incorrect_answers)
                st.dataframe(incorrect_df)
            
            # Sonuç ekranında butonları yan yana göster
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Yeni Quiz Başlat", use_container_width=True):
                    st.session_state.quiz_started = False
                    st.rerun()
            with col2:
                if st.button("🚪 Çıkış", use_container_width=True, type="secondary"):
                    st.session_state.quiz_started = False
                    st.rerun()

    # EĞER QUIZ DEVAM EDİYORSA, SORU EKRANINI GÖSTER
    else:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Quizden Çık"):
                st.session_state.quiz_started = False
                st.rerun()
        with col2:
            st.progress(current_index / total_quiz_words, text=f"Soru {current_index + 1} / {total_quiz_words}")
        st.markdown("---")

        current_word = st.session_state.quiz_words[current_index]

        with st.container(border=True):
            st.markdown(f"<h2>“{current_word['turkce']}”</h2>", unsafe_allow_html=True)
            st.markdown(f"<h6><i>(Hafta {current_word['hafta']})</i></h6>", unsafe_allow_html=True)
            st.write("Yukarıdaki ifadenin İngilizce karşılıklarını yazın:")
            user_v1_answer = st.text_input("Birinci Hali (V1):", key=f"v1_{current_index}", label_visibility="collapsed", placeholder="Birinci Hali (V1)", disabled=st.session_state.answer_submitted)
            user_v2_answer = st.text_input("İkinci Hali (V2):", key=f"v2_{current_index}", label_visibility="collapsed", placeholder="İkinci Hali (V2)", disabled=st.session_state.answer_submitted)
            feedback_placeholder = st.empty()

            if not st.session_state.answer_submitted:
                if st.button("Cevabı Kontrol Et", type="primary", use_container_width=True):
                    st.session_state.user_v1 = user_v1_answer
                    st.session_state.user_v2 = user_v2_answer
                    correct_v1_raw = current_word['ingilizce_v1']
                    correct_v2_raw = current_word['ingilizce_v2']
                    correct_v1_clean = correct_v1_raw.strip().lower()
                    user_v2_clean = user_v2_answer.strip().lower()
                    final_user_v2 = user_v2_clean
                    if ' ' in correct_v1_clean and ' ' not in user_v2_clean:
                        try:
                            v1_verb = correct_v1_clean.split(' ')[0]
                            v1_object = correct_v1_clean.replace(v1_verb, '').strip()
                            final_user_v2 = f"{user_v2_clean} {v1_object}"
                        except IndexError:
                            final_user_v2 = user_v2_clean
                    is_correct = (
                        normalize_answer(user_v1_answer) == normalize_answer(correct_v1_raw) and
                        normalize_answer(final_user_v2) == normalize_answer(correct_v2_raw)
                    )
                    st.session_state.is_correct = is_correct
                    if is_correct:
                        if not st.session_state.get('score_counted', False):
                            st.session_state.score += 1
                            st.session_state.score_counted = True
                    else:
                        if not st.session_state.get('score_counted', False):
                            st.session_state.incorrect_answers.append({
                                'Türkçe': current_word['turkce'],
                                'Doğru V1': correct_v1_raw.strip(),
                                'Doğru V2': correct_v2_raw.strip(),
                                'Senin Cevabın V1': user_v1_answer,
                                'Senin Cevabın V2': user_v2_answer
                            })
                            st.session_state.score_counted = True
                    st.session_state.answer_submitted = True
                    st.rerun()
            else:
                if st.session_state.is_correct:
                    feedback_html = """
                    <div class="pulse">
                        <h3 style='color: #28a745; text-align: center;'><b>Doğru! 🎉</b></h3>
                    </div>
                    """
                    feedback_placeholder.markdown(feedback_html, unsafe_allow_html=True)
                else:
                    correct_v1 = current_word['ingilizce_v1'].strip()
                    correct_v2 = current_word['ingilizce_v2'].strip()
                    feedback_html = f"""
                    <div class="shake">
                         <h4 style='color: #dc3545; text-align: center;'><b>Yanlış!</b><br>Doğru cevap: <code>{correct_v1}</code> → <code>{correct_v2}</code></h4>
                    </div>
                    """
                    feedback_placeholder.markdown(feedback_html, unsafe_allow_html=True)
                
                # Mevcut sorunun son soru olup olmadığını kontrol et
                is_last_question = (current_index == total_quiz_words - 1)
                
                # Koşula göre buton metnini belirle
                if is_last_question:
                    button_text = "🏁 Quizi Bitir"
                else:
                    button_text = "Sonraki Soru →"
                
                # Butonu dinamik metin ile oluştur
                if st.button(button_text, type="primary", use_container_width=True):
                    st.session_state.current_quiz_index += 1
                    st.session_state.answer_submitted = False
                    st.session_state.score_counted = False
                    st.rerun()