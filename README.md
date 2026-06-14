# 🛴 헬멧 착용 감지 기반 킥보드 안전 대여 시스템

> YOLO를 활용한 실시간 헬멧 감지 및 속도 제어 시스템

---

## 프로젝트 배경 및 목적

최근 공유 킥보드 이용자가 급증하면서 **헬멧을 착용하지 않고 주행하는 사례**가 사회적 문제로 부각되고 있습니다.

이로 인해 발생하는 문제는 크게 두 가지입니다.

1. **부상 위험** — 헬멧 미착용 상태에서 사고 발생 시 두부 손상 등 중증 부상으로 이어질 가능성이 높습니다.
2. **인식 저하** — 일부 이용자의 법규 미준수로 인해, 헬멧을 착용하고 올바르게 이용하는 사람들마저 부정적 인식의 피해를 받고 있습니다.

이에 **킥보드 이용 문화 개선 및 사고 예방**을 목적으로, 헬멧 착용 여부를 자동으로 인식하여 대여 가능 여부와 주행 속도를 제어하는 시스템을 개발하였습니다.  
본 프로젝트는 정부 주도의 마이크로모빌리티 안전 캠페인의 일환으로 기획된 서비스입니다.

### 핵심 동작

| 상황 | 동작 |
|------|------|
| 대여 전 헬멧 착용 감지 | 헬멧 착용 확인 시에만 대여 승인 |
| 주행 중 헬멧 착용 유지 | 최대 25 km/h 주행 허용 |
| 주행 중 헬멧 미착용 감지 | 즉시 10 km/h 로 속도 제한 + 경고 표시 |

---

## 프로젝트 구조

```
yolo_test12/
│
├── backend/                        # 핵심 서비스 코드
│   ├── config/
│   │   └── settings.py             # 전역 설정값 (속도·임계값·카메라·경로)
│   ├── core/
│   │   ├── detector.py             # 헬멧 감지 모듈 (YOLO 추론 + 프레임 안정화)
│   │   └── speed_controller.py     # PID 속도 제어 모듈
│   ├── api/                        # (예정) FastAPI 라우터
│   │   └── routes/
│   ├── utils/
│   │   ├── drawing.py              # OpenCV 한글 텍스트 렌더링 (PIL 경유)
│   │   └── logger.py               # 공통 로거
│   ├── model/
│   │   ├── best.pt                 # 학습 완료 모델 (PyTorch)
│   │   └── best.onnx               # 배포용 모델 (ONNX)
│   ├── main.py                     # 메인 실행 파일
│   └── requirements.txt
│
├── frontend/                       # (예정) 웹 UI
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
│
├── train/                          # 모델 학습 관련 일체
│   ├── data/
│   │   ├── raw/                    # 원본 데이터
│   │   │   ├── images/             # 학습 이미지 764장
│   │   │   └── annotations/        # Pascal VOC XML 어노테이션
│   │   ├── processed/
│   │   │   └── labels/             # YOLO 포맷 변환 라벨 (.txt)
│   │   └── dataset.yaml            # 학습 데이터셋 설정
│   ├── pretrained/                 # 재학습 시 기반 가중치 보관
│   ├── scripts/
│   │   ├── train.py                # 학습 실행 스크립트
│   │   ├── convert_labels.py       # Pascal VOC XML → YOLO 포맷 변환
│   │   └── create_yaml.py          # dataset.yaml 자동 생성
│   └── results/
│       └── train7_best/            # 최고 성능 학습 결과 (F1 곡선, PR 곡선 등)
│
└── tests/                          # 단위 테스트
    ├── test_detector.py
    └── test_speed_controller.py
```

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                        입력                              │
│                    웹캠 (Camera)                         │
└────────────────────────┬────────────────────────────────┘
                         │ 프레임
                         ▼
┌─────────────────────────────────────────────────────────┐
│               core / detector.py                        │
│                                                         │
│  YOLO 추론 (best.pt)                                    │
│       │                                                 │
│       ├── With Helmet    (Class 1)  ──→ 착용 감지       │
│       └── Without Helmet (Class 0)  ──→ 미착용 감지     │
│                                                         │
│  7프레임 다수결 버퍼  →  안정화된 헬멧 착용 여부 반환   │
└───────────────────────┬─────────────────────────────────┘
                        │ is_helmet_worn (bool)
                        ▼
┌─────────────────────────────────────────────────────────┐
│              core / speed_controller.py                 │
│                                                         │
│  PID Controller                                         │
│       │                                                 │
│       ├── 헬멧 착용  →  목표 속도 25 km/h              │
│       └── 헬멧 미착용 →  목표 속도 10 km/h (제한)      │
│                                                         │
│  부드러운 가속 / 감속 적용  →  현재 속도 반환           │
└───────────────────────┬─────────────────────────────────┘
                        │ current_speed, warning
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   main.py  HUD                          │
│                                                         │
│  [WAITING]  헬멧 감지 후 R 키로 대여 시작              │
│  [RENTING]  실시간 속도 / 헬멧 상태 / 경고 표시        │
└─────────────────────────────────────────────────────────┘
```

### 상태 전환

```
        헬멧 착용 확인 후 R 키
WAITING ──────────────────────▶ RENTING
        ◀──────────────────────
              R 키 (반납)
```

---

## 데이터셋

### 개요

| 항목 | 내용 |
|------|------|
| 총 이미지 수 | 764장 |
| 클래스 수 | 2개 |
| 원본 어노테이션 형식 | Pascal VOC XML |
| 학습 어노테이션 형식 | YOLO (.txt, 정규화 좌표) |
| 주요 촬영 대상 | 자전거·킥보드 탑승자 (헬멧 착용 / 미착용) |

### 클래스 정의

| ID | 클래스명 | 설명 |
|----|----------|------|
| 0 | Without Helmet | 헬멧 미착용 |
| 1 | With Helmet | 헬멧 착용 |

### 디렉토리 구성

```
train/data/
├── raw/
│   ├── images/           ← 원본 이미지 (.png, 400×267 해상도 기준)
│   └── annotations/      ← Pascal VOC XML (xmin, ymin, xmax, ymax 절댓값 좌표)
├── processed/
│   └── labels/           ← YOLO 포맷 (.txt, 정규화 좌표 cx cy w h)
└── dataset.yaml          ← 학습 설정 (클래스 이름, 경로 등)
```

### 어노테이션 변환 공식

```
center_x = (xmin + xmax) / 2 / image_width
center_y = (ymin + ymax) / 2 / image_height
width    = (xmax - xmin) / image_width
height   = (ymax - ymin) / image_height
```

### 학습 결과 요약 (train7_best)

`train/results/train7_best/` 에서 아래 지표를 확인할 수 있습니다.

| 파일 | 내용 |
|------|------|
| `F1_curve.png` | F1 Score 곡선 |
| `PR_curve.png` | Precision-Recall 곡선 |
| `confusion_matrix.png` | 혼동 행렬 |
| `results.csv` | 에폭별 손실 및 정밀도 수치 |
| `weights/best.pt` | 학습 중 최고 성능 가중치 |

---

## 기술 스택

### 개발 언어 및 런타임

| 항목 | 버전 |
|------|------|
| Python | 3.x (Anaconda 환경 권장) |

### AI / 컴퓨터 비전

| 라이브러리 | 역할 |
|-----------|------|
| [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) `>=8.3` | 객체 감지 모델 학습 및 추론 (YOLOv11 기반) |
| PyTorch `>=2.2` | 딥러닝 프레임워크 |
| torchvision `>=0.17` | 이미지 전처리 |
| OpenCV `>=4.9` | 웹캠 캡처, 프레임 처리, 바운딩박스 렌더링 |
| ONNX | 모델 배포 포맷 변환 |

### 제어 알고리즘

| 항목 | 내용 |
|------|------|
| 속도 제어 | PID 컨트롤러 (직접 구현) |
| 감지 안정화 | 7프레임 슬라이딩 윈도우 다수결 |

### 유틸리티

| 라이브러리 | 역할 |
|-----------|------|
| Pillow `>=10.0` | OpenCV에서 한글 텍스트 렌더링 |

### 개발 환경

| 항목 | 내용 |
|------|------|
| OS | Windows 11 |
| 패키지 관리 | Anaconda |
| 편집기 | VS Code |
| 버전 관리 | Git / GitHub |

---

## 실행 방법

### 1. 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 실행

```bash
cd backend
python main.py
```

### 3. 조작 방법

| 키 | 동작 |
|----|------|
| `R` | 대여 시작 (헬멧 착용 상태에서만 가능) / 반납 |
| `W` | 가속 (누르는 동안 속도 증가) |
| `Q` | 프로그램 종료 |

---

## 테스트 실행

```bash
pip install pytest
pytest tests/ -v
```
