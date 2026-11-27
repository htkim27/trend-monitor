#!/bin/zsh
set -euo pipefail

export PATH="/Users/htkim/.local/bin:/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
REPO_DIR="/Users/htkim/dev/trend-monitor"
LOG_FILE="${REPO_DIR}/state/launchd.log"
LOCK_DIR="${REPO_DIR}/state/.run.lock"

cd "${REPO_DIR}"
mkdir -p "${REPO_DIR}/state"

# 중복 실행 방지 락
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] Already running, skipping." >> "${LOG_FILE}"
  exit 0
fi
trap 'rmdir "${LOCK_DIR}" 2>/dev/null || true' EXIT

echo "============================================================" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] Starting scheduled RoboSpine Trend Monitor run" >> "${LOG_FILE}"

PROMPT="너는 RoboSpine Trend Monitor의 정기 회차 실행자다. 저장소 루트(${REPO_DIR})의 GEMINI.md와 RUN.md를 먼저 읽고 RUN.md 절차를 처음부터 끝까지 그대로 실행한다. run_id는 현재 KST 시각으로 정한다(12시 이전 YYYY-MM-DD-am, 이후 YYYY-MM-DD-pm). 관심 비중은 로봇 하네스·Embodied AI·중국/글로벌 로봇 SDK 80%, 프론티어 모델·에이전트 20%다. 판정 규칙(주제 중심, 커뮤니티 0.4 상한, 비공식 방향성 0.5 상한, 0.2 미만 버림, ai_frontier 브리핑 0.65 이상, 원문에 없는 사실 금지)을 지킨다. 끝나면 archive, trends, site/index.html, state를 커밋하고 origin main으로 push하며, publish-gws를 실행한다. 마지막 응답에는 이번 회차의 '한눈에' 3줄, 급상승/신규 토픽, 실패한 소스를 간결하게 보고한다."

/usr/bin/caffeinate -i /Users/htkim/.local/bin/agy \
  --print "${PROMPT}" \
  --mode auto \
  --dangerously-skip-permissions \
  --print-timeout 30m \
  >> "${LOG_FILE}" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] Finished scheduled run" >> "${LOG_FILE}"
