#!/bin/bash

# 실행 디렉토리 확인
cd "$(dirname "$0")"

# 메인 서버 IP 확인
if [ -z "$1" ]; then
  echo "메인 서버 IP를 입력해주세요!"
  echo "사용법: ./start-worker.sh <메인_서버_IP>"
  exit 1
fi

MAIN_SERVER_IP=$1

# 환경 파일 복사 및 IP 업데이트
cp .env-worker ../.env
sed -i.bak "s/MAIN_SERVER_IP/$MAIN_SERVER_IP/g" ../.env

echo "워커 노드를 시작합니다. 메인 서버 IP: $MAIN_SERVER_IP"
cd ..
docker-compose -f docker-compose-worker-only.yml up -d

echo "워커 노드가 시작되었습니다."
echo "상태 확인: docker-compose -f docker-compose-worker-only.yml ps"
echo "로그 확인: docker-compose -f docker-compose-worker-only.yml logs -f airflow-worker" 