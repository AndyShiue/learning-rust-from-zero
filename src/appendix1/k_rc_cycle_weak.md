# `Rc` 迴圈與 `Weak`

## 本集目標

理解 `Rc` 參考迴圈會造成記憶體洩漏，並學會用 `Weak` 來打破迴圈。

> 本集是**第 5 章**的補充。

## 概念說明

還記得第 5 章學的 `Rc<T>` 嗎？它透過參考計數來管理記憶體——每多一個 `Rc` 指向同一筆資料，計數就加一；每少一個就減一；歸零時釋放記憶體。

聽起來很完美，但有一個致命弱點：**參考迴圈（reference cycle）**。

### 什麼是參考迴圈？

想像兩個節點 A 和 B，A 持有 `Rc` 指向 B，B 也持有 `Rc` 指向 A。當外部不再持有它們的時候：

1. A 的外部 `Rc` 被 `drop` → A 的計數減一，但 B 還在指向 A → 計數不為零 → A 不釋放
2. B 的外部 `Rc` 被 `drop` → B 的計數減一，但 A 還在指向 B → 計數不為零 → B 不釋放

結果：A 和 B **永遠不會被釋放**，這就是記憶體洩漏。從外面看不見、卻互相撐著的環——這才是迴圈問題的本質。

### Weak 是什麼

`Weak<T>` 是一種「弱參考」——它指向同一筆資料，但**不會增加 strong count**。

```rust,noplayground
# use std::rc::{Rc, Weak};
#
# fn main() {
    let strong = Rc::new(42);
    let weak: Weak<i32> = Rc::downgrade(&strong);
# }
```

`Rc::downgrade` 把 `Rc` 降級成 `Weak`。`Rc` 內部有**兩個**計數器：strong count 和 weak count。`.clone()` 增加 strong count，`Rc::downgrade()` 只增加 weak count。`Rc` 判斷「要不要釋放值」只看 strong count——strong count 歸零就釋放，不管 weak count 是多少。

因為 `Weak` 指向的資料可能已經被釋放了，你不能直接存取。必須先 `.upgrade()`：

```rust,editable
# use std::rc::{Rc, Weak};
#
# fn main() {
#     let strong = Rc::new(42);
#     let weak: Weak<i32> = Rc::downgrade(&strong);
#
    match weak.upgrade() {
        Some(rc) => println!("還在：{}", rc),
        None => println!("已經被釋放了"),
    }
# }
```

`upgrade` 回傳 `Option<Rc<T>>`——如果資料還在，給你一個 `Rc`；如果已經釋放，回傳 `None`。

### 用 `Weak` 打破迴圈

回到剛才的例子。關鍵問題是：strong count 構成的圖上有環。只要把其中一個方向改成 `Weak`，strong count 的圖上就沒有環了——因為 `Weak` 不貢獻 strong count。

用一個具體的例子來說明。假設我們想建一個**雙向鏈結串列（doubly linked list）**——每個節點同時指向前一個和後一個節點，這樣我們要從頭走到尾還是從尾走到頭都很容易。如果兩個方向都用 `Rc`，相鄰的兩個節點就形成迴圈。

解法是：`next`（往後）用 `Rc`，`prev`（往前）用 `Weak`：

```rust,noplayground
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Node<T> {
    value: T,
    next: Option<Rc<RefCell<Node<T>>>>,
    prev: Option<Weak<RefCell<Node<T>>>>,
}
#
# fn main() {}
```

為什麼這樣就不會迴圈？看 strong count 的圖：

```text
外部 ──Rc──→ A ──Rc──→ B ──Rc──→ C
              ←·Weak·←   ←·Weak·←
```

`Weak` 那些邊不算在 strong count 裡。strong count 的圖只有從左到右的箭頭，是一條鏈，沒有環。

外部放掉 A → A 的 strong count 歸零 → A 被 `drop` → A 的 `next` 也跟著 `drop` → B 的 strong count 歸零 → B 被 `drop` → …… 連鎖反應一路到底。中間沒有任何節點被 `prev` 撐住，因為 `prev` 是 `Weak`，不貢獻 strong count。

### `upgrade` 出來的 `Rc` 會造成問題嗎？

你可能會想：「如果我 `upgrade` 一個 `Weak` 拿到 `Rc` 之後一直握著不放，不就多了一個 strong count 嗎？」

沒錯，`upgrade` 出來的 `Rc` 確實會讓 strong count +1。但這個 `Rc` 是一個**獨立的變數**——它的 strong count 貢獻記在「持有那個 `Rc` 的變數」頭上，不是記在原本的 `Weak` 欄位上。`Weak` 欄位本身對 strong count 的貢獻永遠是 0。

迴圈問題在資料結構建好的當下就已經被解決或沒被解決了，跟你之後怎麼 `upgrade` 完全無關。

## 範例程式碼

```rust,editable
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Node<T> {
    value: T,
    next: Option<Rc<RefCell<Node<T>>>>,
    prev: Option<Weak<RefCell<Node<T>>>>,
}

impl<T> Node<T> {
    fn new(value: T) -> Rc<RefCell<Node<T>>> {
        Rc::new(RefCell::new(Node { value, next: None, prev: None }))
    }
}

/// 把 b 接在 a 後面
fn link<T>(a: &Rc<RefCell<Node<T>>>, b: &Rc<RefCell<Node<T>>>) {
    a.borrow_mut().next = Some(b.clone());
    b.borrow_mut().prev = Some(Rc::downgrade(a));
}

fn main() {
    let a = Node::new(1);
    let b = Node::new(2);
    let c = Node::new(3);

    link(&a, &b);
    link(&b, &c);

    // 從前往後走（用 Rc）
    print!("往後走：");
    let mut current = Some(a.clone());
    while let Some(node) = current {
        print!("{} ", node.borrow().value);
        // next 是 Option<Rc<...>>，as_ref 變成 Option<&Rc<...>>，再 map clone 出新的 Rc
        current = node.borrow().next.as_ref().map(|rc| rc.clone());
    }
    println!();

    // 從後往前走（用 Weak，需要 upgrade）
    print!("往前走：");
    let mut current = Some(c.clone());
    while let Some(node) = current {
        print!("{} ", node.borrow().value);
        current = node.borrow().prev.as_ref().and_then(|w| w.upgrade());
    }
    println!();

    // 檢查計數
    // strong count 記在被指向的節點上：
    // a.next 指向 b → b 的 strong +1，b.next 指向 c → c 的 strong +1
    // weak count 也記在被指向的節點上：
    // b.prev 指向 a → a 的 weak +1，c.prev 指向 b → b 的 weak +1
    // a: strong=1（變數 a），weak=1（b.prev）
    // b: strong=2（變數 b + a.next），weak=1（c.prev）
    // c: strong=2（變數 c + b.next），weak=0（沒有節點的 prev 指向 c）
    println!("a strong={}, weak={}", Rc::strong_count(&a), Rc::weak_count(&a));
    println!("b strong={}, weak={}", Rc::strong_count(&b), Rc::weak_count(&b));
    println!("c strong={}, weak={}", Rc::strong_count(&c), Rc::weak_count(&c));
}
```

## 重點整理

- `Rc` 的參考迴圈會造成記憶體洩漏——strong count 永遠無法歸零
- `Weak` 不增加 strong count，所以不會阻止資料被釋放
- `Rc::downgrade(&rc)` 建立 `Weak<T>`，`weak.upgrade()` 回傳 `Option<Rc<T>>`
- 用 `Weak` 打破迴圈：讓 strong count 構成的圖上不會有環
- 雙向鏈結串列的做法：`next` 用 `Rc`（擁有後繼），`prev` 用 `Weak`（觀察前驅）
- `Weak` 欄位對 strong count 的貢獻永遠是 0，`upgrade` 出來的 `Rc` 是獨立的變數
- `Rc::strong_count()` 和 `Rc::weak_count()` 可以查看目前的計數
