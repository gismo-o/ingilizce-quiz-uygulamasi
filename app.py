import streamlit as st
import pandas as pd
import time

st.markdown("""
<style>
.title-block {
    text-align: center;
    border-bottom: 3px solid #e64f4f; /* Çizgi artık kapsayıcının altında */
    padding-bottom: 15px; /* Çizgi ile altındaki içerik arasına boşluk */
}
.title-block h1 {
    margin-bottom: 0; /* Başlığın altındaki varsayılan boşluğu kaldır */
    color: white;
}
.title-block p {
    font-style: italic;
    font-size: 1.2em;
    color: #a0a0a0;
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
    return df

df = load_data()

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

st.sidebar.dataframe(goruntulenecek_df, height=300)


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
        question_count = st.number_input(
            label="**2. Adım:** Soru sayısını belirleyin:",
            min_value=1,
            max_value=200,
            value=15,
            step=1
        )
        st.write("")
        if st.button("Quizi Başlat", type="primary", use_container_width=True):
            if not secilen_haftalar:
                st.warning("Lütfen quiz için en az bir hafta seçin.")
            else:
                filtered_df = df[df['hafta'].isin(secilen_haftalar)]
                available_words = len(filtered_df)
                count_to_sample = min(question_count, available_words)
                if count_to_sample == 0:
                    st.error("Seçtiğiniz haftalarda çalışılacak kelime bulunamadı.")
                else:
                    quiz_df = filtered_df.sample(n=count_to_sample).reset_index(drop=True)
                    st.session_state.quiz_words = quiz_df.to_dict('records')
                    st.session_state.current_quiz_index = 0
                    st.session_state.score = 0
                    st.session_state.incorrect_answers = []
                    st.session_state.quiz_started = True
                    st.session_state.answer_submitted = False
                    st.rerun()

# Quiz başladıysa soru ekranını göster
else:
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Quizden Çık"):
            st.session_state.quiz_started = False
            st.rerun()
    total_quiz_words = len(st.session_state.quiz_words)
    current_index = st.session_state.current_quiz_index
    with col2:
        st.progress(current_index / total_quiz_words, text=f"Soru {current_index + 1} / {total_quiz_words}")
    st.markdown("---")

    # Quiz bittiyse sonuç ekranı
    if current_index >= total_quiz_words:
        with st.container(border=True):
            score = st.session_state.score
            success_rate = (score / total_quiz_words) * 100 if total_quiz_words > 0 else 0
            st.markdown(f"<h2 style='text-align: center;'>🎉 Quiz Tamamlandı!</h2>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>Skorun: <b>{score} / {total_quiz_words}</b></h3>", unsafe_allow_html=True)
            if success_rate >= 90:
                st.success("🏆 Mükemmel! Bu haftayı çok iyi öğrenmişsin.")
                st.balloons()
            elif success_rate >= 70:
                st.info("👍 Harika gidiyorsun! Birkaç kelimeyi tekrar etmen yeterli.")
            else:
                st.warning("💪 Çalışmaya devam! Yanlış yaptığın kelimeleri gözden geçirebilirsin.")
            if st.session_state.incorrect_answers:
                st.write("")
                st.markdown("#### Gözden Geçirmen Gerekenler:")
                incorrect_df = pd.DataFrame(st.session_state.incorrect_answers)
                st.dataframe(incorrect_df)
            if st.button("🔄 Yeni Quiz Başlat", use_container_width=True):
                st.session_state.quiz_started = False
                st.rerun()

    # Henüz soru varsa
    else:
        current_word = st.session_state.quiz_words[current_index]

        # Soru kutusu artık varsayılan tema rengini kullanacak
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
                    correct_v1 = current_word['ingilizce_v1'].strip().lower()
                    correct_v2 = current_word['ingilizce_v2'].strip().lower()
                    user_v1_clean = user_v1_answer.strip().lower()
                    user_v2_clean = user_v2_answer.strip().lower()
                    final_user_v2 = ""
                    if ' ' not in user_v2_clean and ' ' in correct_v1:
                        v1_verb = correct_v1.split(' ')[0]
                        v1_object = correct_v1.replace(v1_verb, '').strip()
                        final_user_v2 = f"{user_v2_clean} {v1_object}"
                    else:
                        final_user_v2 = user_v2_clean
                    is_correct = (user_v1_clean == correct_v1 and final_user_v2 == correct_v2)
                    st.session_state.is_correct = is_correct
                    if is_correct:
                        if not st.session_state.get('score_counted', False):
                            st.session_state.score += 1
                            st.session_state.score_counted = True
                    else:
                        if not st.session_state.get('score_counted', False):
                            st.session_state.incorrect_answers.append({ 'Türkçe': current_word['turkce'], 'Doğru V1': correct_v1, 'Doğru V2': correct_v2, 'Senin Cevabın V1': user_v1_answer, 'Senin Cevabın V2': user_v2_answer})
                            st.session_state.score_counted = True
                    st.session_state.answer_submitted = True
                    st.rerun()
            else:
                if st.session_state.is_correct:
                    feedback_placeholder.markdown("<h3 style='color: #28a745; text-align: center;'><b>Doğru! 🎉</b></h3>", unsafe_allow_html=True)
                else:
                    correct_v1 = current_word['ingilizce_v1'].strip().lower()
                    correct_v2 = current_word['ingilizce_v2'].strip().lower()
                    feedback_placeholder.markdown(f"<h4 style='color: #dc3545; text-align: center;'><b>Yanlış!</b><br>Doğru cevap: <code>{correct_v1}</code> → <code>{correct_v2}</code></h4>", unsafe_allow_html=True)
                if st.button("Sonraki Soru →", type="primary", use_container_width=True):
                    st.session_state.current_quiz_index += 1
                    st.session_state.answer_submitted = False
                    st.session_state.score_counted = False
                    st.rerun()
