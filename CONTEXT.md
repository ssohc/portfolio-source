# 포트폴리오 작업 인수인계

다른 컴퓨터나 새 대화에서 이어서 작업할 때, 이 문서를 먼저 읽으면 됩니다.

## 결과물 주소

- 공개 사이트: https://ssohc.github.io/resume/ (저장소 `ssohc/resume`, 빌드 결과물만)
- 미리보기 아티팩트: https://claude.ai/artifact/XH3eCD8amHFGUwzKoJ3gEC
- 피그마 덱 V9: fileKey `nDXYkWYMCVjfl0gyLrfuEZ` (Slides)

## 이 저장소 구성

| 파일 | 설명 |
|---|---|
| `portfolio.html` | 사이트 원본. 내용 수정은 전부 여기서 한다 |
| `build_locked.py` | 암호화 빌드 스크립트 |
| `assets/` | 화면 이미지(webp), 프로필, 이력서·포트폴리오 PDF 원본 |

`locked.html`, `site/`, `assets/*.txt`는 빌드 산출물이라 커밋하지 않는다.

## 수정하고 배포하는 방법

```bash
# 1. portfolio.html 수정

# 2. 빌드 (비밀번호는 환경변수로만 전달, 파일에 저장 금지)
PORTFOLIO_PW='비밀번호' python3 build_locked.py

# 3. 배포용 저장소로 복사 후 푸시
cp site/index.html ~/Documents/portfolio-site/index.html
cp site/assets/*.txt ~/Documents/portfolio-site/assets/
cd ~/Documents/portfolio-site && git add -A && git commit -m "내용 수정" && git push
```

`build_locked.py`는 두 가지를 만든다.

- `locked.html` 아티팩트용 (head 없음, 플랫폼이 붙여줌)
- `site/index.html` 깃허브 페이지용 (완전한 HTML 문서)

의존성: `pymupdf`, `cryptography`, `pillow`, `numpy`

## 사이트 구조

```
상단 고정 네비 (About / Career / Work / Contact)
히어로
ABOUT      일하는 방식 + STEP 01~03 + TOOLS + EDUCATION
           ABOUT 라벨 오른쪽에 이력서·포트폴리오 다운로드 버튼 2개
CAREER     연도별 타임라인 5개사
WORK       회사 탭 전환 (한 번에 한 카드, 맨 오른쪽 '전체' 탭)
CONTACT    이메일 + 클립보드 복사 버튼 + 브런치 링크
```

커리어벗 카드 구성

```
TEAM LEADING
─────────────
협업 체계 구축         PROBLEM / SOLUTION / OUTCOME   (전문)
─────────────
상품·결제 구조 단순화   두 문단                        (요약)
```

상품·결제는 웹에서 짧게 두고, 피그마 덱에서 상세하게 다룬다.

## 비밀번호 잠금 방식

페이지 본문과 이미지를 AES-GCM으로 암호화하고, 비밀번호에서 PBKDF2(25만 회)로 키를 만든다. 비밀번호는 어디에도 저장하지 않는다. PDF 두 개는 같은 키로 따로 암호화해 `assets/*.pdf.txt`(base64)로 올리고, 버튼을 누르면 받아서 복호화한다.

`.enc` 확장자는 아티팩트가 서빙하지 않아 `.txt`를 쓴다.

## 글쓰기 규칙 (지켜야 함)

- 대시(—) 금지
- `운영`이라는 표현으로 본인 역할을 설명하지 않는다. 운영기획은 별도 직무다
- 금액, 할인율, 패키지 상품명은 전부 가린다
- 진행 중인 업무는 넣지 않는다. 완료된 것만
- 팀원이 한 일을 본인이 한 것처럼 쓰지 않는다. 기여 범위를 밝힌다
- 과정 서술("검토받았다", "보고해서 승인됐다")보다 무엇이 바뀌었는지를 쓴다
- 당연한 절차를 성과처럼 쓰지 않는다
- 웍스피어를 잡코리아로 쓰지 않는다

## 남은 작업

### 피그마 덱 (V9)

3페이지가 커리어벗 표지다. Starter 요금제 MCP 호출 한도에 걸려 중단됐다.

1. 3페이지 표지 수정
   - 타이틀: `포털기획팀 리딩과 전사 협업 프로세스 정의`
   - PROJECT 문단 교체
   - 태그에서 `#로드맵 운영` 빼고 `#상품·결제 정책` 추가
   - CONTRIBUTION에 `상품·결제 정책 설계 (100%)` 추가
   - WORK PROCESS 6단계를 AS-IS / TO-BE 대비로 교체
   - PROJECT GOALS에서 `운영` 제거
2. 4페이지 신규: 협업 체계 구축 (PROBLEM / EXECUTION 3단계 / OUTCOME 카드 4개)
3. 5페이지 신규: 상품·결제 구조 단순화 (PROBLEM / AS-IS→TO-BE / EXECUTION 4단계 / OUTCOME 카드 3개)

문구 전문은 대화에 정리해뒀고, 사이트의 커리어벗 카드와 이력서 커리어벗 항목을 합친 내용이다.

### 확인 필요

- 로그아웃 상태에서 깃허브 페이지 다운로드 버튼이 실제로 동작하는지
- 나머지 네 카드(에딧메이트·마켓보로·플랫비·웍스피어)를 이력서 밀도에 맞출지
- 가설·인사이트 블록을 다섯 카드 전부에 넣을지

## 이력서와의 관계

이력서 PDF(`assets/resume.pdf`)가 내용의 기준이다. 사이트 문구는 여기서 파생됐다. 이력서를 고치면 사이트도 같이 본다.

이력서에는 있고 사이트에는 아직 없는 것: 가설·검증·인사이트 블록, 에딧메이트의 "대화 로그를 정량화해 우선순위 도출" 과정.
