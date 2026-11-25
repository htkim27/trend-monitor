# RoboSpine 트렌드 모니터 · 2026-11-26 오전 (07:06 KST)
수집 14 (신규) · 판정 90 · 사건 22 · 버림 57 (off_topic 43, low_significance 14) · 대기 173

## 한눈에
- **[0.90] VLM 도구 호출 조작을 멀티턴 RL로 학습하는 'RoboHarness-RL' 및 비동기 코딩 에이전트 'ACAP' 공개** (arXiv cs.RO — PyRUA-Dex·MARGIN·CATWAY·Boundary-Aware Policy Learning 등 로봇 하네스 핵심 논문 집중 발표)
- **[0.86] Google DeepMind, 차세대 인터랙티브 월드 모델 'Genie 4' 및 Project Genie 공식 출시** (DeepMind 공식 블로그 · YouTube 2곳 병합)
- **[0.86] OpenAI, 코딩·컴퓨터 사용·비용 효율 강화한 'GPT-6.2 Astra 및 Sol' 공개** (ChatGPT Work · Codex · API 전반 출시)

## 로봇 하네스 · 아키텍처
- **[0.90] VLM 도구 호출 조작을 멀티턴 RL로 학습하는 'RoboHarness-RL' 공개** (PyRUA-Dex · MARGIN · CATWAY 병합 클러스터) — 인지·계획·제어 도구를 호출하는 에이전트 하네스에서 소형 오픈 웨이트 VLM의 성능을 끌어올리는 멀티턴 강화학습 프레임워크예요. 교사 시연 SFT 후 별도 VLA 없이 작업 결과 보상 기반 RL로 도구 호출 조작 능력을 개선해요. 함께 공개된 **PyRUA-Dex**(시연 없는 병렬 코딩 에이전트 양손 기민 조작), **MARGIN**(성공 롤아웃의 near-miss margin 기반 취약 코드 표적 수선), **CATWAY**(보정된 LLM 확률 기반 실행·질문·거부 3방향 비용 민감 게이트)와 맞물려 실행·검증·안전 전 축의 하네스 아키텍처가 빠르게 성숙하고 있어요.
- **[0.88] 로봇 제어 그룹별 비동기 코딩 에이전트 팀 아키텍처 'ACAP' 공개** — 단일 코딩 에이전트가 로봇 전체를 제어할 때 생기는 지연을 줄이기 위해, 한 대의 로봇을 팔·그리퍼나 몸통·섀시 등 제어 그룹별 지속 에이전트 팀으로 구성해 비동기 추론·실행과 물리 의존성 조율을 수행하는 구조예요.
- **[0.85] 에이전트-하위 정책 인계 실패를 줄이는 'Boundary-Aware Policy Learning'** (Weight-Space Programming 병합 클러스터) — 상위 멀티모달 에이전트가 하위 시각-운동 정책을 유효 시작 상태(handoff boundary) 밖에서 호출해 실패하는 문제를 정면으로 다뤘어요. 함께 발표된 **Weight-Space Programming(WSP)**은 추가 학습 없이 LLM 에이전트가 사전학습 VLA의 파라미터를 직접 소폭 편집해 반복 교착 실패를 교정하는 접근을 제시했어요.
- **[0.82] Embodied AI 물리 안전·시간·동적 변화 벤치마크 3종 ('EmbodiSafety' · 'RoboClock' · 'CALVIN-MAX')** — **EmbodiSafety**는 844개 시각 시나리오(스냅샷 1,092·궤적 540)에서 6가지 안전 대응 모드를, **RoboClock**은 5개 도메인 60태스크의 시간 창·응답 지연·처리량을, **CALVIN-MAX**는 7,828개 케이스로 실행 도중 물체·카메라·로봇·지시 변화의 영향을 분해 측정해요.
- **[0.81] 단일 실제 시연으로 검증 시뮬을 복원해 스킬을 자가 개선하는 'RESET'** — 단 한 번의 실제 시연에서 장면 기하·최종 성공 기준·물리 충실도 검증 참조를 추출해 LLM 코딩 에이전트가 이종 로봇(cross-embodiment) 스킬을 자가 개선할 수 있는 접촉 중심 월드를 복원해요.
- **[0.80] Ai2, 실제 로봇 조작 포인트 추적 'RoboTrack' Hugging Face 공식 블로그 공개** — AllenAI가 실제 로봇 조작 환경의 포인트 추적 문제를 다룬 RoboTrack 공식 기술 문서를 Hugging Face 블로그에 게시했어요.
- **[0.76] 장시간 조작 RL의 병목 구간을 집중 연습하는 'ReFocus'** — 진행도 기반으로 전역 RL과 국소 RL을 교차해 장시간 조작의 병목 구간을 찾아내고 추가 연습을 집중 배분하는 프레임워크예요.

## 빅테크 · 연구 모델 실험
- **[0.86] Google DeepMind, 차세대 인터랙티브 월드 모델 'Genie 4' 및 Project Genie 공식 출시** (DeepMind 블로그 · YouTube 2곳 병합) — 브라우저에서 자연어로 날씨·캐릭터·행동 전환 등 동적 이벤트를 실시간 트리거하면 시뮬레이션 물리·조명·오디오로 반응하는 차세대 인터랙티브 월드 모델을 Gemini와 결합해 공개했어요.
- **[0.84] NVIDIA, 두 개 프롬프트로 Cosmos 학습용 Physical AI 데이터셋 구축 워크플로 공개** — NVIDIA 공식 개발자 블로그에서 희귀 결함·야간 사고 등 수집이 어려운 엣지 케이스를 단 두 개 프롬프트로 합성해 월드 모델 학습 데이터를 구축하는 방법을 공개했어요.
- **[0.82] VLA 6종 진단 'Seeing Is Not Reaching' 및 경량 WAM 연구 ('DexWAC' · 'LeanWAM' · 'TauPrune-VLA')** — **Seeing Is Not Reaching**은 π0.5 포함 6종 VLA에서 어텐션이 이동한 표적을 따라가도 행동은 학습 위치를 고집하는 지시·장면 단축 현상을 규명했어요. 함께 공개된 **DexWAC**(월드·액터·크리틱 단일 통합), **LeanWAM**(동결 비디오 모델에서 소수 토큰 잠재 WAM 증류), **TauPrune-VLA**(학습 없는 스케일 적응형 시각 토큰 가지치기)가 WAM·VLA의 효율과 표현 공유를 끌어올렸어요.
- **[0.77] 표적·주변 역할을 분리해 4D 동적 조작 지연을 줄이는 'FoveaWAM'** — 표적 물체 자세만 밀리미터 정밀도로 예측하고 주변 환경은 여유 공간과 움직임 중심으로 분리 예측해 동적 조작 지연을 줄였어요.
- **[0.75] π0 연속 학습 진단: 도메인 내 망각은 0에 가까워도 OOD 강건성은 급락** — LIBERO·LIBERO-Plus 검증에서 경험 리플레이로 연속 학습한 π0의 이전 태스크 OOD 성능이 빠르게 붕괴함을 보였어요.

## 로봇 플랫폼 · 미국/중국/한국/글로벌 깃헙 & SDK
- **[0.75] Unitree 휴머노이드 XR 텔레오퍼레이션 'xr_teleoperate' (★1,741) & C++ SDK 'unitree_sdk2' (★1,460) 업데이트** — Unitree 공식 GitHub의 XR 텔레오퍼레이션과 핵심 C++ 제어 SDK가 나란히 업데이트됐어요.
- **[0.73] NVIDIA 오픈소스 로봇 시뮬레이터 'IsaacSim' 공식 GitHub 업데이트 (★4,535)** — Omniverse 기반 오픈소스 로봇 시뮬레이터 IsaacSim 저장소가 업데이트됐어요.
- **[0.72] 중국 AgiBot(지위안) 핸드 SDK 'agilink_omnihand_sdk' 업데이트 (★41)** — C++·Python·ROS2 API를 지원하는 공식 덱스터러스 핸드 SDK가 갱신됐어요.
- **[0.72] Ai2, 종단간 오픈 로봇 학습 생태계 'molmospaces' 공식 GitHub 업데이트 (★533)** — AllenAI의 오픈 로보틱스 학습 생태계 저장소가 업데이트됐어요.
- **[0.71] 중국 LimX Dynamics, 무의존성 저수준 모션 제어 SDK 'limxsdk-lowlevel' 업데이트 (★20)** — Linux·Windows 및 ROS/Gazebo·RL Sim2Real 배포를 지원하는 C++11/Python 저수준 제어 SDK가 업데이트됐어요.

## 프론티어 모델 · 에이전트 (20% 슬라이스)
- **[0.86] OpenAI, 코딩·컴퓨터 사용·비용 효율 강화한 'GPT-6.2 Astra 및 Sol' 공개** — ChatGPT Work·Codex·API 전반에서 전문 결과물·코딩·컴퓨터 사용(computer use) 성능과 비용 효율을 개선한 메이저 릴리스예요.
- **[0.84] Google DeepMind, 'Gemini 4 Neon' 공식 블로그 발표** (DeepMind 공식 · Latent Space 2곳 병합) — Gemini 4 라인업 중급 플래그십 모델의 1차 공식 발표가 게시됐으며, Latent Space 요약 기준 Intelligence Index 61점으로 Opus·Sol 경쟁 구간에 위치했어요.
- **[0.74] OpenAI, 코딩 에이전트의 AI 연구 가속 실측 보고서 'Research acceleration: The jagged frontier' 공개** — 코딩 에이전트가 AI 연구를 가속하는 영역과 불균일하게 실패하는 경계를 실측해 공개했어요.

## 트렌드 · 평소 대비
- 급상승 / 새로 등장(24h vs 7d): 기준선 축적 초기 단계로 24h 대비 급상승/신규 판정 없음 (최근 7일 누적 사건 35건).
- 분야 비중(7일): 로봇 하네스 40.0% · 플랫폼/SDK 37.1% · 빅테크 모델 실험 17.1% · 프론티어 AI 5.7% (로보틱스 94.3% : 프론티어 AI 5.7%)

## 소스 점검
- 전체 활성 소스 수집 성공 (신규 14건 추가, 중복 584건 제외, 만료 8건, 실패 소스 0건)
