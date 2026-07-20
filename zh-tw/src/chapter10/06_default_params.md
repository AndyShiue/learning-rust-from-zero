# 預設參數

## 本集目標

學會型別參數和 `const` generic 參數可以在哪些地方設定預設值，以及如何定義。

## 概念說明

### 預設型別參數

在 `struct`、`enum`、`union`、型別別名和 `trait` 的宣告中，如果某個型別參數大部分情況都是同一種型別，就可以為它設定預設值。使用該型別或 `trait` 時若省略這個引數，就會套用預設值。函數和方法的泛型參數則不能有預設值。

以標準庫的 `PartialEq` 為例：

```rust,noplayground
trait PartialEq<Rhs = Self> {
    fn eq(&self, other: &Rhs) -> bool;
}
#
# fn main() {}
```

`Rhs = Self` 表示：如果你不指定 `Rhs`，預設就是 `Self`。所以 `impl PartialEq for Point` 等同於 `impl PartialEq<Point> for Point`——比較的對象預設是自己。

如果偶爾想比較不同型別，覆蓋就行：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl PartialEq<(i32, i32)> for Point {
    fn eq(&self, other: &(i32, i32)) -> bool {
        self.x == other.0 && self.y == other.1
    }
}
#
# fn main() {}
```

### 自己定義

用 `=` 在泛型定義裡給預設值：

```rust,noplayground
struct Container<T = String> {
    value: T,
}

fn main() {
    let c: Container = Container { value: String::from("hello") }; // T 預設是 String
    let c2: Container<i32> = Container { value: 42 };              // 手動指定
}
```

### `const` generics 的預設值

`const` generic 參數也能在上述型別與 `trait` 宣告中設定預設值，但同樣不能在函數或方法上設定。

```rust,noplayground
struct Buffer<const N: usize = 1024> {
    data: [u8; N],
}

fn main() {
    let buf: Buffer = Buffer { data: [0; 1024] };     // N 預設是 1024
    let small: Buffer<64> = Buffer { data: [0; 64] }; // 手動指定
}
```

### 有預設值的參數必須放後面

```rust,noplayground
struct Pair<T, U = T> { // OK：U 有預設值，放在 T 後面
    first: T,
    second: U,
}
#
# fn main() {}
```

## 範例程式碼

```rust,editable
struct Pair<T, U = T> {
    first: T,
    second: U,
}

impl<T: std::fmt::Debug, U: std::fmt::Debug> Pair<T, U> {
    fn show(&self) {
        println!("({:?}, {:?})", self.first, self.second);
    }
}

fn main() {
    // U 用預設值（= T = i32）
    let p1: Pair<i32> = Pair { first: 1, second: 2 };
    p1.show();

    // 手動指定 U
    let p2: Pair<i32, &str> = Pair { first: 42, second: "hello" };
    p2.show();
}
```

## 重點整理

- 型別參數可以在 `struct`、`enum`、`union`、型別別名和 `trait` 宣告中設定預設值。
- `const` generic 參數也能在相同的位置設定預設值。
- 函數和方法的泛型參數不能有預設值。
- 語法為 `<T = String>`、`<Rhs = Self>` 或 `<const N: usize = 1024>`。
- 不指定就套用預設，指定了就覆蓋。
- `PartialEq<Rhs = Self>` 是標準庫最典型的例子。
- 有預設值的參數必須放在沒有預設值的參數後面。
