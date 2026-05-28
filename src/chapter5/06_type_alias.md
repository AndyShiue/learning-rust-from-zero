# 型別別名

## 本集目標

學會用 `type` 為型別建立別名，讓複雜的泛型型別變得更好讀。

## 概念說明

隨著我們學了泛型，型別會越來越複雜。比如一個三維的資料結構：

```rust,ignore
Vec<Vec<Vec<i32>>>
```

每次都寫完整型別有點累，而且不好讀。Rust 提供了 `type` 關鍵字來建立**型別別名**：

```rust,noplayground
type Grid3D = Vec<Vec<Vec<i32>>>;
#
# fn main() {}
```

從此以後，`Grid3D` 和 `Vec<Vec<Vec<i32>>>` 就是同一個型別——只是換了個名字。它不會建立新型別，就只是一個簡寫。

### 簡單的別名

```rust,noplayground
type Name = String;
#
# fn main() {}
```

`Name` 和 `String` 完全等價，可以互換使用。

### 帶參數的型別別名

型別別名也可以帶泛型參數：

```rust,noplayground
type Pair<T> = (T, T);
#
# fn main() {}
```

這樣 `Pair<i32>` 就等於 `(i32, i32)`，`Pair<String>` 就等於 `(String, String)`。

### 注意

型別別名只是簡寫，不是新型別。`Name` 和 `String` 完全可以互換使用，編譯器視它們為同一個型別。

## 範例程式碼

```rust,editable
// 簡單的型別別名
type Name = String;

// 簡化複雜的巢狀型別
type Grid3D = Vec<Vec<Vec<i32>>>;

// 帶泛型參數的別名
type Pair<T> = (T, T);

fn main() {
    // Name 就是 String
    let greeting: Name = String::from("你好");
    println!("{}", greeting);

    // 三維 Vec 用別名就很清爽
    let mut grid: Grid3D = vec![vec![vec![0; 3]; 3]; 3];
    grid[1][1][1] = 42;
    println!("grid[1][1][1] = {}", grid[1][1][1]);

    // Pair<i32> 就是 (i32, i32)
    let point: Pair<i32> = (3, 7);
    println!("{:?}", point);

    let coords: Pair<f64> = (1.5, 3.7);
    println!("{:?}", coords);
}
```

## 重點整理

- `type Name = ExistingType;` 建立型別別名，只是簡寫，不是新型別
- 型別別名可以帶泛型參數：`type Pair<T> = (T, T);`
- 常見用途：簡化複雜的巢狀型別（如 `Vec<Vec<Vec<i32>>>`）
- 別名和原型別完全等價，可以互換使用
