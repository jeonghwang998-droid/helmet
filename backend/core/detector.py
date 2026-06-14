from ultralytics import YOLO
import cv2
from collections import deque

from config.settings import (
    MODEL_PATH, DETECTION_CONF, DETECTION_BUFFER,
    CLASS_WITHOUT_HELMET, CLASS_WITH_HELMET,
)


class HelmetDetector:
    """
    실시간 헬멧 착용 여부 판별.
    연속 N 프레임 다수결로 오감지(깜빡임) 방지.
    설정값은 config/settings.py 에서 변경.
    """

    def __init__(
        self,
        model_path: str = MODEL_PATH,
        conf_threshold: float = DETECTION_CONF,
        buffer_size: int = DETECTION_BUFFER,
    ):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self._buffer: deque[bool] = deque(maxlen=buffer_size)
        self.last_confidence: float = 0.0

    def detect(self, frame):
        """
        Returns:
            is_helmet_worn (bool): 안정화된 헬멧 착용 여부
            confidence (float): 가장 높은 감지 신뢰도
            annotated_frame: 바운딩박스가 그려진 프레임
        """
        results = self.model.predict(
            frame, imgsz=640, conf=self.conf_threshold, verbose=False,
        )
        boxes = results[0].boxes
        annotated = frame.copy()

        frame_has_helmet = False
        best_conf = 0.0

        for box in boxes:
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if class_id == CLASS_WITH_HELMET:
                color = (0, 200, 0)
                label = f"Helmet ON  {conf:.0%}"
                if conf > best_conf:
                    frame_has_helmet = True
                    best_conf = conf
            else:
                color = (0, 0, 220)
                label = f"No Helmet  {conf:.0%}"
                if conf > best_conf:
                    best_conf = conf

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated, label,
                (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2,
            )

        self._buffer.append(frame_has_helmet)
        self.last_confidence = best_conf

        is_worn = sum(self._buffer) > len(self._buffer) / 2
        return is_worn, best_conf, annotated

    def reset(self):
        self._buffer.clear()
        self.last_confidence = 0.0
