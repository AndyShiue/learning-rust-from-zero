# `RefCell<T>`

## 本集目標

學會用 `RefCell<T>` 在執行期檢查借用規則，搭配 `Rc` 實現可變的共享資料。

## 概念說明

上一集學了 `Cell<T>`，但它的限制是 `T` 必須是 `Copy`。如果你想修改一個 `String` 或 `Vec` 呢？

### `RefCell`：執行期的借用檢查

`RefCell<T>` 和 `Cell` 類似——讓你在不需要 `&mut` 的情況下修改值。差別在於：

- `Cell<T>`：用 `get` / `set`，`T` 必須 `Copy`，**零成本**（編譯後和直接存取沒有差別）
- `RefCell<T>`：用 `.borrow()` 和 `.borrow_mut()` 取得參考，`T` **不需要** `Copy`，但**有執行期成本**（每次借用都要檢查有沒有違反規則）

```rust,editable
use std::cell::RefCell;

fn main() {
    let x = RefCell::new(String::from("hello"));
    x.borrow_mut().push_str(" world"); // 修改裡面的 String
    println!("{}", x.borrow());        // 借用來讀
}
```

### 執行期檢查

普通的 `&` 和 `&mut` 是在**編譯時期**檢查借用規則。`RefCell` 把這個檢查移到了**執行時期**。規則一模一樣（一個 `&mut` 或多個 `&`），只是違反時不是編譯錯誤，而是 **panic**。

```rust,should_panic
# #![allow(unused_variables)]
#
# use std::cell::RefCell;
#
# fn main() {
    let x = RefCell::new(42);
    let a = x.borrow();     // 不可變借用
    let b = x.borrow_mut(); // panic！已經有不可變借用了
# }
```

所以 `RefCell` 不是「繞過」借用規則，而是「延後檢查」。

### `Rc` + `RefCell`：可變的共享資料

`Rc<T>` 可以共享資料，但不能改。`RefCell<T>` 可以改，但不能共享。把它們組合起來：

```rust,noplayground
use std::rc::Rc;
use std::cell::RefCell;

fn main() {
    let shared = Rc::new(RefCell::new(vec![1, 2, 3]));
}
```

這樣多個 `Rc` 可以共享同一份資料，而且透過 `borrow_mut()` 可以修改它。

## 範例程式碼

```rust,editable
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    // 基本的 RefCell 用法
    let data = RefCell::new(String::from("hello"));

    // 不可變借用
    {
        let borrowed = data.borrow();
        println!("讀取：{}", borrowed);
    } // borrowed 離開作用域，釋放借用

    // 可變借用
    {
        let mut borrowed_mut = data.borrow_mut();
        borrowed_mut.push_str(" world");
    } // borrowed_mut 離開作用域，釋放借用

    println!("修改後：{}", data.borrow());

    // 違反借用規則 → panic！
    // 取消下面的註解就會在執行時 panic
    // {
    //     let r1 = data.borrow();      // 不可變借用
    //     let r2 = data.borrow_mut();  // 同時可變借用 → panic!
    // }

    // Rc + RefCell：可變的共享資料
    let shared = Rc::new(RefCell::new(vec![1, 2, 3]));

    let a = shared.clone();
    let b = shared.clone();

    // 透過 a 修改
    a.borrow_mut().push(4);

    // 透過 b 也能看到修改
    println!("透過 b 讀取：{:?}", b.borrow());

    // 透過 b 修改
    b.borrow_mut().push(5);

    // 透過 a 也能看到
    println!("透過 a 讀取：{:?}", a.borrow());
}
```

## 重點整理

- `RefCell<T>` 和 `Cell` 類似——讓你在不需要 `&mut` 的情況下修改值
- `RefCell<T>` 把借用規則的檢查從編譯時移到執行時
- `.borrow()` 取得不可變參考，`.borrow_mut()` 取得可變參考
- `T` **不需要** `Copy`（和 `Cell` 的差別）
- `Cell` 是零成本的，但 `RefCell` 每次借用都有執行期檢查的開銷
- 違反借用規則時會 **panic**（不是編譯錯誤）
- `Rc<RefCell<T>>` 組合：可變的共享資料
