# Spring Boot

## Какую задачу решает

Обычное Spring-приложение требовало большого объёма настройки: XML или
Java-конфигурация для источника данных, транзакционного менеджера, `EntityManager`,
диспетчера запросов, конвертеров сообщений. Плюс подбор совместимых версий
десятков библиотек и развёртывание в отдельно установленный контейнер сервлетов.

Spring Boot убирает эту работу тремя средствами:

```text
стартеры          → согласованный набор зависимостей одной строкой
автоконфигурация  → бины создаются сами, если в classpath есть нужные классы
встроенный сервер → приложение запускается как обычный Java-процесс
```

Важно понимать, что Boot — не новый фреймворк поверх Spring и не замена ему. Это
слой соглашений: те же бины, тот же контейнер, та же AOP, просто настроенные
заранее.

---

## @SpringBootApplication

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

Аннотация составная и раскрывается в три:

```text
@SpringBootConfiguration → по сути @Configuration
@ComponentScan           → сканирование пакета этого класса и вложенных
@EnableAutoConfiguration → включение механизма автоконфигурации
```

Отсюда важное практическое следствие: базовым пакетом сканирования служит пакет
главного класса. Компоненты, лежащие выше по дереву пакетов или в соседней ветке,
найдены не будут.

```text
com.example
├── Application.java        ← главный класс
├── service                 ← найдётся
└── repository              ← найдётся

com.other
└── UtilService             ← не найдётся
```

Это самая частая причина ошибки «бин не найден» у начинающих.

---

## Автоконфигурация

### Как она устроена

Механизм проще, чем кажется, и целиком строится на уже разобранных вещах:
аннотациях, условной регистрации и `BeanDefinition`.

```text
1. @EnableAutoConfiguration импортирует селектор автоконфигураций
2. селектор читает список классов из файла в META-INF
3. каждый класс — обычный @Configuration с условиями
4. условия проверяются, подходящие конфигурации применяются
```

Список хранится в файле:

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

До Spring Boot 2.7 использовался `META-INF/spring.factories` — в старых статьях и
библиотеках встречается именно он.

### Условия

Автоконфигурация — это обычный класс с `@Conditional`-аннотациями:

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {

    @Bean
    public DataSource dataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
}
```

Читается так: если в classpath есть класс `DataSource` и пользователь не объявил
собственный бин этого типа — создать его самим.

Основные условия:

```text
@ConditionalOnClass         → класс присутствует в classpath
@ConditionalOnMissingClass  → класса нет
@ConditionalOnBean          → бин уже определён
@ConditionalOnMissingBean   → бина нет ← ключевое для переопределения
@ConditionalOnProperty      → свойство имеет заданное значение
@ConditionalOnWebApplication → это веб-приложение
@ConditionalOnResource      → файл существует
```

`@ConditionalOnMissingBean` — то, что делает автоконфигурацию ненавязчивой.
Объявив собственный бин, вы автоматически отключаете стандартный, без каких-либо
дополнительных действий.

### Порядок применения

Автоконфигурации зависят друг от друга, и порядок задаётся явно:

```java
@AutoConfiguration(after = DataSourceAutoConfiguration.class)
```

Это существенно: `@ConditionalOnMissingBean` проверяется в момент применения
конфигурации, поэтому неверный порядок дал бы неверный результат. Пользовательские
бины при этом обрабатываются раньше всех автоконфигураций — именно поэтому
переопределение работает надёжно.

### Как посмотреть, что происходит

```text
--debug при запуске
```

Выводится отчёт с двумя разделами: какие автоконфигурации применились и по каким
условиям, и какие не применились с указанием причины. Это первое, куда стоит
смотреть, когда бин появился неожиданно или, наоборот, не появился.

Альтернатива — эндпоинт Actuator `/actuator/conditions`.

### Отключение

```java
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)
```

```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

Типичный случай — приложение без базы данных, в котором стартер JPA присутствует
транзитивно и Boot пытается настроить источник данных.

---

## Стартеры

Стартер — модуль без кода, состоящий из одного файла зависимостей. Его задача —
принести согласованный набор библиотек.

```gradle
implementation 'org.springframework.boot:spring-boot-starter-web'
```

Эта строка приносит Spring MVC, Jackson, валидацию, встроенный Tomcat и
логирование.

```text
spring-boot-starter-web          → REST и MVC
spring-boot-starter-data-jpa     → JPA, Hibernate, пул соединений
spring-boot-starter-security     → аутентификация и авторизация
spring-boot-starter-validation   → Bean Validation
spring-boot-starter-test         → JUnit 5, Mockito, AssertJ, тестовый контекст
spring-boot-starter-actuator     → метрики и эндпоинты состояния
```

### Управление версиями

Версии не указываются, потому что Boot предоставляет BOM — спецификацию, где
зафиксированы совместимые версии сотен библиотек.

```gradle
plugins {
    id 'org.springframework.boot' version '3.3.0'
    id 'io.spring.dependency-management' version '1.1.5'
}
```

Это едва ли не главная ценность Boot на практике: подбор совместимых версий Spring,
Hibernate, Jackson и драйверов вручную — работа неблагодарная и чреватая
конфликтами.

Переопределить версию можно, но осознанно:

```gradle
ext['hibernate.version'] = '6.5.0.Final'
```

### Собственный стартер

Схема простая: модуль с автоконфигурацией, файл `AutoConfiguration.imports` и
класс свойств. Так оформляют общую инфраструктуру для нескольких сервисов —
логирование, трассировку, клиенты внутренних API.

---

## Конфигурация

### Файлы свойств

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/app
    username: app
  jpa:
    hibernate:
      ddl-auto: validate

payment:
  url: https://api.example.com
  timeout: 5000
```

YAML и properties равнозначны; YAML удобнее для вложенных структур.

### Порядок источников

Свойства приходят из разных мест, и приоритет фиксирован. От высшего к низшему, в
сокращении:

```text
1. аргументы командной строки
2. переменные окружения
3. application-{profile}.yml вне jar
4. application.yml вне jar
5. application-{profile}.yml внутри jar
6. application.yml внутри jar
7. значения по умолчанию из автоконфигураций
```

Отсюда стандартная практика: значения по умолчанию лежат в файле внутри артефакта,
а секреты и специфичные для среды параметры приходят из переменных окружения. Это
же удобно для контейнеров.

### Relaxed binding

Одно и то же свойство можно записать по-разному:

```text
payment.api-url
payment.apiUrl
payment.api_url
PAYMENT_APIURL
```

Все варианты привязываются к одному полю. Это важно для переменных окружения, где
точки и дефисы недопустимы: `SPRING_DATASOURCE_URL` соответствует
`spring.datasource.url`.

### @ConfigurationProperties

```java
@ConfigurationProperties(prefix = "payment")
@Validated
public record PaymentProperties(
        @NotBlank String url,
        @Positive int timeout
) {
}
```

Подключение:

```java
@EnableConfigurationProperties(PaymentProperties.class)
```

Преимущества перед `@Value`: типобезопасность, валидация при старте, группировка
связанных настроек, поддержка вложенных объектов и коллекций, автодополнение в IDE.

`@Value` уместен для одиночного значения, `@ConfigurationProperties` — для группы.

### Профили

```yaml
# application.yml
spring:
  profiles:
    active: dev

---
spring:
  config:
    activate:
      on-profile: dev
logging:
  level:
    root: DEBUG

---
spring:
  config:
    activate:
      on-profile: prod
logging:
  level:
    root: WARN
```

Либо отдельными файлами: `application-dev.yml`, `application-prod.yml`. Они
дополняют основной `application.yml`, а не заменяют его.

Активация:

```text
--spring.profiles.active=prod
SPRING_PROFILES_ACTIVE=prod
```

---

## Встроенный сервер

Boot включает сервер прямо в приложение, и запуск сводится к обычному
`java -jar`. Отдельно устанавливать Tomcat не требуется.

```text
Tomcat  → по умолчанию
Jetty   → альтернатива
Undertow → альтернатива
Netty   → для реактивного стека
```

Замена выполняется исключением зависимости:

```gradle
implementation('org.springframework.boot:spring-boot-starter-web') {
    exclude module: 'spring-boot-starter-tomcat'
}
implementation 'org.springframework.boot:spring-boot-starter-undertow'
```

### Исполняемый jar

Boot собирает так называемый fat jar, содержащий и приложение, и все зависимости.
Устройство отличается от обычного архива:

```text
BOOT-INF/classes/   → классы приложения
BOOT-INF/lib/       → jar-файлы зависимостей целиком
org/springframework/boot/loader/  → загрузчик
META-INF/MANIFEST.MF → Main-Class: JarLauncher
```

Стандартный загрузчик классов Java не умеет читать вложенные jar, поэтому Boot
использует собственный: `JarLauncher` создаёт специальный `ClassLoader`, который
работает с архивами внутри архива, и уже затем запускает главный класс приложения.

Это объясняет, почему у fat jar в манифесте указан не ваш класс, а `JarLauncher`, и
почему такой архив нельзя просто подключить как библиотеку к другому проекту.

---

## Что происходит при старте

```text
SpringApplication.run()

1. определяется тип приложения: веб, реактивное или обычное
2. загружаются ApplicationContextInitializer и ApplicationListener
3. подготавливается Environment: файлы свойств, переменные, аргументы
4. выводится баннер
5. создаётся ApplicationContext нужного типа
6. регистрируются определения бинов из сканирования и автоконфигураций
7. применяются BeanFactoryPostProcessor
8. создаются singleton-бины, работают BeanPostProcessor, создаются прокси
9. запускается встроенный сервер
10. вызываются ApplicationRunner и CommandLineRunner
11. публикуется ApplicationReadyEvent
```

Шаги 6–8 — это обычный жизненный цикл контейнера из Spring Core. Специфика Boot
сосредоточена в шагах 3, 6 и 9.

### Код при старте

```java
@Component
public class DataInitializer implements ApplicationRunner {

    @Override
    public void run(ApplicationArguments args) {
        // контекст полностью готов
    }
}
```

Отличие от `@PostConstruct` существенное: `ApplicationRunner` выполняется после
того, как весь контекст создан, поэтому все бины уже проксированы и
`@Transactional` работает. В `@PostConstruct` прокси ещё не существует.

---

## Actuator

Набор эндпоинтов для эксплуатации приложения.

```text
/actuator/health    → состояние приложения и его зависимостей
/actuator/info      → произвольная информация о сборке
/actuator/metrics   → метрики
/actuator/prometheus → метрики в формате Prometheus
/actuator/env       → свойства окружения
/actuator/loggers   → просмотр и изменение уровней логирования на лету
/actuator/conditions → отчёт по автоконфигурации
```

По умолчанию наружу открыты только `health` и `info` — остальные нужно включать
явно:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
```

Осторожность здесь оправдана: `/actuator/env` показывает свойства окружения, а
`/actuator/heapdump` отдаёт дамп памяти. В открытом доступе это утечка.

Практически ценны два эндпоинта: `health` используется контейнерными оркестраторами
для проверок жизнеспособности, а `loggers` позволяет включить отладочный уровень в
проде без перезапуска.

---

## Типичные ошибки

### Главный класс не в корневом пакете

Сканируется пакет главного класса и вложенные. Компоненты в соседних ветках дерева
пакетов не найдутся.

### Добавлять свой @ComponentScan

Он заменяет настройку из `@SpringBootApplication`, а не дополняет её. Часть
компонентов может перестать находиться.

### Ожидать, что автоконфигурация переопределит ваш бин

Наоборот: `@ConditionalOnMissingBean` означает, что ваш бин отменяет
автоматический.

### Не понимать приоритет источников свойств

Переменная окружения перекроет значение из `application.yml`. Это задумано, но
приводит к недоумению при отладке.

### Считать application-prod.yml заменой application.yml

Профильный файл дополняет основной, а не заменяет.

### Забывать @EnableConfigurationProperties

Без него класс свойств не станет бином, если он не помечен `@Component`.

### Открывать все эндпоинты Actuator

`/actuator/env` и `/actuator/heapdump` в открытом доступе раскрывают конфигурацию и
содержимое памяти.

### Использовать fat jar как библиотеку

Структура нестандартная, классы лежат в `BOOT-INF/classes`. Для переиспользования
нужен обычный jar.

### Полагаться на @Transactional в @PostConstruct

Прокси ещё не создан. Нужен `ApplicationRunner` или `ApplicationReadyEvent`.

### Указывать версии библиотек вручную

Смысл BOM в согласованности. Ручное переопределение легко ломает совместимость.

---

## Краткая памятка

```text
@SpringBootApplication
= @SpringBootConfiguration + @ComponentScan + @EnableAutoConfiguration

сканируется пакет главного класса и вложенные
```

```text
автоконфигурация
список в META-INF/spring/...AutoConfiguration.imports
(до 2.7 — spring.factories)

обычные @Configuration с условиями
@ConditionalOnClass / @ConditionalOnMissingBean / @ConditionalOnProperty

@ConditionalOnMissingBean → ваш бин отменяет автоматический
--debug → отчёт о применённых и отклонённых конфигурациях
```

```text
стартеры → набор зависимостей
BOM      → согласованные версии, поэтому версии не указываются
```

```text
приоритет свойств
аргументы → переменные окружения → внешние файлы → файлы в jar → умолчания

relaxed binding
payment.api-url = payment.apiUrl = PAYMENT_APIURL
```

```text
fat jar
BOOT-INF/classes, BOOT-INF/lib
Main-Class = JarLauncher, собственный ClassLoader для вложенных jar
```

```text
@PostConstruct     → прокси ещё нет
ApplicationRunner  → контекст готов полностью
```

---

## Краткий ответ для собеседования

Spring Boot — слой соглашений поверх Spring, а не отдельный фреймворк. Он решает
три задачи: стартеры приносят согласованный набор зависимостей, автоконфигурация
создаёт типовые бины, встроенный сервер позволяет запускать приложение обычной
командой `java -jar`.

`@SpringBootApplication` объединяет `@Configuration`, `@ComponentScan` и
`@EnableAutoConfiguration`, поэтому сканируется пакет главного класса и вложенные в
него.

Автоконфигурация устроена просто: список классов лежит в файле в `META-INF`, каждый
класс — обычная конфигурация с условными аннотациями. Условия проверяют наличие
классов в classpath, значения свойств и отсутствие пользовательских бинов. Ключевое
из них — `@ConditionalOnMissingBean`: объявив собственный бин, вы автоматически
отключаете стандартный. Посмотреть, что применилось и почему, можно запуском с
флагом `--debug`.

Стартеры сами по себе не содержат кода, они приносят зависимости, а версии берутся
из BOM, где зафиксированы совместимые сочетания библиотек.

Свойства приходят из нескольких источников с фиксированным приоритетом: аргументы
командной строки, переменные окружения, внешние файлы, файлы внутри артефакта,
значения по умолчанию. Благодаря relaxed binding одно и то же свойство можно
записать разными способами, что позволяет задавать его переменной окружения.

Приложение собирается в исполняемый jar с зависимостями внутри. Поскольку
стандартный загрузчик не умеет читать вложенные архивы, точкой входа служит
`JarLauncher` со своим загрузчиком классов.

---

## Вопросы на собеседовании

### 1. Что даёт Spring Boot по сравнению с обычным Spring?

**Ответ:** стартеры с согласованными зависимостями, автоконфигурацию типовых бинов
и встроенный сервер. Это слой соглашений, контейнер и механизмы остаются теми же.

### 2. Из чего состоит @SpringBootApplication?

**Ответ:** из `@SpringBootConfiguration`, `@ComponentScan` и
`@EnableAutoConfiguration`.

### 3. Какие пакеты сканируются по умолчанию?

**Ответ:** пакет главного класса и все вложенные в него.

### 4. Как работает автоконфигурация?

**Ответ:** `@EnableAutoConfiguration` подключает список классов из файла в
`META-INF`. Каждый класс — конфигурация с условными аннотациями, и применяются
только те, чьи условия выполнены.

### 5. Где хранится список автоконфигураций?

**Ответ:** в `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
До версии 2.7 использовался `META-INF/spring.factories`.

### 6. Какие условные аннотации применяются?

**Ответ:** `@ConditionalOnClass`, `@ConditionalOnMissingBean`,
`@ConditionalOnBean`, `@ConditionalOnProperty`, `@ConditionalOnWebApplication` и
другие.

### 7. Как переопределить бин, создаваемый автоконфигурацией?

**Ответ:** объявить собственный бин того же типа. Автоконфигурация помечена
`@ConditionalOnMissingBean` и отключится сама.

### 8. Как посмотреть, какие автоконфигурации применились?

**Ответ:** запустить с флагом `--debug` либо открыть эндпоинт
`/actuator/conditions`. Отчёт покажет и применённые, и отклонённые с причиной.

### 9. Что такое стартер?

**Ответ:** модуль без кода, приносящий согласованный набор зависимостей для
определённой задачи.

### 10. Почему в зависимостях не указываются версии?

**Ответ:** Boot предоставляет BOM с зафиксированными совместимыми версиями
библиотек.

### 11. Какой приоритет у источников свойств?

**Ответ:** аргументы командной строки, затем переменные окружения, внешние файлы
конфигурации, файлы внутри артефакта и значения по умолчанию.

### 12. Что такое relaxed binding?

**Ответ:** привязка одного свойства к разным вариантам написания — с дефисами, в
camelCase, с подчёркиваниями, в верхнем регистре. Нужна для переменных окружения.

### 13. Чем @ConfigurationProperties лучше @Value?

**Ответ:** типобезопасность, валидация при старте, группировка связанных настроек,
поддержка вложенных структур. `@Value` уместен для одиночного значения.

### 14. Как работают профили?

**Ответ:** активный профиль определяет, какие бины регистрируются и какие файлы
свойств применяются. Профильный файл дополняет основной, а не заменяет его.

### 15. Как заменить встроенный Tomcat?

**Ответ:** исключить `spring-boot-starter-tomcat` из веб-стартера и добавить
стартер Jetty или Undertow.

### 16. Как устроен исполняемый jar?

**Ответ:** классы приложения лежат в `BOOT-INF/classes`, зависимости целыми
архивами — в `BOOT-INF/lib`. Точка входа — `JarLauncher`, который создаёт загрузчик,
умеющий читать вложенные jar.

### 17. Почему нельзя подключить fat jar как библиотеку?

**Ответ:** структура нестандартная, классы находятся не в корне архива. Нужен
обычный jar.

### 18. Что происходит при вызове SpringApplication.run?

**Ответ:** определяется тип приложения, готовится окружение, создаётся контекст,
регистрируются определения бинов из сканирования и автоконфигураций, создаются
бины и прокси, запускается сервер, вызываются runner-ы и публикуется
`ApplicationReadyEvent`.

### 19. Чем ApplicationRunner отличается от @PostConstruct?

**Ответ:** `ApplicationRunner` выполняется после полной готовности контекста, когда
все бины проксированы. В `@PostConstruct` прокси ещё не создан, поэтому
`@Transactional` там не работает.

### 20. Зачем нужен Actuator и о чём стоит помнить?

**Ответ:** он даёт эндпоинты для эксплуатации — проверку состояния, метрики,
управление уровнями логирования. Наружу по умолчанию открыты только `health` и
`info`, и расширять этот список нужно осторожно: `env` и `heapdump` раскрывают
конфигурацию и содержимое памяти.

---

## См. также

- [`01-spring-core.md`](01-spring-core.md) — контейнер, жизненный цикл бинов и
  условная регистрация, на которых построена автоконфигурация
- [`02-spring-aop.md`](02-spring-aop.md) — почему прокси не существует на момент
  `@PostConstruct`
- [`../java-core/11-annotations.md`](../java-core/11-annotations.md) —
  мета-аннотации, из которых собран `@SpringBootApplication`
- [`../jvm/01-jvm-memory.md`](../jvm/01-jvm-memory.md) — загрузчики классов,
  которые Boot расширяет ради вложенных jar