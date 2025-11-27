# app.py (Operation: Mirror MVP - Wizard of Oz Implementation v1.1)
import streamlit as st
import os
import json
from datetime import datetime
import time
import uuid
import pandas as pd
import io
from PIL import Image # 이미지 처리를 위해 Pillow 사용

# ---------------------------------------
# 0. 시스템 설정 및 초기화
# ---------------------------------------
st.set_page_config(
    page_title="Mirror AI - 스마트 뷰티 분석 플랫폼",
    page_icon="💎",
    layout="centered"
)

# 데이터 저장소 설정 (리드 및 이미지 저장 폴더)
LEAD_DIR = "mirror_leads"
IMAGE_DIR = os.path.join(LEAD_DIR, "images")
LEAD_FILE = os.path.join(LEAD_DIR, "leads.jsonl")

# 폴더 생성 확인
try:
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
except Exception as e:
    # 파일 시스템 접근이 불가능한 환경일 경우 경고 표시
    st.error(f"데이터 저장소 생성 실패: {e}. 호스팅 환경의 파일 시스템 권한을 확인하세요.")

# ---------------------------------------
# 1. UI/UX 스타일링 (Clinical Aesthetic)
# ---------------------------------------
custom_css = """
<style>
#MainMenu, footer, header, .stDeployButton {visibility:hidden;}
html, body {
    font-family: 'Pretendard', sans-serif;
    color: #333;
}
h1 {
    color: #00529B; /* Clinical Blue */
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
}
h2 {
    color: #00529B;
    border-bottom: 2px solid #00529B;
    padding-bottom: 5px;
    margin-top: 25px;
}
.stButton>button[kind="primary"] {
    width: 100%;
    font-weight: bold;
    font-size: 18px !important;
    padding: 15px;
    background-color: #00529B;
    color: white;
    border-radius: 10px;
}
.disclaimer {
    font-size: 13px;
    color: #777;
    text-align: justify;
    background-color: #f0f0f0;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 2. 데이터 저장 함수 (The Vault)
# ---------------------------------------
def save_lead_data(lead_id, data, images):
    """리드 데이터(JSONL)와 이미지를 저장합니다."""
    data["id"] = lead_id
    data["timestamp"] = datetime.now().isoformat()
    data["image_files"] = []

    # 이미지 저장 로직 (Pillow 사용)
    for key, img_file in images.items():
        if img_file:
            try:
                image = Image.open(img_file)
                # JPEG로 통일하여 저장 (용량 및 호환성 고려)
                img_filename = f"{lead_id}_{key}.jpeg"
                img_path = os.path.join(IMAGE_DIR, img_filename)
                
                # 파일을 디스크에 저장
                image.save(img_path, format='JPEG', quality=85)
                    
                data["image_files"].append(img_filename)
            except Exception as e:
                print(f"Image saving error: {e}")

    # JSONL 파일에 추가 (한 줄씩 저장)
    try:
        with open(LEAD_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        print(f"Lead data saving error: {e}")
        return False

# ---------------------------------------
# 3. 관리자 기능 (Admin Access - Wizard of Oz 운영용)
# ---------------------------------------
with st.sidebar:
    st.header("🔑 IMD Admin Access")
    password = st.text_input("Admin Password", type="password")
    # 보안을 위해 비밀번호는 Secrets에서 로드 (기본값: imd_architect)
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "imd_architect") 
    
    if password == ADMIN_PASSWORD:
        st.success("Admin Login Successful")
        if os.path.exists(LEAD_FILE) and os.path.getsize(LEAD_FILE) > 0:
            try:
                # JSONL 파일을 Pandas DataFrame으로 로드
                df_leads = pd.read_json(LEAD_FILE, lines=True)
                if not df_leads.empty:
                    st.subheader(f"수집된 리드 데이터 ({len(df_leads)})")
                    
                    # 데이터프레임 가공 (nested JSON 파싱)
                    display_df = df_leads.copy()
                    display_df['Name'] = display_df['contact'].apply(lambda x: x.get('name') if isinstance(x, dict) else 'N/A')
                    display_df['Phone'] = display_df['contact'].apply(lambda x: x.get('phone') if isinstance(x, dict) else 'N/A')
                    display_df['Areas'] = display_df['concerns'].apply(lambda x: ', '.join(x.get('areas', [])) if isinstance(x, dict) else 'N/A')
                    
                    st.dataframe(display_df[['timestamp', 'Name', 'Phone', 'Areas', 'id']])
                    
                    # CSV 다운로드 버튼
                    csv_buffer = io.BytesIO()
                    # UTF-8 BOM 추가하여 엑셀 호환성 확보
                    df_leads.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="📥 리드 데이터 다운로드 (CSV)",
                        data=csv_buffer.getvalue(),
                        file_name="mirror_ai_leads.csv",
                        mime="text/csv",
                    )
                    st.warning("⚠️ 이미지는 서버 폴더(`mirror_leads/images`)에서 수동으로 확인해야 합니다.")
            except Exception as e:
                st.error(f"리드 로딩 오류: {e}")
        else:
            st.info("수집된 리드가 없습니다.")
    elif password:
        st.error("비밀번호가 틀렸습니다.")

# ---------------------------------------
# 4. 메인 애플리케이션 로직 (Frontend)
# ---------------------------------------

st.title("Mirror AI 💎")
st.markdown("<h3 style='text-align: center; color: #555;'>AI 기반 스마트 뷰티 외형 분석 플랫폼</h3>", unsafe_allow_html=True)
st.markdown("---")

st.info("💡 후기 검색은 그만! 내 얼굴 데이터를 기반으로 AI가 최적의 시술 정보를 분석하고 전문가를 매칭해 드립니다.")

# 세션 상태를 사용하여 멀티스텝 폼 구현
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'images' not in st.session_state:
    st.session_state.images = {}

# --- Step 1: 법적 고지 및 동의 (의료법 준수) ---
if st.session_state.step == 1:
    st.markdown("<h2>0. 분석 전 확인사항 (의료법 준수)</h2>", unsafe_allow_html=True)

    disclaimer_text = """
    **[법적 고지 및 이용 안내]**
    본 서비스 'Mirror AI'는 사용자가 제공한 외형 정보(사진)와 입력 데이터를 기반으로 미용 정보를 제공하고 전문가 매칭을 돕는 **'정보 중개 플랫폼'**입니다. 본 서비스는 의료 행위(진단, 처방)를 수행하지 않으며, 제공되는 모든 분석 결과는 의학적 진단을 대체할 수 없습니다. 정확한 진료 및 시술 결정은 반드시 전문 의료기관을 방문하여 의사와의 대면 상담을 통해 이루어져야 합니다. 분석 결과의 활용 및 해석에 대한 책임은 사용자 본인에게 있습니다.
    """
    st.markdown(f"<div class='disclaimer'>{disclaimer_text}</div>", unsafe_allow_html=True)

    agree = st.checkbox("위 내용을 확인하였으며, 서비스 이용에 동의합니다.")
    
    if st.button("동의하고 시작하기", type="primary"):
        if agree:
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("동의 후 서비스 이용이 가능합니다.")

# --- Step 2: 데이터 입력 (사진 및 고민) ---
elif st.session_state.step == 2:
    st.markdown("<h2>1. AI 분석을 위한 사진 업로드</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        img_front = st.file_uploader("정면 사진 업로드 (필수)", type=["jpg", "jpeg", "png"], help="화장기 없는 상태에서 밝은 조명 아래 촬영해주세요.")
    with col2:
        img_side = st.file_uploader("측면(45도 또는 90도) 사진 업로드 (선택)", type=["jpg", "jpeg", "png"], help="윤곽 및 코 라인 분석에 도움이 됩니다.")

    st.markdown("<h2>2. 고민 부위 및 내용 입력</h2>", unsafe_allow_html=True)

    areas = st.multiselect(
        "가장 고민되는 부위를 선택하세요 (중복 가능)",
        options=["눈 (쌍꺼풀/트임)", "코 (콧대/코끝)", "안면 윤곽 (광대/턱)", "리프팅/탄력", "피부 (색소/모공/흉터)", "체형 (지방흡입/가슴)"]
    )

    details = st.text_area(
        "구체적인 고민 내용을 자유롭게 작성해주세요.",
        height=150,
        placeholder="예시: 눈이 졸려 보이고 콧대가 낮아서 고민이에요. 자연스러운 라인을 원합니다."
    )

    if st.button("다음 단계로", type="primary"):
        if not img_front:
            st.warning("정면 사진을 업로드해야 합니다.")
        elif not areas or not details:
            st.warning("고민 부위와 내용을 모두 입력해주세요.")
        else:
            # 파일 객체 자체를 세션 상태에 저장
            st.session_state.images = {"front": img_front, "side": img_side}
            st.session_state.data['concerns'] = {"areas": areas, "details": details}
            st.session_state.step = 3
            st.rerun()

# --- Step 3: 연락처 입력 및 제출 ---
elif st.session_state.step == 3:
    st.markdown("<h2>3. AI 분석 리포트 수신 정보</h2>", unsafe_allow_html=True)
    st.info("정밀 분석 결과 및 전문가 매칭 정보는 입력하신 연락처(카카오톡 또는 문자)로 전송됩니다.")

    name = st.text_input("성함")
    phone = st.text_input("연락처 (하이픈(-) 포함 입력)")

    if st.button("AI 분석 요청 및 리포트 받기", type="primary"):
        if not name or not phone:
            st.warning("결과 수신을 위해 성함과 연락처를 정확히 입력해주세요.")
        else:
            st.session_state.data['contact'] = {"name": name, "phone": phone}
            
            # 고유 ID 생성
            lead_id = str(uuid.uuid4())[:8]

            # 데이터 저장 실행 (백엔드 동작)
            if save_lead_data(lead_id, st.session_state.data, st.session_state.images):
                # AI 분석 시뮬레이션 (Wizard of Oz)
                with st.spinner("AI 엔진이 이미지 및 입력 데이터를 정밀 분석 중입니다... (예상 소요 시간 15초)"):
                    # 사용자가 기다리게 하여 실제 분석이 이루어지는 것처럼 연출.
                    time.sleep(10) 
                
                st.session_state.step = 4
                st.rerun()
            else:
                st.error("❌ 요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. (데이터 저장 실패)")

# --- Step 4: 완료 화면 ---
elif st.session_state.step == 4:
    st.success("✅ AI 분석 요청이 성공적으로 접수되었습니다!")
    st.balloons()
    
    name = st.session_state.data.get('contact', {}).get('name', '고객')
    st.header(f"감사합니다, {name}님!")
    st.subheader("AI 정밀 분석 리포트 및 전문가 매칭 결과는 영업일 기준 1~2일 내에 입력하신 연락처로 전송될 예정입니다.")
    st.info("Mirror AI를 이용해주셔서 감사합니다. 곧 최고의 전문가와 연결해드리겠습니다.")
    
    if st.button("새로운 분석 시작하기"):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
