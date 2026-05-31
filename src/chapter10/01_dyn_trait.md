# `dyn Trait` 基礎

## 本集目標

學會用 `dyn Trait` 在同一個位置存放不同型別的值，理解動態分派的原理。

## 概念說明

### 問題：不同型別放在同一個地方

第 5 章學了 `impl Trait`，可以寫 `fn print_it(x: &impl Display)` 讓函數接受任何實作 `Display` 的型別。但如果你想把不同型別的值放在同一個 `Vec` 裡呢？

```rust,noplayground
trait Describe {
    fn describe(&self) -> String;
}

struct Cat;
struct Dog;

impl Describe for Cat {
    fn describe(&self) -> String {
        String::from("一隻貓")
    }
}

impl Describe for Dog {
    fn describe(&self) -> String {
        String::from("一隻狗")
    }
}
#
# fn main() {}
```

`Cat` 和 `Dog` 是不同型別——你沒辦法寫 `Vec<impl Describe>` 把它們放在一起。`impl Trait` 在編譯期就決定了具體型別，而 `Vec` 裡的每個元素必須是同一個型別。

### `dyn Trait` 登場

`dyn Describe` 代表「某個實作了 `Describe` 的型別，但具體是什麼我不知道」。

但既然不知道具體是什麼，`dyn Describe` 的大小就不固定——`Cat` 可能佔 1 byte，`Dog` 可能佔 100 bytes，編譯器在編譯期不知道會是哪個。所以 `dyn Describe` 是 DST（附錄一最後一集學過），必須放在指標後面：

- `&dyn Describe` — 借用
- `Box<dyn Describe>` — 擁有

```rust,editable
# trait Describe {
#     fn describe(&self) -> String;
# }
#
# struct Cat;
# struct Dog;
#
# impl Describe for Cat {
#     fn describe(&self) -> String {
#         String::from("一隻貓")
#     }
# }
#
# impl Describe for Dog {
#     fn describe(&self) -> String {
#         String::from("一隻狗")
#     }
# }
#
# fn main() {
    let animals: Vec<Box<dyn Describe>> = vec![
        Box::new(Cat),
        Box::new(Dog),
    ];

    for animal in &animals {
        println!("{}", animal.describe());
    }
# }
```

同樣的道理，函數回傳也能用 `dyn Trait`：

```rust,noplayground
# trait Describe {
#     fn describe(&self) -> String;
# }
#
# struct Cat;
# struct Dog;
#
# impl Describe for Cat {
#     fn describe(&self) -> String {
#         String::from("一隻貓")
#     }
# }
#
# impl Describe for Dog {
#     fn describe(&self) -> String {
#         String::from("一隻狗")
#     }
# }
#
fn make_animal(is_cat: bool) -> Box<dyn Describe> {
    if is_cat {
        Box::new(Cat)
    } else {
        Box::new(Dog)
    }
}
#
# fn main() {}
```

`impl Trait` 做不到這件事——因為 `if` 的兩個分支回傳不同型別，編譯器在編譯期無法決定是哪一個。

### 胖指標：位址 + vtable

附錄一最後一集學過 `&[T]` 是胖指標（位址 + 長度）。`&dyn Trait` 也是胖指標，但存的東西不同：

```ignore
&[T]         = [資料位址][長度]
&dyn Trait   = [資料位址][vtable 指標]
```

vtable（虛擬方法表）是一張表，裡面存著這個具體型別對這個 `trait` 的所有方法的函數指標。`Cat` 的 vtable 裡有指向 `Cat::describe` 的指標，`Dog` 的 vtable 裡有指向 `Dog::describe` 的指標。

當你呼叫 `animal.describe()` 的時候，Rust 會去 vtable 裡查「`describe` 是哪個函數」，然後呼叫它。

```rust,editable
use std::mem::size_of;
#
# trait Describe {
#     fn describe(&self) -> String;
# }

fn main() {
    println!("{}", size_of::<&usize>());        // 8
    println!("{}", size_of::<&dyn Describe>()); // 16（位址 + vtable 指標）
    println!("{}", size_of::<&[i32]>());        // 16（位址 + 長度）
}
```

### 動態分派 vs 靜態分派

**靜態分派**（`impl Trait` / 泛型）：編譯器知道具體型別，為每個型別各生成一份函數的程式碼。這叫做 **monomorphization**（單態化）。呼叫方法時直接跳到對的函數，速度快，但如果型別很多，程式碼會變大。

```rust,editable
# use std::fmt::Display;
#
fn print_it(x: &impl Display) {
    println!("{}", x);
}

fn main() {
    print_it(&42);      // 編譯器生成 print_it::<i32>
    print_it(&"hello"); // 編譯器生成 print_it::<&str>
}
```

**動態分派**（`dyn Trait`）：編譯器只生成一份程式碼，執行期透過 vtable 查找要呼叫的函數。程式碼只有一份，但每次呼叫多了一層 vtable 查找。

| | 靜態分派（impl Trait / 泛型） | 動態分派（dyn Trait） |
|--|--|--|
| 決定時機 | 編譯期 | 執行期 |
| 程式碼量 | 每個型別一份 | 只有一份 |
| 呼叫速度 | 快（直接呼叫） | 稍慢（查 vtable） |
| 能混合不同型別 | 不能 | 能 |

大部分情況用靜態分派就好。需要把不同型別放在同一個位置的時候才用 `dyn Trait`。

### `Box<dyn Fn()>` vs `impl Fn()`

第 6 章學了閉包。`Box<dyn Fn()>` 讓你把不同的閉包統一成同一個型別：

```rust,editable
# fn main() {
    let callbacks: Vec<Box<dyn Fn()>> = vec![
        Box::new(|| println!("hello")),
        Box::new(|| println!("world")),
    ];

    for cb in &callbacks {
        cb();
    }
# }
```

`Vec<impl Fn()>` 做不到，因為每個閉包是不同的匿名型別。

### `dyn Trait` 的 lifetime bound

`dyn Trait` 後面可以加 lifetime bound，寫成 `dyn Trait + 'a`，讀成 `dyn (Trait + 'a)`——跟泛型裡的 `T: Trait + 'a` 意思一樣，`dyn` 把這個 bound 變成一個型別。

在某些位置，如果你沒寫 lifetime bound，編譯器會自動補上預設值。`Box<dyn Trait>` 的預設是 `'static`，所以完整寫法是 `Box<dyn Trait + 'static>`。`+ 'static` 代表裡面裝的具體型別不能包含任何非 `'static` 的參考。看看這個例子：

```rust,compile_fail
# trait Describe {
#     fn describe(&self) -> String;
# }
#
struct Foo<'a>(&'a str);

impl<'a> Describe for Foo<'a> {
    fn describe(&self) -> String { String::from(self.0) }
}

// 這個函數不會過編譯！
// Box<dyn Describe> = Box<dyn Describe + 'static>
// 但 Foo 借用了 s，s 不是 'static
fn make_box(s: &str) -> Box<dyn Describe> {
    Box::new(Foo(s))
}
#
# fn main() {}
```

如果需要裝有借用的型別，明確寫出 lifetime，覆蓋掉預設的 `'static`：

```rust,noplayground
# trait Describe {
#     fn describe(&self) -> String;
# }
# struct Foo<'a>(&'a str);
# impl<'a> Describe for Foo<'a> {
#     fn describe(&self) -> String { String::from(self.0) }
# }
#
fn make_box<'a>(s: &'a str) -> Box<dyn Describe + 'a> {
    Box::new(Foo(s))
}
```

`&'a dyn Trait` 則預設是 `&'a (dyn Trait + 'a)`——比較不用特別處理。

### `trait` upcasting

如果 `trait B` 是 `trait A` 的 subtrait（`trait B: A`），那 `dyn B` 可以轉成 `dyn A`：

```rust,noplayground
trait Animal {
    fn name(&self) -> &str;
}

trait Pet: Animal {
    fn owner(&self) -> &str;
}

fn print_animal_name(a: &dyn Animal) {
    println!("{}", a.name());
}

fn example(pet: &dyn Pet) {
    print_animal_name(pet); // dyn Pet → dyn Animal，OK
}
#
# fn main() {}
```

`Pet` 一定是 `Animal`，所以 `dyn Pet` 當然可以當 `dyn Animal` 用。

## 範例程式碼

```rust,editable
trait Describe {
    fn describe(&self) -> String;
}

struct Cat { name: String }
struct Dog { name: String }

impl Describe for Cat {
    fn describe(&self) -> String {
        format!("貓咪 {}", self.name)
    }
}

impl Describe for Dog {
    fn describe(&self) -> String {
        format!("狗狗 {}", self.name)
    }
}

fn make_animal(is_cat: bool, name: &str) -> Box<dyn Describe> {
    if is_cat {
        Box::new(Cat { name: String::from(name) })
    } else {
        Box::new(Dog { name: String::from(name) })
    }
}

fn main() {
    let animals: Vec<Box<dyn Describe>> = vec![
        Box::new(Cat { name: String::from("小花") }),
        Box::new(Dog { name: String::from("小黑") }),
        make_animal(true, "咪咪"),
        make_animal(false, "旺財"),
    ];

    for animal in &animals {
        println!("{}", animal.describe());
    }

    println!(
        "&dyn Describe 大小：{} bytes",
        std::mem::size_of::<&dyn Describe>()
    );
}
```

## 重點整理

- `dyn Trait` 代表「某個實作了 `Trait` 的型別，具體是什麼不知道」
- `dyn Trait` 是 DST，必須放在指標後面：`&dyn Trait`、`Box<dyn Trait>`
- `&dyn Trait` 是胖指標：資料位址 + vtable 指標
- 動態分派（`dyn Trait`）透過 vtable 查找方法；靜態分派（`impl Trait`）編譯期決定
- 大部分情況用靜態分派，需要混合不同型別時才用 `dyn Trait`
- `Box<dyn Fn()>` 可以把不同閉包統一成同一個型別
- `Box<dyn Trait>` 在某些地方預設隱含 `+ 'static`；`dyn Trait + 'a` 讀成 `dyn (Trait + 'a)`，`dyn` 把 `trait` bound 變成型別
- `dyn SubTrait` 可以轉成 `dyn SuperTrait`（trait upcasting）