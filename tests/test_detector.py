"""
HelmetDetector 단위 테스트 (모델 없이 동작 구조만 검증)

실행: python -m pytest tests/ -v
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from core.detector import HelmetDetector


class _FakeBox:
    def __init__(self, cls_id, conf, coords):
        self.cls  = [cls_id]
        self.conf = [conf]
        self.xyxy = [coords]


class _FakeResults:
    def __init__(self, boxes):
        self.boxes = boxes


def _patch_model(detector, boxes):
    """실제 모델 없이 원하는 boxes 반환하도록 패치"""
    detector.model = type("M", (), {
        "predict": lambda self, *a, **kw: [_FakeResults(boxes)]
    })()


def test_buffer_majority_vote():
    det = HelmetDetector.__new__(HelmetDetector)
    from collections import deque
    det._buffer = deque(maxlen=7)
    det.last_confidence = 0.0

    # WITH_HELMET 박스 패치
    _patch_model(det, [_FakeBox(1, 0.9, [10, 10, 100, 100])])
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 4번 연속 헬멧 착용 → 과반수 → True
    for _ in range(4):
        is_worn, _, _ = det.detect(frame)
    assert is_worn is True


def test_no_detection_returns_false():
    det = HelmetDetector.__new__(HelmetDetector)
    from collections import deque
    det._buffer = deque(maxlen=7)
    det.last_confidence = 0.0

    _patch_model(det, [])  # 아무것도 감지 안 됨
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    for _ in range(7):
        is_worn, _, _ = det.detect(frame)
    assert is_worn is False


def test_reset_clears_buffer():
    det = HelmetDetector.__new__(HelmetDetector)
    from collections import deque
    det._buffer = deque([True, True, True, True], maxlen=7)
    det.last_confidence = 0.9
    det.reset()
    assert len(det._buffer) == 0
    assert det.last_confidence == 0.0
