# Rust 教學

用繁體中文寫的 Rust 程式語言教學，口語化風格，每集 10 分鐘內讀完。

📖 **線上閱讀**：[https://andyshiue.github.io/rust-book/](https://andyshiue.github.io/rust-book/)

## 目錄

### 第一章：基礎（27 集）
變數、型別、if/else、迴圈、基本 I/O。從零開始，不需要任何程式經驗。

### 第二章：函數、陣列與切片（15 集）
函數、陣列、切片、`for` 迴圈走訪。

### 第三章：Struct、Enum 與 Pattern Matching（30 集）
自訂型別、match 表達式、各種 pattern（tuple、slice、nested、guard 等）、method 與 associated function。

### 第四章：所有權與借用（14 集）
Rust 最核心的概念——所有權、move、借用規則、String vs &str、Vec。

### 第五章：泛型、Trait Bound 與生命週期（33 集）
泛型函數與型別、trait 與 trait bound、impl Trait、Box、Rc、Deref、Cell/RefCell、生命週期、Cow。

### 第六章：閉包與迭代器（15 集）
閉包語法、Fn/FnMut/FnOnce、Iterator trait、常用迭代器方法。

### 第七章：Cargo、Crate 與 Mod 系統（10 集）
Cargo 專案管理、use/mod、可見性、cargo test、發布 crate。

### 附錄一（11 集）
數字字面值、格式化字串、break 回傳值、raw string、struct 放 main 裡、struct update syntax、ref/match ergonomics、panic!/todo!/unreachable!、Rc 迴圈與 Weak、fully qualified syntax、DST 簡介。

### 第八章：多執行緒（13 集）
指標與記憶體位址、thread::spawn、Send/Sync、RefCell 與 Rc 在多執行緒下的限制、Arc、Atomic 型別、Mutex、RwLock、poisoning、mpsc channel、死鎖、thread::scope。

### 第九章：進階語言功能（19 集）
dyn Trait、dyn compatibility、const fn、associated const、const generics、預設參數、運算子重載、型別轉換 as、enum discriminant、attribute 總覽、cfg! macro、macro_rules!、proc macro、unsafe、static 變數、LazyLock、extern blocks、union、never type。

## 特色

- **繁體中文**，不是翻譯，是原生中文撰寫
- **口語化**風格，像在跟朋友解釋
- **每集短小**，適合零碎時間閱讀
- 不會用到還沒教過的概念
- 範例程式碼都能編譯通過
- Rust edition 2024

## 本地建置

需要 Python 3 和 `markdown` 套件：

```bash
pip install markdown
python build_book.py
```

會產出 `rust_book.html`，用瀏覽器開啟即可。

## 授權

本教學內容由 [Andy Shiue](https://github.com/AndyShiue) 撰寫。