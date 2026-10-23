# Журнал ознакомления

Этот файл фиксирует первый проход по конспектам — чтение и повторение материала.

Он не заменяет [`topic-tracker.md`](topic-tracker.md). Там отметка `[x]` ставится
только после прогона по вопросам вслух. Здесь отметка означает другое: конспект
прочитан внимательно, а не пролистан.

## Как вести

Отметка `[x]` ставится, когда конспект прочитан целиком. Рядом пишется дата.

В колонку «Заметки» записывается то, что оказалось новым, забытым или непонятным.
Это будущий список для прогона по вопросам. Если всё было знакомо, колонку можно
оставить пустой.

```text
[ ] → не читал
[~] → начал, не дочитал
[x] → прочитал целиком
```

## Порядок

Порядок задан по весу темы на собеседовании, а не по номерам файлов. Внутри
этапа сохраняется порядок блоков из трекера, потому что он учитывает зависимости
между темами.

Kafka стоит сразу после Spring: она заявлена в опыте, поэтому про неё спросят
глубже, чем обычно спрашивают у джуна.

При чтении полезно сверяться с таблицей «Сквозные темы» в трекере. Механизм,
который встречается в нескольких конспектах, лучше связать сразу.

---

## Этап 1. Ядро backend-интервью

### Протокол и база данных

| Конспект | Уровень | Прочитан | Дата       | Заметки                                                           |
|---|---|-----|------------|-------------------------------------------------------------------|
| [`http_rest/01-http-rest.md`](../http_rest/01-http-rest.md) | J | [x] | 23.10.2026 | нет, все понятно                                                  |
| [`databases/01-sql-basics.md`](../databases/01-sql-basics.md) | J | [x] | 23.10.2026 | тема глубоко разобрана, для собеседований как по мне даже слишком |
| [`databases/02-indexes.md`](../databases/02-indexes.md) | J+ | [ ] |            |                                                                   |
| [`databases/03-transactions.md`](../databases/03-transactions.md) | J+ | [ ] |            |                                                                   |
| [`databases/05-migrations.md`](../databases/05-migrations.md) | J+ | [ ] |            |                                                                   |

### Spring

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`spring/01-spring-core.md`](../spring/01-spring-core.md) | J | [ ] | | |
| [`spring/02-spring-aop.md`](../spring/02-spring-aop.md) | J+ | [ ] | | |
| [`spring/03-spring-boot.md`](../spring/03-spring-boot.md) | J | [ ] | | |
| [`spring/04-spring-mvc.md`](../spring/04-spring-mvc.md) | J | [ ] | | |
| [`spring/06-spring-security-jwt.md`](../spring/06-spring-security-jwt.md) | J+ | [ ] | | |
| [`spring/07-http-clients.md`](../spring/07-http-clients.md) | J+ | [ ] | | |

### Персистентность

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`hibernate/01-jpa-basics.md`](../hibernate/01-jpa-basics.md) | J | [ ] | | |
| [`hibernate/02-relationships-fetching.md`](../hibernate/02-relationships-fetching.md) | J | [ ] | | |
| [`hibernate/03-hibernate-problems.md`](../hibernate/03-hibernate-problems.md) | J+ | [ ] | | |
| [`spring/08-spring-data-jpa.md`](../spring/08-spring-data-jpa.md) | J | [ ] | | |
| [`spring/05-spring-transactions.md`](../spring/05-spring-transactions.md) | J+ | [ ] | | |
| [`databases/04-jdbc.md`](../databases/04-jdbc.md) | J+ | [ ] | | |

### Kafka

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`kafka/01-kafka.md`](../kafka/01-kafka.md) | J+ | [ ] | | |
| [`kafka/02-spring-kafka.md`](../kafka/02-spring-kafka.md) | J+ | [ ] | | |

---

## Этап 2. Java Core

### Основы языка и объектная модель

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`java-core/00-java-language-basics.md`](../java-core/00-java-language-basics.md) | J | [ ] | | |
| [`java-core/07-oop-object-string-wrappers.md`](../java-core/07-oop-object-string-wrappers.md) | J | [ ] | | |
| [`java-core/03-equals-hashcode.md`](../java-core/03-equals-hashcode.md) | J | [ ] | | |

### Коллекции

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`java-core/01-collections-framework.md`](../java-core/01-collections-framework.md) | J | [ ] | | |
| [`java-core/02-map.md`](../java-core/02-map.md) | J | [ ] | | |

### Обобщения и исключения

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`java-core/04-generics.md`](../java-core/04-generics.md) | J+ | [ ] | | |
| [`java-core/05-exceptions.md`](../java-core/05-exceptions.md) | J | [ ] | | |

### Функциональная Java

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`java-core/08-functional-interfaces-lambda.md`](../java-core/08-functional-interfaces-lambda.md) | J | [ ] | | |
| [`java-core/06-stream-api.md`](../java-core/06-stream-api.md) | J | [ ] | | |
| [`java-core/09-optional.md`](../java-core/09-optional.md) | J | [ ] | | |

### Современная Java и аннотации

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`java-core/10-modern-java.md`](../java-core/10-modern-java.md) | J+ | [ ] | | |
| [`java-core/11-annotations.md`](../java-core/11-annotations.md) | J+ | [ ] | | |

---

## Этап 3. JVM и конкурентность

### Устройство JVM

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`jvm/01-jvm-memory.md`](../jvm/01-jvm-memory.md) | J+ | [ ] | | |
| [`jvm/02-garbage-collection.md`](../jvm/02-garbage-collection.md) | M | [ ] | | |

### Модель памяти и потоки

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`concurrency/01-java-memory-model.md`](../concurrency/01-java-memory-model.md) | J+ | [ ] | | |
| [`concurrency/02-multithreading-basics.md`](../concurrency/02-multithreading-basics.md) | J | [ ] | | |

### Инструменты конкурентности

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`concurrency/03-locks-atomics-executors.md`](../concurrency/03-locks-atomics-executors.md) | J+ | [ ] | | |
| [`concurrency/04-concurrent-collections.md`](../concurrency/04-concurrent-collections.md) | J+ | [ ] | | |
| [`concurrency/05-completable-future.md`](../concurrency/05-completable-future.md) | J+ | [ ] | | |
| [`concurrency/06-virtual-threads.md`](../concurrency/06-virtual-threads.md) | M | [ ] | | |

---

## Этап 4. Эксплуатация и архитектура

### Эксплуатация

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`logging/01-logging.md`](../logging/01-logging.md) | J | [ ] | | |
| [`testing/01-testing.md`](../testing/01-testing.md) | J | [ ] | | |

### Архитектура и инфраструктура

| Конспект | Уровень | Прочитан | Дата | Заметки |
|---|---|---|---|---|
| [`system-design/01-backend-architecture.md`](../system-design/01-backend-architecture.md) | J+ | [ ] | | |
| [`system-design/02-system-design.md`](../system-design/02-system-design.md) | J+ | [ ] | | |
| [`docker/01-docker-cicd.md`](../docker/01-docker-cicd.md) | J+ | [ ] | | |
| [`git/01-git.md`](../git/01-git.md) | J | [ ] | | |
| [`build-tools/01-gradle-maven.md`](../build-tools/01-gradle-maven.md) | J | [ ] | | |
