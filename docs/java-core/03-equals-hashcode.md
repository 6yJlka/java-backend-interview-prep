# equals и hashCode в Java

Методы `equals()` и `hashCode()` определены в классе `Object`, поэтому присутствуют у каждого Java-объекта.

```java
public class Object {

    public boolean equals(Object object) {
        return this == object;
    }

    public native int hashCode();
}
```

По умолчанию `equals()` сравнивает ссылки на объекты.

---

# Оператор == и метод equals

Для ссылочных типов оператор `==` проверяет, указывают ли две переменные на один объект.

```java
String first = new String("Java");
String second = new String("Java");

System.out.println(first == second);      // false
System.out.println(first.equals(second)); // true
```

Переменные содержат ссылки на разные объекты, поэтому `==` возвращает `false`.

Класс `String` переопределяет `equals()` и сравнивает последовательности символов.

```text
==       → сравнение ссылок
equals() → логическое равенство объектов
```

Для примитивных типов `==` сравнивает значения.

```java
int first = 10;
int second = 10;

System.out.println(first == second); // true
```

---

# Зачем переопределять equals

Рассмотрим объект, представляющий идентификатор пользователя.

```java
public final class UserKey {

    private final Long id;

    public UserKey(Long id) {
        this.id = id;
    }
}
```

Создадим два объекта:

```java
UserKey first = new UserKey(10L);
UserKey second = new UserKey(10L);
```

Логически они представляют один идентификатор.

Но стандартный `equals()` сравнивает ссылки:

```java
first.equals(second); // false
```

Для логического сравнения метод нужно переопределить.

```java
@Override
public boolean equals(Object object) {
    if (this == object) {
        return true;
    }

    if (!(object instanceof UserKey other)) {
        return false;
    }

    return id.equals(other.id);
}
```

Теперь:

```java
first.equals(second); // true
```

---

# Контракт equals

Корректный метод `equals()` обязан соблюдать пять требований.

## Рефлексивность

Объект равен самому себе.

```java
x.equals(x) == true
```

## Симметричность

Если `x` равен `y`, то `y` должен быть равен `x`.

```java
x.equals(y) == y.equals(x)
```

## Транзитивность

Если:

```java
x.equals(y) == true
y.equals(z) == true
```

то:

```java
x.equals(z) == true
```

## Согласованность

Если объекты не изменялись, повторные вызовы должны возвращать одинаковый результат.

```java
x.equals(y);
x.equals(y);
x.equals(y);
```

## Сравнение с null

Ненулевой объект не равен `null`.

```java
x.equals(null) == false
```

Метод не должен выбрасывать исключение при сравнении с `null`.

---

# Структура equals

```java
@Override
public boolean equals(Object object) {
    if (this == object) {
        return true;
    }

    if (!(object instanceof UserKey other)) {
        return false;
    }

    return id.equals(other.id);
}
```

## Проверка ссылки

```java
if (this == object) {
    return true;
}
```

Если ссылки одинаковые, дополнительное сравнение не требуется.

## Проверка типа

```java
if (!(object instanceof UserKey other)) {
    return false;
}
```

Эта конструкция:

- проверяет `null`
- проверяет тип объекта
- приводит объект к нужному типу

## Сравнение полей

```java
return id.equals(other.id);
```

Сравниваются поля, определяющие логическое равенство.

---

# Метод hashCode

Метод `hashCode()` возвращает число типа `int`.

```java
int hash = object.hashCode();
```

Он используется хешированными структурами:

- `HashMap`
- `HashSet`
- `Hashtable`
- `ConcurrentHashMap`

Упрощённая схема поиска:

```text
объект
→ hashCode
→ бакет
→ equals
→ точный объект
```

`hashCode()` помогает выбрать бакет.

`equals()` помогает найти нужный объект внутри бакета.

---

# Контракт hashCode

Главное правило:

> Если два объекта равны по equals, их hashCode обязан совпадать.

```java
first.equals(second) == true
```

означает:

```java
first.hashCode() == second.hashCode()
```

Обратное утверждение неверно.

```java
first.hashCode() == second.hashCode()
```

не гарантирует:

```java
first.equals(second) == true
```

Разные объекты могут иметь одинаковый хеш. Это называется коллизией.

---

# Почему коллизии допустимы

`hashCode()` возвращает `int`.

Количество возможных значений ограничено:

```text
от -2 147 483 648
до 2 147 483 647
```

Количество возможных объектов значительно больше.

Поэтому разные объекты неизбежно могут иметь одинаковый `hashCode()`.

После попадания объектов в один бакет `HashMap` различает их через `equals()`.

---

# Почему нужно переопределять оба метода

Плохой вариант:

```java
@Override
public boolean equals(Object object) {
    if (!(object instanceof UserKey other)) {
        return false;
    }

    return id.equals(other.id);
}
```

`equals()` переопределён, но `hashCode()` остался стандартным.

```java
UserKey first = new UserKey(10L);
UserKey second = new UserKey(10L);

first.equals(second); // true
```

При этом хеши могут отличаться.

```java
Map<UserKey, String> map = new HashMap<>();

map.put(first, "User");

String value = map.get(second); // может вернуть null
```

Причина:

1. `first` добавляется в бакет по своему хешу.
2. Для `second` вычисляется другой хеш.
3. Поиск выполняется в другом бакете.
4. До сравнения через `equals()` карта не доходит.

Правило:

> При переопределении equals необходимо переопределить hashCode.

---

# Корректная реализация

```java
public final class UserKey {

    private final Long id;

    public UserKey(Long id) {
        this.id = Objects.requireNonNull(id);
    }

    @Override
    public boolean equals(Object object) {
        if (this == object) {
            return true;
        }

        if (!(object instanceof UserKey other)) {
            return false;
        }

        return id.equals(other.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
```

`equals()` и `hashCode()` используют одно и то же значимое поле.

---

# Сравнение нескольких полей

```java
public final class IncidentKey {

    private final String category;
    private final IncidentPriority priority;

    public IncidentKey(
            String category,
            IncidentPriority priority
    ) {
        this.category = category;
        this.priority = priority;
    }

    @Override
    public boolean equals(Object object) {
        if (this == object) {
            return true;
        }

        if (!(object instanceof IncidentKey other)) {
            return false;
        }

        return Objects.equals(category, other.category)
                && priority == other.priority;
    }

    @Override
    public int hashCode() {
        return Objects.hash(category, priority);
    }
}
```

Оба метода используют:

```text
category
priority
```

Enum можно сравнивать через `==`, потому что каждая enum-константа существует в одном экземпляре.

---

# Objects.equals

```java
Objects.equals(first, second);
```

Метод безопасно работает с `null`.

```text
оба значения null     → true
одно значение null    → false
оба значения не null  → first.equals(second)
```

Пример:

```java
return Objects.equals(email, other.email);
```

---

# Objects.hash

```java
@Override
public int hashCode() {
    return Objects.hash(category, priority);
}
```

Метод вычисляет общий хеш нескольких полей.

Он удобен и читаем, хотя может быть немного менее эффективным, чем ручное вычисление.

---

# Какие поля включать в equals и hashCode

Нужно определить, что означает логическое равенство объектов.

## Value Object

Объект-значение обычно сравнивается по всем значимым полям.

```java
public record Money(
        BigDecimal amount,
        Currency currency
) {
}
```

Два объекта `Money` равны, если совпадают сумма и валюта.

## Entity

Сущность обладает идентичностью.

Изменение имени пользователя не должно превращать его в другого пользователя.

```text
одинаковый идентификатор
→ та же сущность
```

Однако для JPA-сущностей сравнение по идентификатору имеет дополнительные сложности.

---

# Изменяемые поля

Поля, участвующие в `equals()` и `hashCode()`, желательно делать неизменяемыми.

```java
public class UserKey {

    private String email;

    @Override
    public int hashCode() {
        return email.hashCode();
    }
}
```

Добавим объект в карту:

```java
UserKey key = new UserKey("old@example.com");

Map<UserKey, String> map = new HashMap<>();

map.put(key, "value");
```

Затем изменим email:

```java
key.changeEmail("new@example.com");
```

Теперь хеш объекта изменился.

```java
map.get(key);    // может вернуть null
map.remove(key); // может вернуть null
```

Объект физически остаётся в бакете, вычисленном по старому хешу.

Поиск выполняется в новом бакете.

Правило:

> Не изменять поля ключа, участвующие в equals и hashCode, пока объект находится в HashMap или HashSet.

---

# HashSet и hashCode

`HashSet` внутри использует `HashMap`.

Упрощённо:

```java
private HashMap<E, Object> map;

private static final Object PRESENT = new Object();
```

Добавление элемента:

```java
map.put(element, PRESENT);
```

Схема:

```text
элемент HashSet → ключ HashMap
PRESENT         → служебное значение
```

Поэтому `HashSet` зависит от правильной реализации:

- `equals()`
- `hashCode()`

---

# instanceof и getClass

Существует два распространённых способа проверки типа.

## instanceof

```java
if (!(object instanceof UserKey other)) {
    return false;
}
```

Принимает объект указанного класса и его наследников.

## getClass

```java
if (object == null || getClass() != object.getClass()) {
    return false;
}
```

Требует точного совпадения классов.

Для `final`-классов практическая разница обычно отсутствует.

При наследовании выбор способа влияет на контракт `equals()`.

---

# Наследование и equals

```java
class Point {

    private int x;
    private int y;
}

class ColoredPoint extends Point {

    private String color;
}
```

```java
Point point = new Point(1, 2);
ColoredPoint coloredPoint =
        new ColoredPoint(1, 2, "red");
```

`Point` может сравнивать только координаты:

```java
point.equals(coloredPoint); // true
```

`ColoredPoint` может учитывать цвет:

```java
coloredPoint.equals(point); // false
```

Нарушается симметричность.

Поэтому классы-значения часто объявляют `final`.

```java
public final class UserKey {
}
```

---

# JPA-сущности

Реализация равенства JPA-сущностей сложнее обычных классов.

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

До сохранения:

```java
incident.getId(); // null
```

После сохранения:

```java
incident.getId(); // 15
```

Если `hashCode()` зависит от `id`, он изменится после `persist()`.

```java
Set<Incident> incidents = new HashSet<>();

Incident incident = new Incident(...);

incidents.add(incident);

entityManager.persist(incident);
```

После появления идентификатора множество может перестать находить объект.

---

# Hibernate-прокси

Для ленивых связей Hibernate может вернуть прокси.

```text
User
```

может быть представлен объектом вида:

```text
User$HibernateProxy
```

Проверка через:

```java
getClass() != object.getClass()
```

может считать сущность и её прокси разными объектами.

При реализации равенства JPA-сущностей нужно учитывать:

- transient-состояние
- generated ID
- managed-состояние
- detached-состояние
- Hibernate-прокси
- использование в хешированных коллекциях

Поэтому в `User` и `Incident` проекта IncidentHub методы `equals()` и `hashCode()` пока не переопределены.

---

# record как ключ

Для составных неизменяемых ключей удобно использовать `record`.

```java
public record IncidentKey(
        String category,
        IncidentPriority priority
) {
}
```

Java автоматически создаёт:

- конструктор
- методы доступа
- `equals()`
- `hashCode()`
- `toString()`

```java
Map<IncidentKey, Integer> statistics =
        new HashMap<>();

IncidentKey key = new IncidentKey(
        "Infrastructure",
        IncidentPriority.CRITICAL
);

statistics.put(key, 5);
```

Компоненты `record` нельзя переназначить.

Но `record` не гарантирует глубокую неизменяемость:

```java
public record MutableKey(List<String> values) {
}
```

Ссылку `values` изменить нельзя, но содержимое списка изменить можно.

---

# Типичные ошибки

## Переопределён только equals

Нарушается контракт с `hashCode()`.

## Переопределён только hashCode

`equals()` продолжает сравнивать ссылки.

## Методы используют разные поля

Плохо:

```text
equals   → id
hashCode → email
```

## Используются изменяемые поля

Объект может перестать находиться в хешированной коллекции.

## Строки сравниваются через ==

Плохо:

```java
email == other.email
```

Правильно:

```java
Objects.equals(email, other.email)
```

## Не учитывается null

```java
object.getClass()
```

при `object == null` выбросит `NullPointerException`.

## Требование уникального hashCode

`hashCode()` не обязан быть уникальным.

Коллизии допустимы.

Он должен быть:

- согласован с `equals()`
- стабильным при неизменных полях
- достаточно равномерно распределённым

---

# Краткая памятка

```text
==       → ссылки
equals   → логическое равенство
hashCode → определение бакета
```

```text
equals true
→
hashCode обязательно одинаковый
```

```text
hashCode одинаковый
не означает
equals true
```

```text
Переопределил equals
→
переопредели hashCode
```

```text
Поля equals и hashCode
не должны меняться внутри HashMap и HashSet
```

---

# Вопросы для самопроверки

1. Чем `==` отличается от `equals()`?
2. Какие требования входят в контракт `equals()`?
3. Какое правило связывает `equals()` и `hashCode()`?
4. Означает ли одинаковый хеш равенство объектов?
5. Что произойдёт, если переопределить только `equals()`?
6. Почему изменяемый ключ опасен?
7. Как `HashMap` использует `hashCode()` и `equals()`?
8. Почему `HashSet` зависит от этих методов?
9. Чем `instanceof` отличается от `getClass()`?
10. Какие проблемы возникают при наследовании?
11. Почему JPA-сущности сложно сравнивать?
12. Как generated ID влияет на `hashCode()`?
13. Почему Hibernate-прокси нужно учитывать?
14. Почему `record` подходит для ключа?
15. Гарантирует ли `record` глубокую неизменяемость?