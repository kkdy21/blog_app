create database if not exists blog_db;

use blog_db;

drop table if exists blog;

create table blog (
    id integer primary key auto_increment,
    title varchar(200) not null,
    author varchar(100) not null,
    content varchar(4000) not null,
    image_loc varchar(300) null,
    modified_dt datetime not null
);

-- truncate는 테이블의 모든 데이터를 빠르게 삭제하는 SQL 명령어입니다.
truncate table blog;

insert into
    blog (
        title,
        author,
        content,
        modified_dt
    )
values (
        'FastAPI 비동기 프로그래밍: async/await 완전 정복',
        '코어 개발자',
        'FastAPI의 가장 큰 장점 중 하나는 네이티브 비동기 지원입니다. \n`async`와 `await` 키워드를 사용하면, 데이터베이스 쿼리나 외부 API 호출처럼 I/O 작업이 많은 환경에서 논블로킹(non-blocking) 방식으로 코드를 실행하여 월등히 높은 처리량을 달성할 수 있습니다. \n하나의 요청을 기다리는 동안 다른 요청을 처리할 수 있어 서버 자원을 효율적으로 사용합니다. \n별도의 작업이나 라이브러리 없이 경로 작동 함수를 `async def`로 선언하기만 하면 FastAPI가 알아서 비동기적으로 처리해주므로, 고성능 웹 애플리케이션을 놀랍도록 쉽게 만들 수 있습니다.',
        NOW()
    );

insert into
    blog (
        title,
        author,
        content,
        modified_dt
    )
values (
        'Pydantic으로 FastAPI 데이터 유효성 검사 마스터하기',
        '데이터 마스터',
        'FastAPI는 Pydantic 라이브러리를 통해 강력하고 사용하기 쉬운 데이터 유효성 검사를 제공합니다.\n단순히 데이터 타입을 선언하는 것만으로 요청 본문(request body)의 JSON 데이터를 파싱하고, 타입이 맞는지, 필수 필드가 누락되지 않았는지 자동으로 검증합니다.\n또한, Pydantic 모델을 응답 모델(response_model)로 지정하면 출력 데이터의 구조와 타입을 보장하고, 민감한 정보가 외부로 노출되는 것을 방지할 수 있습니다. \n복잡한 중첩 JSON 구조나 상세한 유효성 검사 규칙도 손쉽게 정의할 수 있어 API의 안정성을 크게 향상시킵니다.',
        NOW()
    );

insert into
    blog (
        title,
        author,
        content,
        modified_dt
    )
values (
        'FastAPI 의존성 주입(Dependency Injection)의 모든 것',
        '클린 코더',
        '의존성 주입(DI)은 FastAPI의 코드 재사용성과 모듈화를 극대화하는 핵심 기능입니다.\n`Depends`를 사용하면 데이터베이스 세션, 인증/인가 로직, 공통 파라미터 등 반복적으로 사용되는 로직을 별도의 함수로 분리하고, 필요한 경로 작동 함수에서 선언적으로 주입받아 사용할 수 있습니다.\n이를 통해 코드 중복을 줄이고, 각 컴포넌트의 역할을 명확하게 분리하여 테스트하기 쉬운 코드를 작성할 수 있습니다.\n계층적인 의존성을 생성하여 복잡한 시스템도 체계적으로 관리할 수 있게 해주는 강력한 도구입니다.',
        NOW()
    );

COMMIT;

/* connection 모니터링 스크립트. root로 수행 필요. */
select * from sys.session where db='blog_db' order by conn_id;

create table user
(
    id integer auto_increment primary key,
    name varchar(100) not null,
    email varchar(100) not null unique,
    hashed_password varchar(200) not null,
    created_at datetime not null,
);
