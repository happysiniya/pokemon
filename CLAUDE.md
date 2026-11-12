# 우리 아이 포켓몬 도감

7살 아이가 혼자 포켓몬 그림을 보고, 울음소리를 듣고, 이름을 찾아보는 한국어 도감 웹앱이에요.
빌드 도구나 프레임워크 없이 정적 파일만으로 동작해요.

## 누가, 어디서 쓰나요
- **사용자:** 7살 아이. 글을 아직 잘 못 읽을 수 있어요.
  - 큰 글씨와 큰 버튼을 쓰고, 그림·소리 위주로 만들어요.
  - 화면 문구는 쉬운 한국어로 써요.
- **기기:** 안드로이드 태블릿의 Chrome에서 **"앱 설치"(PWA)**로 깔아서 써요.
  - 세로와 가로 화면 모두 고려해요.
  - "홈 화면에 추가"는 바로가기만 만들어서 아이콘이 'G'로 보였어요. 설치를 안내할 때는 항상 **"앱 설치"**라고 말해요.
- **배포:** GitHub Pages (`https://happysiniya.github.io/pokemon/`).
  - 저장소: https://github.com/happysiniya/pokemon (Public, `main` 브랜치 루트에서 Pages 배포)
  - PC 폴더 `c:\Users\KJS\Desktop\dev\pockemon`이 이 저장소와 **git으로 연결**돼 있어요 (`origin/main` 추적).
  - `git push`하면 1~2분 뒤 사이트에 반영돼요. 인증은 Windows Git Credential Manager가 처리해요.
  - `gh` CLI는 설치돼 있지 않아요.
  - 예전에는 github.com 웹 화면에서 파일을 끌어다 놓아 올렸어요. 지금도 그 방법을 쓸 수 있어요.

## 파일
| 파일 | 역할 | GitHub에 올리기 |
|---|---|---|
| `index.html` | 화면 전부 (HTML, CSS, JS 한 파일) | ✅ |
| `pokemon-data.js` | `const POKEMON = [...]` 한국어 포켓몬 데이터 (1025마리, 1~9세대) + `const MEGA = [...]` 메가진화 97개 | ✅ |
| `manifest.json` | PWA 앱 정보 (이름, 아이콘, 전체 화면) | ✅ |
| `sw.js` | 서비스 워커: 화면은 네트워크 우선, 포켓몬 그림은 캐시 우선. 울음소리는 캐시하지 않음 | ✅ |
| `icon-192.png`, `icon-512.png` | 포켓볼 앱 아이콘 (maskable 여백 포함) | ✅ |
| `tools/build-data.py` | PokeAPI CSV로 `pokemon-data.js`를 다시 만드는 스크립트 | 선택 (사이트 동작과 무관) |
| `CLAUDE.md` | 이 문서 | 선택 (사이트 동작과 무관) |

## 데이터와 외부 자원
- **데이터:** [PokeAPI](https://pokeapi.co) CSV (`github.com/PokeAPI/pokeapi` 저장소의 `data/v2/csv`).
  - 한국어는 `language_id = 3`이에요.
  - 각 포켓몬 필드:
    - `id`: 번호
    - `n`: 이름
    - `g`: 분류
    - `gen`: 세대
    - `t`: 타입 배열
    - `from`: 진화 전 번호
    - `ch`: 진화 계열 번호
    - `leg`: 0 일반, 1 전설, 2 환상
    - `d`: 도감 설명. 8·9세대 127마리는 비어 있어요.
  - 메가진화 `MEGA` 필드: `id`(10000번대 그림·울음소리 번호), `b`(원래 포켓몬 번호), `n`(이름), `t`(메가진화 후 타입).
    - `pokemon_forms.csv`의 `is_mega = 1`에서 뽑아요. 한국어 이름은 `pokemon_form_names.csv`(키는 form id)에 있어요.
    - 레전드 Z-A 메가진화(10278번~)는 한국어 이름이 아직 없어서 "메가" + 원래 이름 + X/Y/Z(+모습 이름)으로 만들어요.
    - 일부 메가진화는 색이 다른 모습(shiny) 그림이 없어요. 그림을 못 불러오면 원래 그림으로 돌아가요.
  - GraphQL API(beta.pokeapi.co)는 401 오류가 나서 쓸 수 없어요. CSV를 써요.
- **그림:** `raw.githubusercontent.com/PokeAPI/sprites/.../official-artwork/{id}.png`
  - 색이 다른 모습은 `.../shiny/{id}.png`
  - `<img crossorigin="anonymous">`로 불러와요. CORS 응답이 opaque면 캐시 용량을 많이 잡아먹기 때문이에요.
- **울음소리:** `raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{id}.ogg`
  - 실패하면 `legacy/`를 써요.
- **나무위키:** 상세 화면에 `https://namu.wiki/w/{이름}` 링크만 둬요. 크롤링하지 않아요.
- **폰트:** Google Fonts "Jua". 실패하면 맑은 고딕으로 보여요.

## 기능과 정해진 동작
- **세대 탭:** 1~9세대(지방 이름 포함)와 "⭐ 좋아요" 탭(`gen === 0`)이 있어요.
- **검색:** 다음으로 찾을 수 있어요.
  - 이름 일부
  - 초성 (ㅍㅋㅊ)
  - 번호
  - 타입 이름 (불꽃)
- **🎤 말로 찾기:** Web Speech API(ko-KR)를 써요. https에서만 동작해요.
  - 이름이 정확히 같은 포켓몬을 먼저 찾아요.
  - 없으면 말한 문장 안에 들어 있는 가장 긴 이름을 찾아요.
- **🎲 주사위:** 지금 보고 있는 세대와 상관없이 **전체** 포켓몬에서 뽑아요.
- **◀ ▶ 화살표, 좌우 스와이프:**
  - 보통은 **도감 번호 순서**로 넘겨요. 검색이나 세대 탭에서 연 경우 모두 해당돼요.
  - "좋아요" 탭에서 연 경우에만 좋아요 목록 안에서 넘겨요.
  - 예전에는 화면 목록 안에서만 넘겨서, 검색 후에 진화 전/후로 이동하지 않는 버그가 있었어요.
- **상세 화면:** 열리면 울음소리가 나와요.
  - 그림을 누르면 흔들리면서 다시 울어요.
  - 버튼: 🗣️ 이름 듣기(speechSynthesis), ✨ 색이 다른 모습, 🤍 좋아요
  - 진화 단계를 그림으로 보여 주고, 누르면 그 포켓몬으로 이동해요.
- **메가진화:** `index.html`에서 `MEGAS`로 만들어 `byId`에 넣어요.
  - 원래 포켓몬의 정보(분류, 진화 계열 `ch`, 세대)를 이어받고, `from = b`라서 진화 줄에서 원래 포켓몬 다음 단계로 보여요. 예: 메탕 ▶ 메탕구 ▶ 메타그로스 ▶ 메가메타그로스
  - 검색, 좋아요, 진화 줄에는 나오지만(`ALL`), 세대 탭과 🎲 주사위에는 나오지 않아요(`POKEMON`만).
  - 화면의 도감 번호는 원래 포켓몬 번호(`dexNo()`)로 보여요. 나무위키 링크도 원래 포켓몬 이름으로 연결해요.
  - 메가진화에서 ◀ ▶를 누르면 원래 포켓몬 번호 기준으로 앞뒤로 넘어가요.
- **좋아요:** `localStorage`의 `pk-favs`에 저장해요. 기기와 주소마다 따로 저장돼요.
- **뒤로 버튼:** 상세 화면을 열 때 `history.pushState`를 해요.
  - 안드로이드 '뒤로'를 누르면 앱이 꺼지지 않고 상세 화면만 닫혀요.
- **주소 해시:** `index.html#25`로 열면 그 포켓몬이 바로 열려요. 스크린샷 테스트에도 써요.
- **레이아웃:** 너비 700px 이상이면 카드가 커져요. 가로 태블릿(800px 이상이고 5:4보다 넓은 화면)은 상세 화면을 그림 왼쪽, 정보 오른쪽으로 배치해요.

## 고칠 때 순서
1. 코드를 고친 뒤 `sw.js` 맨 위 `VERSION`을 하나 올려요 (현재 **v4**). 태블릿이 새 화면을 받게 하려는 거예요.
2. 확인해요.
   - 문법 검사: `node -e` 로 `index.html`의 `<script>` 부분을 `new Function()`에 넣어 봐요.
   - 화면 확인: Edge headless로 태블릿 크기 스크린샷을 찍어요.
     ```
     "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --hide-scrollbars \
       --virtual-time-budget=8000 --window-size=800,1280 --screenshot=<스크래치패드>/shot.png "file:///.../index.html#6"
     ```
     가로 화면은 `--window-size=1280,800`으로 찍어요.
     - 가끔 Edge가 끝나지 않고 멈춰요. 앞에 `timeout 60`을 붙이고 `--user-data-dir=<스크래치패드>/edge`를 따로 줘요.
     - 실행하면 프로젝트 폴더에 `NVIDIA Corporation/` 로그 폴더가 생겨요. `.gitignore`에 넣어 두었고, 지워도 돼요.
3. 커밋하고 올려요.
   - 커밋 메시지: 한국어 제목 한 줄 + Markdown 설명 (바뀐 점, 바뀐 파일).
   - **push는 사용자가 하라고 할 때만** 해요. Public 저장소라 올리면 바로 공개되고 태블릿 앱에도 반영돼요.
   - 사용자에게 바뀐 파일과 커밋 내용을 알려 주고, 1~2분 뒤 태블릿 앱을 완전히 닫았다가 다시 열라고 안내해요.

## 새 포켓몬이 나왔을 때 (데이터 업데이트)
1. 도감 폴더에서 `python -I tools/build-data.py`를 실행해요.
   - CSV를 임시 폴더에 받아서 `pokemon-data.js`를 다시 만들어요.
   - 마리 수, 세대 범위, 한국어 이름이 없는 포켓몬 목록을 출력해요.
2. 새 세대가 생겼으면 `index.html`의 `GENS` 배열에 탭을 추가해요. 예: `[10, '10세대', '지방이름']`
3. `sw.js`의 `VERSION`을 올리고, `pokemon-data.js`, `index.html`, `sw.js`를 커밋해요.

## 하지 말 것
- 나무위키 같은 사이트를 크롤링하지 않아요.
- 빌드 도구나 npm 패키지를 넣지 않아요. 사용자가 파일을 그대로 끌어다 올리는 구조를 유지해요.
- `localStorage` 키(`pk-favs`)와 GitHub 저장소 주소를 바꾸지 않아요. 바꾸면 아이의 좋아요 목록이 사라져요.
