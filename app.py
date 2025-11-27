# app.py (Mirror v3.0 - Vision AI First Architecture)
import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import io

# ---------------------------------------
# 0. 시스템 설정 및 초기화
# ---------------------------------------
st.set_page_config(
    page_title="Mirror AI v3.0 - 비전 기반 뷰티 분석",
    page_icon="💎",
    layout="centered"
)

# API 키 설정 (Streamlit Secrets 사용)
try:
    # 보안을 위해 API 키는 Streamlit Secrets에서 로드해야 합니다.
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    # 비전 분석이 가능한 모델 로드 (Gemini 1.5 Flash는 속도와 이미지 분석 능력의 균형이 좋음)
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"❌ AI 엔진 초기화 실패: GOOGLE_API_KEY를 Streamlit Secrets에 설정하세요. {e}")
    # 개발 중 임시 폴백 (필요시 주석 해제하고 키 입력)
    # API_KEY = "YOUR_API_KEY_HERE"
    # genai.configure(api_key=API_KEY)
    # model = genai.GenerativeModel('gemini-1.5-flash-latest')
    st.stop()

# CSS 스타일링 (Clinical Aesthetic)
custom_css = """
<style>
#MainMenu, footer, header, .stDeployButton {visibility:hidden;}
h1 { color: #00529B; font-weight: 800; text-align: center; margin-bottom: 10px; }
.stButton>button[kind="primary"] { width: 100%; font-weight: bold; font-size: 18px !important; padding: 15px; background-color: #00529B; color: white; border-radius: 10px; }
.disclaimer { font-size: 13px; color: #777; background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
.report-section { border-left: 4px solid #00529B; padding-left: 15px; margin-bottom: 20px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 1. 비전 AI 분석 프롬프트 (★핵심 IP★)
# ---------------------------------------
def generate_vision_analysis_prompt(concerns):
    """고민 부위에 따라 동적으로 분석 프롬프트를 생성합니다."""
    
    # 종합 분석 항목 정의
    analysis_sections = {
        "눈 성형 (쌍꺼풀/트임/눈매교정)": "눈 분석: 눈꺼풀 형태(홑꺼풀/쌍꺼풀), 몽고주름 유무, 안검하수 여부, 눈 크기, 지방 분포도를 분석.",
        "코 성형 (콧대/코끝/복코)": "코 분석: 콧대 높이, 코끝 모양, 콧볼 넓이, 전체적인 길이 및 각도를 분석.",
        "안면 윤곽 (광대/턱/이마)": "안면 윤곽 분석: 광대뼈 돌출 정도, 턱 라인 선명도, 이마 형태, 전반적인 V라인 형태를 분석.",
        "리프팅/안티에이징 (처짐/주름)": "노화 징후 분석: 피부 처짐, 심부볼, 주름(팔자/이마/눈가) 깊이, 전반적인 탄력도를 분석.",
        "피부 시술 (색소/모공/여드름)": "피부 상태 분석: 피부결, 톤, 색소 침착(기미/잡티), 모공 크기, 여드름 및 흉터를 분석.",
        "체형 성형 (가슴/지방흡입)": "체형 분석 (사진에 포함된 경우): 비율, 지방 분포도 또는 언급된 특정 신체 고민을 분석.",
    }

    # 사용자가 선택한 항목만 포함
    selected_analysis = ""
    for concern in concerns:
        if concern in analysis_sections:
            selected_analysis += f"- {analysis_sections[concern]}\n"

    if not selected_analysis:
        selected_analysis = "- 전반적인 얼굴 비율, 조화, 피부 상태를 분석."

    # 시스템 프롬프트 설계
    prompt = f"""
    [시스템 역할: AI 미용 분석 컨설턴트]
    당신은 성형외과/피부과 수석 상담 실장입니다. 업로드된 이미지(들)를 분석하고 사용자가 선택한 고민 영역에 초점을 맞춰 상세한 미용 분석 리포트를 제공하십시오.

    [분석 지침]
    1. 어조: 전문적이고 객관적이며 임상적인 한국어 사용. supportive tone.
    2. 초점: 이미지를 기반으로 선택된 영역을 집중 분석.
    3. 내용: 
        a) 이미지 기반 현재 상태 객관적 묘사 (예: "사진상으로 눈꺼풀이 두껍고 몽고주름이 관찰됩니다.").
        b) 미용적 개선 가능 영역 식별.
        c) 관련 시술/수술 정보 제안 (예: "절개 눈매교정", "울쎄라", "코끝 자가연골").
    4. 면책 조항: 의학적 진단이 아닌 AI 기반 미용 분석임을 명확히 할 것.

    [분석 대상 영역 (이미지 기반 분석)]
    {selected_analysis}

    [출력 형식 (반드시 이 구조를 준수)]

    ### 💎 Mirror AI 종합 외형 분석 리포트

    #### 1. AI 비전 분석 개요 (Visual Summary)
    *(사진을 기반으로 한 전체적인 첫인상과 주요 외형적 특징을 요약합니다.)*

    ---
    *(선택된 각 영역에 대해 아래 형식 반복)*

    #### [영역 이름] 집중 분석 (예: 눈 성형 분석)
    * **현재 상태 (사진 기반 관찰):** *(이미지를 기반으로 한 상세하고 객관적인 묘사)*
    * **개선 방향 제안:** *(잠재적인 미용적 개선 방향)*
    * **고려 가능한 시술/수술 정보:** 
        - **[시술/수술명]:** *(어떻게 문제를 해결하는지 간단한 설명)*

    ---

    #### 📊 종합 솔루션 및 권장 사항
    *(분석 결과를 종합하여 최적의 시술 조합과 시너지 효과를 제안합니다.)*

    ---
    **[법적 고지]** 본 리포트는 AI 기반의 미용 정보 분석이며, 의학적 진단을 대체할 수 없습니다. 정확한 진료는 반드시 전문의와의 대면 상담이 필요합니다.
    """
    return prompt

# ---------------------------------------
# 2. 메인 애플리케이션 로직
# ---------------------------------------

st.title("Mirror AI v3.0 💎")
st.markdown("<h3 style='text-align: center; color: #555;'>비전 AI 기반 토탈 뷰티 분석 엔진</h3>", unsafe_allow_html=True)
st.markdown("---")

# 세션 상태 관리
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

if not st.session_state.analysis_done:

    # --- 입력 폼 ---
    st.header("1. 분석 대상 사진 업로드")
    st.info("최대 3장까지 업로드 가능합니다. (정면, 측면 등 다양한 각도 권장)")
    
    # 여러 파일 업로드 지원
    uploaded_files = st.file_uploader("분석할 부위의 사진을 업로드해주세요.", type=["jpg", "jpeg", "png"], accept_multiple_files=True, help="고화질일수록 분석 정확도가 높습니다.")

    image_inputs = []
    if uploaded_files:
        # 최대 3장까지만 처리
        files_to_process = uploaded_files[:3]
        cols = st.columns(len(files_to_process))
        for i, file in enumerate(files_to_process):
            try:
                # PIL 이미지로 변환하여 메모리에 저장
                img = Image.open(file)
                image_inputs.append(img)
                with cols[i]:
                    st.image(img, caption=f"이미지 {i+1}", width=150)
            except Exception:
                st.error(f"이미지 {i+1} 처리 실패.")

    st.header("2. 집중 분석 영역 선택")
    # 포괄적인 카테고리 설정
    concerns = st.multiselect(
        "AI가 집중적으로 분석하길 원하는 영역을 선택하세요 (중복 가능)",
        options=[
            "눈 성형 (쌍꺼풀/트임/눈매교정)", 
            "코 성형 (콧대/코끝/복코)", 
            "안면 윤곽 (광대/턱/이마)", 
            "리프팅/안티에이징 (처짐/주름)", 
            "피부 시술 (색소/모공/여드름)",
            "체형 성형 (가슴/지방흡입)"
        ],
        default=["눈 성형 (쌍꺼풀/트임/눈매교정)", "코 성형 (콧대/코끝/복코)", "리프팅/안티에이징 (처짐/주름)"]
    )

    st.markdown("---")

    # 법적 고지
    disclaimer_text = """
    **[의료법 준수 고지]** 본 서비스는 AI 기반의 미용 정보 분석이며, 의학적 진단을 대체할 수 없습니다. 정확한 진료는 반드시 전문의와의 대면 상담이 필요합니다.
    """
    st.markdown(f"<div class='disclaimer'>{disclaimer_text}</div>", unsafe_allow_html=True)

    # --- 분석 실행 ---
    if st.button("AI 비전 분석 시작하기", type="primary"):
        if not image_inputs:
            st.warning("분석을 위해 최소 1장 이상의 사진을 업로드해야 합니다.")
        elif not concerns:
            st.warning("최소 하나 이상의 분석 영역을 선택해주세요.")
        else:
            with st.spinner("🧠 멀티모달 AI 엔진이 이미지를 정밀 분석 중입니다... (약 15~30초 소요)"):
                try:
                    # 프롬프트 생성
                    prompt = generate_vision_analysis_prompt(concerns)

                    # 멀티모달 입력 구성
                    input_payload = [prompt]
                    
                    # 이미지 데이터를 API 형식으로 준비
                    for img in image_inputs:
                        img_byte_arr = io.BytesIO()
                        # JPEG로 통일하여 처리 (RGB 변환 추가하여 PNG/RGBA 파일 호환성 확보)
                        img.convert('RGB').save(img_byte_arr, format='JPEG', quality=85)
                        image_data = img_byte_arr.getvalue()
                        input_payload.append({"mime_type": "image/jpeg", "data": image_data})

                    # Gemini Vision API 호출
                    # 창의성 설정 (Temperature 0.7로 설정하여 전문성과 자연스러움의 균형 유지)
                    generation_config = genai.GenerationConfig(temperature=0.7)
                    response = model.generate_content(input_payload, generation_config=generation_config)
                    
                    analysis_report = response.text

                    # 결과 저장 및 화면 전환
                    st.session_state.analysis_report = analysis_report
                    st.session_state.analysis_done = True
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ 분석 중 오류가 발생했습니다. 입력 형식을 확인하거나 잠시 후 다시 시도해주세요. (오류: {e})")

# --- 결과 출력 화면 ---
else:
    st.success("✅ AI 비전 분석 완료!")
    
    # 생성된 마크다운 리포트 출력
    st.markdown(st.session_state.analysis_report, unsafe_allow_html=True)
    
    # 후속 조치 유도 (리드 확보)
    st.markdown("---")
    st.header("💡 전문가 매칭 및 상담 신청")
    st.info("분석 결과를 바탕으로 최적의 전문가와 상담을 원하시면 아래 정보를 입력해주세요.")

    # 리드 수집 폼 (Wizard of Oz 연결점)
    with st.form(key='lead_form'):
        name = st.text_input("성함")
        phone = st.text_input("연락처")
        submit_button = st.form_submit_button(label='전문가 상담 신청하기 (무료)', type="primary")

        if submit_button:
            if name and phone:
                # 여기서 데이터를 저장하거나 관리자에게 알림 전송 (실제 구현 필요)
                st.success(f"{name}님, 상담 신청이 완료되었습니다. 곧 전문가가 연락드릴 예정입니다. (데모 버전)")
                # (실제 운영 시 여기에 데이터 저장 로직(DB/Email/Slack) 추가 필요)
            else:
                st.warning("성함과 연락처를 입력해주세요.")

    if st.button("다시 분석하기"):
        st.session_state.analysis_done = False
        st.rerun()
