# 多參數 `trait`

## 本集目標

學會定義帶其他型別參數的 `trait`，讓同一個型別可以針對不同目標型別實作同一個 `trait`。

## 概念說明

到目前為止，我們的 `trait` 都比較簡單——`Clone`、`Display`、`Describe`，沒有其他型別參數。但有時候你想定義的行為和**另一個型別**有關。

比如「轉換」這件事：`i32` 可以轉成 `f64`，也可以轉成 `String`。同一個型別，轉換的目標不同，邏輯也不同。

### 帶其他型別參數的 `trait`

```rust,noplayground
trait Convert<T> {
    fn convert(self) -> T;
}
#
# fn main() {}
```

`Convert<T>` 的意思是：「可以轉換成 `T` 型別」。同一個型別可以實作 `Convert<f64>`、`Convert<String>` 等不同版本。

### 實作多參數 `trait`

```rust,noplayground
# trait Convert<T> {
#     fn convert(self) -> T;
# }
#
impl Convert<(i32,)> for i32 {
    fn convert(self) -> (i32,) {
        (self,)
    }
}
#
# fn main() {}
```

這裡 `i32` 實作了 `Convert<(i32,)>`——把自己轉成單元素 tuple。

同一個型別可以實作多次，只要型別參數不同：

```rust,noplayground
# trait Convert<T> {
#     fn convert(self) -> T;
# }
#
impl Convert<String> for i32 {
    fn convert(self) -> String {
        // 用 ToString trait（i32 已經有了）
        self.to_string()
    }
}
#
# fn main() {}
```

### 和沒有其他參數的 `trait` 的差別

- `Clone`（沒有其他參數）：一個型別只能實作一次 `Clone`
- `Convert<T>`（有其他參數）：一個型別可以實作 `Convert<String>`、`Convert<(i32,)>` 等多個版本

## 範例程式碼

```rust,editable
// 定義一個帶型別參數的 trait
trait Convert<T> {
    fn convert(self) -> T;
}

// i32 轉成單元素 tuple
impl Convert<(i32,)> for i32 {
    fn convert(self) -> (i32,) {
        (self,)
    }
}

// i32 轉成 String
impl Convert<String> for i32 {
    fn convert(self) -> String {
        self.to_string()
    }
}

// bool 轉成 i32
impl Convert<i32> for bool {
    fn convert(self) -> i32 {
        if self {
            1
        } else {
            0
        }
    }
}

fn main() {
    // i32 -> (i32,)
    let x: i32 = 42;
    let tuple: (i32,) = x.convert();
    println!("{:?}", tuple);

    // i32 -> String
    let y: i32 = 100;
    let s: String = y.convert();
    println!("{}", s);

    // bool -> i32
    let b = true;
    let n: i32 = b.convert();
    println!("{}", n);
}
```

## 重點整理

- `trait` 可以帶其他型別參數：`trait Convert<T> { ... }`
- 同一個型別可以對不同的 `T` 實作同一個 `trait`（例如 `Convert<String>` 和 `Convert<(i32,)>`）
- 這和沒有其他參數的 `trait` 不同——一個型別只能實作一次那些 `trait`
- 多參數 `trait` 讓「和另一個型別相關的行為」可以統一定義
