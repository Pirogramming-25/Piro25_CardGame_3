# Python 3.13 slim 이미지 사용 (가볍고 안정적)
FROM python:3.13-slim

# 파이썬 출력 버퍼링 끄기, .pyc 파일 생성 방지
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 (필요한 것만)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 먼저 복사 후 설치 (Docker 캐시 활용)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# 나머지 프로젝트 파일 전부 복사
COPY . /app/

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 포트 노출
EXPOSE 8000

# 실행 (gunicorn으로 프로덕션 서버)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]