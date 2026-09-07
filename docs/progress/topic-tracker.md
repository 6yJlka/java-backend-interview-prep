# Backend Interview Preparation Tracker

Все конспекты написаны. Этот файл задаёт порядок прохождения материала и
отслеживает, что уже проработано.

Подробные чек-листы по темам — в [`backend-roadmap.md`](backend-roadmap.md).

## Как проходить

Блоками, а не подряд по номерам файлов. Внутри блока конспекты связаны общим
механизмом, поэтому читаются вместе и лучше запоминаются.

После каждого блока — ответить на вопросы из прочитанных конспектов, не
подглядывая. Пока ответы не проговариваются вслух связно, блок не считается
пройденным.

Отметка `[x]` ставится не после чтения, а после успешного прогона по вопросам.

---

## Этап 1. Java Core

### Блок 1. Основы языка и объектная модель

- [ ] `java-core/00-java-language-basics.md`
- [ ] `java-core/07-oop-object-string-wrappers.md`
- [ ] `java-core/03-equals-hashcode.md`

Сквозная тема — pass-by-value и то, что копируется значение ссылки. Из неё же
вырастает контракт `equals` и `hashCode`.

### Блок 2. Коллекции

- [ ] `java-core/01-collections-framework.md`
- [ ] `java-core/02-map.md`

Читается сразу после контракта `equals` и `hashCode`: без него устройство
`HashMap` не объясняется.

### Блок 3. Обобщения и исключения

- [ ] `java-core/04-generics.md`
- [ ] `java-core/05-exceptions.md`

Generics опираются на ковариантность массивов из первого блока.

### Блок 4. Функциональная Java

- [ ] `java-core/08-functional-interfaces-lambda.md`
- [ ] `java-core/06-stream-api.md`
- [ ] `java-core/09-optional.md`

Строгий порядок: лямбды дают фундамент под Stream API, а `Optional` завершает
тему, поскольку его возвращают терминальные операции.

### Блок 5. Современная Java и аннотации

- [ ] `java-core/10-modern-java.md`
- [ ] `java-core/11-annotations.md`

Аннотации нужны до Spring: без `RetentionPolicy.RUNTIME` и рефлексии непонятно,
как работает `@Transactional`.

---

## Этап 2. JVM и конкурентность

### Блок 6. Устройство JVM

- [ ] `jvm/01-jvm-memory.md`
- [ ] `jvm/02-garbage-collection.md`

Второй конспект начинается там, где заканчивается первый.

### Блок 7. Модель памяти и потоки

- [ ] `concurrency/01-java-memory-model.md`
- [ ] `concurrency/02-multithreading-basics.md`

Только в этом порядке: `synchronized` и `volatile` объясняются гарантиями
happens-before, а не наоборот.

### Блок 8. Инструменты конкурентности

- [ ] `concurrency/03-locks-atomics-executors.md`
- [ ] `concurrency/04-concurrent-collections.md`
- [ ] `concurrency/05-completable-future.md`
- [ ] `concurrency/06-virtual-threads.md`

Самый объёмный блок. Для Junior-собеседования достаточно первых двух конспектов,
остальные — про запас.

---

## Этап 3. Ядро backend-интервью

Основной блок по важности: на собеседовании эти темы занимают больше половины
разговора.

### Блок 9. Протокол и база данных

- [ ] `http_rest/01-http-rest.md`
- [ ] `databases/01-sql-basics.md`
- [ ] `databases/02-indexes.md`
- [ ] `databases/03-transactions.md`

Транзакции читаются последними: они опираются на понимание блокировок и планов
запросов.

### Блок 10. Spring

- [ ] `spring/01-spring-core.md`
- [ ] `spring/02-spring-aop.md`
- [ ] `spring/03-spring-boot.md`
- [ ] `spring/04-spring-mvc.md`

Порядок обязателен: контейнер, затем прокси, затем автоконфигурация поверх обоих.

### Блок 11. Персистентность

- [ ] `hibernate/01-jpa-basics.md`
- [ ] `hibernate/02-relationships-fetching.md`
- [ ] `hibernate/03-hibernate-problems.md`
- [ ] `spring/05-spring-transactions.md`
- [ ] `databases/04-jdbc.md`

Транзакции Spring идут после Hibernate: они смыкают прокси, контекст
персистентности и уровни изоляции. JDBC в конце — как объяснение того, что лежит
под ORM.

---

## Этап 4. Production Backend

### Блок 12. Эксплуатация

- [ ] `logging/01-logging.md`
- [ ] `testing/01-testing.md`
- [ ] `kafka/01-kafka.md`

### Блок 13. Архитектура и инфраструктура

- [ ] `system-design/01-backend-architecture.md`
- [ ] `system-design/02-system-design.md`
- [ ] `docker/01-docker-cicd.md`
- [ ] `git/01-git.md`
- [ ] `build-tools/01-gradle-maven.md`

System Design читается после архитектуры: разбор задач опирается на приёмы
устойчивости из первого конспекта.

---

## Если времени мало

Приоритет при подготовке к конкретному собеседованию, в порядке убывания
вероятности вопроса:

```text
1. блок 9  — HTTP, SQL, индексы, транзакции
2. блок 10 — Spring
3. блок 11 — JPA и Hibernate
4. блок 2  — коллекции и Map
5. блок 1  — основы и equals / hashCode
6. блок 4  — лямбды и Stream API
7. блок 7  — модель памяти и потоки
```

Остальное — по времени.

---

## Сквозные темы

Механизмы, встречающиеся в нескольких конспектах. Полезно уметь показать связь:
на собеседовании это отличает понимание от заучивания.

| Тема | Где встречается |
|---|---|
| Идемпотентность | HTTP, Kafka, JPA `@Version`, архитектура, System Design |
| Оптимистическая блокировка | HTTP `ETag`, транзакции БД, JPA `@Version`, System Design |
| Прокси и self-invocation | аннотации, Spring AOP, Spring Transactions, Hibernate |
| Поверхностная неизменяемость | лямбды, `record`, JMM, коллекции |
| Привязка к потоку | Spring Transactions, `ThreadLocal`, MDC в логировании |
| Стирание типов | generics, коллекции, лямбды |

---

## Отложено

| Раздел | Тема | Причина |
|---|---|---|
| Java Core | Date and Time API | читается обзорно перед собеседованием |
| Java Core | Java I/O и NIO | для backend-интервью спрашивают редко |
| Concurrency | Structured Concurrency, Scoped Values | выходит за рамки Junior+ |