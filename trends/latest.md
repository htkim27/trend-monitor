# RoboSpine 트렌드 모니터 · 2026-11-25 오후 (22:55 KST)
수집 262 · 판정 27 (핵심 샘플 1차) · 사건 17 · 버림 7 (off_topic 7) · 대기 235

## 한눈에
- **[0.94] Unitree, 프론티어 모델(GPT-6 Astra 등) 직접 연결용 공식 로봇 스킬 하네스 `unitree_robotskills` 공개** ([GitHub](https://github.com/unitreerobotics/unitree_robotskills)) · 공식
- **[0.88] VLAs Execute, Code Recovers** — 에이전트 플래너가 동결된 VLA 원자 스킬을 조합하고 코드로 복구하는 3D 스킬 엔벨로프 하네스 ([arXiv:2611.32245](https://arxiv.org/abs/2611.32245v1)) · 공식
- **[0.85] ICLWorld** — 디지털 컴퓨터 사용에서 물리 로봇 세계까지 동일 프론티어 에이전트의 인컨텍스트 학습(ICL) 통합 벤치마크 ([arXiv:2611.32649](https://arxiv.org/abs/2611.32649v1)) · 공식

## 로봇 하네스·아키텍처 (arXiv · 오픈소스)
| 중요도 | 토픽 | 무엇이 달라졌나 | 출처 |
|---|---|---|---|
| 0.94 | Unitree RobotSkills | GPT-6 Astra 등 프론티어 모델을 유니트리 로봇에 연결·스킬 작성하는 공식 프레임워크 | [GitHub](https://github.com/unitreerobotics/unitree_robotskills) |
| 0.88 | VLA-as-Tool | 동결 VLA 스킬 조합 격차를 3D 스킬 엔벨로프 + 코드 복구로 메우는 에이전트 하네스 | [arXiv](https://arxiv.org/abs/2611.32245v1) |
| 0.85 | Robot Harness | 디지털~물리 세계 프론티어 에이전트 인컨텍스트 학습(ICL) 통합 벤치마크 `ICLWorld` | [arXiv](https://arxiv.org/abs/2611.32649v1) |
| 0.84 | Long-Horizon | VLM 에이전트 추론 기반 원자 스킬 조합(`Atomic Policy`) & 전역 절차 사전(`RoboDemo`) | [arXiv](https://arxiv.org/abs/2611.32813v1) 외 1곳 |
| 0.82 | Embodied Memory | 파라미터 업데이트 없는 자가 검색 메모리(`MXI-MemICL`) & 서브태스크 키 메모리(`KeyMemVLA`) | [arXiv](https://arxiv.org/abs/2611.32564v1) 외 1곳 |
| 0.80 | Robot Harness | 플러그앤플레이 스킬 실행 인지 조율(`SkillHarness`) & 뉴로-심볼릭 안전·감사 계층 | [arXiv](https://arxiv.org/abs/2611.32186) 외 1곳 |
| 0.72 | RoboProbe | 거울 하나로 현재 로봇 조작 정책이 붕괴하는 시각적 취약점 진단(`Mirror Test`) | [arXiv](https://arxiv.org/abs/2611.33010v1) |

## 빅테크·연구 로보틱스 모델 실험
- [0.78] **NVIDIA Cosmos 3 Nano** · Hugging Face Diffusers를 활용해 GPU 메모리 제약이 있는 로컬 AI 디바이스에서 월드 모델 Cosmos 3 Nano를 구동하는 공식 가이드 공개 ([NVIDIA Blog](https://developer.nvidia.com/blog/how-to-run-nvidia-cosmos-3-on-local-ai-devices-using-hugging-face-diffusers)) · 공식
- [0.76] **DiffGR00T** · 휴머노이드 전신 제어(WBC)를 위한 실행 인지 미분 가능 VLA 학습 프레임워크 ([arXiv:2611.32665](https://arxiv.org/abs/2611.32665v1)) · 공식
- [0.58] **Figure AI** · 작업 현장에서 사람 팔 동작을 실시간 수집해 휴머노이드 학습·원격 제어에 활용하는 웨어러블 시스템 특허 출원 ([로봇신문](https://www.irobotnews.com/news/articleView.html?idxno=49793)) · 비공식

## 로봇 플랫폼 · 중국/글로벌 깃헙 & SDK
- [0.76] **Unitree** · MuJoCo 기반 공식 강화학습 프레임워크 `unitree_rl_mjlab` 활발한 업데이트 (★740, C++) ([GitHub](https://github.com/unitreerobotics/unitree_rl_mjlab)) · 공식
- [0.74] **I2RT · YAM** · YAM 로봇 암 공식 Python 제어 SDK `i2rt-robotics/i2rt` 최신 푸시 (★184) ([GitHub](https://github.com/i2rt-robotics/i2rt)) · 공식
- [0.72] **AgiBot (智元)** · 공식 시뮬레이션 플랫폼 `genie_sim`(★1,765) 및 텔레오퍼레이션·1인칭 캡처 인프라 `IsaacCapture` 업데이트 ([GitHub](https://github.com/AgibotTech/genie_sim)) · 공식
- [0.72] **Hugging Face × NVIDIA** · Isaac Lab + 차세대 물리 엔진 Newton 기반 Microduck 장애물 회피 Sim2Real 워크플로 공개 ([HF Blog](https://huggingface.co/blog/nvidia/microduck-obstacle-avoidance)) · 공식
- [0.70] **LimX Dynamics** · 휴머노이드 Python RL 배포(`humanoid-rl-deploy-python`, ONNX/MuJoCo) 및 TRON2 16종 시뮬 에셋 업데이트 ([GitHub](https://github.com/limxdynamics/humanoid-rl-deploy-python)) · 공식
- [0.68] **Booster Robotics** · 공식 C++ 제어 SDK `booster_robotics_sdk` 업데이트 (★123) ([GitHub](https://github.com/BoosterRobotics/booster_robotics_sdk)) · 공식

## 프론티어 모델·에이전트 트렌드 (20% 슬라이스)
- [0.74] **Gemini 4 Neon** · LiveBench에서 GPT-6 Astra·Claude Fable을 상회하고 TS/Rust 코드 벤치마크 실행 시간을 48.6% 단축 ([Latent Space](https://latent.space/p/ainews-gemini-4-neon-marks-gdm-s-full-return-as-a-frontier-lab)) · 비공식

## 트렌드 · 평소 대비
- 새로 등장: `robot-harness` (2건), `nvidia-groot` (2건)
- 분야 비중(7일): 로봇 하네스 41.2% · 플랫폼/SDK 35.3% · 빅테크 모델 실험 17.6% · 프론티어 AI(20% 슬라이스) 5.9%

## 내 키워드
### Unitree
- [0.94] `unitree_robotskills` — 프론티어 모델(GPT-6 Astra 등) 연결용 공식 로봇 스킬 프레임워크 ([GitHub](https://github.com/unitreerobotics/unitree_robotskills))
- [0.76] `unitree_rl_mjlab` 업데이트 (★740) ([GitHub](https://github.com/unitreerobotics/unitree_rl_mjlab))

### YAM
- [0.74] `i2rt-robotics/i2rt` 공식 Python SDK 최신 푸시 (★184) ([GitHub](https://github.com/i2rt-robotics/i2rt))

### training-free · long-horizon · VLA
- [0.88] `VLAs Execute, Code Recovers` ([arXiv](https://arxiv.org/abs/2611.32245v1))
- [0.82] `MXI-MemICL` 자가 검색 상호작용 메모리 ([arXiv](https://arxiv.org/abs/2611.32564v1))

## 소스 점검
- 전체 27개 활성 소스 수집 성공 (실패 0건)
- 제외(rejected) 이관: `physical_intelligence` (429 봇 차단), `hn_robotics_ai` (hnrss 502 → Algolia API `hn_algolia_robotics`로 대체)
- Google Workspace 발행: `config/settings.yaml`에 Apps Script Webhook URL 설정 시 자동 활성화
