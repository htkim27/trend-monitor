# RoboSpine Trend Monitor

**프론티어 모델 기반 로봇 하네스(80%) + 프론티어 AI·에이전트 트렌드(20%)**를 자동 수집·판정·누적하고, **Antigravity 스케줄링(`/schedule`)**과 **Google Workspace(Docs · Sheets · Gmail)**로 발행하는 개인 트렌드 아카이브입니다.

- **DB 없음 / 외부 LLM API 키 불필요**: 파일(`state/*.jsonl`, `config/*.yaml`)이 DB이고, 수집·중복제거·집계는 `scripts/vt.py`가, 의미 판정과 아카이브 편집은 **Gemini(Antigravity)**가 직접 수행합니다.
- **검증된 27개 활성 소스**: arXiv (`cs.RO` + 로봇 하네스 정밀 API), 빅테크(DeepMind, NVIDIA, OpenAI, Anthropic, Qwen, Hugging Face), 해외/국내 로보틱스 블로그(BAIR, Robohub, The Robot Report, IEEE Spectrum, 로봇신문, NAVER D2), 공식 유튜브(Unitree, DeepMind, NVIDIA), 중국/오픈소스 로보틱스 깃헙(`unitreerobotics`, `i2rt-robotics` YAM, `AgibotTech`, `OpenGalaxea`, `limxdynamics`, `BoosterRobotics`, `RoboProbe`).

---

## 1. Antigravity 스케줄링 설정 (`/schedule`)

Antigravity 채팅창에서 `/schedule`을 입력하거나 왼쪽 사이드바의 **Scheduled Tasks**에서 아래 설정으로 등록합니다.

- **이름**: `robospine-trend-monitor`
- **워크스페이스**: `/Users/htkim/dev/trend-monitor`
- **Cron 일정**: 매일 07:00, 18:00 KST → `0 7,18 * * *` (로컬 시간대 기준)
- **프롬프트**:

```text
너는 RoboSpine Trend Monitor의 정기 회차 실행자다.
저장소 루트의 GEMINI.md와 RUN.md를 먼저 읽고 RUN.md 절차를 처음부터 끝까지 그대로 실행한다.
run_id는 현재 KST 시각으로 정한다(12시 이전 YYYY-MM-DD-am, 이후 YYYY-MM-DD-pm).
관심 비중은 로봇 하네스·Embodied AI·중국/글로벌 로봇 SDK 80%, 프론티어 모델·에이전트 20%다.
판정 규칙(주제 중심, 커뮤니티 0.4 상한, 비공식 방향성 0.5 상한, 0.2 미만 버림, ai_frontier 브리핑 0.65 이상, 원문에 없는 사실 금지)을 지킨다.
끝나면 archive, trends, site/index.html, state를 커밋하고(원격이 있으면 push) publish-gws를 실행한다.
마지막 응답에는 이번 회차의 '한눈에' 3줄, 급상승/신규 토픽, 실패한 소스를 간결하게 보고한다.
```

---

## 2. Google Workspace 연동 (Docs · Sheets · Gmail, 2분 설정)

복잡한 OAuth 설정 없이 개인 Google 계정으로 바로 연동할 수 있도록 Apps Script 브릿지([`docs/gws-apps-script.gs`](docs/gws-apps-script.gs))를 제공합니다.

1. [script.google.com](https://script.google.com)에서 새 프로젝트를 만들고 [`docs/gws-apps-script.gs`](docs/gws-apps-script.gs) 내용을 붙여넣습니다.
2. **배포 → 새 배포 → 웹 앱** 선택 (`실행 주체: 나`, `액세스 권한: 모든 사용자`) 후 발급된 **Web App URL**을 복사합니다.
3. [`config/settings.yaml`](config/settings.yaml)의 `google_workspace:` 섹션에 입력합니다:
   - `apps_script_webhook_url`: 복사한 Web App URL (또는 환경변수 `GWS_WEBHOOK_URL`)
   - `doc_id`: 모바일 Google Docs 앱에서 열어볼 리포트 문서 ID
   - `sheet_id`: 사건 원장을 쌓을 Google Sheets ID
   - `notify_email` & `send_email_on_run: true`: 회차별 Gmail 브리핑을 받고 싶을 때 설정
4. 테스트: `python3 scripts/vt.py publish-gws --run-id 2026-11-25-pm`

---

## 3. 자주 쓰는 명령

```bash
# 소스 전체 상태 확인
python3 scripts/vt.py status

# 소스 URL 실제 HTTP 검증
python3 scripts/vt.py source-check --all

# 수동 수집 + 프리필터
python3 scripts/vt.py collect && python3 scripts/vt.py prefilter

# 읽기 화면 HTML 재생성 (site/index.html)
python3 scripts/vt.py render-page

# 단위 테스트
python3 -m unittest discover -s tests -v
```

자연어로도 바로 관리할 수 있습니다: *"이 유튜브 채널 소스로 추가해줘"*, *"Unitree 요즘 어때?"*, *"지금 업데이트해줘"*, *"소스 정리해줘"*.
