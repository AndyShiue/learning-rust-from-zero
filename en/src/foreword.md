# Learning Rust from Zero

Hello! The main goal of this tutorial is to help complete beginners — people who have never written a program before — understand the many concepts in the Rust programming language. There are already plenty of Rust tutorials out there, but they all seem to be written for learners who already know at least one other programming language, so I hope this tutorial can fill that gap. Rust is a language with a very distinctive character: it is powerful, programs written in Rust run fast, and when you use Rust, it's easier to catch mistakes early on, while you're still writing the code. C++, which everyone has heard of, is likewise powerful and fast, but it sacrifices quite a lot when it comes to safety. Because of these characteristics, Rust also plays a pivotal role in this era of AI-assisted programming.

The approach of this tutorial is therefore aligned with how development works in the current AI era: it doesn't assign "homework" on the assumption that you must be able to write algorithms to a particular specification. Instead, this tutorial aims to get you to the point where you can read Rust code and understand roughly what it's doing, and hopefully also understand how the architecture of a real piece of software gets designed. I'd even say that if you can't be bothered to use a computer, simply reading this tutorial without actually writing any code is a viable way to learn Rust too.

That said, I still recommend reading this tutorial chapter by chapter. If you have some background in a statically typed language, you can probably skip Chapter 1, but what I'd recommend even more is spending just a few minutes skimming Chapter 1 before moving on. If you're a complete beginner, that goes without saying. Of course, if you're not worried about missing anything, you can also jump straight to whatever interests you, or use the search feature to read ahead to explanations that only come later in the tutorial — these are all perfectly workable approaches. Oh, and one more thing: there's a chapter called "Appendix I" — despite the name, I recommend reading all of it as well.

If, while reading, you run into a passage you don't understand, want practice problems, or your program won't run, and you'd like to ask an AI for help, I've prepared a zip archive for AIs to read, so that the AI can respond to your needs more precisely. To use it, just upload the entire archive to the AI, tell it "Please read the `GUIDE.md` inside the archive before answering me," let the AI know which chapter and episode you're currently on, and then state your request. The download link for the archive is below:

> `rust-book-src.zip`: [https://andyshiue.github.io/learning-rust-from-zero/en/rust-book-src.zip](https://andyshiue.github.io/learning-rust-from-zero/en/rust-book-src.zip)

I strongly recommend using a good AI model to read the archive! A free AI might not even bother to read what's inside.

A little slow on the uptake, I only realized later that many readers might hand the entire tutorial to an AI instead of reading it themselves. If you've diligently made it this far into the foreword — or if your AI has reached this part — here are my thoughts for readers who choose that approach:

1. I had considered that some people might use the tutorial this way, but I didn't expect so many to do so. It is, of course, a perfectly valid approach.
2. Even so, the tutorial itself exists for a reason; otherwise, I wouldn't have written it. Asking an AI only when you encounter code you don't understand may leave you able to read programs but unable to write them, though I admit that readers in exactly that position were part of my intended audience from the beginning.
3. The value of the tutorial itself is that it lets you gradually build a comprehensive understanding of Rust's features.
4. Even if you use AI to help you read, that doesn't mean you can't come back to the tutorial itself whenever you need it.
5. You don't actually need to go to GitHub and `git clone` my project; the `.zip` file above already contains the entire tutorial (you can extract it yourself and take a look). I recommend giving the archive to an AI instead of having it read the website directly because the archive contains plain text, which is easier for an AI to process.
6. I only realized later that there may not be all that many true "complete beginners" these days, so some readers may want to skip Chapter 1. As noted above, that may be workable, but if you find that you don't quite grasp the most basic concepts, the episodes in Chapter 1 are all very short. Reading them really won't take much time.
7. Pay special attention to the first half of the chapter on asynchronous programming. Its essence lies in practicing how to read and understand code, and that remains true even if you use AI to read it. I especially recommend the book [*Asynchronous Programming in Rust*](https://www.packtpub.com/en-us/product/asynchronous-programming-in-rust-9781805126621). I wrote this tutorial's chapter on asynchronous programming in my own way, using that book as a reference.

This tutorial also has a PDF version available for download:

> PDF version: [https://andyshiue.github.io/learning-rust-from-zero/en/book.pdf](https://andyshiue.github.io/learning-rust-from-zero/en/book.pdf)

However, I may not maintain the PDF version in the long run, so I recommend reading the interactive web version instead. If you happen to be reading the PDF version right now, here's the URL of the web version:

> Web version: [https://andyshiue.github.io/learning-rust-from-zero/en/](https://andyshiue.github.io/learning-rust-from-zero/en/)

Finally, let me mention the interactive features I referred to above, since otherwise I'm afraid nobody would notice them: you can run the code directly inside the web version of this tutorial. There are a few buttons at the top-right corner of each code snippet in the text — press them and you'll see what happens. That's about it for now......

Apart from the outline, the first draft of this tutorial was written by AI and revised by humans:

- Models: Claude 4.5 ~ 5 / GPT-5.5 ~ 5.6
- Harnesses: OpenClaw / Claude Code / ChatGPT (Codex)
