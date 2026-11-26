# RoboSpine 트렌드 모니터 · 2026-11-27 오전 (07:38 KST)
수집 13 (신규) · 판정 128 · 사건 14 (신규 14, 기존 병합 1) · 버림 112 (off_topic 111, low_significance 1) · 대기 0

## 한눈에
- **[0.78] 이산 스킬 어휘의 폐루프 실패를 분해 진단하는 'MPQ' 및 태스크 주도 시뮬 생성 플랫폼 'EmbodiedStudio' 공개** (arXiv cs.RO — 스킬 라이브러리 실패 귀속 분석과 자동 시뮬레이션 물리·채점 신뢰도 확보)
- **[0.72] Hugging Face, 모델-하네스 맞춤 최적화 'Harness Adapters' 및 OpenAI 'Codex 샌드박스' 격리 구조 공개** (프론티어 에이전트 하네스의 비용·성능 어댑테이션과 크로스플랫폼 실행 안전 경계 제시)
- **[0.68] 中 샤오펑, 통합 '튜링 피지컬 AI(VLA 3.0)' 및 1,500+ 촉각점 휴머노이드 '아이언' 공개** (차량·휴머노이드 공통 VLA 스택 통합 + DeepMind 'Genie 4' 내장 에이전트 비하인드 병합)

## 로봇 하네스 · 아키텍처
- **[0.78] 이산 스킬 어휘의 폐루프 실패를 분해 진단하는 'MPQ' 공개** ([arXiv](https://arxiv.org/abs/2611.32858v1)) — 유한 어휘에서 모션을 실행하는 기존 이산 스킬 정책은 잠재 코드북을 선택기·디코더와 함께 학습해, 폐루프 실패 시 어휘·선택·실행 중 어디가 원인인지 추적하기 어려웠어요. 본 연구는 학습된 정책 내부가 아닌 뒤에 시연 모션 라이브러리를 배치하는 Movement Prototype Quantization(MPQ)을 제안했어요. MPQ는 예측된 행동 청크를 가장 가까운 라이브러리 요소로 치환한 뒤 유한 범위 내에서 예측값 방향으로 보정해요. 스킬 라이브러리 기반 로봇 하네스에서 실패 원인을 단계별로 분해 진단하고 제어 안정성을 높이는 설계 근거가 돼요.
- **[0.76] 태스크 주도형 로봇 시뮬레이션 생성·평가 플랫폼 'EmbodiedStudio' 공개** ([arXiv](https://arxiv.org/abs/2611.32534v1)) — 로봇 학습과 평가를 위한 자동 생성 시뮬레이션 환경은 겉보기에 그럴듯해도 의도된 상호작용이나 물리적 안정성이 무너지거나, 생성된 채점 프로그램이 태스크 조건을 충실히 구현하지 못하는 실무 간극이 있었어요. 이 논문은 두 가지 간극을 정면으로 겨냥한 태스크 주도형 시뮬레이션 생성 플랫폼 'EmbodiedStudio'를 제안했어요. 프론티어 모델 기반 로봇 하네스를 다양한 태스크에서 신뢰성 있게 평가·검증하기 위한 자동 시뮬레이션 인프라 연구로 의미가 커요.

## 빅테크 · 연구 모델 실험
- **[0.72] Google DeepMind, 'Genie 4' 실시간 월드 시뮬레이션 및 내장 에이전트 제작 비하인드 공개** (기존 Genie 4 출시 사건 병합 · [YouTube](https://www.youtube.com/watch?v=pVc6KkjeCfU)) — Google DeepMind 공식 YouTube에서 차세대 인터랙티브 월드 모델 'Genie 4'와 Project Genie의 제작 비하인드 영상을 공개했어요. 정적 비디오 생성이 아니라 텍스트 프롬프트를 수초 만에 탐색 가능한 동적 월드로 만들고, 키보드 조작과 라이브 프롬프트로 장면을 실시간 제어하는 과정을 보여줬어요. 특히 Project Genie 내장 에이전트로 키보드 단축키에 매핑된 커스텀 앱을 만들어 캐릭터 이동·대화·이벤트를 실시간 트리거하고 프롬프트를 재현 가능한 시드로 활용한 점이 Embodied 시뮬레이션 관점에서 주목할 만해요.
- **[0.68] 中 샤오펑, 통합 '튜링 피지컬 AI(VLA 3.0)' 및 1,500+ 촉각점 휴머노이드 '아이언' 공개** ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49826)) — 중국 샤오펑(XPENG)이 11월 25일 광저우 제8회 '샤오펑 AI 데이'에서 차세대 휴머노이드 로봇과 자율주행차에 공통 적용할 '튜링 피지컬 AI 아키텍처(VLA 3.0)'와 차세대 범용 휴머노이드 로봇 '아이언(IRON)'을 공개했어요. VLA 3.0은 AI의 인지 능력·실시간 의사결정·물리적 실행 능력을 단일 시스템으로 통합한 구조예요. 아이언에 1,500개 이상 촉각 감지점을 탑재한 점과 차량·휴머노이드 공통 VLA 스택 전략이 중국 피지컬 AI 하드웨어·모델 통합 흐름을 잘 보여줘요.
- **[0.45] 중국 '2026 피지컬 AI 보고서', 삼지일체 전략 및 생산성 지표 'Worken' 제시** (비공식 2차 해설 · [로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49758)) — 중국 신화사·중국정보통신연구원이 공동 발표한 '2026 피지컬 AI 산업혁신 보고서'에서 운동지능·작업지능·상호작용지능을 통합하는 '삼지일체' 전략과 출하량 대신 현장 작업 생산성을 평가하는 지표 'Worken'이 제시됐다고 로봇신문이 전했어요. 중국 피지컬 AI 진영이 단순 하드웨어 양산에서 실제 작업 수행 능력 평가로 초점을 옮기는 방향성을 참고할 수 있어요.

## 로봇 플랫폼 · 미국/중국/한국/글로벌 깃헙 & SDK
- **[0.68] NVIDIA Isaac Sim, 시뮬레이션 데이터 자동화 저장소 'isaac-sim/AutoData' (★19) & 'IsaacLabTutorial' (★84) 업데이트** ([AutoData](https://github.com/isaac-sim/AutoData) · [IsaacLabTutorial](https://github.com/isaac-sim/IsaacLabTutorial) 병합) — NVIDIA Isaac Sim 공식 GitHub 조직의 Python 저장소 `isaac-sim/AutoData`(★19)와 Isaac Lab 공식 문서 연계 튜토리얼 프로젝트 `isaac-sim/IsaacLabTutorial`(★84)이 나란히 업데이트됐어요. Isaac Sim 생태계의 시뮬레이션 기반 로봇 데이터 자동 생성 파이프라인과 RL 태스크 구성 예제 툴체인이 지속적으로 보강되고 있어요.
- **[0.64] Unitree, 공식 로봇 카메라 캘리브레이션 도구 'uni_calib' GitHub 공개 (★5)** ([GitHub](https://github.com/unitreerobotics/uni_calib)) — Unitree 공식 GitHub에 로봇 카메라 캘리브레이션 도구 `unitreerobotics/uni_calib`(★5)가 등록·업데이트됐어요. 시각 기반 로봇 하네스와 3D 인지 도구를 실제 Unitree 하드웨어에 연결할 때 필수적인 카메라 보정을 공식 툴체인으로 지원하는 저장소예요.
- **[0.58] 中 애지봇(AgiBot), 美 로보스토어와 공식 유통 계약 체결하며 북미 진출** ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49767)) — 중국 로봇 기업 애지봇(AGIBOT·智元)이 미국 로봇 유통업체 로보스토어(RoboStore)와 공식 유통 계약을 체결하고 미국 시장에 본격 진출했어요. 휴머노이드 로봇, 4족 보행 로봇, 정교한 로봇손 등 주요 제품군을 미국 연구자·교육기관·개발자·기업에 공급할 예정이에요. 중국 주요 휴머노이드·덱스터러스 핸드 플랫폼의 북미 연구·개발 접근성이 넓어지는 움직임이에요.
- **[0.56] 중국 Booster Robotics, 3v3 시뮬레이션 프레임워크 'sim-3v3-simple-framework' 업데이트 (★18)** ([GitHub](https://github.com/BoosterRobotics/sim-3v3-simple-framework)) — 중국 Booster Robotics 공식 GitHub의 Python 저장소 `BoosterRobotics/sim-3v3-simple-framework`(★18)가 업데이트됐어요. 다중 휴머노이드 시뮬레이션과 협업 제어 실험을 지원하는 공식 오픈소스 프레임워크예요.
- **[0.50] 美 SiMa.ai, 단일 칩 다중 피지컬 AI 실행 SW '팔레트 3.0' 출시** ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49756)) — 미국 시마닷에이아이(SiMa.ai)가 엄격한 전력 제한 내 단일 칩 위에서 여러 피지컬 AI 모델을 최적화해 동시 실행할 수 있는 '팔레트 3.0(Palette 3.0)' 소프트웨어를 출시했다고 보도됐어요. 지난 6월 발표한 '에이전틱 팔레트'를 기반으로 복잡한 기계 추론과 구동을 지원하는 엣지 배포 SW예요.

## 프론티어 모델 · 에이전트 (20% 슬라이스)
- **[0.72] Hugging Face, 모델-하네스 맞춤 최적화 'Harness Adapters' 공개** ([Hugging Face Blog](https://huggingface.co/blog/harness-adapters-at-scale)) — Hugging Face 공식 블로그에서 선호하는 모델을 특정 에이전트 하네스에 맞춰 적응시켜 성능과 비용 효율을 동시에 개선하는 'Harness Adapters'를 공개했어요. 프론티어 모델 자체를 통째로 재학습하는 대신, 특정 하네스의 도구 호출·실행 구조에 맞춘 어댑터로 실전 효율을 끌어올리는 접근이에요. 로봇 하네스에서도 동일한 제어 인터페이스 위에 다양한 VLM·LLM을 비용 효율적으로 연결할 때 직접 응용할 수 있는 설계 패턴이에요.
- **[0.70] OpenAI, 크로스플랫폼 'Codex 샌드박스' 내부 격리 구조 공개** ([OpenAI](https://openai.com/index/inside-the-codex-sandbox)) — OpenAI 공식 블로그에서 코딩 에이전트 Codex가 로컬 머신에서 명령을 실행할 때 파일시스템과 네트워크 제한을 강제하는 샌드박스 아키텍처를 공개했어요. macOS·Linux·Windows 전반에서 사용자가 제어하는 권한 경계를 OS 수준으로 일관되게 강제하는 실행 구조를 설명해요. 코드 실행형 로봇 하네스에서 에이전트의 명령 실행 권한과 안전 경계(safety boundary)를 설계할 때 참고 가치가 높은 1차 문서예요.
- **[0.66] Hugging Face, 멀티 에이전트 구축·학습·평가 가이드 'Swarms, Flocks, Gangs' 공개** ([Hugging Face Blog](https://huggingface.co/blog/training-swarms)) — Hugging Face 공식 블로그에서 멀티 에이전트 시스템을 구축하고 학습·평가하는 방법론을 다룬 기술 포스트 'Swarms, Flocks, Gangs'를 게시했어요. 단일 에이전트를 넘어 다중 에이전트 협업 구조를 설계하고 체계적으로 평가하는 실무 기준을 다뤘어요. 팔·그리퍼·이동체 등 제어 그룹별 멀티 에이전트 로봇 하네스를 설계하고 검증할 때도 유용한 참고 자료예요.

## 트렌드 · 평소 대비
- 급상승 / 새로 등장(24h vs 7d): 24시간 대비 급상승·신규 판정 없음 (최근 7일 누적 사건 68건).
- 분야 비중(7일): 로봇 하네스 35.3% · 플랫폼/SDK 30.9% · 빅테크 모델 실험 20.6% · 프론티어 AI 13.2% (로보틱스 86.8% : 프론티어 AI 13.2%)

## 소스 점검
- 실패 소스 2건: `arxiv_robot_harness` (read timeout 15s, 누적 실패 1), `latent_space` (read timeout 15s, 누적 실패 1)
- 그 외 활성 소스 수집 성공 (총 491건 조회, 신규 13건 추가, 중복 478건 제외, 만료 0건)
