"""
SpeedController 단위 테스트

실행: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from core.speed_controller import SpeedController
from config.settings import MAX_SPEED, LIMITED_SPEED


def test_speed_increases_with_throttle():
    ctrl = SpeedController()
    for _ in range(50):
        ctrl.update(is_helmet_worn=True, throttle=True)
    assert ctrl.current_speed > 0


def test_speed_never_exceeds_max():
    ctrl = SpeedController()
    for _ in range(200):
        ctrl.update(is_helmet_worn=True, throttle=True)
    assert ctrl.current_speed <= MAX_SPEED + 0.01


def test_speed_limited_when_no_helmet():
    ctrl = SpeedController()
    # 먼저 최대 속도까지 가속
    for _ in range(200):
        ctrl.update(is_helmet_worn=True, throttle=True)
    # 헬멧 벗은 후 수렴할 때까지 진행
    for _ in range(200):
        ctrl.update(is_helmet_worn=False, throttle=True)
    assert ctrl.current_speed <= LIMITED_SPEED + 0.01


def test_warning_active_when_no_helmet_and_moving():
    ctrl = SpeedController()
    for _ in range(50):
        ctrl.update(is_helmet_worn=True, throttle=True)
    ctrl.update(is_helmet_worn=False, throttle=True)
    assert ctrl.warning_active is True


def test_reset_clears_state():
    ctrl = SpeedController()
    for _ in range(50):
        ctrl.update(is_helmet_worn=True, throttle=True)
    ctrl.reset()
    assert ctrl.current_speed == 0.0
    assert ctrl.is_limited is False
