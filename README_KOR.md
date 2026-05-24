# G-BungE Log Analysis

영문 문서는 [README.md](README.md)를 참고하세요.

## 프로젝트 개요

이 레포지토리는 GIST 자작 전기차 팀 G-BungE의 Baja EV Mk.4 주행 로그를 Python으로 파싱하고, GPS / 토크 / 모터 제어 / 전력 / 열 / 냉각 데이터를 분석하기 위한 도구입니다.

Mk.4 차량에서 저장된 binary log와 CAN 데이터를 읽어 `VehicleLog` 형태로 정리하고, 실제 주행 중 발생한 토크 응답, RPM 변화, Id/Iq 전류, 약계자 제어, 전력 흐름, 모터 온도, 냉각 경향, GPS 궤적 등을 그래프로 확인할 수 있게 구성했습니다.

기존 MATLAB 스크립트는 `MatLab/` 폴더에 참고용으로 남겨 두었고, 현재 반복 분석의 중심은 Python CLI와 대화형 메뉴입니다.

## 개발 배경

기존에는 로그를 확인할 때 MATLAB 기반 스크립트나 수동 실행 방식에 의존하는 부분이 컸고, 분석할 그래프를 바꿀 때마다 코드를 직접 수정해야 하는 불편함이 있었습니다. 이 프로젝트는 로그 그룹과 파일, 분석 항목을 CLI 또는 대화형 메뉴에서 선택할 수 있게 하여 반복 분석을 더 빠르고 일관되게 만드는 것을 목표로 합니다.

Mk.4 테스트와 경기 주행에서는 저속 고부하 구간, 모터/인버터 발열, 출력 저하, 토크 제한, GPS 튐, CAN 데이터 누락 등을 빠르게 확인해야 했습니다. 따라서 단순히 그래프를 그리는 것보다, 여러 로그를 같은 방식으로 반복 실행하고 비교할 수 있는 workflow가 중요했습니다.

## 주요 기능

- binary vehicle log 파싱
- `Logs/<그룹>/<파일명>.log` 구조 기반 로그 선택
- 여러 개로 나뉜 split-session 로그를 순서대로 이어서 로딩
- CLI 명령과 대화형 메뉴 지원
- GPS 궤적, 속도, slip ratio, g-force, 랩 분할 분석
- 토크 명령/실측 토크, RPM, T-N envelope 분석
- Id/Iq, vector control, field weakening, motor-control constraint 분석
- 배터리 전류, 전력, moving RMS, current-efficiency 분석
- 모터 온도, 온도 상승률, thermal lag, cooling trend regression 분석
- sparse log에서 `NaN` / infinite 값 필터링 후 보간, 회귀, binning 수행
- 분석 함수의 bin width, window length, threshold 등을 call site에서 조정 가능

## 분석 항목

### Core / GPS

- `gps-only`: GPS 주행 궤적 확인
- `gps-velocity-and-slip`: GPS 속도와 slip ratio 확인
- `gps-gforce-map`: GPS 기반 g-force 경향 확인
- `split-laps`: GPS 기준 랩 분할
- `laps-slideshow`: 랩별 주행 궤적 확인

### Torque / Motor Control

- `torque-performance`: 토크 명령값, 실제 토크, RPM 비교
- `vector-control`: Id/Iq 전류와 DC link 전압 확인
- `field-weakening`: 고속 구간 약계자 제어 여부 확인
- `advanced-id-iq-analysis`: Id-Iq 운전점 분포 확인
- `id-iq-vs-rpm`: RPM별 Id/Iq 경향 확인
- `auto-field-weakening-trend`: RPM별 약계자 전류 추세 확인
- `torque-vs-iq`: Iq 대비 실제 토크 관계 확인
- `motor-control-constraints`: 전류/전압 제한과 운전점 비교
- `torque-vs-temperature`: 온도에 따른 토크 변화 확인
- `tn-curve-envelope`: RPM별 토크 상한 경향 확인

### Power / Efficiency

- `power-and-temp`: 입력 전력과 모터 온도 비교
- `moving-rms`: 이동 RMS 기반 전력/전류 경향 확인
- `power-vs-rpm`: RPM별 출력 경향 확인
- `power-flow`: 배터리 전류 흐름 확인
- `current-efficiency`: 배터리 전류와 상전류 관계 확인

### Thermal / Cooling

- `temperature-profile`: 모터 온도 시간 그래프
- `power-vs-temp-slope`: 입력 전력과 온도 상승률 관계 확인
- `cooling-trend-regression`: 저부하 구간에서 냉각 경향 회귀
- `thermal-lag`: 전력 입력과 온도 반응 사이 지연 확인
- `cooling-trend-high-temp`: 고온 저부하 조건의 냉각 속도 확인

### Vehicle Dynamics

- `vehicle-dynamics-mv-avg`: 이동 평균 기반 가속도/G-G 경향 확인

## CAN 데이터 매핑

현재 parser는 2025 Mk.4 로그 포맷을 기준으로 작성되어 있습니다.

| Source | Key | 데이터 |
| --- | --- | --- |
| 1 | 0x0A | 실제 토크, 실제 전류, 속도/RPM |
| 1 | 0x0B | Ud, Uq, Vmod, Vcap |
| 1 | 0x0C | L, Vlim, Iflux, Iqmax |
| 1 | 0x0D | 모터 온도, 배터리 전류, 토크 명령, 실제 토크 |
| 1 | 0x0E | Vtgt, Id, Iq |
| 5 | - | 가속도계 |
| 6 | 0 | GPS 위치 |
| 6 | 1 | GPS 속도와 course |
| 6 | 2 | GPS time |

## 설치 방법

macOS / Linux:

```bash
python3 -m pip install -r requirements.txt
```

Windows:

```powershell
py -m pip install -r requirements.txt
```

`py` 명령이 없다면 다음처럼 실행할 수 있습니다.

```powershell
python -m pip install -r requirements.txt
```

## 실행 방법

대화형 메뉴:

```bash
python3 main.py
```

실행 권한이 설정되어 있다면:

```bash
./main.py
```

Windows:

```powershell
py main.py
```

대화형 메뉴에서는 다음 순서로 선택합니다.

1. 로그 그룹 선택
2. 로그 파일 선택
3. 실행할 분석 항목 선택

번호 입력은 `1`, `1,4,7`, `3-6`, `all` 형식을 지원합니다.

## CLI 사용 예시

도움말 확인:

```bash
python3 main.py --help
```

사용 가능한 로그 목록 확인:

```bash
python3 main.py --list-logs
```

사용 가능한 분석 항목 확인:

```bash
python3 main.py --list-plots
```

하나의 로그에서 GPS 궤적만 확인:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" \
  --plot gps-only
```

같은 로그에 여러 분석을 연속 실행:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" \
  --plot torque-performance \
  --plot vector-control \
  --plot power-and-temp
```

이어진 주행 세션을 여러 로그 파일로 합쳐 분석:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" "2025-08-17 05-44-54.log" \
  --plot torque-performance \
  --plot vector-control
```

선택한 로그가 없으면 즉시 실패하도록 실행:

```bash
python3 main.py \
  --group "Main Competition" \
  --log "2025-08-30 08-32-10.log" \
  --plot temperature-profile \
  --strict
```

## 로그 파일 구조

기본 로그 위치는 다음과 같습니다.

```text
Logs/<로그 그룹>/<timestamp>.log
```

예시:

```text
Logs/2nd Test Week/2025-08-17 05-31-36.log
Logs/Main Competition/2025-08-30 08-32-10.log
```

`--group`에는 `Logs/` 아래의 폴더 이름을 넣고, `--log`에는 해당 그룹 안의 파일 이름을 넣습니다. 절대 경로를 직접 넘기는 것도 가능합니다.

한 주행 세션이 여러 `.log` 파일로 나뉘어 저장된 경우, `--log` 뒤에 시간 순서대로 파일을 나열해야 합니다.

## 실무상 주의점

- NaN은 실제 물리값이 아니라 해당 시점에 신호가 없었거나 파싱되지 않았거나 CAN 데이터가 수신되지 않았음을 의미합니다.
- sparse log에서는 특정 신호가 모든 timestamp에 존재하지 않을 수 있습니다.
- 온도/냉각 분석은 유효하지 않은 값과 샘플 수가 부족한 구간을 제외하고 계산합니다.
- 로그 포맷이나 CAN key가 바뀌면 `logFetcher.py`의 mapping도 함께 확인해야 합니다.
- 일부 단위와 scaling은 현재 Mk.4 logger 포맷을 기준으로 하므로, firmware 변경 시 재검증이 필요합니다.

## 분석 파라미터 조정 방법

일부 분석 함수는 다음과 같은 값을 인자로 받을 수 있습니다.

- RPM bin width
- Iq bin width
- minimum samples per bin
- current limit
- field-weakening threshold
- thermal window length
- cooling regression 조건

특정 주행 로그에 맞게 기준을 바꾸고 싶다면, 가능하면 `logPostProcessor.py`의 함수 자체를 바꾸기보다 `main.py`에서 해당 분석 함수를 호출하는 부분의 인자를 조정하는 방식이 좋습니다. 이렇게 하면 같은 분석 함수를 여러 세션에 재사용하기 쉽습니다.

예시:

```python
visualizer.plot_id_iq_vs_rpm(
    rpm_bin_width=100.0,
    min_samples_per_bin=10,
    current_limit=None,
)
```

sparse log에서는 bin width를 넓히거나 minimum sample count를 낮추면 더 많은 구간을 볼 수 있습니다.

## 나의 기여

- MATLAB 중심의 수동 분석 흐름을 Python CLI / 대화형 메뉴 기반 workflow로 정리했습니다.
- 테스트 주간과 본선 로그처럼 로그 그룹이 나뉜 구조를 선택할 수 있게 구성했습니다.
- 여러 파일로 나뉜 주행 세션을 순서대로 로딩해 하나의 세션처럼 분석할 수 있게 정리했습니다.
- GPS, 토크, 모터 제어, 전력, 열, 냉각, 차량 동역학 관련 분석 항목을 추가하거나 메뉴 구조로 정리했습니다.
- 보간, 회귀, binning 전에 `NaN` / infinite / sparse signal을 방어적으로 처리하도록 정리했습니다.
- CAN 데이터 mapping과 실제 분석 시 필요한 가정, 주의점을 문서화했습니다.

## 향후 개선 계획

- README에 실제 분석 plot 이미지 추가
- parser, analysis, visualization module을 더 명확히 분리
- binary parsing과 CAN field mapping에 대한 테스트 추가
- 공개 가능한 anonymized sample log 또는 synthetic log generator 추가
- 분석 결과를 CSV/Markdown summary로 export

추가 설명은 [docs/analysis_notes.md](docs/analysis_notes.md)와 [docs/future_work.md](docs/future_work.md)를 참고하세요.
