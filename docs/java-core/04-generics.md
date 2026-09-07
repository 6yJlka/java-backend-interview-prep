# Generics в Java

Generics позволяют задавать типы, с которыми работает класс, интерфейс или метод.

Основные цели:

- типобезопасность на этапе компиляции
- уменьшение количества ручных приведений типов
- создание переиспользуемого кода
- более точное описание API

---

## Код без generics

```java
List values = new ArrayList();

values.add("Java");
values.add(10);
values.add(new Object());
```

Коллекция может содержать объекты разных типов.

При чтении требуется ручное приведение:

```java
String value = (String) values.get(0);
```

Ошибка может появиться во время выполнения:

```java
String value = (String) values.get(1);
```

В элементе находится `Integer`.

Результат:

```text
ClassCastException
```

---

## Код с generics

```java
List<String> values = new ArrayList<>();

values.add("Java");
values.add("Spring");
```

Добавить число нельзя:

```java
values.add(10);
```

Ошибка обнаруживается компилятором.

Основной принцип:

> Generics переносят проверку типов со времени выполнения на этап компиляции.

---

## Параметр и аргумент типа

```java
public class Box<T> {
}
```

`T` — параметр типа.

```java
Box<String> box;
```

`String` — аргумент типа.

Аналогично обычному методу:

```java
void print(String value)
```

`value` является параметром метода.

Конкретная переданная строка является аргументом.

---

## Generic-класс

```java
public class Box<T> {

  private T value;

  public Box(T value) {
    this.value = value;
  }

  public T getValue() {
    return value;
  }

  public void setValue(T value) {
    this.value = value;
  }
}
```

Использование:

```java
Box<String> stringBox = new Box<>("Java");

String text = stringBox.getValue();
```

С другим типом:

```java
Box<Integer> integerBox = new Box<>(10);

Integer number = integerBox.getValue();
```

Один класс может работать с различными типами без `Object` и ручных cast.

---

## Несколько параметров типа

```java
public class Pair<K, V> {

  private final K key;
  private final V value;

  public Pair(K key, V value) {
    this.key = key;
    this.value = value;
  }

  public K getKey() {
    return key;
  }

  public V getValue() {
    return value;
  }
}
```

Использование:

```java
Pair<Long, String> user =
        new Pair<>(1L, "Dmitry");
```

Распространённые обозначения:

```text
T → Type
E → Element
K → Key
V → Value
R → Result
N → Number
```

Это соглашение об именовании, а не требование языка.

---

## Generic-метод

Метод может иметь собственный параметр типа.

```java
public static <T> T first(List<T> values) {
  return values.getFirst();
}
```

Расположение `<T>`:

```java
public static <T> T first(...)
              ↑   ↑
параметр   возвращаемый тип
```

Использование:

```java
String firstName =
        first(List.of("Alice", "Bob"));

Integer firstNumber =
        first(List.of(10, 20));
```

Компилятор обычно самостоятельно выводит аргумент типа.

---

## Generic-класс и generic-метод

Generic-класс:

```java
public class Box<T> {

  public T getValue() {
    return value;
  }
}
```

Тип задаётся при создании объекта:

```java
Box<String> box = new Box<>("Java");
```

Generic-метод:

```java
public static <T> T identity(T value) {
  return value;
}
```

Тип определяется при каждом вызове:

```java
String text = identity("Java");
Integer number = identity(10);
```

---

## Raw types

Raw type — использование generic-типа без аргумента типа.

```java
List values = new ArrayList();
```

Вместо:

```java
List<String> values = new ArrayList<>();
```

Raw types существуют для совместимости со старым Java-кодом.

Проблемы:

```java
List values = new ArrayList();

values.add("Java");
values.add(10);
```

Компилятор не обеспечивает полноценную проверку.

```java
String value = (String) values.get(1);
```

Ошибка возникает во время выполнения:

```text
ClassCastException
```

В новом коде raw types использовать не следует.

---

## Инвариантность generics

`Integer` наследует `Number`.

```text
Integer <: Number
```

Но:

```text
List<Integer>
```

не является наследником:

```text
List<Number>
```

Такой код не компилируется:

```java
List<Integer> integers = new ArrayList<>();

List<Number> numbers = integers;
```

Если бы это разрешалось:

```java
numbers.add(3.14);
```

В `List<Integer>` удалось бы добавить `Double`.

Поэтому generics в Java инвариантны.

```text
Integer является Number

не означает

List<Integer> является List<Number>
```

---

## Wildcard

Wildcard обозначается символом `?`.

```java
List<?>
```

Это список неизвестного типа.

```java
public static void print(List<?> values) {
  for (Object value : values) {
    System.out.println(value);
  }
}
```

Метод принимает:

```java
List<String>
List<Integer>
List<User>
```

Читать элементы можно как `Object`.

```java
Object value = values.get(0);
```

Добавлять обычные значения нельзя.

```java
values.add("Java");
values.add(10);
```

Компилятор не знает реальный тип списка.

Добавить можно только `null`.

```java
values.add(null);
```

---

## Upper bounded wildcard

```java
List<? extends Number>
```

Означает:

> Список неизвестного типа, который является Number или его наследником.

Можно передать:

```java
List<Integer>
List<Long>
List<Double>
```

Пример:

```java
public static double sum(
        List<? extends Number> values
) {
  double result = 0;

  for (Number value : values) {
    result += value.doubleValue();
  }

  return result;
}
```

Использование:

```java
sum(List.of(1, 2, 3));
sum(List.of(1.5, 2.5));
```

Читать можно как `Number`.

```java
Number value = values.get(0);
```

Добавлять конкретные значения нельзя.

```java
values.add(10);
values.add(10.5);
```

Реальный список может быть:

```text
List<Integer>
List<Double>
List<Long>
```

Разрешён только `null`.

---

## Lower bounded wildcard

```java
List<? super Integer>
```

Означает:

> Список неизвестного типа, который является Integer или родительским типом Integer.

Допустимые варианты:

```java
List<Integer>
List<Number>
List<Object>
```

Добавлять можно `Integer`.

```java
public static void addNumbers(
        List<? super Integer> values
) {
  values.add(10);
  values.add(20);
}
```

Читать можно только как `Object`.

```java
Object value = values.get(0);
```

Компилятор не знает, является ли реальный список:

```text
List<Integer>
List<Number>
List<Object>
```

---

## PECS

PECS:

```text
Producer Extends
Consumer Super
```

### Producer Extends

Структура производит значения для чтения.

```java
List<? extends Number>
```

```java
Number value = values.get(0);
```

### Consumer Super

Структура принимает значения.

```java
List<? super Integer>
```

```java
values.add(10);
```

Краткое правило:

```text
нужно читать T
→ ? extends T

нужно добавлять T
→ ? super T
```

---

## Пример копирования

```java
public static <T> void copy(
        List<? extends T> source,
        List<? super T> destination
) {
  for (T value : source) {
    destination.add(value);
  }
}
```

Здесь:

```text
source      → producer → extends
destination → consumer → super
```

Использование:

```java
List<Integer> source =
        List.of(1, 2, 3);

List<Number> destination =
        new ArrayList<>();

copy(source, destination);
```

---

## Ограниченный параметр типа

```java
public static <T extends Number> double sum(
        List<T> values
) {
  double result = 0;

  for (T value : values) {
    result += value.doubleValue();
  }

  return result;
}
```

`T` должен быть `Number` или его наследником.

Допустимо:

```java
sum(List.of(1, 2, 3));
sum(List.of(1.5, 2.5));
```

Недопустимо:

```java
sum(List.of("A", "B"));
```

---

## Несколько ограничений

```java
<T extends Number & Comparable<T>>
```

Тип должен:

- быть `Number` или его наследником
- реализовывать `Comparable<T>`

```java
public static <
        T extends Number & Comparable<T>
        > T max(T first, T second) {
  return first.compareTo(second) >= 0
          ? first
          : second;
}
```

Класс должен указываться первым.

Правильно:

```java
<T extends Number & Comparable<T>>
```

Неправильно:

```java
<T extends Comparable<T> & Number>
```

В generic-ограничениях `extends` используется и для классов, и для интерфейсов.

```java
<T extends Comparable<T>>
```

Слово `implements` не используется.

---

## Wildcard и параметр типа

Wildcard:

```java
public static void print(List<?> values) {
}
```

Используется, когда конкретный тип не важен.

Параметр типа:

```java
public static <T> T first(List<T> values) {
}
```

Используется, когда нужно связать несколько частей сигнатуры.

```java
public static <T> void add(
        List<T> values,
        T value
) {
  values.add(value);
}
```

Здесь тип списка и добавляемого значения обязан совпадать.

Главное различие:

```text
? → неизвестный тип

T → именованный тип,
    связывающий параметры и результат
```

---

## Type erasure

Generics в Java реализованы в основном через стирание типов.

Исходный код:

```java
List<String> values =
        new ArrayList<>();
```

После компиляции информация о `String` в значительной степени удаляется.

Упрощённо JVM работает с:

```java
List values = new ArrayList();
```

Компилятор добавляет проверки и приведения типов.

```java
String value = values.get(0);
```

Упрощённо превращается в:

```java
String value =
        (String) values.get(0);
```

Причины применения стирания:

- совместимость со старым байткодом
- одна реализация generic-класса для разных типов

Следствия стирания создают ограничения generics.

---

## Ограничения generics

### Нельзя создать new T

```java
public class Factory<T> {

  public T create() {
    return new T();
  }
}
```

После стирания типов неизвестно:

- какой класс представляет `T`
- существует ли конструктор без аргументов
- доступен ли конструктор

Обычно передают фабрику:

```java
public class Factory<T> {

  private final Supplier<T> supplier;

  public Factory(Supplier<T> supplier) {
    this.supplier = supplier;
  }

  public T create() {
    return supplier.get();
  }
}
```

Использование:

```java
Factory<ArrayList<String>> factory =
        new Factory<>(ArrayList::new);
```

---

### Нельзя создать массив T

```java
T[] values = new T[10];
```

Также нельзя:

```java
List<String>[] lists =
        new List<String>[10];
```

Массивы знают свой тип во время выполнения.

Generic-типы стираются.

---

### Нельзя использовать примитивы

Нельзя:

```java
List<int>
```

Нужно:

```java
List<Integer>
```

Generics работают только со ссылочными типами.

Автоупаковка:

```java
List<Integer> values =
        new ArrayList<>();

values.add(10);
```

Значение `int` автоматически преобразуется в `Integer`.

---

### Нельзя instanceof List<String>

Нельзя:

```java
if (value instanceof List<String>) {
        }
```

После стирания JVM не различает:

```text
List<String>
List<Integer>
```

Можно:

```java
if (value instanceof List<?>) {
        }
```

---

### Нельзя static T

```java
public class Box<T> {

  private static T value;
}
```

Статическое поле принадлежит классу и является общим для всех экземпляров.

Но параметр типа задаётся отдельно:

```java
Box<String>
Box<Integer>
```

Общее поле не может одновременно иметь тип `String` и `Integer`.

---

## Таблица wildcard

| Тип | Чтение | Добавление |
|---|---|---|
| `List<T>` | `T` | `T` |
| `List<?>` | `Object` | только `null` |
| `List<? extends T>` | `T` | только `null` |
| `List<? super T>` | `Object` | `T` и его наследники |

Для:

```java
List<? super Number>
```

можно добавлять:

```java
Number
        Integer
Long
        Double
```

Нельзя добавлять:

```java
Object
        String
```

---

## Типичные ошибки

### Raw type

```java
List values = new ArrayList();
```

Теряется проверка типов.

### Нарушение инвариантности

```java
List<Integer> integers =
        new ArrayList<>();

List<Number> numbers = integers;
```

Такой код не компилируется.

### Запись в extends

```java
List<? extends Number> values
```

Предназначен в первую очередь для чтения.

### Точное чтение из super

```java
List<? super Integer> values
```

Читать безопасно можно только как `Object`.

### Неправильное применение wildcard

Когда нужно связать типы нескольких аргументов или результата, следует использовать `<T>`.

---

## Краткая памятка

```text
Generics
→ типобезопасность на этапе компиляции
```

```text
List<Integer>
не является
List<Number>
```

```text
? → неизвестный тип
T → именованный связанный тип
```

```text
Producer Extends
Consumer Super
```

```text
? extends T
→ читаем T
→ не добавляем

? super T
→ добавляем T
→ читаем Object
```

```text
Type erasure
→ параметры типов в основном стираются после компиляции
```

---

## Вопросы на собеседовании

### 1. Для чего нужны generics?

**Ответ:** для типобезопасности на этапе компиляции и избавления от приведения
типов. Ошибка обнаруживается компилятором, а не как `ClassCastException` во время
выполнения.

### 2. Чем параметр типа отличается от аргумента типа?

**Ответ:** параметр — это заполнитель в объявлении, например `T` в `class Box<T>`.
Аргумент — конкретный тип при использовании, например `String` в `Box<String>`.

### 3. Что такое generic-класс?

**Ответ:** класс, объявленный с параметрами типа, которые используются в его полях
и методах. Конкретные типы задаются при создании экземпляра.

### 4. Что такое generic-метод?

**Ответ:** метод с собственными параметрами типа, объявленными перед возвращаемым
типом. Может находиться и в обычном классе, а тип обычно выводится из аргументов.

### 5. Что такое raw type?

**Ответ:** использование обобщённого типа без указания аргументов, например просто
`List`. Осталось ради совместимости с кодом, написанным до Java 5.

### 6. Почему raw type опасен?

**Ответ:** проверки типов отключаются, и в коллекцию можно положить что угодно.
Ошибка проявится позже, при чтении, в виде `ClassCastException` — то есть
теряется всё преимущество generics.

### 7. Что означает инвариантность generics?

**Ответ:** `List<Integer>` не является ни подтипом, ни супертипом `List<Number>`,
несмотря на отношение между `Integer` и `Number`.

### 8. Почему List<Integer> не является List<Number>?

**Ответ:** иначе через ссылку типа `List<Number>` можно было бы добавить `Double` в
список целых, и последующее чтение дало бы `ClassCastException`. Именно так
устроены массивы, и там эта дыра закрыта проверкой во время выполнения с
`ArrayStoreException`.

### 9. Что означает `List<?>`?

**Ответ:** список с неизвестным типом элементов. Подходит, когда конкретный тип не
важен — например, для подсчёта размера.

### 10. Что можно читать и добавлять в `List<?>`?

**Ответ:** читать можно как `Object`, добавлять нельзя ничего, кроме `null`. Тип
элементов неизвестен, поэтому компилятор не может гарантировать безопасность
записи.

### 11. Что означает `? extends T`?

**Ответ:** неизвестный тип, являющийся `T` или его наследником. Из такой коллекции
можно безопасно читать как `T`, но нельзя добавлять — неизвестно, какой именно
подтип там хранится.

### 12. Что означает `? super T`?

**Ответ:** неизвестный тип, являющийся `T` или его предком. В такую коллекцию можно
добавлять `T` и его наследников, а чтение возможно только как `Object`.

### 13. Как расшифровывается PECS?

**Ответ:** producer extends, consumer super. Если структура отдаёт данные,
используется `extends`; если принимает — `super`.

### 14. Чем wildcard отличается от `<T>`?

**Ответ:** параметр `T` именует тип и позволяет ссылаться на него в нескольких
местах сигнатуры, связывая их между собой. Wildcard анонимен и годится, когда тип
упоминается однократно и связывать нечего.

### 15. Что означает `<T extends Number>`?

**Ответ:** ограничение сверху: аргументом типа может быть только `Number` или его
наследник. Внутри класса или метода к `T` применимы методы `Number`.

### 16. Как указать несколько ограничений?

**Ответ:** через амперсанд: `<T extends Number & Comparable<T>>`. Класс, если он
присутствует, указывается первым, остальные ограничения — интерфейсы.

### 17. Что такое type erasure?

**Ответ:** удаление информации о типовых аргументах при компиляции. В байт-коде
остаётся либо `Object`, либо верхняя граница, а компилятор вставляет необходимые
приведения. Сделано ради совместимости с кодом, написанным до появления generics.

### 18. Почему нельзя создать `new T()`?

**Ответ:** во время выполнения тип `T` неизвестен из-за стирания, и JVM не знает,
конструктор какого класса вызывать. Обходной путь — передать фабрику или объект
`Class<T>`.

### 19. Почему нельзя создать массив `T[]`?

**Ответ:** массивы хранят информацию о типе элементов во время выполнения и
проверяют её при записи. Из-за стирания подставить нужный тип невозможно, поэтому
такое создание запрещено. Используют `Object[]` с приведением или коллекции.

### 20. Почему нельзя использовать `List<int>`?

**Ответ:** аргументом типа может быть только ссылочный тип, поскольку после
стирания остаётся `Object`, а примитив им не является. Применяют обёртки либо
специализированные структуры без упаковки.

### 21. Почему нельзя проверить `instanceof List<String>`?

**Ответ:** во время выполнения информация об аргументе типа отсутствует, и все
списки неотличимы. Допустима лишь проверка `instanceof List<?>`.

### 22. Почему нельзя объявить статическое поле типа T?

**Ответ:** статическое поле принадлежит классу, а не экземпляру, тогда как аргумент
типа задаётся при создании конкретного экземпляра. Одно поле не может
соответствовать разным типам одновременно.

---

## См. также

- [`01-collections-framework.md`](01-collections-framework.md) — generics в
  сигнатурах коллекций и ковариантность массивов
- [`00-java-language-basics.md`](00-java-language-basics.md) — приведение типов
  и различие cast и conversion
- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  обобщённые функциональные интерфейсы и примитивные специализации
- [`06-stream-api.md`](06-stream-api.md) — где PECS встречается на практике