# Code Convention

## 적용 범위

이 문서는 Python과 JavaScript/JSX를 함께 사용하는 프로젝트의 공통 규칙과 언어별 규칙을 구분한다. 한 언어의 문법 관례를 다른 언어에 그대로 적용하지 않는다.

## 공통 규칙

- 가독성을 위해 한 줄에는 하나의 실행 문장만 작성한다.
- 이항 연산자와 콤마 뒤에는 공백을 둔다.
- 주석은 설명 대상 코드와 같은 들여쓰기 수준에 작성한다.
- 문자열 따옴표는 파일 안에서 일관되게 사용한다. 이 프로젝트의 Python과 JavaScript/JSX 예제는 쌍따옴표를 기본으로 한다.

## Python 규칙

- **문장 끝에 세미콜론을 쓰지 않는다.** Python에서는 줄바꿈이 문장의 끝을 나타낸다.
- 함수, 변수, 모듈 이름은 `snake_case`로 작성한다.
- 클래스 이름은 `PascalCase`로 작성한다.
- 상수는 `UPPER_SNAKE_CASE`로 작성한다.
- 함수 호출의 키워드 인자와 기본값에도 일반적인 Python 표기(`key=value`)를 사용한다.

```python
MAX_RESULTS = 100


class PaperRepository:
    def load_papers(self, limit=MAX_RESULTS):
        # Supabase에서 논문을 읽는다.
        return self.client.table("papers").select("*").limit(limit).execute()
```

## JavaScript / JSX 규칙

- 문장 끝에는 세미콜론을 붙인다.
- 함수와 변수 이름은 `camelCase`로 작성한다.
- 클래스와 생성자 함수 이름은 `PascalCase`로 작성한다.

```jsx
const maxResults = 100;

function PaperRepository() {
  // 논문 저장소를 초기화한다.
  return { maxResults };
}
```

## 코드 컨벤션이 필요한 이유

- 팀원이 같은 기준으로 코드를 작성하면 리뷰와 유지보수가 쉬워진다.
- 언어별 관례를 지키면 린터, 포매터, 라이브러리 예제와 자연스럽게 호환된다.
- 프로젝트의 협업 방식을 명확하게 보여 줄 수 있다.

## 참고

- [Python PEP 8](https://peps.python.org/pep-0008/)
- [TOAST UI 코딩 컨벤션](https://ui.toast.com/fe-guide/ko_CODING-CONVENTION)
