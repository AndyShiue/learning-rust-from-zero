# `trait` 簡介

## 本集目標

學會定義 `trait` 和為型別實作 `trait`，並認識 `#[derive]` 這個自動產生實作的捷徑。

## 概念說明

### 什麼是 `trait`？

在進入所有權的主題之前，我們先來學一個重要的工具：**`trait`**。它和上一集的鑰匙圈比喻沒有直接關係，但之後講 `Clone`、`Copy` 等概念的時候會用到，所以先學起來。

在第 3 章，我們學會了用 `impl` 幫 `struct` 和 `enum` 加上 method。但如果我們想要規定「某些型別都必須有某個功能」呢？

比如說，我想規定：「某些型別都必須能打招呼。」這就是 **`trait`** 的用途——它定義了一組「能力」或「行為」，然後不同的型別可以各自實作這些行為。

`trait` 就像一張「規格表」，上面寫著：「你要符合這個規格，就必須提供這些功能。」

### 定義 `trait`

用 `trait` 關鍵字來定義：

```rust,noplayground
trait Greet {
    fn greet(self);
}
#
# fn main() {}
```

這段程式碼的意思是：「凡是實作了 `Greet` 這個 `trait` 的型別，都必須有一個 `greet` method。」

### 為型別實作 `trait`

```rust,noplayground
# trait Greet {
#     fn greet(self);
# }
#
# struct Cat;
#
impl Greet for Cat {
    fn greet(self) {
        println!("喵～");
    }
}
#
# fn main() {}
```

之前我們寫 `impl Cat { ... }` 是直接幫 `Cat` 加 method。現在寫 `impl Greet for Cat { ... }` 是說「`Cat` 符合 `Greet` 這個規格」，然後在裡面提供 `Greet` 要求的 method。

### `derive`：自動產生實作的捷徑

有些 `trait` 的實作方式很固定，Rust 編譯器可以幫你自動產生。這時候就用 `#[derive(...)]`：

```rust,noplayground
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

還記得第 2 章我們用 `{:?}` 印出 tuple 和陣列嗎？其實 `{:?}` 就是在使用 `Debug` 這個 `trait`。tuple 和陣列內建就有 `Debug`，但我們自己定義的 `struct` 和 `enum` 沒有——所以要加 `#[derive(Debug)]`，讓 Rust 自動幫我們產生 `Debug` 的實作。

## 範例程式碼

```rust,editable
// 定義一個 trait：所有實作者都必須能「打招呼」
trait Greet {
    fn greet(self);
}

// 定義兩種動物
struct Cat;
struct Dog;

// 幫 Cat 實作 Greet
impl Greet for Cat {
    fn greet(self) {
        println!("我是一隻貓咪喵～");
    }
}

// 幫 Dog 實作 Greet
impl Greet for Dog {
    fn greet(self) {
        println!("我是一隻狗狗汪！");
    }
}

// 用 derive 讓 Rust 自動產生 Debug 實作
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let cat = Cat;
    let dog = Dog;

    // 呼叫 trait method
    cat.greet();
    dog.greet();

    // 用 {:?} 印出 struct（因為有 #[derive(Debug)]）
    let p = Point { x: 3, y: 7 };
    println!("{:?}", p);
}
```

## 重點整理

- **`trait`** 是一組行為的規格定義，像是一張「能力清單」
- 用 `impl TraitName for TypeName` 來幫型別實作 `trait`（例如 `impl Greet for Cat`）
- `#[derive(Debug)]` 讓 Rust 自動幫你的 `struct` / `enum` 實作 `Debug` `trait`
- 加了 `#[derive(Debug)]` 之後，就可以用 `{:?}` 來印出自訂的 `struct` / `enum`
