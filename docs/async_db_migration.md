### 목적
기존 동기 SQLAlchemy/MySQL 접근을 비동기(`sqlalchemy.ext.asyncio` + `aiomysql`)로 전환하고, 전후 성능을 동일 조건에서 비교한다.

### 변경 요약
- `src/utils/db/db.py`
  - 동기 `Engine/Connection` → 비동기 `AsyncEngine/AsyncConnection`
  - 커넥션 의존성 `get_connection_db`를 `async` 제너레이터로 변경(트랜잭션 begin/commit/rollback 포함)
  - 드라이버: `mysql+aiomysql`
  - 풀 옵션: `pool_size=30`, `max_overflow=10`, `pool_recycle=300`
- `src/service/blog_svc.py`
  - 모든 서비스 메서드 `async def`로 전환, `await conn.execute(...)` 사용
- `src/router/blog.py`
  - FastAPI 핸들러에서 `AsyncConnection` 주입, 서비스 호출을 `await`로 변경
- `src/utils/bootstrap.py`
  - 애플리케이션 종료 시 `await db.engine.dispose()`로 리소스 정리
- `src/main.py`
  - 요청 처리시간 헤더 노출 미들웨어 추가: `X-Process-Time`
- `docker-compose.yml`
  - `DATABASE_URL` 예: `mysql+aiomysql://root:root1234$@db:3306/blog_db`

### 실행 방법
1) 컨테이너 기동(이 프로젝트는 항상 Docker Compose로 실행)
```bash
VOLUME_PATH=/usr/src/app docker compose up -d --build
```

2) (선택) 샘플 데이터 주입
```bash
docker exec -i blog_app-db-1 mysql -uroot -proot1234$ < initial_data.sql
```

3) 동작 확인 및 처리시간 헤더 확인
```bash
curl -s -D - http://localhost:8000/blogs/ -o /dev/null
# 응답 헤더에 X-Process-Time: <xx.xx>ms 확인
```

### 측정 방법(재현 가능)
- 도구: k6(Docker 이미지 사용)
- 시나리오: `/blogs/` GET, ramping VU, 최대 30 VU, 총 30초

1) 스크립트 작성
```bash
cat >/tmp/k6_read.js <<'EOF'
import http from 'k6/http';
import { sleep } from 'k6';
export const options = {
  scenarios: {
    ramp: { executor: 'ramping-vus', stages: [
      { duration: '5s', target: 1 },
      { duration: '20s', target: 30 },
      { duration: '5s', target: 0 },
    ] }
  },
  thresholds: { http_req_failed: ['rate<0.01'] },
};
export default function () {
  http.get('http://app:8000/blogs/');
  sleep(0.1);
}
EOF
```

2) 실행(Compose 네트워크에서 앱 호스트명은 `app`)
```bash
docker run --rm --network blog_app_default -v /tmp/k6_read.js:/test.js grafana/k6 run /test.js
```

### 측정 결과(동일 조건, 30 VU, 30s)
- 변경 전(동기 DB)
  - http_req_duration: avg 30.56ms, p90 40.61ms, p95 42.98ms, max 64.47ms
  - 처리량: 96.7 req/s
  - 실패율: 0.00%
- 변경 후(비동기 DB)
  - http_req_duration: avg 30.43ms, p90 41.96ms, p95 44.98ms, max 66.99ms
  - 처리량: 96.8 req/s
  - 실패율: 0.00%

요약: 테스트 조건(읽기 중심, 30 VU)에서는 전후 차이가 미미함. 현재 워크로드에서는 DB I/O가 주요 병목이 아니며, 템플릿 렌더링/네트워크 I/O 등이 지배적일 수 있음.

### 리소스 스냅샷(참고)
```text
app: 0.23% CPU / 84.8MiB
db : 0.70% CPU / 422.4MiB
```

### 다음 단계 제안
- 동시성 상향으로 tail-latency 관찰: 100/200 VU에서 p95/p99 변화 확인
- 쓰기 경로 포함 시나리오(POST `/blogs/new`, 이미지 업로드 포함)
- 남은 동기 I/O 비동기화: `ImageManager.save_image`를 `aiofiles` 또는 `asyncio.to_thread`로 오프로딩
- 쿼리 시간 로깅 도입: 서비스 레이어에서 `time.perf_counter()`로 SQL 실행 시간을 로그로 기록

### k6란? (부하 테스트 도구)
- **정의**: k6는 Go로 구현된 오픈소스 성능/내구성 테스트 도구로, 테스트를 **JavaScript**로 작성해 CLI로 실행한다. HTTP(주), WebSocket/gRPC도 지원하며, 로컬/CI/Docker 환경에서 headless로 실행 가능.
- **사용 목적**: API의 지연시간 분포(p50/p95/p99), 처리량(RPS), 실패율 등을 다양한 동시 사용자 패턴으로 재현·측정·검증.

### 작동 원리(핵심 개념)
- **VU(Virtual User)**: 가상의 사용자. 각 VU는 `default` 함수를 반복(루프) 실행하며 요청을 발생시킨다.
- **Iteration**: `default` 함수 1회 실행을 1 iteration으로 집계.
- **Scenario/Executor**: 동시성·부하 패턴을 정의. 예) `ramping-vus`(VU 수를 단계적으로 증감), `constant-arrival-rate`(초당 요청 도착률 유지) 등.
- **Pacing**: `sleep()`을 사용해 각 iteration 간 간격을 제어(과도한 폭주 방지, 현실적인 think time 반영).
- **Thresholds**: SLO 형태의 합격 기준. 예) `http_req_failed: ['rate<0.01']`, `http_req_duration: ['p(95)<200']`.
- **Checks**: 개별 응답 조건 검증(상태코드/본문 등). 통과율이 보고된다.
- **메트릭/태그**: 요청에 태그를 부여해 메트릭을 그룹화·필터링할 수 있다.

### 주요 메트릭 해설(요약)
- **http_req_duration**: 요청 시작→응답 완료까지 총 시간. p50/95/99 백분위가 핵심 지표.
- **http_req_failed**: 실패율(비-2xx/3xx 또는 예외). `rate`로 보고.
- **http_reqs**: 총 요청 수(=RPS 계산 근거). 실행 시간으로 나눠 초당 요청수 추정.
- **iteration_duration**: `default` 함수 1회 수행 시간(think time 포함).
- **vus / vus_max**: 현재/최대 동시 가상 사용자 수.

### Docker로 실행하는 법(이 프로젝트 기준)
- Compose 네트워크에서 앱 호스트명은 `app` 이다. 즉, 스크립트 내 URL은 `http://app:8000/...`를 사용한다.
- 실행 예시:
```bash
docker run --rm --network blog_app_default -v /tmp/k6_read.js:/test.js grafana/k6 run /test.js
```

### 간단 스크립트 예시
```javascript
import http from 'k6/http';
import { sleep, check } from 'k6';
export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-vus',
      stages: [
        { duration: '5s', target: 1 },
        { duration: '20s', target: 30 },
        { duration: '5s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<200'],
  },
};
export default function () {
  const res = http.get('http://app:8000/blogs/');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(0.1);
}
```

### 쓰기 경로(이미지 업로드 포함) 부하 스크립트
- 목적: POST `/blogs/new` 경로에 대해 멀티파트 업로드를 포함한 쓰기 부하를 재현
- 주의: 이미지 파일이 컨테이너의 볼륨 경로에 저장되므로 디스크 사용량이 증가할 수 있음

1) 테스트 이미지(1x1 PNG) 생성
```bash
cat >/tmp/test.png.base64 <<'EOF'
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAuMBgudGgOIA
AAAASUVORK5CYII=
EOF
base64 -d /tmp/test.png.base64 >/tmp/test.png
```

2) k6 스크립트 작성(쓰기)
```bash
cat >/tmp/k6_write.js <<'EOF'
import http from 'k6/http';
import { sleep, check } from 'k6';

// 컨테이너 내부 경로에 마운트된 테스트 이미지 로드
const img = open('/data/test.png', 'b');

export const options = {
  scenarios: {
    write: {
      executor: 'ramping-vus',
      stages: [
        { duration: '5s', target: 1 },
        { duration: '20s', target: 10 },
        { duration: '5s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const payload = {
    title: `k6 post ${__VU}-${__ITER}`,
    author: `k6-vu${__VU}`,
    content: 'performance test content from k6',
    image_file: http.file(img, 'test.png', 'image/png'),
  };
  const res = http.post('http://app:8000/blogs/new', payload);
  check(res, { 'redirect 303': (r) => r.status === 303 });
  sleep(0.2);
}
EOF
```

3) 실행(이미지와 스크립트를 컨테이너에 마운트)
```bash
docker run --rm --network blog_app_default \
  -v /tmp/k6_write.js:/test.js \
  -v /tmp/test.png:/data/test.png \
  grafana/k6 run /test.js
```

4) 참고: 결과 해석 포인트
- 쓰기 경로는 DB INSERT와 파일 저장 I/O가 포함되어 읽기 대비 지연시간이 높을 수 있음
- 전환 효과 평가는 p95/p99, 실패율, 처리량 변화로 확인


