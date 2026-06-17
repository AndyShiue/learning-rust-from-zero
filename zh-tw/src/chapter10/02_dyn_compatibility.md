# `dyn` compatibility

## 本集目標

理解哪些 `trait` 可以用 `dyn`、哪些不行，以及背後的原因。

## 概念說明

### 不是所有 `trait` 都能用 `dyn`

上一集學了 `dyn Trait`。但如果你嘗試寫 `dyn Clone`，會得到編譯錯誤。這是因為 `Clone` 不是 **`dyn` compatible** 的。

### 核心概念：`impl Trait for dyn Trait`

要理解 dyn compatibility，先想想 `dyn Trait` 是怎麼運作的。編譯器自動生成了一個：

```rust,ignore
impl Trait for dyn Trait {
    fn method(&self, ...) {
        // 查 vtable，呼叫實際的實作
    }
}
```

在這個自動生成的 `impl` 裡，`Self` = `dyn Trait`。而 `dyn Trait` 是 DST——大小不固定、不是 `Sized`。

如果 `trait` 的某些方法在 `Self = dyn Trait` 的情況下沒辦法運作，這個 `trait` 就不是 `dyn` compatible 的。具體來說有以下幾種情況：

### 限制一：`Self` 不能出現在 `self` 之外的型別中

```rust,ignore
trait Compare {
    fn compare(&self, other: &Self) -> bool;
}

impl Compare for Cat {
    fn compare(&self, other: &Cat) -> bool { ... }
}

impl Compare for Dog {
    fn compare(&self, other: &Dog) -> bool { ... }
}
```

`compare` 的第二個參數是 `&Self`。當你用 `dyn Compare` 的時候，具體型別已經被抹掉了——你不知道裡面是 `Cat` 還是 `Dog`。但 `Cat::compare` 期望的是 `&Cat`，`Dog::compare` 期望的是 `&Dog`。

如果有人傳了一個 `Dog` 進來，但 vtable 找到的函數是 `Cat::compare`，函數就會把 `Dog` 的資料當成 `Cat` 來用——型別搞混了。

要確保不搞混，編譯器就需要在執行期檢查「傳進來的 `y` 的具體型別跟 `x` 的具體型別一樣」。但 `dyn` 的重點就是把具體型別抹掉了，編譯器已經不知道原本是什麼型別，沒辦法做這個檢查。所以 Rust 直接禁止這樣做。

### 限制二：方法不能有泛型參數

```rust,noplayground
trait Converter {
    fn convert<U>(&self) -> U;
}
#
# fn main() {}
```

vtable 是一張固定大小的函數指標表。但泛型方法對每個不同的 `U` 都是一個不同的函數——`convert::<i32>` 和 `convert::<String>` 是兩個不同的函數指標。vtable 沒辦法塞進無限多個版本。

主要是 vtable 必須在編譯 `impl` 的那一方建好——因為只有那邊才知道 `Self` 的具體型別。但編譯 `impl` 的時候，你不知道使用者之後會用哪些 `U`，所以 vtable 不可能提前準備好所有版本。

### 限制三：`trait` 本身不能要求 `Self: Sized`

回頭看開頭的問題——為什麼 `dyn Clone` 不行？除了回傳 `Self`，其實 `Clone` 有一個 supertrait 就是 `Sized`：

```rust,noplayground
trait Clone: Sized {
    fn clone(&self) -> Self;
}
#
# fn main() {}
```

`Clone: Sized` 代表「實作 Clone 的型別必須是 Sized」。但 `dyn Clone` 是 DST，不是 `Sized`。所以 `impl Clone for dyn Clone` 根本不成立，`dyn Clone` 無法存在。

### 退出機制：`where Self: Sized`

如果一個 `trait` 只有一部分的方法是 `dyn` compatible，其他不是，可以在那些其他方法上全部加 `where Self: Sized` 讓它們退出：

```rust,noplayground
trait MyTrait {
    fn normal(&self) -> String; // dyn MyTrait 上能呼叫
    fn special(&self) -> Self   // 回傳 Self，不 dyn compatible
        where Self: Sized;      // 加上這個，讓它退出
}
#
# fn main() {}
```

`where Self: Sized` 的意思是「只有 `Self` 是 `Sized` 的時候才能呼叫這個方法」。`dyn MyTrait` 不是 `Sized`，所以這個方法在 `dyn MyTrait` 上不能呼叫——但 `trait` 本身還是 `dyn` compatible 的，其他方法仍然能透過 `dyn MyTrait` 使用。

```rust,ignore
let x: &dyn MyTrait = &something;
x.normal(); // OK
// x.special(); // 編譯錯誤：dyn MyTrait 不是 Sized
```

`dyn` compatibility 的完整規則其實比這集講的更複雜，但八九不離十就是這些了。

## 範例程式碼

```rust,editable
// dyn compatible 的 trait
trait Greet {
    fn greet(&self) -> String;
}

struct Alice;
struct Bob;

impl Greet for Alice {
    fn greet(&self) -> String { String::from("Hi, I'm Alice!") }
}

impl Greet for Bob {
    fn greet(&self) -> String { String::from("Hey, I'm Bob!") }
}

// 混合使用 where Self: Sized 的 trait
trait Animal {
    fn name(&self) -> &str;

    // 這個方法不 dyn compatible（回傳 Self），用 where Self: Sized 退出
    fn duplicate(&self) -> Self
    where
        Self: Sized + Clone;
}

#[derive(Clone)]
struct Cat { name: String }

impl Animal for Cat {
    fn name(&self) -> &str { &self.name }
    fn duplicate(&self) -> Self
    where
        Self: Sized + Clone,
    {
        self.clone()
    }
}

fn main() {
    // dyn Greet：不同型別放在同一個 Vec
    let greeters: Vec<Box<dyn Greet>> = vec![
        Box::new(Alice),
        Box::new(Bob),
    ];

    for g in &greeters {
        println!("{}", g.greet());
    }

    // dyn Animal：name() 能用，duplicate() 不能用
    let cat = Cat { name: String::from("小花") };
    let animal: &dyn Animal = &cat;
    println!("動物：{}", animal.name());  // OK
    // animal.duplicate(); // 編譯錯誤：dyn Animal 不是 Sized

    // 但用具體型別就能呼叫 duplicate
    let cat2 = cat.duplicate();
    println!("複製：{}", cat2.name());
}
```

## 重點整理

- 不是所有 `trait` 都能用 `dyn`——必須是 `dyn` compatible 的
- 核心概念：編譯器自動生成 `impl Trait for dyn Trait`，`Self` = `dyn Trait`（DST）
- `Self` 不能出現在 `self` 之外的型別中——具體型別已被抹掉
- 方法不能有泛型參數——vtable 固定大小，放不下無限多版本
- trait 不能要求 `Self: Sized`——`dyn Trait` 是 DST，不是 `Sized`
- 個別方法加 `where Self: Sized` 可以讓它退出 `dyn`，`trait` 本身仍然 `dyn` compatible
