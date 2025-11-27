# diagnostic_logic.py

def analyze_skin_concerns(inputs):
    """규칙 기반 안티에이징 시술 추천 로직 (v1.0)"""
    
    # 입력값 추출
    age = inputs.get("age")
    skin_type = inputs.get("skin_type")
    sagging_level = inputs.get("sagging_level") # 1(약함) ~ 5(심함)
    wrinkle_level = inputs.get("wrinkle_level")
    budget = inputs.get("budget")
    downtime_ok = inputs.get("downtime_ok")

    recommendations = []
    logic = []

    # --- 핵심 로직 (Decision Tree) ---

    # Rule 1: 심한 처짐 (고강도 초음파/고주파)
    if sagging_level >= 4 or (age >= 40 and sagging_level >= 3):
        if budget == "고예산 (150만 원 이상)":
            recommendations.append({"name": "울쎄라 (HIFU)", "intensity": "400-600샷", "reason": "깊은 근막층(SMAS) 타겟팅으로 강력한 리프팅 효과."})
            recommendations.append({"name": "써마지 FLX (RF)", "intensity": "600샷", "reason": "진피층 콜라겐 재생 유도, 피부 타이트닝 및 잔주름 개선."})
            logic.append("심한 처짐과 노화 징후에는 고강도 에너지 시술이 필수적입니다.")
        else:
            recommendations.append({"name": "슈링크 유니버스/텐쎄라 (국산 HIFU)", "intensity": "600샷 이상", "reason": "울쎄라 대비 합리적인 비용으로 유사한 리프팅 효과."})
            logic.append("심한 처짐이 관찰되나, 예산을 고려하여 국산 고강도 초음파 시술을 우선 추천합니다.")

    # Rule 2: 중간 정도 처짐 및 지방 (복합 시술)
    elif sagging_level >= 2 and age >= 30:
        recommendations.append({"name": "인모드 FX+Forma", "intensity": "3회 이상", "reason": "불필요한 지방 제거(FX) 및 타이트닝(Forma) 동시 효과."})
        logic.append("중간 정도의 처짐과 이중턱/심부볼 지방에는 인모드 복합 시술이 효과적입니다.")
        if wrinkle_level >= 3:
            recommendations.append({"name": "리쥬란 힐러/쥬베룩 (스킨부스터)", "intensity": "2cc 이상", "reason": "피부 속 환경 개선 및 잔주름 완화."})
            logic.append("피부결 및 잔주름 개선을 위해 스킨부스터 병행을 권장합니다.")

    # Rule 3: 초기 노화 및 예방 (저강도 관리)
    elif age < 30 or (sagging_level <= 2 and wrinkle_level <= 2):
        recommendations.append({"name": "LDM 물방울 리프팅", "intensity": "주 1회 관리", "reason": "통증 없이 피부 장벽 강화 및 탄력 유지."})
        recommendations.append({"name": "보톡스 (주름/턱)", "intensity": "주기적 시술", "reason": "표정 주름 예방 및 턱 라인 정리."})
        logic.append("초기 노화 단계에서는 강력한 시술보다는 꾸준한 관리형 시술이 적합합니다.")

    # Rule 4: 피부 타입 고려 (민감성)
    if skin_type == "민감성/홍조":
        logic.append("민감성 피부이므로, 강한 에너지 시술(HIFU/RF)은 주의가 필요하며 진정 관리가 필수입니다.")
        # 고강도 시술 추천 시 강도 하향 조정
        for rec in recommendations:
            if "울쎄라" in rec["name"] or "써마지" in rec["name"]:
                rec["intensity"] = "저강도/샷수 조절 필요"

    return {"recommendations": recommendations, "logic": " ".join(logic)}
