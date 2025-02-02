<img src="https://img.shields.io/github/contributors/wafflestudio/22-5-team8-server?color=yellow">
<img src="https://img.shields.io/github/commit-activity/t/wafflestudio/22-5-team8-server">
<img src="https://img.shields.io/github/issues-pr/wafflestudio/22-5-team8-server?color=deep%20green">
<img src="https://img.shields.io/github/issues-pr-closed/wafflestudio/22-5-team8-server?color=violet">
<br><br>

<div align="center">
<h1>🧇Wachapedia</h1>
<h4>WaffleStudio 22-5 Team 8 토이프로젝트<h4>
</div>

## 배포 링크
프론트엔드 배포 링크: https://d2vsqxcvld4zf7.cloudfront.net (모바일로 들어가는 걸 추천 드립니다)
<br>백엔드 배포 링크: http://52.79.121.53

## ❓ About The Project
Wachapedia는 [**왓챠피디아**](https://pedia.watcha.com/ko-KR/)의 클론 프로젝트입니다.
<br>왓챠피디아는 사용자들이 영화, 드라마, 도서, 웹툰 등 다양한 콘텐츠에 대해 **별점과 리뷰**를 남기고  이를 바탕으로 개인화된 **추천 서비스**를 제공받을 수 있는 서비스입니다.
저희 팀에서는 시간상의 한계와 개발 역량을 고려해 영화 컨텐츠에 대해서만 구현하기로 결정하였습니다.

이 레포지토리는 Backend 레포지토리로, Frontend 내용은 [**Frontend 레포지토리**](https://github.com/wafflestudio/22-5-team8-web) 를 참고하시기 바랍니다.
### 💡와챠피디아(Wachapedia)만의 신기능
-  🔎 왓챠피디아에선 할 수 없었던 장르 필터 검색이 가능합니다. 장르 필터를 사용하면 해당 장르의 영화들을 모아볼 수 있습니다.
- 🙈 차단하고 싶은 유저가 있으신가요? 유저 블록 기능을 통해, 영화 리뷰 조회 시 해당 유저의 리뷰를 숨길 수 있습니다.
- ✏️ 영화 N차 관람의 시대. 리뷰에 감상 일자 추가 기능을 만들어 재감상 기록을 남길 수 있습니다.

**메인 기능**
- [x] 메인 페이지
- [x] 영화 정보 : 영화 정보, 코멘트 (장르, 개봉년도, 시놉시스, 출연배우, 포스터, …)
- [x] 검색: 영화
- [x] 평점 : 평점 매기기 · 코멘트 · 좋아요

**필수 기능**
- [x] 로그인 : 소셜 로그인
- [x] 유저 페이지: 추천 목록, 팔로우, 언팔로우
- [x] 검색: 제목, 인물, 컬렉션, 유저, 필터(새로운 기능)
- [x] 감독/배우 페이지: 작품 목록
- [x] 평점: 대댓글
- [x] 컬렉션: 컬렉션 생성/수정 및 컬렉션 댓글

**추가 기능**
- [x] 캘린더: 어떤 날짜에 뭘 봤는지 달력에 표시
- [x] 취향 분석: 별점 분포, 선호 태그, 국가, 장르 등
- [x] 영화 추천 페이지: 예상 평점
- [x] 유저 차단


## Contributors
<img src="https://img.shields.io/badge/%EC%9D%B4%EA%B2%BD%ED%91%9C-deveroskp-dark_green?link=https%3A%2F%2Fgithub.com%2Fdeveroskp">
<ul>
    <li>팀장</li>
    <li>로그인: 소셜 로그인</li>
    <li>유저 페이지: 추천 목록, 팔로우, 언팔로우</li>
    <li>감독/배우 페이지: 작품 목록</li>
    <li>유저 블록 기능</li>
</ul>

<img src="https://img.shields.io/badge/%EC%8B%A0%EC%A7%80%EC%9B%90-anandashin-purple?color=9370DB&link=https%3A%2F%2Fgithub.com%2Fanandashin">
<ul>
    <li>영화 정보 크롤링: 영화 정보, 코멘트 (장르, 개봉년도, 시놉시스, 출연배우, 포스터, …)</li>
    <li>검색: 영화</li>
    <li>컬렉션: 컬렉션 생성/수정 및 컬렉션 댓글</li>
    <li>CI/CD 구현</li>
</ul>

<img src="https://img.shields.io/badge/%EA%B9%80%EB%AF%BC%EC%84%B1-minchok125-magenta?link=https%3A%2F%2Fgithub.com%2Fminchok125">
<ul>
    <li>평점 : 평점 매기기 · 코멘트 · 좋아요</li>
    <li>평점: 대댓글</li>
    <li>영화 추천 페이지: 예상 평점</li>
</ul>

<img src="https://img.shields.io/badge/%EC%9D%B4%ED%98%B8%EC%84%9D-arcstone09-green?link=https%3A%2F%2Fgithub.com%2Farcstone09">
<ul>
    <li>검색: 제목, 인물, 컬렉션, 유저, 필터(새로운 기능)</li>
    <li>캘린더: 어떤 날짜에 뭘 봤는지 달력에 표시</li>
    <li>취향 분석: 별점 분포, 선호 태그, 국가, 장르 등</li>
</ul>

## 🛠 기술 스택

### BackEnd
<div>
<img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi">
<img src="https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8D">
<img src="https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white">
<img src="https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white">
<img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=for-the-badge&logo=Amazon RDS&logoColor=orange">
</div>

### CI/CD
<div>
<img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"> 
<img src="https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white">
</div>

## 📆 개발 과정

#### 커밋 컨벤션
| 이름        | 목적       |
|-----------|----------|
| feat      | 새로운 기능 추가 |
| fix       | 버그 수정    |
| docs      | 문서 업데이트  |
| style     | 스타일 변경   |
| refactor  | 리팩토링     |
| test      | 테스트 추가   |
| chore     | 유지보수     |

#### PR 템플릿

```
## 개요
<!---- 변경 사항 및 관련 이슈에 대해 간단하게 작성해주세요. 어떻게보다 무엇을 왜 수정했는지 설명해주세요. -->
<!---- Resolves: #(Isuue Number) -->
## PR 유형
어떤 변경 사항이 있나요?
- [ ] 새로운 기능 추가
- [ ] 버그 수정
- [ ] CSS 등 사용자 UI 디자인 변경
- [ ] 코드에 영향을 주지 않는 변경사항(오타 수정, 탭 사이즈 변경, 변수명 변경)
- [ ] 코드 리팩토링
- [ ] 주석 추가 및 수정
- [ ] 문서 수정
- [ ] 테스트 추가, 테스트 리팩토링
- [ ] 빌드 부분 혹은 패키지 매니저 수정
- [ ] 파일 혹은 폴더명 수정
- [ ] 파일 혹은 폴더 삭제
## PR Checklist
PR이 다음 요구 사항을 충족하는지 확인하세요.
- [ ] 커밋 메시지 컨벤션에 맞게 작성했습니다.  Commit message convention 참고
- [ ] 변경 사항에 대한 테스트를 했습니다.(버그 수정/기능에 대한 테스트).
<!---- 노션 칸반보드 업데이트, 슬랙에 알리는 것도 잊지 마세요! -->
```


#### 팀 컨벤션

| **소통**| <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">|
|:-----------|:----------:|
| **칸반** | <img src="https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white">|
| **API 문서** | <img src="https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white"> <img src="https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white"> |
| **스크럼** | **데일리 스크럼<br>주간 스크럼(줌 or 대면, 매주 목 오후 1시)** |

#### 개발 일정
| 스프린트1| 12/26~1/4| <ul><li>클론 서비스 선정</li><li>모델 다이어그램 완성</li><li>레포 셋업 <br><li>로그인 로직 구현</li><li>CI/CD 적용<ul>|
|-------------|---------|----------|
| 스프린트2|1/5~1/11| <ul><li>영화 정보 페이지 api</li><li>감독, 배우 api</li><li>유저 프로필 api</li><li>리뷰, 코멘트 api</li></ul>|
| 스프린트3|1/12~1/17| <ul><li>컬렉션 api</li><li>유저 팔로우 기능</li></ul>|
| 스프린트4 |1/18~1/24| <ul><li>검색 api</li><li>유저 차단 기능</li></ul>  |
| 스프린트5|1/24~2/1| <ul><li>캘린더 api</li><li>영화 추천, 취향 분석 api</li></ul>|

