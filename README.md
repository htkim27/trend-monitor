# RoboSpine Trend Monitor

전 세계 로보틱스 논문·빅테크 발표·오픈소스 업데이트 중 **프론티어 AI 기반 로봇 제어(80%)**와 **핵심 AI 에이전트 트렌드(20%)**를 매일 아침 자동으로 수집·선별·요약해 주는 데일리 트렌드 브리핑 시스템입니다.

---

## 왜 만들었나요?

로보틱스와 프론티어 AI 분야는 매일 수많은 논문, 기업 블로그, 오픈소스 릴리스가 쏟아지지만 단순 홍보성 기사나 중복 보도, 사소한 패치 노이즈가 대부분입니다.

- **기사 나열이 아닌 '사건' 단위 통합**: 중복 보도를 하나의 사건(Event)으로 묶어, 지금 실제로 주목해야 할 흐름을 한눈에 파악합니다.
- **엔지니어링 관점의 핵심 요약**: 단순 번역이 아니라 *무엇이 바뀌었는지*, *어떤 기술적 메커니즘인지*, *로보틱스·하네스 엔지니어에게 어떤 시사점이 있는지*만 간결하게 정리합니다.
- **가볍고 투명한 운영**: 별도 DB나 외부 LLM API 키 없이 Git 파일(`state/`, `config/`)과 Python 스크립트(`scripts/vt.py`), 그리고 Antigravity(Gemini)만으로 매일 자동 동작합니다.

---

## 무엇을 추적하나요?

### 주요 모니터링 키워드
- **로봇 하네스·제어**: Robot Harness, RoboDojo(RoboProbe), RoboCurve, Training-Free, Long-Horizon, VLA·WAM
- **글로벌·중국 로보틱스**: Physical Intelligence(π0), Dream-1, Boston Dynamics, Skild AI, Figure AI, 1X·Optimus·Agility, Unitree, YAM(I2RT), AgiBot, Galaxea, LimX, Booster, Fourier
- **프론티어 AI × 로봇**: GPT-6·Gemini 4·Claude(Astra·Argon·Neon·Fable·Opus 등)의 로봇 제어·하네스 활용, OpenAI, Anthropic
- **핵심 연구자**: Jim Fan, Sergey Levine, Chelsea Finn, Pieter Abbeel, Fei-Fei Li, Shuran Song 등 Embodied AI 리더

### 모니터링 소스 (총 36곳)
| 분류 | 출처 |
|---|---|
| **학술·연구실** | arXiv(로보틱스 전체·하네스 정밀 검색), UC Berkeley BAIR, Stanford SAIL, MIT CSAIL |
| **빅테크·로봇 기업** | Google DeepMind, NVIDIA, Dream Labs, Hugging Face, OpenAI, Anthropic, Qwen, NAVER D2 |
| **오픈소스 GitHub** | Physical Intelligence, Boston Dynamics, NVIDIA Isaac Sim, AllenAI(Ai2), RoboProbe, Unitree, I2RT(YAM), AgiBot, Galaxea, LimX, Booster, Fourier |
| **유튜브·매체·커뮤니티** | Boston Dynamics·Unitree·DeepMind·NVIDIA 공식 유튜브, IEEE Spectrum, The Robot Report, Robohub, 로봇신문, Latent Space, Simon Willison, Hacker News(80점 이상 로보틱스) |

---

## 어떻게 작동하나요?

```text
[1. 수집] 36개 소스 자동 수집·중복 제거 (scripts/vt.py)
   ↓
[2. 선별·병합] AI가 도메인 관련성·중요도 판정 후 동일 이슈를 하나의 '사건'으로 통합 (Gemini)
   ↓
[3. 랭킹·누적] 최근 24시간 급증 토픽 계산 및 아카이브·웹페이지 생성
   ↓
[4. 발행] Git 커밋/푸시 + Google Docs · Sheets · Gmail 브리핑 전송 (매일 07:00 KST)
```

- **선별 기준**: 4개 핵심 도메인(`harnesses`, `embodied_models`, `hardware_sdk`, `ai_frontier`) 외의 글과 중요도 0.2 미만(단순 홍보·사소한 패치)은 제외합니다.
- **랭킹 메커니즘**: 커뮤니티 글(상한 0.4)과 비공식 해설(상한 0.5)의 과대평가를 방지하며, 단순 보도량이 아닌 **최근 24시간 동안 직전 7일 평균 대비 초과 발생한 토픽(급증 건수)**과 중요도를 기준으로 우선순위를 매깁니다.

### 주요 디렉터리 구조
- `trends/latest.md` — 가장 최근 회차 브리핑
- `archive/YYYY/MM/` — 일자별 브리핑 아카이브
- `site/index.html` — 브라우저용 트렌드 뷰어
- `config/` — 모니터링 소스(`sources.yaml`), 키워드(`keywords.yaml`), 관심 도메인(`interests.yaml`), 랭킹·연동 설정(`settings.yaml`)
- `scripts/vt.py` — 수집·프리필터·병합·트렌드 계산·발행 CLI

---

## 어떻게 사용하나요?

### 1. 브리핑 확인하기
- 저장소의 [`trends/latest.md`](trends/latest.md)에서 최신 브리핑을 바로 읽거나, [`site/index.html`](site/index.html)을 브라우저로 열어 확인할 수 있습니다.
- Google Workspace를 연동해 두면 매일 오전 7시에 Gmail·Google Docs로 자동 받아볼 수 있습니다.

### 2. 자연어로 관리하기 (Antigravity)
이 저장소를 Antigravity에서 열고 별도 명령어 없이 자연어로 요청하면 됩니다.

- *"지금 업데이트해줘"* — 즉시 1회 수집·판정·브리핑 실행
- *"이 사이트/깃헙/유튜브 소스로 추가해줘"* — 실제 HTTP 검증 후 `config/sources.yaml` 등록
- *"X 소스 빼줘"* / *"소스 상태 봐줘"* — 소스 제외 및 상태 점검
- *"X 키워드 넣어줘"* — 모니터링 키워드 추가 (`config/keywords.yaml`)
- *"Unitree 요즘 어때?"* / *"요즘 로봇 하네스 뭐가 떴어?"* — 아카이브 기반 출처 포함 답변

### 3. 매일 자동 실행 설정 (매일 07:00 KST)
macOS `launchd`(`scripts/run_scheduled.sh`) 또는 Antigravity `/schedule`(`0 7 * * *`)로 매일 오전 7시에 자동 실행됩니다.

<details>
<summary>Antigravity <code>/schedule</code> 등록 프롬프트 보기</summary>

- **이름**: `robospine-trend-monitor`
- **Cron**: `0 7 * * *` (매일 07:00 KST)
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

</details>

### 4. Google Workspace 연동 (선택: Docs · Sheets · Gmail)
복잡한 OAuth 설정 없이 Apps Script 브릿지([`docs/gws-apps-script.gs`](docs/gws-apps-script.gs))로 연동합니다.

1. [script.google.com](https://script.google.com)에서 새 프로젝트를 만들고 [`docs/gws-apps-script.gs`](docs/gws-apps-script.gs) 코드를 붙여넣습니다.
2. **배포 → 새 배포 → 웹 앱** (`실행 주체: 나`, `액세스 권한: 모든 사용자`) 배포 후 **Web App URL**을 복사합니다.
3. `.env` 또는 [`config/settings.yaml`](config/settings.yaml)의 `google_workspace` 항목에 Web App URL, `doc_id`, `sheet_id`, `notify_email`을 입력합니다.
4. 테스트: `python3 scripts/vt.py publish-gws --run-id <run_id>`

### 5. 자주 쓰는 CLI 명령
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
