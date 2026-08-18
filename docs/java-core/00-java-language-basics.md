# Java Language Basics

# Примитивные и ссылочные типы

В Java типы данных делятся на две большие группы:

```text
примитивные типы
ссылочные типы
```

## Примитивные типы

К примитивам относятся:

```text
byte
short
int
long
float
double
char
boolean
```

Примитивная переменная хранит само значение.

```java
int number = 10;
boolean active = true;
char grade = 'A';
```

## Ссылочные типы

К ссылочным типам относятся классы, интерфейсы, массивы, `enum`, `record`, `String` и wrapper-классы.

```java
User user = new User();
String text = "Java";
int[] numbers = {1, 2, 3};
```

Ссылочная переменная хранит значение ссылки на объект.

```text
user
  │
  └────→ User object
```

Несколько переменных могут ссылаться на один объект:

```java
User first = new User();
User second = first;
```

```text
first  ──┐
         ↓
      User object
         ↑
second ──┘
```

Изменение объекта через одну ссылку будет видно через другую.

---

# Pass-by-value в Java

Java всегда передаёт аргументы в методы **по значению**.

```text
Java → pass-by-value
```

Отдельного механизма pass-by-reference в Java нет.

Главное различие состоит в том, что именно является значением:

```text
primitive type → копируется примитивное значение
reference type → копируется значение ссылки
```

## Передача примитива

```java
public static void change(int value) {
    value = 100;
}

public static void main(String[] args) {
    int number = 10;

    change(number);

    System.out.println(number);
}
```

Результат:

```text
10
```

В метод передаётся копия значения. Изменение `value` не влияет на `number`.

## Передача ссылки на объект

```java
static class User {

    String name;

    User(String name) {
        this.name = name;
    }
}
```

```java
public static void change(User user) {
    user.name = "Alex";
}
```

Здесь в метод передаётся копия ссылки, но обе ссылки указывают на один объект. Поэтому изменение поля видно снаружи.

## Переназначение ссылки внутри метода

```java
public static void change(User user) {
    user = new User("Alex");
}
```

Такое присваивание меняет только локальную копию ссылки.

```text
изменили объект через ссылку
→ результат виден снаружи

переназначили параметр
→ снаружи ссылка не меняется
```

## Почему swap не работает

```java
public static void swap(User first, User second) {
    User temp = first;
    first = second;
    second = temp;
}
```

Метод меняет местами только локальные копии ссылок. Ссылки вызывающего кода не изменяются.

## Immutable-объекты

`String` и wrapper-классы вроде `Integer` immutable.

```java
public static void change(String text) {
    text = text + " World";
}
```

Создаётся новое строковое значение и меняется только локальная ссылка.

Аналогично:

```java
public static void change(Integer value) {
    value = 100;
}
```

`value = 100` не меняет существующий объект `Integer`, а переназначает локальную ссылку.

## Изменяемый объект

```java
public static void change(List<Integer> list) {
    list.add(100);
}
```

Если передан `ArrayList`, метод меняет тот же объект, поэтому изменение видно снаружи.

## Краткий ответ для собеседования

> Java всегда использует pass-by-value. Для примитивов копируется само значение. Для ссылочных типов копируется значение ссылки на объект. Поэтому через параметр можно изменить состояние объекта, если обе ссылки указывают на него, но переназначение параметра не изменяет ссылку у вызывающего кода.

---

# Casting примитивных типов

Для примитивов важно различать:

```text
widening
narrowing
```

## Widening conversion

```java
int number = 10;
long value = number;
```

Явный cast не нужен.

Основные направления:

```text
byte → short → int → long → float → double
char → int → long → float → double
```

## Narrowing conversion

```java
long value = 100L;
int number = (int) value;
```

Явный cast обязателен. Возможна потеря данных.

```java
long value = 3_000_000_000L;
int number = (int) value;
```

`int` не способен представить исходное значение, поэтому результат изменится.

## Приведение double к int

```java
double value = 10.9;
int number = (int) value;
```

Результат:

```text
10
```

Дробная часть **отбрасывается**, а не округляется.

```text
10.9  → 10
10.1  → 10
-10.9 → -10
```

Для округления используют отдельные методы, например `Math.round()`.

---

# Numeric promotion

В арифметических выражениях Java автоматически расширяет `byte`, `short` и `char` до `int`.

```java
byte a = 10;
byte b = 20;

byte c = a + b;
```

Такой код не компилируется, потому что `a + b` имеет тип `int`.

Нужен явный cast:

```java
byte c = (byte) (a + b);
```

## Compile-time constants

```java
byte value = 10 + 20;
```

Такой код компилируется, потому что компилятор заранее вычисляет `30` и видит, что значение помещается в `byte`.

## Составные операторы присваивания

```java
byte number = 10;
number += 20;
```

Такой код компилируется. Упрощённо `+=` включает приведение результата обратно к типу левой части.

```text
number += 20
≈
number = (byte) (number + 20)
```

Но это не защищает от переполнения.

## Инкремент и декремент

Аналогичная логика работает для `++` и `--`.

```java
char value = 'A';
value++;

System.out.println(value); // B
```

При этом:

```java
value = value + 1;
```

без cast не скомпилируется, потому что результат имеет тип `int`.

---

# Casting ссылочных типов

Рассмотрим:

```java
class Animal {}
class Dog extends Animal {}
class Cat extends Animal {}
```

## Upcasting

```java
Dog dog = new Dog();
Animal animal = dog;
```

Это:

```text
Dog → Animal
```

Upcasting безопасен и выполняется автоматически.

## Downcasting

```java
Animal animal = new Dog();
Dog dog = (Dog) animal;
```

Это:

```text
Animal → Dog
```

Явный cast обязателен.

## ClassCastException

```java
Animal animal = new Cat();
Dog dog = (Dog) animal;
```

Код скомпилируется, но во время выполнения возникнет:

```text
ClassCastException
```

Реальный объект является `Cat`, а не `Dog`.

## instanceof

Перед downcasting можно проверить реальный тип объекта:

```java
if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
}
```

Современный вариант:

```java
if (animal instanceof Dog dog) {
    // dog уже имеет тип Dog
}
```

Для `null`:

```text
null instanceof SomeType
→ false
```

Исключение не возникает.

## Cast и conversion

```java
Object value = "Java";
String text = (String) value;
```

Работает, потому что реальный объект уже является `String`.

```java
Object value = 10;
String text = (String) value;
```

приведёт к `ClassCastException`, потому что реальный объект имеет тип `Integer`.

Если нужно строковое представление значения:

```java
String text = String.valueOf(value);
```

```text
cast
→ объект уже должен иметь совместимый тип

conversion
→ создаётся представление значения в другом типе
```

---

# Arrays

Массив является объектом и относится к ссылочным типам.

```java
int[] numbers = {1, 2, 3};
```

## Присваивание массива

```java
int[] a = {1, 2, 3};
int[] b = a;
```

Новый массив не создаётся. `a` и `b` указывают на один объект.

```java
b[0] = 100;

System.out.println(a[0]); // 100
```

## Передача массива в метод

```java
public static void change(int[] numbers) {
    numbers[0] = 100;
}
```

Изменяется тот же объект массива, поэтому изменение видно снаружи.

## Переназначение массива внутри метода

```java
public static void change(int[] numbers) {
    numbers = new int[]{100, 200, 300};
}
```

Такое присваивание меняет только локальную копию ссылки.

## clone массива примитивов

```java
int[] a = {1, 2, 3};
int[] b = a.clone();
```

Создаётся отдельный массив со скопированными значениями.

## clone массива объектов

```java
User[] a = {new User("Dima")};
User[] b = a.clone();
```

Массивы разные, но ссылки внутри них указывают на тот же объект `User`.

```text
array.clone()
→ новый массив
→ shallow copy для ссылочных элементов
```

## Многомерные массивы

Двумерный массив в Java фактически является массивом массивов.

```java
int[][] matrix = {
        {1, 2},
        {3, 4}
};
```

```java
int[][] copy = matrix.clone();
```

копирует только внешний массив. Внутренние массивы остаются общими.

## Длина массива

```java
int[] numbers = new int[3];

numbers.length; // 3
```

Размер массива фиксируется при создании.

```java
numbers.length = 10;
```

не компилируется.

Для другого размера создаётся новый массив, например через `Arrays.copyOf()`.

## Значения по умолчанию

Элементы массива автоматически инициализируются.

| Тип элемента | Значение |
|---|---|
| `byte`, `short`, `int`, `long` | `0` |
| `float`, `double` | `0.0` |
| `boolean` | `false` |
| `char` | `'\u0000'` |
| ссылочный тип | `null` |

## Ковариантность массивов

Массивы в Java ковариантны.

Если:

```text
Dog <: Animal
```

то:

```text
Dog[] <: Animal[]
```

Поэтому допустимо:

```java
Animal[] animals = new Dog[2];
```

Но:

```java
animals[1] = new Cat();
```

приведёт к:

```text
ArrayStoreException
```

Реальный тип массива — `Dog[]`.

Это отличается от generics:

```text
массивы → ковариантны
generics → инвариантны
```

---

# Локальные переменные и default values

Поля объектов и элементы массивов получают значения по умолчанию.

Локальные переменные — нет.

```java
public static void main(String[] args) {
    int number;

    System.out.println(number);
}
```

Код не скомпилируется.

Локальная переменная должна быть гарантированно инициализирована до чтения.

---

# Scope

Scope — область программы, в которой имя переменной доступно.

```java
public static void main(String[] args) {
    int number = 10;

    if (true) {
        int value = 20;
        System.out.println(number);
    }

    System.out.println(value);
}
```

`number` доступен во вложенном блоке. `value` за пределами `if` недоступен.

```text
внешний блок
→ переменная доступна во вложенных блоках

внутренний блок
→ переменная снаружи недоступна
```

## Scope переменной цикла

```java
for (int i = 0; i < 3; i++) {
    System.out.println(i);
}

System.out.println(i);
```

Последняя строка не скомпилируется.

## Повторное объявление локальной переменной

```java
int number = 10;

if (true) {
    int number = 20;
}
```

Такой код не скомпилируется.

Локальную переменную нельзя повторно объявить во вложенной области, пока внешняя переменная всё ещё находится в scope.

## Shadowing поля класса

Поле класса можно скрыть параметром или локальной переменной.

```java
class User {

    private String name;

    void setName(String name) {
        this.name = name;
    }
}
```

```text
name      → параметр метода
this.name → поле объекта
```

---

# Varargs

Varargs позволяет передать в метод переменное количество аргументов одного типа.

```java
public static void print(String... values) {
}
```

Внутри метода `values` имеет тип:

```text
String[]
```

Допустимые вызовы:

```java
print();
print("A");
print("A", "B", "C");
```

Можно передать готовый массив:

```java
String[] values = {"A", "B"};
print(values);
```

## Пустой вызов

```java
public static void print(String... values) {
    System.out.println(values.length);
}

print();
```

Результат:

```text
0
```

При обычном вызове без аргументов передаётся пустой массив.

## Явная передача null

Технически можно написать:

```java
print((String[]) null);
```

Тогда `values == null`.

## Ограничения varargs

Varargs-параметр должен быть последним.

Корректно:

```java
void print(int count, String... values) {
}
```

Некорректно:

```java
void print(String... values, int count) {
}
```

Также нельзя объявить два varargs-параметра:

```java
void test(String... names, int... numbers) {
}
```

---

# Package

`package` определяет пакет, к которому относится текущий класс.

```java
package com.example.service;
```

Пакеты используются для:

- организации кода
- формирования полного имени класса
- управления package-private доступом
- избежания конфликтов одинаковых имён

Полное имя класса:

```text
com.example.service.UserService
```

---

# Import

`import` позволяет использовать тип по короткому имени.

```java
import java.util.List;
```

После этого можно писать:

```java
List<String> values;
```

вместо:

```java
java.util.List<String> values;
```

`import` не загружает библиотеку во время выполнения. Он влияет на разрешение имён компилятором.

## Wildcard import

```java
import java.util.*;
```

Позволяет использовать доступные типы непосредственно из `java.util`.

Подпакеты не импортируются. Например, `java.util.concurrent.*` сюда не входит.

## Static import

```java
import static java.lang.Math.*;
```

Импортирует статические члены класса `Math`.

После этого:

```java
sqrt(16);
max(10, 20);
PI;
```

вместо:

```java
Math.sqrt(16);
Math.max(10, 20);
Math.PI;
```

```text
import
→ импорт типов

import static
→ импорт static-методов и static-полей
```

---

# Access modifiers

Для полей и методов используются четыре уровня доступа:

```text
private
package-private
protected
public
```

`package-private` получается, когда модификатор не указан.

```java
class Example {

    private int first;
    int second;
    protected int third;
    public int fourth;
}
```

## private

Доступен только внутри класса, в котором объявлен.

## package-private

Доступен только внутри того же package.

Наследование из другого package не даёт доступ к package-private члену.

## protected

Доступен:

- внутри того же package
- наследникам из других package

Пример:

```java
package com.example.first;

public class Parent {
    protected int value = 10;
}
```

```java
package com.example.second;

public class Child extends Parent {

    public void print() {
        System.out.println(value);
    }
}
```

## public

Доступен из любого места, если сам класс тоже доступен.

## Таблица access modifiers

| Модификатор | Тот же класс | Тот же package | Наследник в другом package | Любой код |
|---|---:|---:|---:|---:|
| `private` | Да | Нет | Нет | Нет |
| package-private | Да | Да | Нет | Нет |
| `protected` | Да | Да | Да | Нет |
| `public` | Да | Да | Да | Да |

---

# Типичные ошибки

## Считать Java pass-by-reference

Неверно:

```text
объект передаётся по ссылке
```

Точнее:

```text
ссылка передаётся по значению
```

## Путать изменение объекта и переназначение ссылки

```java
user.name = "Alex";
```

изменяет объект.

```java
user = new User("Alex");
```

меняет только локальную ссылку.

## Считать Integer изменяемым

`Integer` immutable.

## Ожидать округление при double → int

```java
(int) 10.9
```

даёт `10`, а не `11`.

## Забывать про numeric promotion

```java
byte a = 10;
byte b = 20;
byte c = a + b;
```

не компилируется, потому что результат имеет тип `int`.

## Выполнять небезопасный downcast

```java
Dog dog = (Dog) animal;
```

может привести к `ClassCastException`.

## Путать cast и conversion

```java
(String) value
```

не превращает произвольный объект в строку.

## Считать clone глубоким копированием

Для массива объектов копируются ссылки, а не сами объекты.

## Забывать про ковариантность массивов

```java
Animal[] animals = new Dog[2];
animals[0] = new Cat();
```

приведёт к `ArrayStoreException`.

## Ожидать default value у локальной переменной

Локальные переменные должны быть инициализированы до чтения.

## Ставить varargs не последним

Varargs обязан быть последним параметром метода.

## Считать import загрузкой библиотеки

`import` только позволяет компилятору разрешать короткие имена типов.

---

# Краткий ответ для собеседования

Java делит типы на примитивные и ссылочные. Примитивная переменная хранит значение, ссылочная — ссылку на объект.

Java всегда использует pass-by-value. Для примитивов копируется само значение, для объектов копируется значение ссылки. Поэтому метод может изменить состояние объекта через скопированную ссылку, но переназначение параметра не меняет ссылку вызывающего кода.

Для примитивов widening обычно выполняется автоматически, narrowing требует явного cast и может приводить к потере данных. В арифметике `byte`, `short` и `char` обычно продвигаются до `int`.

Для ссылочных типов upcasting безопасен и выполняется автоматически. Downcasting требует явного cast и может завершиться `ClassCastException`, поэтому реальный тип часто проверяют через `instanceof`.

Массив является объектом. Его размер фиксирован. `clone()` создаёт новый массив, но для массива объектов выполняет shallow copy. Массивы ковариантны, из-за чего возможен `ArrayStoreException`.

Локальные переменные должны быть явно инициализированы. Их видимость определяется блоком, в котором они объявлены. Varargs внутри метода представлен массивом и должен быть последним параметром.

`package` определяет принадлежность класса к пакету, `import` сокращает использование полных имён типов. Основные уровни доступа — `private`, package-private, `protected` и `public`.

---

# Краткая памятка

```text
Java
→ всегда pass-by-value
```

```text
primitive
→ копируется значение

reference type
→ копируется значение ссылки
```

```text
изменили объект
→ видно снаружи

переназначили параметр
→ снаружи не видно
```

```text
widening
→ обычно автоматически

narrowing
→ явный cast
→ возможна потеря данных
```

```text
byte / short / char
→ арифметика обычно через int
```

```text
Dog → Animal
→ upcasting
→ автоматически
```

```text
Animal → Dog
→ downcasting
→ явный cast
→ возможен ClassCastException
```

```text
array
→ объект
→ фиксированная length
```

```text
array.clone()
→ новый массив
→ shallow copy для ссылочных элементов
```

```text
Dog[] является Animal[]
→ массивы ковариантны
→ возможен ArrayStoreException
```

```text
поля и элементы массива
→ получают default value

локальные переменные
→ должны быть инициализированы
```

```text
String... values
→ внутри String[]
→ 0 или больше аргументов
→ varargs только последний
```

```text
private
→ только класс

package-private
→ package

protected
→ package + наследники

public
→ отовсюду
```

```text
package
→ пакет текущего класса

import
→ короткое имя типа

import static
→ static-члены класса
```

---

# Вопросы для самопроверки

1. Чем примитивный тип отличается от ссылочного?
2. Что именно хранит ссылочная переменная?
3. Как Java передаёт аргументы в методы?
4. Что копируется при передаче примитива?
5. Что копируется при передаче объекта?
6. Почему изменение поля объекта внутри метода видно снаружи?
7. Почему `user = new User()` внутри метода не меняет ссылку вызывающего кода?
8. Почему обычный `swap(a, b)` не меняет ссылки снаружи?
9. Почему `String` не меняется при конкатенации внутри метода?
10. Почему присваивание нового `Integer` не меняет исходную переменную?
11. Чем widening отличается от narrowing?
12. Когда требуется явный cast примитива?
13. Что происходит с дробной частью при `double → int`?
14. Почему `byte + byte` даёт `int`?
15. Почему `byte += int` может компилироваться?
16. Почему `char++` компилируется?
17. Что такое upcasting?
18. Что такое downcasting?
19. Когда возникает `ClassCastException`?
20. Для чего используется `instanceof`?
21. Что возвращает `null instanceof SomeType`?
22. Чем cast отличается от преобразования значения?
23. Что происходит при `int[] b = a`?
24. Чем `clone()` массива отличается от обычного присваивания?
25. Почему `clone()` массива объектов является shallow copy?
26. Как устроен двумерный массив в Java?
27. Можно ли изменить `array.length`?
28. Какие default values получают элементы массива?
29. Почему локальная переменная без инициализации не компилируется?
30. Что такое ковариантность массивов?
31. Когда возникает `ArrayStoreException`?
32. Что такое scope?
33. Почему переменная из `if` недоступна после блока?
34. Можно ли повторно объявить локальную переменную во вложенном блоке?
35. Что означает `String... values`?
36. Как varargs представлен внутри метода?
37. Сколько аргументов можно передать в varargs?
38. Почему varargs должен быть последним?
39. Что делает `package`?
40. Что делает `import`?
41. Импортирует ли `java.util.*` подпакет `java.util.concurrent`?
42. Что делает `import static`?
43. Какие четыре уровня доступа есть в Java?
44. Чем `protected` отличается от package-private?
45. Как коротко объяснить pass-by-value на собеседовании?
