# 정기 회차 실행 절차 (RUN.md)

`run_id`는 현재 KST 시각 기준으로 정한다: 12시 이전이면 `YYYY-MM-DD-am`, 12시 이후면 `YYYY-MM-DD-pm`.

1. `GEMINI.md`와 `RUN.md`를 읽는다.
2. 수집: `python3 scripts/vt.py collect` (월요일 오전이면 `--include-standby` 자동 적용). 실패 소스는 기록만 하고 계속한다.
3. 프리필터: `python3 scripts/vt.py prefilter`로 `state/pending.jsonl`의 `keymap` 힌트를 채운다.
4. **Gemini 판정**: `state/pending.jsonl`에서 최신 순 최대 150건(키맵/키워드 히트 우선)을 20~30건씩 묶어 판정하고 `state/classified/<run_id>.jsonl`에 쓴다.
   - 관련성(`relevant`)은 4개 도메인 주제만 본다.
   - 커뮤니티 0.4 상한, 비공식 방향성 0.5 상한, 0.2 미만 버림(`low_significance`), `ai_frontier` 브리핑 기준 0.65.
   - 원문에 없는 수치·버전·사실을 추가하지 않는다.
   - 문체: `headline_ko`는 축약적인 명사형·구 스타일, `detail_ko`는 핵심 변경점·기술 구조·로봇 하네스 관점의 시사점을 담아 **해요체 3~4문장**(단순 소식은 2~3문장)으로 명확하게 쓴다.
5. 구조적 병합: `python3 scripts/vt.py merge-structural --run-id <run_id>`
6. **의미 병합(Gemini)**: `semantic_review_needed > 0`이면 후보를 검토해 같은 사건 매핑을 `state/merges/<run_id>_semantic.json` (`{"cluster_id": "existing_event_id"}`)에 쓴다.
7. 누적: `python3 scripts/vt.py accumulate --run-id <run_id>`
8. **토픽 상태 갱신(Gemini)**: 업데이트된 토픽의 `status_ko`를 `state/topics.json`에 2~3문장으로 갱신한다.
9. 트렌드 계산: `python3 scripts/vt.py trends`
10. 월요일 오전이면 `trends/direction.md`를 갱신한다. 매월 1일 오전이면 `python3 scripts/vt.py profile --apply`를 실행한다.
11. **아카이브 작성(Gemini)**: `archive/YYYY/MM/DD-am|pm.md`를 쓰고 `trends/latest.md`를 덮어쓴다.
12. 마감: `python3 scripts/vt.py finalize --run-id <run_id>` (판정 완료 건을 `pending` → `seen` 이동, `runs.jsonl` 기록).
13. 읽기 화면 렌더링: `python3 scripts/vt.py render-page` (`site/index.html` 갱신).
14. **Google Workspace 발행**: `python3 scripts/vt.py publish-gws --run-id <run_id>` (Google Docs 최상단 추가, Google Sheets 사건 원장 행 추가, 옵션 Gmail 요약 발송). 미설정 시 건너뛰고 실패로 회차를 중단하지 않는다.
15. Git 커밋: `git add -A && git commit -m "archive: <run_id> (사건 N, 버림 M)"` (원격 저장소가 연결돼 있으면 `git push`).
