# RoboSpine Trend Monitor — 시스템 규칙 (GEMINI.md)

이 저장소는 **프론티어 모델 기반 로봇 하네스(80%) + 프론티어 AI·에이전트 트렌드(20%)**를 추적하는 개인 트렌드 아카이브다.
수집·중복 제거·프리필터·구조적 병합·집계·트렌드 계산·렌더링·Google Workspace 전송은 `scripts/vt.py`가 맡고,
**관련성·중요도 판정, 의미 병합, 토픽 상태 요약, 아카이브 편집은 Gemini(너)가 직접 수행한다.**

---

## 1. 지켜야 할 원칙
- 관심 분야는 `config/interests.yaml`의 4개 도메인뿐이다: `harnesses`(로봇 하네스·아키텍처), `embodied_models`(빅테크·연구 모델 실험), `hardware_sdk`(로봇 플랫폼·중국/글로벌 깃헙·SDK), `ai_frontier`(프론티어 모델·에이전트 20% 슬라이스). 나머지는 `off_topic`으로 버린다.
- 스크립트 결과를 손으로 고치지 않는다. 별칭·키워드·URL을 코드에 넣지 않고 전부 `config/`에 둔다.
- 소스는 실제 HTTP 요청(`vt.py source-check`)으로 검증한 뒤에만 등록한다. 죽거나 쓸모없는 소스는 지우지 않고 `rejected:`로 옮긴다.
- 원문에 없는 사실을 만들지 않는다. 수치·버전·날짜는 원문에 있는 것만 쓴다.
- **문체 규칙**: `headline_ko`는 축약적이지만 핵심이 바로 꽂히는 **명사형·구 스타일**로 쓴다. `detail_ko`는 전달할 핵심(무엇이 바뀌었는지 / 구체적 기술 메커니즘·수치 / 로봇 하네스·엔지니어에게 왜 중요한지)을 명확히 타겟해 **해요체 3~4문장**으로 충실하게 쓴다(단순 업데이트는 2~3문장도 가능).
- 커뮤니티 글은 중요도 **0.4 상한**, 비공식 방향성 해설은 **0.5 상한**, `0.2 미만`은 버림(`low_significance`), `ai_frontier` 20% 슬라이스는 브리핑 기준선 **0.65**를 적용한다.
- 기사가 아니라 **사건**이 쌓이고, 사건이 아니라 **토픽 상태**가 쌓인다. 트렌드 순위는 비율이 아니라 평소 대비 초과 건수로 매긴다.
- 모든 관리 기능은 슬래시 명령 없이 **자연어 요청**만으로 동작한다.

---

## 2. 자연어 관리 요청 처리 절차

관리 작업을 마치면 항상 변경 사항을 커밋한다. 보고는 모바일에서도 읽기 좋게 짧게(표 4열 이하) 쓴다.

### 2.1 소스 추가 ("이 사이트/깃헙/유튜브 추가해줘")
1. 사용자가 준 주소를 그대로 요청한다. 경로를 지어내지 않는다.
2. RSS/Atom이면 그대로 등록. HTML이면 `<link rel="alternate" type="application/rss+xml|atom+xml">`를 찾는다.
3. 피드가 없으면 `robots.txt`의 `Sitemap:` 및 `/sitemap.xml`을 확인해 경로 분포를 보여주고 `include_paths`를 제안한다.
4. YouTube 채널이면 채널 ID를 확인해 `https://www.youtube.com/feeds/videos.xml?channel_id=<ID>`(type: `atom`)로 등록한다.
5. GitHub 조직/유저면 `https://api.github.com/orgs/<org>/repos?sort=pushed&per_page=10`(또는 `/users/<user>/repos`) `json_list`로 등록한다(패치 노이즈가 심한 일반 릴리스 피드는 피한다).
6. `python3 scripts/vt.py source-check --source <id>` 통과 후에만 `config/sources.yaml`에 `verified_at`, `selected`를 적어 등록한다.
7. 사이트맵·카탈로그·html_list는 추가 즉시 1회 수집해 기준선 스냅샷을 저장한다.

### 2.2 소스 제외 ("X 소스 빼줘")
지우지 않고 `config/sources.yaml`의 `rejected:`로 옮기고 사유와 날짜를 적는다.

### 2.3 소스 목록·점검 ("소스 뭐 있어?", "소스 상태 봐줘")
`python3 scripts/vt.py status`를 실행해 보여준다. 점검 요청이면 `python3 scripts/vt.py source-check --all`을 실행한다.

### 2.4 적중률 재측정 ("소스 정리해줘")
`python3 scripts/vt.py profile` 결과로 상태 변경(`active`/`standby`/`dormant`) 제안을 보여주고 확인 후 `--apply`한다.

### 2.5 키워드 추가·삭제 ("X 키워드 넣어줘/빼줘")
- 추가: `config/keywords.yaml`에 추가한다. 3글자 미만이면 오탐 위험을 알리고 `require_any` 문맥어를 받는다. "트렌드에도 넣어줘"면 `promote: true`.
- 삭제: `keywords.yaml`에서 제거한다(`promote` 토픽은 `archived`로 유지).

### 2.6 토픽 관리 ("X 토픽 보여줘/없애줘/Y랑 합쳐줘")
`state/topics.json`과 `state/events.jsonl`을 조회·갱신한다. 제거는 `state: "removed"`로 바꿔 자동 재생성을 막는다.

### 2.7 질문 ("요즘 로봇 하네스 뭐가 떴어?", "유니트리 요즘 어때?")
`trends/latest.md`, `trends/direction.md`, `state/events.jsonl`, `state/topics.json`에서만 답하고 문장마다 날짜와 출처 링크를 단다. 없는 내용은 "아카이브에 없음"이라고 답한다.

### 2.8 지금 업데이트 ("지금 업데이트해줘")
`RUN.md` 절차를 현재 KST 시각 기준 `run_id`로 1회 실행한다.
