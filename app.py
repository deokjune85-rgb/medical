# app.py (Mirror v2.0 - Hybrid Analysis Engine)
import streamlit as st
import google.generativeai as genai
from diagnostic_logic import analyze_skin_concerns
import time

# ---------------------------------------
# 0. 시스템 설정 및 초기화
# ---------------------------------------
st.set_page_config(page_title="Mirror AI v2.0 - 안티에이징 진단", page_icon="💎", layout="centered")

# API 키 설정 (Streamlit Secrets 사용)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    # AI 모델 로드 (개인화된 설명 생성용)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.warning("AI 엔진 연결 경고: 개인화된 설명 생성 기능이 제한됩니다. (API 키 확인 필요)")
    model = None

# CSS 스타일링 (Clinical Aesthetic)
custom_css = """
<style>
#MainMenu, footer, header, .stDeployButton {visibility:hidden;}
h1 { color: #00529B; font-weight: 800; text-align: center; margin-bottom: 10px; }
.stButton>button[kind="primary"] { width: 100%; font-weight: bold; font-size: 18px !important; padding: 15px; background-color: #00529B; color: white; border-radius: 10px; }
.disclaimer { font-size: 13px; color: #777; text-align: justify; background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 1. AI 기반 개인화 설명 생성 함수 (★핵심★)
# ---------------------------------------
def generate_personalized_explanation(inputs, analysis_result):
    """AI를 활용하여 분석 결과를 전문가 수준의 상담 스크립트로 변환."""
    if not model:
        return analysis_result['logic']

    recommendations_text = "\n".join([f"- {r['name']} ({r['intensity']}): {r['reason']}" for r in analysis_result['recommendations']])

    prompt = f"""
    당신은 전문 피부과 상담 실장입니다. 고객 정보를 바탕으로 AI 분석 결과를 설명하고 시술을 권장하는 스크립트를 작성해주세요. 전문적이고 신뢰감 있으면서도 부드러운 어조를 사용하세요.

    [고객 정보]
    - 나이대: {inputs['age']}대
    - 피부 타입: {inputs['skin_type']}
    - 처짐 고민 정도 (1-5): {inputs['sagging_level']}
    - 주름 고민 정도 (1-5): {inputs['wrinkle_level']}
    - 예산 범위: {inputs['budget']}

    [AI 분석 결과 (참고용)]
    - 핵심 논리: {analysis_result['logic']}
    - 추천 시술: 
    {recommendations_text}

    [스크립트 작성 지침]
    1. 고객의 현재 상태(나이, 고민 정도)에 공감하며 분석 결과를 요약하세요.
    2. 추천된 시술들이 왜 고객에게 필요한지 구체적이고 쉽게 설명하세요.
    3. 시술 후 기대 효과를 강조하여 기대감을 높이세요.
    4. 마지막으로 내원 상담을 자연스럽게 유도하세요. (약 4~6문장)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"스크립트 생성 오류: {e}\n\n(기본 논리): {analysis_result['logic']}"

# ---------------------------------------
# 2. 메인 애플리케이션 로직
# ---------------------------------------

st.title("Mirror AI v2.0 💎")
st.markdown("<h3 style='text-align: center; color: #555;'>AI 기반 안티에이징 시술 분석 엔진</h3>", unsafe_allow_html=True)
st.markdown("---")

# --- 입력 폼 (상세화) ---
st.header("1. 기본 정보 입력")
col1, col2 = st.columns(2)
inputs = {}
with col1:
    # 나이를 숫자로 변경하여 로직에 활용
    inputs['age'] = st.selectbox("나이대", options=[20, 30, 40, 50, 60], format_func=lambda x: f"{x}대")
with col2:
    inputs['skin_type'] = st.selectbox("피부 타입", options=["건성", "지성", "복합성", "민감성/홍조"])

st.header("2. 고민 정도 체크")
st.info("슬라이더를 움직여 현재 상태를 체크해주세요. (1: 약함, 5: 심함)")

inputs['sagging_level'] = st.slider("피부 처짐 (이중턱/볼살) 고민 정도", min_value=1, max_value=5, value=3)
inputs['wrinkle_level'] = st.slider("주름 (팔자/눈가/이마) 고민 정도", min_value=1, max_value=5, value=3)

st.header("3. 시술 계획")
col3, col4 = st.columns(2)
with col3:
    inputs['budget'] = st.selectbox("예상 예산 범위 (1회 기준)", options=["저예산 (50만 원 이하)", "중간예산 (50~150만 원)", "고예산 (150만 원 이상)"])
with col4:
    inputs['downtime_ok'] = st.radio("시술 후 회복 기간 (멍/붓기) 감수 가능 여부", options=["가능", "불가능"])

st.markdown("---")

# 법적 고지 (의료법 준수)
disclaimer_text = """
**[법적 고지]** 본 서비스는 입력된 정보를 기반으로 미용 정보를 제공하는 AI 분석이며, 의학적 진단을 대체할 수 없습니다. 정확한 진료는 반드시 전문의와의 대면 상담을 통해 이루어져야 합니다.
"""
st.markdown(f"<div class='disclaimer'>{disclaimer_text}</div>", unsafe_allow_html=True)

# --- 분석 실행 및 결과 출력 ---
if st.button("AI 분석 결과 보기", type="primary"):
    with st.spinner("AI 엔진이 데이터를 분석하고 최적의 시술 조합을 설계 중입니다..."):
        # 분석 연출용 딜레이
        time.sleep(2) 

        # 핵심 로직 호출
        analysis_result = analyze_skin_concerns(inputs)
        
        # AI 개인화 설명 생성 (★핵심★)
        personalized_script = generate_personalized_explanation(inputs, analysis_result)

    st.markdown("---")
    st.header("💎 AI 분석 리포트")

    if not analysis_result['recommendations']:
        st.warning("분석 결과, 현재 상태에 적합한 추천 시술을 찾지 못했습니다. 내원 상담을 권장합니다.")
    else:
        st.subheader("🧑‍⚕️ AI 전문가 코멘트 (Personalized)")
        # AI가 생성한 개인화된 스크립트 출력
        st.info(personalized_script)

        st.subheader("🎯 추천 시술 조합")
        for rec in analysis_result['recommendations']:
            st.markdown(f"#### {rec['name']}")
            st.markdown(f"* **권장 강도/횟수:** {rec['intensity']}")
            st.markdown(f"* **핵심 이유:** {rec['reason']}")
            st.markdown("---")

    st.success("분석이 완료되었습니다. 이 결과를 바탕으로 전문가와 상담하세요.")
