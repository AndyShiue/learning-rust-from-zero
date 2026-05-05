# 安裝 Rust

## 本集目標
把 Rust 裝到你的電腦上，確認它可以用。

## 正文

哈囉！歡迎來到 Rust 教學系列！

今天是第一集，我們什麼程式都還不寫，先把工具裝好就好。就像你要煮菜，總得先有鍋子對吧？

### 安裝 rustup

Rust 有一個官方的安裝工具叫 **rustup**，它會幫你把所有需要的東西一次裝好。

打開你的瀏覽器，去這個網址：

```ignore
https://rustup.rs
```

- **Windows 使用者**：下載 `rustup-init.exe`，雙擊執行，然後一路按 Enter 選預設就好
- **Mac / Linux 使用者**：打開終端機（Terminal），貼上這行指令：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

它會問你要不要用預設設定，直接按 Enter 就好。

### 確認安裝成功

裝完之後，**重新打開**一個終端機（這很重要，舊的終端機可能還抓不到），然後輸入：

```bash
rustc --version
```

如果你看到類似這樣的東西：

```ignore
rustc 1.XX.X (xxxxxxx 20XX-XX-XX)
```

恭喜你！Rust 已經裝好了！

`rustc` 就是 Rust 的編譯器，它負責把你寫的程式碼變成電腦能執行的東西。至於什麼是編譯器，之後我們慢慢聊，現在你只要知道「裝好了、能用了」就夠了。

## 重點整理
- 用 **rustup** 安裝 Rust，它會幫你把所有需要的工具一次裝好
- 安裝完要重新開終端機，再用 `rustc --version` 確認安裝成功
- `rustc` 是 Rust 的編譯器，負責把程式碼轉成電腦能執行的東西
