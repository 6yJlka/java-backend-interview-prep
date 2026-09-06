# Spring MVC

## DispatcherServlet

В основе лежит шаблон Front Controller: все запросы проходят через одну точку
входа, которая решает, кому их передать.

```text
HTTP-запрос
    ↓
Servlet-контейнер (Tomcat)
    ↓
Filter chain
    ↓
DispatcherServlet
    ↓
HandlerMapping      → какой метод обработает запрос
    ↓
HandlerInterceptor  → preHandle
    ↓
HandlerAdapter      → вызывает метод, готовит аргументы
    ↓
контроллер
    ↓
HttpMessageConverter → объект в JSON
    ↓
HandlerInterceptor  → postHandle, afterCompletion
    ↓
HTTP-ответ
```

Разберём ключевые звенья.

**`HandlerMapping`** сопоставляет запрос с методом контроллера. Учитывается путь,
метод HTTP, заголовки, параметры. Если совпадения нет — `404`, если путь совпал, а
метод нет — `405`.

**`HandlerAdapter`** вызывает найденный метод. Его работа не сводится к простому
вызову: он разбирает сигнатуру и готовит аргументы через набор
`HandlerMethodArgumentResolver` — извлекает переменные пути, параметры запроса,
десериализует тело, подставляет `Principal`. Именно поэтому методы контроллера
могут принимать почти произвольный набор параметров.

**`HttpMessageConverter`** преобразует объекты в тело ответа и обратно. Для JSON
это `MappingJackson2HttpMessageConverter`. Выбор конвертера зависит от заголовков
`Content-Type` и `Accept` — это и есть согласование содержимого.

### Модель «поток на запрос»

Классический Spring MVC блокирующий: каждый запрос обрабатывается отдельным
потоком из пула Tomcat, и поток занят всё время обработки, включая ожидание ответа
базы.

```text
пул Tomcat по умолчанию → 200 потоков
200 одновременных медленных запросов → пул исчерпан
остальные ждут в очереди
```

Отсюда следует, почему долгие внешние вызовы в контроллере опасны и почему
виртуальные потоки в Java 21 так уместны именно здесь: они снимают ограничение на
число одновременно блокированных обработчиков.

---

## Контроллеры

### @Controller и @RestController

```java
@Controller
public class ViewController {

    @GetMapping("/orders")
    public String list(Model model) {
        model.addAttribute("orders", orderService.findAll());
        return "orders";          // имя шаблона
    }
}
```

```java
@RestController
public class OrderController {

    @GetMapping("/api/orders")
    public List<OrderResponse> list() {
        return orderService.findAll();   // сериализуется в JSON
    }
}
```

Разница в том, как трактуется возвращаемое значение. У `@Controller` строка — имя
представления, которое разрешает `ViewResolver`. `@RestController` — это
`@Controller` плюс `@ResponseBody`, и результат попадает прямо в тело ответа через
конвертер.

Для REST API используется `@RestController`.

### Маппинг

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @GetMapping                       // GET  /api/orders
    @GetMapping("/{id}")              // GET  /api/orders/1
    @PostMapping                      // POST /api/orders
    @PutMapping("/{id}")
    @PatchMapping("/{id}")
    @DeleteMapping("/{id}")
}
```

Все они — специализации `@RequestMapping` с зафиксированным методом. Можно
уточнять и по другим признакам:

```java
@PostMapping(
    value = "/{id}",
    consumes = MediaType.APPLICATION_JSON_VALUE,
    produces = MediaType.APPLICATION_JSON_VALUE
)
```

### Параметры

```java
@GetMapping("/{orderId}/items")
public List<ItemResponse> items(
        @PathVariable Long orderId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(required = false) String status,
        @RequestHeader("X-Request-Id") String requestId
) {
}
```

```text
@PathVariable   → часть пути, идентифицирует ресурс
@RequestParam   → query-параметр, уточняет выборку
@RequestHeader  → заголовок
@RequestBody    → тело запроса, десериализуется конвертером
@CookieValue    → значение cookie
```

Разделение между `@PathVariable` и `@RequestParam` — то же, что обсуждалось в
конспекте по REST: путь именует ресурс, query фильтрует.

Для группы параметров удобнее объект:

```java
@GetMapping
public Page<OrderResponse> search(OrderSearchRequest request, Pageable pageable) {
}
```

Поля заполняются из query-параметров автоматически, аннотация не нужна.

### ResponseEntity

Когда нужно управлять кодом ответа и заголовками:

```java
@PostMapping
public ResponseEntity<OrderResponse> create(@RequestBody @Valid OrderRequest request) {
    OrderResponse created = orderService.create(request);

    return ResponseEntity
            .created(URI.create("/api/orders/" + created.id()))
            .body(created);
}
```

Альтернатива для простых случаев — `@ResponseStatus`:

```java
@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public OrderResponse create(@RequestBody @Valid OrderRequest request) {
    return orderService.create(request);
}
```

`ResponseEntity` гибче, `@ResponseStatus` короче. Смешивать в одном API не стоит.

---

## DTO

### Зачем они нужны

Соблазн отдавать сущности напрямую велик — меньше кода. Но это плохая идея, и
причин несколько.

**Внутренняя модель протекает в API.** Переименование поля сущности ломает
контракт для всех клиентов. Слои перестают быть независимыми.

**Утечка данных.** В ответ попадает всё, включая хеш пароля и служебные поля.
Защищаться приходится через `@JsonIgnore` на каждом поле — подход «запрещаем по
списку», где легко что-то забыть.

**LazyInitializationException.** Сериализация сущности обращается к её геттерам,
включая ленивые коллекции. Если транзакция уже закрыта, Jackson получит исключение
посреди записи ответа — когда часть JSON уже ушла клиенту. Ответ окажется
обрезанным.

**Скрытые запросы.** Если сессия ещё открыта, ленивые связи не упадут, а
подгрузятся — и сериализация списка из ста заказов молча выполнит сотню
дополнительных запросов.

**Циклические ссылки.** Двунаправленная связь `Order ↔ Item` при сериализации даёт
бесконечную рекурсию.

### Как оформлять

`record` подходит идеально: неизменяемость, краткость, готовые `equals` и
`hashCode`.

```java
public record OrderRequest(
        @NotNull Long productId,
        @Positive int quantity
) {}

public record OrderResponse(
        Long id,
        String status,
        BigDecimal total,
        Instant createdAt
) {}
```

Разделять запрос и ответ полезно: у них разные наборы полей. В запросе нет `id` и
`createdAt`, в ответе нет служебных флагов.

Преобразование выносится в отдельный компонент — вручную или через MapStruct,
который генерирует код на этапе компиляции.

---

## Валидация

### Базовое применение

```java
public record OrderRequest(
        @NotNull(message = "productId обязателен")
        Long productId,

        @Positive
        int quantity,

        @Email
        String contactEmail,

        @Size(max = 500)
        String comment
) {}
```

```java
@PostMapping
public OrderResponse create(@RequestBody @Valid OrderRequest request) {
}
```

Без `@Valid` аннотации на полях не проверяются — это самая частая ошибка в теме.
При нарушении выбрасывается `MethodArgumentNotValidException`.

### Основные ограничения

```text
@NotNull  → не null
@NotEmpty → не null и не пустой (строка, коллекция)
@NotBlank → не null и содержит непробельные символы
@Size     → длина или размер в диапазоне
@Min @Max @Positive @Negative
@Email @Pattern
@Past @Future
```

Разница между тремя первыми — частый вопрос. `@NotNull` пропустит пустую строку,
`@NotEmpty` пропустит строку из пробелов, `@NotBlank` не пропустит ни то ни другое.
Для строк обычно нужен `@NotBlank`.

### Вложенные объекты

```java
public record OrderRequest(
        @NotNull @Valid AddressRequest address,
        @NotEmpty @Valid List<ItemRequest> items
) {}
```

Без `@Valid` на поле вложенный объект не проверяется.

### @Valid и @Validated

```text
@Valid     → из Bean Validation, работает на параметрах и полях
@Validated → из Spring, дополнительно поддерживает группы
             и включает валидацию на уровне методов бина
```

```java
@Service
@Validated
public class OrderService {

    public void process(@NotNull @Valid OrderRequest request) {
    }
}
```

В этом случае валидация выполняется через AOP-прокси — со всеми уже известными
ограничениями, включая неработающий self-invocation.

---

## Обработка исключений

### @ExceptionHandler

Внутри контроллера — обрабатывает только его исключения:

```java
@ExceptionHandler(OrderNotFoundException.class)
public ResponseEntity<ErrorResponse> handle(OrderNotFoundException e) {
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("ORDER_NOT_FOUND", e.getMessage()));
}
```

### @RestControllerAdvice

Глобальный обработчик для всех контроллеров — стандартное решение:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(EntityNotFoundException e) {
        return new ErrorResponse("NOT_FOUND", e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ValidationErrorResponse handleValidation(MethodArgumentNotValidException e) {
        List<FieldError> errors = e.getBindingResult().getFieldErrors().stream()
                .map(fe -> new FieldError(fe.getField(), fe.getDefaultMessage()))
                .toList();

        return new ValidationErrorResponse("VALIDATION_FAILED", errors);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleUnexpected(Exception e, HttpServletRequest request) {
        log.error("Unexpected error on {}", request.getRequestURI(), e);
        return new ErrorResponse("INTERNAL_ERROR", "Внутренняя ошибка");
    }
}
```

Последний обработчик важен: он не даёт утечь наружу деталям реализации. Сообщение
исключения может содержать текст SQL-запроса или путь в файловой системе, поэтому
наружу отдаётся общая формулировка, а подробности уходят в лог.

`@RestControllerAdvice` — это `@ControllerAdvice` плюс `@ResponseBody`. Область
действия можно ограничить пакетом или аннотацией.

### ProblemDetail

С Spring 6 есть встроенная поддержка RFC 7807:

```java
@ExceptionHandler(OrderNotFoundException.class)
public ProblemDetail handle(OrderNotFoundException e) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, e.getMessage()
    );
    problem.setTitle("Заказ не найден");
    problem.setType(URI.create("https://example.com/problems/order-not-found"));
    return problem;
}
```

Ответ имеет тип `application/problem+json` — тот самый стандартный формат ошибок из
конспекта по REST.

### Важное ограничение

Обработчик работает только с исключениями, вылетевшими из контроллера. Исключение
из фильтра до `DispatcherServlet` не долетит — там обработка своя.

---

## Фильтры и перехватчики

```text
Filter
→ уровень Servlet API, до DispatcherServlet
→ работает с HttpServletRequest и HttpServletResponse
→ не знает, какой контроллер будет вызван
→ подходит для логирования, CORS, аутентификации

HandlerInterceptor
→ уровень Spring MVC, после выбора обработчика
→ знает метод контроллера и его аннотации
→ подходит для проверки прав по аннотациям, метрик по эндпоинтам
```

```java
@Component
public class LoggingInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        return true;   // false прервёт обработку
    }
}
```

Практическое правило: если нужно знать, какой контроллер вызывается, — перехватчик,
если задача чисто транспортная — фильтр. Spring Security построен на фильтрах и
потому работает до контроллеров.

---

## Типичные ошибки

### Отдавать сущности вместо DTO

Внутренняя модель протекает в API, возможны утечка данных, рекурсия и
`LazyInitializationException` посреди сериализации.

### Забыть @Valid

Аннотации на полях DTO без него не проверяются, и запрос уходит в сервис как есть.

### Забыть @Valid на вложенном объекте

Проверяется только верхний уровень.

### Использовать @NotNull для строк

Пустая строка и строка из пробелов пройдут проверку. Нужен `@NotBlank`.

### Ловить исключения в контроллере

Блоки `try-catch` в каждом методе дублируются и мешают единообразию ответов. Место
обработки — `@RestControllerAdvice`.

### Отдавать сообщение исключения клиенту

Может содержать SQL, пути и версии библиотек. Наружу — общая формулировка,
подробности в лог.

### Возвращать 200 на ошибку

Клиент не может обработать её стандартно, мониторинг не видит проблемы.

### Выполнять долгие операции в контроллере

Поток из пула занят всё время обработки. При исчерпании пула сервис перестаёт
принимать запросы.

### Смешивать ResponseEntity и @ResponseStatus

Оба подхода рабочие, но в пределах одного API стоит выбрать один.

### Считать, что @ControllerAdvice поймает всё

Исключения из фильтров возникают до `DispatcherServlet` и обрабатываются иначе.

---

## Краткая памятка

```text
путь запроса
Filter → DispatcherServlet → HandlerMapping → Interceptor.preHandle
→ HandlerAdapter → контроллер → HttpMessageConverter → ответ
```

```text
@Controller     → возвращает имя представления
@RestController → @Controller + @ResponseBody, результат в тело
```

```text
@PathVariable  идентификация ресурса
@RequestParam  фильтрация и пагинация
@RequestBody   тело, через конвертер
ResponseEntity полный контроль над ответом
```

```text
@NotNull  → не null, пустая строка пройдёт
@NotEmpty → не пустой, пробелы пройдут
@NotBlank → есть непробельные символы

@Valid обязателен на параметре
@Valid обязателен на вложенном объекте
```

```text
@RestControllerAdvice → глобальная обработка
ProblemDetail         → RFC 7807, Spring 6

ловит только исключения из контроллеров
```

```text
Filter      → до DispatcherServlet, транспортный уровень
Interceptor → знает контроллер и его аннотации
```

```text
поток на запрос
пул Tomcat ~200
долгие операции исчерпывают пул
```

---

## Краткий ответ для собеседования

Spring MVC построен на шаблоне Front Controller: все запросы проходят через
`DispatcherServlet`. Он обращается к `HandlerMapping`, чтобы найти подходящий метод
контроллера, затем к `HandlerAdapter`, который разбирает сигнатуру, готовит
аргументы через резолверы и вызывает метод. Результат преобразуется в тело ответа
через `HttpMessageConverter`, для JSON это конвертер на основе Jackson.

`@RestController` отличается от `@Controller` тем, что возвращаемое значение
попадает прямо в тело ответа, а не трактуется как имя представления.

Наружу отдаются DTO, а не сущности. Иначе внутренняя модель протекает в контракт,
возможна утечка полей, циклические ссылки при двунаправленных связях и
`LazyInitializationException` прямо во время сериализации, когда часть ответа уже
отправлена.

Валидация выполняется через Bean Validation. Аннотации на полях работают только при
наличии `@Valid` на параметре, и для вложенных объектов его нужно ставить отдельно.
Нарушение приводит к `MethodArgumentNotValidException`.

Исключения обрабатываются глобально в `@RestControllerAdvice`. Наружу отдаётся код
ошибки и безопасное сообщение, а подробности пишутся в лог. С Spring 6 доступен
`ProblemDetail` — реализация стандартного формата ошибок RFC 7807.

Модель обработки блокирующая: каждый запрос занимает поток из пула на всё время
выполнения, поэтому долгие операции в контроллере способны исчерпать пул.

---

## Вопросы на собеседовании

### 1. Что такое DispatcherServlet?

**Ответ:** единая точка входа для всех запросов, реализация шаблона Front
Controller. Он находит обработчик, вызывает его и формирует ответ.

### 2. Опишите путь запроса в Spring MVC.

**Ответ:** фильтры, `DispatcherServlet`, `HandlerMapping` для поиска метода,
перехватчики, `HandlerAdapter` для вызова, контроллер, `HttpMessageConverter` для
формирования тела ответа.

### 3. Зачем нужен HandlerAdapter?

**Ответ:** он вызывает метод контроллера, разбирая его сигнатуру и подготавливая
аргументы через резолверы. Поэтому методы могут принимать разные наборы параметров.

### 4. Что делает HttpMessageConverter?

**Ответ:** преобразует объекты в тело ответа и разбирает тело запроса. Конвертер
выбирается по заголовкам `Content-Type` и `Accept`.

### 5. Чем @RestController отличается от @Controller?

**Ответ:** `@RestController` включает `@ResponseBody`, поэтому результат метода
идёт в тело ответа. У `@Controller` возвращаемая строка трактуется как имя
представления.

### 6. Когда использовать @PathVariable, а когда @RequestParam?

**Ответ:** переменная пути идентифицирует ресурс, query-параметр уточняет
выборку — фильтрация, сортировка, пагинация.

### 7. Зачем нужен ResponseEntity?

**Ответ:** чтобы управлять кодом ответа и заголовками, например вернуть `201` с
заголовком `Location`.

### 8. Почему нельзя возвращать сущности напрямую?

**Ответ:** внутренняя модель попадает в контракт API, возможна утечка служебных
полей, рекурсия при двунаправленных связях и `LazyInitializationException` во время
сериализации.

### 9. Что произойдёт при сериализации сущности с ленивой коллекцией вне транзакции?

**Ответ:** Jackson обратится к геттеру, прокси попытается загрузить данные и
выбросит `LazyInitializationException`. Часть ответа к этому моменту может быть уже
отправлена, и клиент получит обрезанный JSON.

### 10. Как работает валидация?

**Ответ:** через Bean Validation. Аннотации на полях DTO проверяются, если параметр
помечен `@Valid`; при нарушении выбрасывается `MethodArgumentNotValidException`.

### 11. Чем отличаются @NotNull, @NotEmpty и @NotBlank?

**Ответ:** `@NotNull` запрещает только `null`, `@NotEmpty` дополнительно требует
непустое значение, `@NotBlank` требует наличия непробельных символов. Для строк
обычно нужен последний.

### 12. Чем @Valid отличается от @Validated?

**Ответ:** `@Valid` из стандарта Bean Validation. `@Validated` — аннотация Spring,
поддерживающая группы валидации и включающая проверку на уровне методов бина через
прокси.

### 13. Как проверить вложенный объект?

**Ответ:** поставить `@Valid` на соответствующее поле, иначе проверяется только
верхний уровень.

### 14. Как обрабатывать исключения централизованно?

**Ответ:** через `@RestControllerAdvice` с методами `@ExceptionHandler`. Это
избавляет от блоков `try-catch` в контроллерах и даёт единый формат ошибок.

### 15. Поймает ли @ControllerAdvice исключение из фильтра?

**Ответ:** нет. Фильтры работают до `DispatcherServlet`, и такие исключения
обрабатываются отдельно.

### 16. Что такое ProblemDetail?

**Ответ:** реализация стандартного формата ошибок RFC 7807, появившаяся в Spring 6.
Ответ отдаётся с типом `application/problem+json`.

### 17. Чем фильтр отличается от перехватчика?

**Ответ:** фильтр работает на уровне Servlet API до `DispatcherServlet` и не знает
о контроллере. Перехватчик работает после выбора обработчика и имеет доступ к
методу и его аннотациям.

### 18. Как Spring MVC обрабатывает параллельные запросы?

**Ответ:** каждый запрос занимает отдельный поток из пула контейнера на всё время
обработки, включая ожидание ввода-вывода.

### 19. Чем опасны долгие операции в контроллере?

**Ответ:** пул потоков ограничен, и при заполнении новые запросы встают в очередь.
Сервис перестаёт отвечать, хотя нагрузка на процессор невелика.

### 20. Что вернуть при создании ресурса?

**Ответ:** `201 Created` с заголовком `Location`, указывающим на созданный ресурс.

---

## См. также

- [`../http_rest/01-http-rest.md`](../http_rest/01-http-rest.md) — коды ответов,
  проектирование URI и формат ошибок RFC 7807
- [`01-spring-core.md`](01-spring-core.md) — контейнер и внедрение зависимостей в
  контроллеры
- [`02-spring-aop.md`](02-spring-aop.md) — прокси, через который работает
  `@Validated` на уровне методов
- [`../java-core/10-modern-java.md`](../java-core/10-modern-java.md) — `record`
  как форма DTO
- [`../concurrency/06-virtual-threads.md`](../concurrency/06-virtual-threads.md) —
  почему модель «поток на запрос» упирается в размер пула