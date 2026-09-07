# 네이버 웹툰 유료화 전환 작품 — 관심수 · 별점

네이버 웹툰 공지 게시판에서 **“유료화”로 검색한 가장 최신 공지**를 열어,
거기 적힌 작품들의 **관심수**와 **별점**을 한 번에 보여줍니다.
관심수 **100,000 이상**은 핑크색으로 표시합니다.

두 가지 방법으로 쓸 수 있습니다.

| 방법 | 실행 | 특징 |
|---|---|---|
| 바탕화면 스크립트 | `유료화_관심수_확인.bat` 더블클릭 | 콘솔에 바로. 항상 실시간 |
| 웹사이트 | 깃허브 페이지 주소 접속 → **[지금 불러오기]** | 어디서나. 아래 설정 필요 |

---

## 무엇을 어떻게 읽어오나

1. `api/notice/list?searchWord=유료화&page=1` — 공지 목록의 **가장 위 글**(최신)
2. `api/notice/detail?noticeId=…` — 그 공지 본문에서 `1. 작품명` 꼴의 줄을 순서대로 추출
3. `api/search/all?keyword=작품명` — 작품 검색 → `titleId`
4. `api/article/list/info?titleId=…` — **관심수**(`favoriteCount`)
5. `api/article/list?titleId=…&page=1&sort=DESC` — **별점**(`starScore`)

### 알아둘 점

- **별점은 작품 단위 값이 네이버 API에 없습니다.** 그래서 회차 별점을 씁니다.
  `별점` = 최신 회차 점수, `최근 20화 평균` = 최신 20개 회차 평균.
- **공지 링크가 틀린 경우가 있습니다.** (2026년 9월 공지에서 “회귀자는 나만 지킨다”의
  링크가 다른 작품 “ZD”를 가리켰습니다.) 링크로 받은 작품명이 공지에 적힌 이름과 다르면
  **이름으로 다시 검색해 바로잡고**, 표에 그 사실을 적어 둡니다.
- **성인 작품은 관심수·별점이 안 나올 수 있습니다.** 로그인이 필요해서이고, `–` 로 표시됩니다.

---

## 웹사이트(깃허브 페이지) 올리는 방법

### 0. 준비

깃허브 계정이 필요합니다. `git`은 이미 깔려 있습니다(`git --version`으로 확인).

### 1. 깃허브에 빈 저장소 만들기

<https://github.com/new> 에서

- **Repository name**: `naver-webtoon-paid` (원하는 이름으로)
- **Public** 선택 — 무료 계정은 Public 이어야 깃허브 페이지가 켜집니다
- **Add a README / .gitignore / license 는 모두 체크 해제** (이미 여기 있습니다)
- **Create repository**

### 2. 올리기

`깃허브_올리기.bat` 을 더블클릭하면 사용자명·저장소 이름·이메일을 물어보고 알아서 올립니다.
처음 올릴 때 브라우저로 깃허브 로그인 창이 한 번 뜹니다.

직접 하려면 이 폴더에서:

```bash
git init
git config user.name  "깃허브사용자명"
git config user.email "깃허브에등록된메일"
git add .
git commit -m "네이버 웹툰 유료화 전환 작품 관심수/별점"
git branch -M main
git remote add origin https://github.com/사용자명/naver-webtoon-paid.git
git push -u origin main
```

### 3. 깃허브 페이지 켜기

저장소 → **Settings** → 왼쪽 **Pages**

- **Source**: `Deploy from a branch`
- **Branch**: `main` / 폴더는 **`/docs`** 선택 → **Save**

1~2분 뒤 주소가 나옵니다:

```
https://사용자명.github.io/naver-webtoon-paid/
```

### 4. 자동 갱신 켜기 (선택)

`.github/workflows/update.yml` 이 **매일 오전 9시 10분(한국시간)** 에 자료를 새로 받아
`docs/data.json` 을 갱신합니다. 그 커밋이 되려면 권한을 한 번 열어줘야 합니다.

저장소 → **Settings** → **Actions** → **General** →
맨 아래 **Workflow permissions** → **Read and write permissions** → **Save**

바로 한 번 돌려보려면 **Actions** 탭 → 왼쪽 `유료화 공지 자료 갱신` → **Run workflow**.

---

## 웹사이트가 동작하는 방식

깃허브 페이지는 정적 호스팅이라 서버가 없고, 네이버 API 는 **CORS 를 열어주지 않습니다.**
그래서 브라우저에서 `comic.naver.com` 을 직접 부르면 막힙니다. 두 갈래로 처리했습니다.

- **[지금 불러오기]** (실시간 조회 체크됨) — 공개 CORS 프록시를 거쳐 그 자리에서 조회합니다.
  프록시는 남의 무료 서비스라 가끔 죽거나 횟수 제한이 걸립니다. 여러 개를 차례로 시도하고,
  전부 실패하면 아래 저장본으로 자동으로 넘어갑니다.
- **저장본** — GitHub Actions 가 매일 만들어 둔 `docs/data.json`. 프록시와 무관하게 항상 뜹니다.
  페이지를 열면 이것부터 먼저 보여줍니다.

프록시가 계속 말썽이면 “실시간으로 새로 조회” 체크를 끄고 저장본만 쓰면 됩니다.
그 대신 자료는 하루 한 번 갱신됩니다.

주소 끝에 **`#auto`** 를 붙여 두면 (`…github.io/naver-webtoon-paid/#auto`)
페이지를 여는 즉시 버튼을 누른 것처럼 실시간 조회까지 알아서 합니다. 즐겨찾기에 그렇게 넣어 두면 편합니다.

---

## 파일 구성

```
유료화_관심수_확인.bat    콘솔로 바로 보기 (실시간)
사이트_미리보기.bat       올리기 전에 로컬에서 사이트 확인 (localhost:8765)
깃허브_올리기.bat         깃허브 저장소로 올리는 도우미
scripts/
  naver_paid_core.py     공지 파싱 + 관심수·별점 조회 (공용)
  run_console.py         콘솔 출력 (핑크색 표시)
  build_data.py          docs/data.json 생성
docs/                    ← 깃허브 페이지가 이 폴더를 그대로 서비스
  index.html             사이트 본체
  data.json              저장본 (Actions 가 갱신)
.github/workflows/
  update.yml             매일 자동 갱신
```

기준값을 바꾸려면 `scripts/naver_paid_core.py` 의 `THRESHOLD` 와
`docs/index.html` 의 `THRESHOLD` 를 같이 고칩니다.
공지 검색어는 `SEARCH_WORD` 입니다.
