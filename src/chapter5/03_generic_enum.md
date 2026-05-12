# 泛型 `enum`

## 本集目標

學會定義帶型別參數的 `enum`。

## 概念說明

上一集學了泛型 `struct`，這一集來看泛型 `enum`。其實概念完全一樣——在 `enum` 名稱後面加 `<T>`，讓 variant 攜帶的資料可以是任何型別。

### 定義泛型 `enum`

假設我們想做一個「也許有值」的型別，裡面可能有東西，也可能是空的：

```rust,noplayground
enum Maybe<T> {
    Something(T),
    Nothing,
}
#
# fn main() {}
```

`Something(T)` 攜帶一個 `T` 型別的值，`Nothing` 什麼都不帶。

泛型 `enum` 也可以有多個型別參數。比如一個「二選一」的型別：

```rust,noplayground
enum Either<L, R> {
    Left(L),
    Right(R),
}
#
# fn main() {}
```

`Either<L, R>` 要嘛是 `Left(L)`，要嘛是 `Right(R)`——兩個型別完全獨立。

## 範例程式碼

```rust
// 自己定義的泛型 enum
#[derive(Debug)]
enum Maybe<T> {
    Something(T),
    Nothing,
}

// 兩個型別參數的泛型 enum
#[derive(Debug)]
enum Either<L, R> {
    Left(L),
    Right(R),
}

fn main() {
    let a: Maybe<i32> = Maybe::Something(42);
    let b: Maybe<i32> = Maybe::Nothing;

    println!("{:?}", a);
    println!("{:?}", b);

    // 用 match 取出值
    match a {
        Maybe::Something(val) => println!("裡面有：{}", val),
        Maybe::Nothing => println!("空的"),
    }

    // 兩個型別參數
    let x: Either<i32, &str> = Either::Left(100);
    let y: Either<i32, &str> = Either::Right("hello");

    println!("{:?}", x);
    println!("{:?}", y);
}
```

## 重點整理

- `enum` 也可以帶型別參數：`enum Maybe<T> { ... }`
- variant 攜帶的資料型別可以用 `T` 來泛化
- 可以有多個型別參數：`enum Either<L, R> { Left(L), Right(R) }`
- 標準庫裡有很多重要的泛型 `enum`，之後會陸續認識
