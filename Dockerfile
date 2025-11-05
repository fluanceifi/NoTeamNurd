# 1. 베이스 이미지: NVIDIA CUDA 12.1.1 + cuDNN 8 (딥러닝용)
# devel 이미지는 파이썬 패키지 빌드에 필요한 도구(gcc 등)를 포함합니다.
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# 2. 시스템 환경 설정 (Non-interactive)
ENV DEBIAN_FRONTEND=noninteractive

# 3. Python 3.12 및 시스템 의존성 설치
# (Ubuntu 22.04에 Python 3.12를 설치하기 위해 PPA 추가)
# 3. Python 3.12 및 시스템 의존성 설치
# (Ubuntu 22.04에 Python 3.12를 설치하기 위해 PPA 추가)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    build-essential \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. python3.12를 기본 python/pip으로 설정
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# pip 업그레이드 (get-pip.py 스크립트로 수동 설치)
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# 5. 작업 디렉토리 설정
WORKDIR /app

# 6. PyTorch (GPU - CUDA 12.1) 버전 설치 -> gpu가 없다면 알아서 callback 후 cpu로 돌아감
# (requirements.txt에 torch가 없어야 합니다)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 7. 나머지 의존성 설치
COPY requirements.txt .

# pip가 제거하지 못하는 OS 기본 blinker 패키지를 강제로 삭제
RUN rm -rf /usr/lib/python3/dist-packages/blinker*

RUN pip install --no-cache-dir --break-system-packages -r requirements.txt
 # 8. 프로젝트 소스 코드 복사
COPY . .

# 9. 포트 노출
EXPOSE 5050

# 10. 애플리케이션 실행 (app.py 가정)
CMD ["python3", "backend/app.py"]