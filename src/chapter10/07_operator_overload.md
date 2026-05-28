# 運算子重載

## 本集目標

學會幫自己的型別實作 `+`、`-` 等運算子。

## 概念說明

### 運算子就是 `trait` 方法

Rust 裡 `a + b` 其實是 `a.add(b)` 的簡寫——`+` 對應 `std::ops::Add` trait。幫你的型別實作 `Add`，就能用 `+`。

### `Add` `trait` 的定義

```rust,noplayground
trait Add<Rhs = Self> {
    type Output;
    fn add(self, rhs: Rhs) -> Self::Output;
}
#
# fn main() {}
```

三個重點：

- `Rhs = Self`：上一集學的預設參數，加法右邊預設和左邊同型別
- `type Output`：第 5 章學的 associated type，加法的結果不一定跟輸入同型別
- `self` 不是 `&self`：`add` 會消耗左邊的值（`Copy` 的型別不受影響）

### 幫 `Point` 實作 `Add`

```rust,noplayground
use std::ops::Add;

#[derive(Debug)]
struct Point { x: i32, y: i32 }

impl Add for Point {
    type Output = Point;
    fn add(self, rhs: Point) -> Point {
        Point {
            x: self.x + rhs.x,
            y: self.y + rhs.y,
        }
    }
}
#
# fn main() {}
```

### 常用運算子

`std::ops` 裡常用的 `trait`：

| 運算子 | `trait` | 方法 |
|--------|---------|------|
| `+` | `Add` | `add(self, rhs)` |
| `-` | `Sub` | `sub(self, rhs)` |
| `*` | `Mul` | `mul(self, rhs)` |
| `/` | `Div` | `div(self, rhs)` |
| `%` | `Rem` | `rem(self, rhs)` |
| `-x` | `Neg` | `neg(self)` |
| `!x` | `Not` | `not(self)` |
| `&` | `BitAnd` | `bitand(self, rhs)` |
| `\|` | `BitOr` | `bitor(self, rhs)` |
| `^` | `BitXor` | `bitxor(self, rhs)` |
| `<<` | `Shl` | `shl(self, rhs)` |
| `>>` | `Shr` | `shr(self, rhs)` |
| `+=` | `AddAssign` | `add_assign(&mut self, rhs)` |
| `&=` | `BitAndAssign` | `bitand_assign(&mut self, rhs)` |
| `[]` | `Index` | `index(&self, idx)` |
| `[]` 可變 | `IndexMut` | `index_mut(&mut self, idx)` |

位元運算子（`&`、`|`、`^`、`<<`、`>>`、`!`）在系統程式設計中很常用——處理旗標、遮罩、位元欄位等等。如果你還不熟悉位元運算，建議自行查閱相關資料。

上面列的所有二元運算子都有對應的 assign 版本（例如 `&=` 對應 `BitAndAssign`、`<<=` 對應 `ShlAssign`），用法跟前面教過的 `+=` 或 `-=` 類似。

### `AddAssign` vs `Add`

`a += b` 和 `a = a + b` 在 Rust 裡的實作不一定一樣：

- `Add::add(self, rhs)` 消耗 `a`，產生新值
- `AddAssign::add_assign(&mut self, rhs)` 就地修改 `a`

對 `i32` 感覺差不多，但對非 `Copy` 型別（如 `String`），`s1 += &s2` 直接追加內容，`s1 = s1 + &s2` 先消耗 `s1` 再建新的。效率和語意不同，所以需要分開的 `trait`。

`Add` 和 `AddAssign` 是完全獨立的——實作了 `Add` 不代表 `+=` 自動能用，反過來也是。沒實作就是編譯錯誤。

### `Index` / `IndexMut`

`Vec` 能用 `v[i]` 就是因為它實作了 `Index`：

```rust,noplayground
use std::ops::Index;

struct MyVec(Vec<i32>);

impl Index<usize> for MyVec {
    type Output = i32;
    fn index(&self, idx: usize) -> &i32 {
        &self.0[idx]
    }
}
#
# fn main() {}
```

### 不同型別相加

覆蓋 `Rhs` 的預設值：

```rust,noplayground
use std::ops::Add;

struct Meters(f64);
struct Centimeters(f64);

impl Add<Centimeters> for Meters {
    type Output = Meters;
    fn add(self, rhs: Centimeters) -> Meters {
        Meters(self.0 + rhs.0 / 100.0)
    }
}
#
# fn main() {}
```

## 範例程式碼

```rust,editable
use std::ops::{Add, Neg};

#[derive(Debug, Clone, Copy)]
struct Vec2 { x: f64, y: f64 }

impl Add for Vec2 {
    type Output = Vec2;
    fn add(self, rhs: Vec2) -> Vec2 {
        Vec2 { x: self.x + rhs.x, y: self.y + rhs.y }
    }
}

impl Neg for Vec2 {
    type Output = Vec2;
    fn neg(self) -> Vec2 {
        Vec2 { x: -self.x, y: -self.y }
    }
}

fn main() {
    let a = Vec2 { x: 1.0, y: 2.0 };
    let b = Vec2 { x: 3.0, y: 4.0 };
    let c = a + b;
    println!("a + b = {:?}", c);
    println!("-a = {:?}", -a);
}
```

## 重點整理

- `a + b` 是 `Add::add(a, b)` 的簡寫，其他運算子同理
- `Add` 的簽名用了預設參數（`Rhs = Self`）和 associated type（`Output`）
- `AddAssign`（`+=`）是就地修改（`&mut self`），`Add`（`+`）是產生新值（`self`）
- `Index` / `IndexMut` 讓你的型別能用 `[]` 運算子
- 覆蓋 `Rhs` 可以實現不同型別之間的運算
