"""
킥보드 헬멧 감지 + 속도제어 메인 실행 파일

실행:
    cd backend
    python main.py

조작:
    W  키 누르기  → 가속
    W  키 떼기   → 감속
    R  키        → 대여 시작 / 종료 토글
    Q  키        → 종료
"""

import sys
import os

# backend/ 를 import 루트로 등록
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
from core.detector import HelmetDetector
from core.speed_controller import SpeedController
from config.settings import MODEL_PATH, CAM_INDEX, CAM_WIDTH, CAM_HEIGHT
from utils.drawing import put_text_kr

STATE_WAITING = "WAITING"
STATE_RENTING = "RENTING"


def draw_ui(frame, state: str, is_helmet_worn: bool, speed: float, warning: bool):
    h, w = frame.shape[:2]

    # 반투명 상단 바
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 72), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # 상태 표시 [WAITING] / [RENTING]
    state_color = (0, 220, 0) if state == STATE_RENTING else (0, 200, 220)
    cv2.putText(frame, f"[{state}]", (12, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, state_color, 2)

    # 헬멧 상태
    helmet_color = (0, 200, 0) if is_helmet_worn else (0, 0, 220)
    helmet_text = "HELMET: ON" if is_helmet_worn else "HELMET: OFF"
    cv2.putText(frame, helmet_text, (w // 2 - 110, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, helmet_color, 2)

    # 속도 (대여 중만)
    if state == STATE_RENTING:
        spd_color = (0, 220, 0) if not warning else (0, 100, 255)
        cv2.putText(frame, f"{speed:.1f} km/h", (w - 210, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, spd_color, 2)

    # 경고 배너 (하단)
    if warning:
        cv2.rectangle(frame, (0, h - 76), (w, h), (0, 0, 160), -1)
        frame = put_text_kr(
            frame,
            "  ⚠ 헬멧을 다시 착용해 주세요!  속도가 10 km/h 로 제한됩니다.",
            (10, h - 60), size=26, color=(255, 255, 255),
        )

    # 대기 안내 (하단)
    if state == STATE_WAITING:
        guide_color = (0, 200, 0) if is_helmet_worn else (180, 180, 180)
        guide = "R 키를 눌러 대여를 시작하세요" if is_helmet_worn else "헬멧을 착용하면 대여할 수 있습니다"
        frame = put_text_kr(frame, guide, (12, h - 48), size=28, color=guide_color)

    # 조작 안내 (우하단, 영문)
    cv2.putText(frame, "W:Accel  R:Rent/Return  Q:Quit",
                (w - 370, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (140, 140, 140), 1)

    return frame


def main():
    detector   = HelmetDetector()        # 경로·임계값 모두 settings.py 에서
    controller = SpeedController()

    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다. 장치 번호를 확인하세요.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    state    = STATE_WAITING
    throttle = False

    print("=== 킥보드 헬멧 감지 시스템 시작 ===")
    print(f"모델: {MODEL_PATH}")
    print("W: 가속  |  R: 대여 시작/종료  |  Q: 종료")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽지 못했습니다.")
            break

        is_helmet_worn, confidence, frame = detector.detect(frame)

        if state == STATE_RENTING:
            speed   = controller.update(is_helmet_worn, throttle)
            warning = controller.warning_active
        else:
            speed   = 0.0
            warning = False

        frame = draw_ui(frame, state, is_helmet_worn, speed, warning)
        cv2.imshow("Kickboard Helmet Detection", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('w'):
            throttle = True
        elif key == ord('r'):
            if state == STATE_WAITING:
                if is_helmet_worn:
                    state = STATE_RENTING
                    controller.reset()
                    detector.reset()
                    print("[대여 시작] 헬멧 착용 확인")
                else:
                    print("[대여 거절] 헬멧을 먼저 착용하세요")
            else:
                state    = STATE_WAITING
                throttle = False
                controller.reset()
                detector.reset()
                print("[대여 종료]")
        else:
            throttle = False

    cap.release()
    cv2.destroyAllWindows()
    print("=== 종료 ===")


if __name__ == "__main__":
    main()
