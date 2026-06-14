from config.settings import MAX_SPEED, LIMITED_SPEED, PID_KP, PID_KI, PID_KD


class PIDController:
    def __init__(self, kp: float = PID_KP, ki: float = PID_KI, kd: float = PID_KD):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._prev_error: float = 0.0
        self._integral: float = 0.0

    def compute(self, setpoint: float, measured: float) -> float:
        error = setpoint - measured
        self._integral += error
        derivative = error - self._prev_error
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        self._prev_error = error
        return output

    def reset(self):
        self._prev_error = 0.0
        self._integral = 0.0


class SpeedController:
    """
    헬멧 착용 여부 + 가속 입력 → PID 속도 제어.
    최대/제한 속도는 config/settings.py 에서 변경.

    사용 예:
        ctrl = SpeedController()
        speed = ctrl.update(is_helmet_worn=True, throttle=True)
    """

    def __init__(self):
        self._pid = PIDController()
        self.current_speed: float = 0.0
        self.target_speed: float = 0.0
        self.is_limited: bool = False
        self.warning_active: bool = False

    @property
    def speed_limit(self) -> float:
        return LIMITED_SPEED if self.is_limited else MAX_SPEED

    def update(self, is_helmet_worn: bool, throttle: bool) -> float:
        self.is_limited = not is_helmet_worn
        self.warning_active = self.is_limited and self.current_speed > 0

        self.target_speed = self.speed_limit if throttle else 0.0

        control = self._pid.compute(self.target_speed, self.current_speed)
        self.current_speed = max(0.0, min(self.current_speed + control * 0.1, self.speed_limit))

        return self.current_speed

    def reset(self):
        self._pid.reset()
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.is_limited = False
        self.warning_active = False
