"""
프로젝트 전역 설정
- 여기 값만 바꾸면 detector, speed_controller 동작이 모두 바뀜
"""
import os

# ── 경로 ────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

# ── 헬멧 감지 ────────────────────────────────────────────────
DETECTION_CONF      = 0.55   # 감지 신뢰도 임계값 (낮추면 더 민감, 올리면 더 엄격)
DETECTION_BUFFER    = 7      # 안정화 프레임 수 (높을수록 판정이 느리지만 안정적)

# 클래스 ID (dataset.yaml 기준)
CLASS_WITHOUT_HELMET = 0
CLASS_WITH_HELMET    = 1

# ── 속도 제어 ────────────────────────────────────────────────
MAX_SPEED       = 25.0   # 헬멧 착용 시 최대 속도 (km/h)
LIMITED_SPEED   = 10.0   # 헬멧 미착용 시 제한 속도 (km/h)

# PID 이득 (응답 속도 vs 안정성 트레이드오프)
PID_KP = 1.2
PID_KI = 0.02
PID_KD = 0.01

# ── 카메라 ────────────────────────────────────────────────────
CAM_INDEX  = 0      # 웹캠 장치 번호
CAM_WIDTH  = 1280
CAM_HEIGHT = 720
