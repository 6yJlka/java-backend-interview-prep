# Optional

## Зачем нужен Optional

Метод, который может не найти результат, до Java 8 возвращал `null`:

```java
public User findByEmail(String email) {
    return users.get(email);
}
```

Проблема не в самом `null`, а в том, что сигнатура о нём молчит. Вызывающий код
не отличает «метод может вернуть отсутствие» от «метод всегда возвращает объект»,
и `NullPointerException` всплывает далеко от места, где отсутствие возникло.

`Optional<T>` переносит эту информацию в тип:

```java
public Optional<User> findByEmail(String email) {
    return Optional.ofNullable(users.get(email));
}
```

Теперь компилятор не даст вызвать `user.getName()` напрямую. Обработать отсутствие
придётся явно.

Ключевая мысль, которую важно проговорить на собеседовании: `Optional` создавался
как **тип возвращаемого значения** для методов, у которых отсутствие результата —
нормальный исход. Это не универсальная замена `null` во всём коде и не средство
защиты от `NullPointerException` вообще.

---

## Создание

### Optional.of

```java
Optional<User> optional = Optional.of(user);
```

Требует ненулевое значение. Если передать `null`, немедленно бросается
`NullPointerException`.

Это не недостаток, а нужное поведение: `of()` применяют там, где `null` означал бы
ошибку в программе, и падение должно произойти сразу.

### Optional.ofNullable

```java
Optional<User> optional = Optional.ofNullable(user);
```

Допускает `null` и превращает его в пустой `Optional`. Основной способ обернуть
результат чужого API, который может вернуть `null`.

### Optional.empty

```java
Optional<User> optional = Optional.empty();
```

Явно пустое значение.

```text
of(value)          → значение обязано быть непустым, иначе NPE
ofNullable(value)  → null превращается в empty
empty()            → пустой Optional
```

Типичная ошибка — использовать `of()` там, где значение может отсутствовать:

```java
Optional.of(map.get(key)); // NPE, если ключа нет
```

---

## Проверка наличия

```java
optional.isPresent();  // есть значение
optional.isEmpty();    // значения нет, начиная с Java 11
```

Оба метода нужны редко. Как только в коде появляется `isPresent()`, чаще всего
следом идёт `get()`, и это признак того, что `Optional` используется как
переусложнённая проверка на `null`:

```java
if (optional.isPresent()) {
    User user = optional.get();
    process(user);
}
```

Тот же смысл выражается короче и без риска:

```java
optional.ifPresent(this::process);
```

---

## Извлечение значения

### get

```java
User user = optional.get();
```

Бросает `NoSuchElementException`, если значения нет. Начиная с Java 10 существует
`orElseThrow()` без аргументов, делающий ровно то же самое, и с Java 10 `get()`
считается нежелательным именно потому, что не сообщает читателю о возможном
падении.

```java
User user = optional.orElseThrow(); // предпочтительнее get()
```

### orElse

```java
User user = optional.orElse(GUEST);
```

Возвращает значение или переданную альтернативу.

### orElseGet

```java
User user = optional.orElseGet(this::createGuest);
```

Принимает `Supplier`, который вызывается только при отсутствии значения.

### orElseThrow

```java
User user = optional.orElseThrow(
        () -> new UserNotFoundException(email)
);
```

Основной способ превратить отсутствие результата в бизнес-исключение. Именно так
чаще всего выглядит сервисный слой:

```java
public User getUser(long id) {
    return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
}
```

---

## orElse и orElseGet

Самый частый вопрос по теме.

Разница в том, когда вычисляется альтернатива. Аргумент `orElse()` — обычное
выражение, поэтому он вычисляется **всегда**, независимо от наличия значения.
Аргумент `orElseGet()` — `Supplier`, и его `get()` вызывается только при пустом
`Optional`.

```java
Optional<User> optional = Optional.of(existingUser);

User a = optional.orElse(createGuest());       // createGuest() выполнится
User b = optional.orElseGet(this::createGuest); // createGuest() не выполнится
```

В обоих случаях результат один и тот же — `existingUser`. Но в первом варианте
лишняя работа уже сделана.

Пока альтернатива дешёвая, разница только в наносекундах:

```java
String name = optional.map(User::getName).orElse("unknown");
```

Здесь `orElse()` уместнее: константа, `Supplier` был бы шумом.

Разница становится существенной, когда альтернатива дорогая или имеет побочный
эффект:

```java
User user = optional.orElse(userRepository.createGuest());
```

Запрос к базе выполнится при каждом вызове, даже когда пользователь найден. Это
не ошибка компиляции и не исключение — просто лишние обращения к БД, которые
трудно заметить.

```text
orElse(value)
→ аргумент вычисляется всегда
→ подходит для готовой константы

orElseGet(supplier)
→ supplier вызывается только при отсутствии значения
→ нужен для вычислений, запросов и побочных эффектов
```

Аналогичное правило действует для `orElseThrow()`: создание объекта исключения там
тоже отложено в `Supplier`, поэтому stack trace не собирается впустую.

---

## Преобразование

### map

```java
Optional<String> name = optional.map(User::getName);
```

Применяет функцию к значению, если оно есть. Пустой `Optional` остаётся пустым, и
функция не вызывается.

Если функция вернёт `null`, результатом станет пустой `Optional` — `map()`
оборачивает результат через `ofNullable()`.

### flatMap

Нужен, когда функция сама возвращает `Optional`:

```java
Optional<Address> address = optional.flatMap(User::findAddress);
```

С `map()` получилось бы вложение:

```java
Optional<Optional<Address>> nested = optional.map(User::findAddress);
```

```text
map      → T → R,           результат оборачивается автоматически
flatMap  → T → Optional<R>, лишнее оборачивание не создаётся
```

Соотношение ровно то же, что между `Stream.map()` и `Stream.flatMap()` и между
`CompletableFuture.thenApply()` и `thenCompose()`.

### filter

```java
Optional<User> active = optional.filter(User::isActive);
```

Если предикат не выполнился, результат пуст.

### Цепочки

Основная сила `Optional` — в комбинации операций:

```java
String city = userRepository.findById(id)
        .filter(User::isActive)
        .flatMap(User::findAddress)
        .map(Address::getCity)
        .orElse("unknown");
```

Ни одной явной проверки на `null`, и каждый шаг выполняется только если предыдущий
дал результат.

### or

С Java 9 можно подставить альтернативный `Optional`:

```java
Optional<User> user = findInCache(id)
        .or(() -> findInDatabase(id));
```

В отличие от `orElseGet()`, результатом остаётся `Optional`, поэтому цепочку можно
продолжать.

### stream

С Java 9 `Optional` превращается в поток из нуля или одного элемента:

```java
List<User> users = ids.stream()
        .map(userRepository::findById)
        .flatMap(Optional::stream)
        .toList();
```

Пустые `Optional` отбрасываются, значения остаются. До Java 9 писали
`.filter(Optional::isPresent).map(Optional::get)`.

---

## Действия

### ifPresent

```java
optional.ifPresent(user -> log.info("found {}", user.getEmail()));
```

### ifPresentOrElse

С Java 9 можно задать и ветку отсутствия:

```java
optional.ifPresentOrElse(
        user -> log.info("found {}", user.getEmail()),
        () -> log.warn("user not found")
);
```

Обе ветки ничего не возвращают. Если нужен результат, используются `map()` и
`orElse()`, а не эти методы.

---

## Где Optional использовать не стоит

Это вторая половина темы, и на собеседовании она ценится не меньше знания API.

### Поле сущности или DTO

```java
class User {
    private Optional<String> middleName; // так не делают
}
```

Причины:

- `Optional` не реализует `Serializable`;
- Hibernate и большинство библиотек сериализации не рассчитаны на такое поле;
- появляется третье состояние: поле может быть `null` само по себе;
- на каждый экземпляр создаётся лишняя обёртка.

Правильно — обычное поле, допускающее `null`, и `Optional` в геттере, если он
нужен:

```java
class User {

    private String middleName;

    public Optional<String> findMiddleName() {
        return Optional.ofNullable(middleName);
    }
}
```

### Параметр метода

```java
void register(String email, Optional<String> phone) { // так не делают
}
```

Вызывающий обязан оборачивать аргумент вручную, а сам параметр всё равно может
оказаться `null`. Вместо этого используют перегрузку или допускают `null` с явной
документацией:

```java
void register(String email);
void register(String email, String phone);
```

### Коллекции

```java
Optional<List<User>> findAll(); // так не делают
```

У коллекции уже есть способ выразить отсутствие результата — пустая коллекция.
Двойная семантика (пустой `Optional` против пустого списка) только добавляет
ветвлений на вызывающей стороне.

По той же причине не нужен `List<Optional<User>>`: список должен содержать
найденные элементы, а не дырки.

### Замена исключений

`Optional` подходит там, где отсутствие — ожидаемый исход. Если аргумент
некорректен или нарушен инвариант, это исключение, а не пустой `Optional`.

### Конструкторы и внутренние поля

Обёртка внутри класса, куда снаружи никто не заглядывает, ничего не даёт, а
накладные расходы и лишний уровень косвенности остаются.

```text
уместно
→ возвращаемое значение метода поиска

обычно неуместно
→ поле сущности
→ параметр метода
→ обёртка вокруг коллекции
→ замена исключения
```

---

## Optional в Spring и JPA

Spring Data возвращает `Optional` из стандартных методов поиска:

```java
Optional<User> findById(Long id);
```

Производные методы репозитория тоже могут объявлять `Optional`:

```java
Optional<User> findByEmail(String email);
```

Отсюда типовой сервисный код:

```java
@Transactional(readOnly = true)
public UserView getUser(long id) {
    return userRepository.findById(id)
            .map(userMapper::toView)
            .orElseThrow(() -> new UserNotFoundException(id));
}
```

Здесь `Optional` играет ровно свою роль: репозиторий сообщает об отсутствии, а
сервис решает, что это значит для бизнес-сценария, и превращает в исключение,
которое затем обработает `@ControllerAdvice`.

---

## Типичные ошибки

### isPresent вместе с get

```java
if (optional.isPresent()) {
    process(optional.get());
}
```

Это переписанная проверка на `null`. Нужен `ifPresent()`, `map()` или
`orElseThrow()`.

### get без проверки

```java
User user = optional.get();
```

`NoSuchElementException` вместо `NullPointerException` — не улучшение. Используется
`orElseThrow()` с осмысленным исключением.

### Optional.of вместо ofNullable

```java
Optional.of(repository.findRaw(id)); // NPE при отсутствии
```

### Дорогое выражение в orElse

```java
optional.orElse(loadDefaultFromDatabase());
```

Запрос выполняется всегда. Нужен `orElseGet()`.

### Optional как поле сущности

Не сериализуется, ломает ORM, добавляет третье состояние.

### Optional вокруг коллекции

Пустая коллекция уже выражает отсутствие результата.

### Возврат null вместо пустого Optional

```java
public Optional<User> findByEmail(String email) {
    return null; // худшее из обоих миров
}
```

Вызывающий видит в сигнатуре гарантию, которой нет.

### Сравнение через ==

```java
if (optional == Optional.empty()) { // не работает надёжно
}
```

`Optional.empty()` не обязан возвращать один и тот же экземпляр в смысле, на
который можно опираться. Проверка — `isEmpty()`.

При этом `equals()` у `Optional` сравнивает содержимое: два `Optional` с равными
значениями равны, и два пустых равны между собой.

### Вложенный Optional

```java
Optional<Optional<Address>> nested = optional.map(User::findAddress);
```

Признак того, что нужен `flatMap()`.

### Optional ради защиты от NPE

Оборачивание всего подряд не убирает `null` из программы, а добавляет уровень
косвенности. `Optional` решает задачу выразительности сигнатуры, а не задачу
безопасности вообще.

---

## Краткая памятка

```text
of(value)          → NPE при null
ofNullable(value)  → null становится empty
empty()            → пустой

get()              → нежелателен, предпочтителен orElseThrow()
orElse(value)      → аргумент вычисляется всегда
orElseGet(supplier)→ вызывается только при отсутствии
orElseThrow(sup)   → исключение создаётся только при отсутствии

map      → T → R
flatMap  → T → Optional<R>
filter   → предикат не выполнен → empty
or       → альтернативный Optional, Java 9
stream   → 0 или 1 элемент, Java 9

ifPresent        → действие при наличии
ifPresentOrElse  → обе ветки, Java 9
isEmpty          → Java 11
```

```text
Optional предназначен для
→ возвращаемого значения метода

Optional обычно не предназначен для
→ полей
→ параметров
→ коллекций
→ замены исключений
```

```text
Optional не Serializable
```

---

## Краткий ответ для собеседования

`Optional<T>` — контейнер, который может содержать значение или быть пустым. Он
создавался как тип возвращаемого значения для методов, где отсутствие результата
является нормальным исходом, чтобы эта возможность была видна в сигнатуре, а не
обнаруживалась через `NullPointerException`.

Создаётся через `of()`, который бросает `NPE` на `null`, `ofNullable()`, который
превращает `null` в пустой контейнер, и `empty()`. Извлекается через `orElse()`,
`orElseGet()` и `orElseThrow()`. `get()` с Java 10 нежелателен: `orElseThrow()`
делает то же самое, но честно сообщает о возможном падении.

Главное практическое различие — между `orElse()` и `orElseGet()`. Аргумент
`orElse()` вычисляется всегда, даже когда значение присутствует, поэтому дорогие
вычисления и запросы к базе помещают в `orElseGet()`.

Преобразования выполняются через `map()`, `flatMap()` и `filter()`, что позволяет
строить цепочки без явных проверок. `flatMap()` нужен, когда функция сама
возвращает `Optional`.

`Optional` не стоит использовать как поле сущности, поскольку он не сериализуем и
плохо сочетается с ORM, как параметр метода, поскольку вызывающий всё равно может
передать `null`, и как обёртку вокруг коллекции, поскольку пустая коллекция уже
выражает отсутствие результата.

---

## Вопросы на собеседовании

### 1. Какую задачу решает Optional?

**Ответ:** делает возможное отсутствие результата видимым в сигнатуре метода.
Вызывающий обязан обработать этот случай явно, а не узнавать о нём через
`NullPointerException` в неожиданном месте.

### 2. Чем отличаются of, ofNullable и empty?

**Ответ:** `of()` требует ненулевое значение и бросает `NPE` на `null`.
`ofNullable()` превращает `null` в пустой `Optional`. `empty()` создаёт пустой
контейнер явно.

### 3. Когда уместен of, а когда ofNullable?

**Ответ:** `of()` — когда `null` означал бы ошибку в программе и падение должно
произойти сразу. `ofNullable()` — при оборачивании результата API, который
законно может вернуть `null`.

### 4. В чём разница между orElse и orElseGet?

**Ответ:** аргумент `orElse()` вычисляется всегда, потому что это обычное
выражение. `orElseGet()` принимает `Supplier` и вызывает его только при отсутствии
значения.

### 5. Когда эта разница важна на практике?

**Ответ:** когда альтернатива дорогая или имеет побочный эффект — запрос к базе,
обращение к внешнему сервису, создание тяжёлого объекта. Для готовой константы
разницы нет и `orElse()` читается лучше.

### 6. Почему get считается нежелательным?

**Ответ:** он не сообщает о возможном `NoSuchElementException`. С Java 10 есть
`orElseThrow()` без аргументов с тем же поведением и более честным именем.

### 7. Чем map отличается от flatMap?

**Ответ:** `map()` принимает функцию `T → R` и оборачивает результат сам.
`flatMap()` принимает функцию `T → Optional<R>` и не создаёт вложенный `Optional`.

### 8. Что вернёт map, если функция вернула null?

**Ответ:** пустой `Optional`. Результат оборачивается через `ofNullable()`.

### 9. Можно ли использовать Optional как поле сущности?

**Ответ:** обычно нет. `Optional` не реализует `Serializable`, плохо сочетается с
Hibernate и сериализацией, добавляет третье состояние, поскольку само поле тоже
может быть `null`. Поле оставляют обычным, а `Optional` возвращают из геттера.

### 10. Стоит ли принимать Optional параметром метода?

**Ответ:** обычно нет. Вызывающий вынужден оборачивать аргумент, а сам параметр
всё равно может оказаться `null`. Лучше перегрузка метода.

### 11. Стоит ли возвращать Optional<List<T>>?

**Ответ:** нет. Пустая коллекция уже выражает отсутствие результата, а двойная
семантика добавляет лишние ветвления.

### 12. Как отфильтровать пустые Optional в стриме?

**Ответ:** через `flatMap(Optional::stream)` начиная с Java 9. Раньше писали
`filter(Optional::isPresent).map(Optional::get)`.

### 13. Что делает метод or?

**Ответ:** подставляет альтернативный `Optional`, если текущий пуст. В отличие от
`orElseGet()`, результатом остаётся `Optional`, поэтому цепочку можно продолжить.

### 14. Можно ли сравнивать Optional через ==?

**Ответ:** нет, для проверки на пустоту используется `isEmpty()`. При этом
`equals()` сравнивает содержимое: два `Optional` с равными значениями равны.

### 15. Заменяет ли Optional проверки на null во всём коде?

**Ответ:** нет. Он решает задачу выразительности сигнатуры возвращаемого значения.
Внутри методов, в полях и в параметрах обычные проверки остаются уместными.

### 16. Что не так с конструкцией isPresent плюс get?

**Ответ:** это переписанная проверка на `null`, которая не даёт преимуществ
`Optional`. Тот же смысл выражается через `ifPresent()`, `map()` или
`orElseThrow()`.

---

## См. также

- [`06-stream-api.md`](06-stream-api.md) — `findFirst()` и `findAny()` возвращают
  `Optional`, а `reduce()` без начального значения тоже
- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  `Supplier`, `Function` и `Predicate` в сигнатурах методов `Optional`
- [`05-exceptions.md`](05-exceptions.md) — превращение пустого результата в
  бизнес-исключение через `orElseThrow()`