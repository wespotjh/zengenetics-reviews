# 검색엔진 소유 확인 파일

여기에 넣은 파일은 **빌드 때 사이트 루트로 그대로 복사**된다.

| 넣는 것 | 결과 |
|---|---|
| `google1a2b3c.html` (Search Console 다운로드 파일) | `https://review.zengenetics.co.kr/google1a2b3c.html` 로 서빙 |
| `naver1a2b3c.html` 등 타 검색엔진 파일 | 동일 |
| `meta.txt` | 파일 안의 `<meta ...>` 태그를 **전 페이지 `<head>`** 에 삽입 |

`meta.txt` 예시 (Search Console 의 "HTML 태그" 방식):

```
<meta name="google-site-verification" content="여기에_토큰" />
```

> DNS 를 건드리지 않아도 된다. 이 사이트는 우리가 빌드하므로 여기 넣고 푸시하면
> 워크플로가 배포까지 처리한다.
