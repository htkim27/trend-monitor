# RoboSpine 트렌드 모니터 · 2026-11-27 오후 (21:18 KST)
수집 19 (신규) · 판정 19 · 사건 3 (신규 3, 기존 병합 0) · 버림 11 (off_topic 10, low_significance 1) · 대기 0

## 한눈에
- **[0.72] LimX Dynamics, TRON2A·TRON2·TRON1 전 계층 오픈소스 스택 6종 동시 공개** (Isaac Lab+PPO RL 학습 `tron2_rl_lab`, WebSocket SDK+MuJoCo 양팔 컨트롤러 `tron2_manipulation_controller`, ROS 2 자율주행·비주얼 파지·ONNX 배포 포함)
- **[0.52] AMD·中 카스봇, '라이젠 AI 임베디드 X100' 기반 휴머노이드 엣지 AI 검증 완료** (CASBOT 02 온디바이스 로컬 대형 모델·멀티모달 상호작용·작업 스케줄링 실증)
- **[0.45] 볼보자동차, 벨기에 겐트 공장에 헥사곤 휴머노이드 '이온(AEON)' 첫 실증 배치** (조립라인 직투입 대신 직원·기존 설비와 협업 훈련하며 현장 안정성 검증)

## 로봇 하네스 · 아키텍처
- 이번 회차 신규 사건 없음.

## 빅테크 · 연구 모델 실험
- 이번 회차 신규 사건 없음.

## 로봇 플랫폼 · 미국/중국/한국/글로벌 깃헙 & SDK
- **[0.72] LimX Dynamics, TRON2A·TRON2·TRON1 학습·제어·내비게이션·배포 오픈소스 6종 공개** ([tron2_rl_lab](https://github.com/limxdynamics/tron2_rl_lab) · [tron2_manipulation_controller](https://github.com/limxdynamics/tron2_manipulation_controller) · [tron2-navigation-ros2](https://github.com/limxdynamics/tron2-navigation-ros2) · [tron2-navigation-pct-gpl](https://github.com/limxdynamics/tron2-navigation-pct-gpl) · [tron1-rl-deploy-arm](https://github.com/limxdynamics/tron1-rl-deploy-arm) · [tron2_visual_grasp](https://github.com/limxdynamics/tron2_visual_grasp) 병합) — 중국 LimX Dynamics 공식 GitHub에 TRON2A 휴머노이드용 Isaac Lab + PPO(`rsl_rl`) 강화학습 파이프라인 `tron2_rl_lab`(★15, 발바닥형·휠-레그형·전신 양팔 DASF 변형 지원)과 WebSocket SDK 기반 QP 모션 플래닝·PD 제어 및 로컬 MuJoCo 워크스페이스를 제공하는 `tron2_manipulation_controller`(★4)가 공개됐어요. 함께 공개된 `tron2-navigation-ros2`(★2)와 `tron2-navigation-pct-gpl`(★3)는 ROS 2 Humble 환경에서 RoboSense LiDAR·FAST-LIO·계단 인식 PCT 플래너·SCAN 로컬 플래너와 fail-closed 섀시 게이트웨이를 통합해요. 여기에 손목 D405 기반 탐지-접근-무릎굽힘-파지 데모 `tron2_visual_grasp`(★1)와 TRON1 암 ONNX RL 실로봇 배포 저장소 `tron1-rl-deploy-arm`(★3)까지 더해져, 상위 로봇 하네스가 WebSocket SDK·ROS 2·MuJoCo·Isaac Lab을 거쳐 양팔 모바일 플랫폼을 제어할 때 참고할 공식 툴체인이 크게 보강됐어요.
- **[0.52] AMD·中 카스봇, '라이젠 AI 임베디드 X100' 기반 휴머노이드 엣지 AI 검증 완료** ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49825)) — AMD와 중국 휴머노이드 로봇 기업 카스봇(CASBOT, 中科慧灵)이 휴머노이드 로봇 기기 내 엣지 AI 연산 협력 성과를 공개했다고 상하이정췐바오가 전했어요. 양사는 AMD의 '라이젠 AI 임베디드 X100' 시리즈 컴퓨팅 플랫폼을 기반으로 휴머노이드 '카스봇 02'에서 로컬 대규모 모델 운영, 멀티모달 상호작용, 지능형 작업 스케줄링 검증을 완료했어요. 클라우드 의존도를 낮추고 온디바이스에서 언어 이해부터 작업 스케줄링까지 처리하려는 휴머노이드 엣지 컴퓨트 스택 확장 흐름을 보여줘요.
- **[0.45] 볼보자동차, 벨기에 겐트 공장에 헥사곤 휴머노이드 '이온(AEON)' 첫 실증 배치** ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49833)) — 스웨덴 볼보자동차가 헥사곤 로보틱스(Hexagon Robotics)의 휴머노이드 로봇 '이온(AEON)'을 벨기에 겐트 공장에 배치하며 자사 생산시설에 처음 휴머노이드를 도입했어요. 이번 실증은 로봇을 곧바로 조립라인에 투입하지 않고 공장 내 직원 및 기존 자동화 설비와 함께 훈련하며 작업 안정성을 검증하는 단계에 초점을 맞추고 있어요. 글로벌 완성차 제조 현장에서 휴머노이드 플랫폼의 실전 파일럿 도입 사례가 확대되고 있어요.

## 프론티어 모델 · 에이전트 (20% 슬라이스)
- 이번 회차 신규 사건 없음.

## 트렌드 · 평소 대비
- 급상승 / 새로 등장(24h vs 7d): 24시간 대비 급상승·신규 판정 없음 (최근 7일 누적 사건 70건).
- 분야 비중(7일): 로봇 하네스 34.3% · 플랫폼/SDK 34.3% · 빅테크 모델 실험 20.0% · 프론티어 AI 11.4% (로보틱스 88.6% : 프론티어 AI 11.4%)

## 소스 점검
- 실패 소스 1건: `gh_allenai` (read timeout 15s, 누적 실패 1)
- 그 외 활성 소스 수집 성공 (총 391건 조회, 신규 19건 추가, 중복 372건 제외, 만료 0건)
