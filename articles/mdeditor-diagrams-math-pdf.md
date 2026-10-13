---
title: "Markdownを読むためにVS Codeを開くのが面倒で、Windowsアプリを作った"
emoji: ""
type: "tech"
topics: ["markdown", "windows", "mermaid", "katex", "pdf"]
published: false
---

<!--
ファイル名 / File: articles/mdeditor-diagrams-math-pdf.md
概要 / Description: mdEditor用途記事 / mdEditor use-case article
作成者 / Author: 5garashi.com設計事務所 / 5garashi.com Design Office
作成日 / Created: 2026-10-13
版 / Version: 1.2.0
ライセンス / License: MIT
SPDX-License-Identifier: MIT
-->

Markdownファイルの中身をちょっと読みたい。必要なら数行だけ直したい。そのためにVS Codeを開き、図や数式を見るための拡張機能を用意するのが、私には少し面倒でした。

そこで、Markdownを開いて読む、編集する、PDFで共有するためのWindowsアプリ「mdEditor」を作りました。5garashi.com設計事務所の開発作品として、Microsoft Storeで無料で公開しています。

この記事では、実画面と短い技術メモを使って、図・数式の表示、別ウィンドウのプレビュー、PDF保存を紹介します。VS Codeとの速度やメモリ使用量の比較はしていません。ここで書くのは、私が普段のMarkdown閲覧で欲しかった使い方です。

## まずはMarkdownを開いて読む

![mdEditorで編集欄とプレビューを並べた実画面。数式・フローチャート・表が表示されている。](https://5garashi.github.io/mdEditor/assets/app-ja.png)

左にMarkdown、右に表示結果を並べて使います。見出しや表に加え、Mermaidの図、KaTeXの数式もプレビューできます。読んでいて気づいた箇所は、左側の文章を直して確認します。

[Microsoft Storeから無料で入手](https://apps.microsoft.com/detail/9nww2qrclmhc?hl=ja-JP&gl=JP)できます。[使い方と40秒の操作実演](https://5garashi.github.io/mdEditor/)も用意しました。この記事の画面と手順はソース版1.0.5で確認しています。

## 図と数式を含む小さなメモで試す

Markdownはテキストファイルなので、見出しや表を文章と一緒に編集できます。Mermaidの図もテキストで記述でき、KaTeXで表示する数式はTeX記法で記述します。

- 編集用: `.md`。計算条件や作業手順を後から直す。
- 配布用: `.pdf`。読み手がMarkdownを表示する環境を用意しなくても読める形で渡す。

PDFは共有する時点の記録です。元のMarkdownを変更しても、以前に保存したPDFは自動更新されません。修正後はPDFも保存し直します。

[Microsoft Store](https://apps.microsoft.com/detail/9nww2qrclmhc?hl=ja-JP&gl=JP)からmdEditorを導入し、「開く」で手元のmdファイルを選びます。新しく試す場合は、[図と数式のサンプル](https://5garashi.github.io/mdEditor/samples/quickstart-engineering-note.md)のコピーを使ってください。

以下は、抵抗の消費電力を記録する例です。`$...$` が文章中の数式、`$$...$$` が独立した数式です。Mermaidのコードブロックは図としてプレビューされます。

````markdown
# 抵抗の消費電力

条件は $R=100\,\Omega$、$V=10\,\mathrm{V}$ とする。

$$P=\frac{V^2}{R}=\frac{10^2}{100}=1\,\mathrm{W}$$

```mermaid
flowchart LR
 A[条件を整理] --> B[計算] --> C[仕様を確認]
 classDef default fill:#FFFDF2,stroke:#385723,color:#385723
 linkStyle default stroke:#385723
```

| 電圧 | 抵抗 | 消費電力 |
| --- | --- | --- |
| 5 V | 100 Ω | 0.25 W |
| 10 V | 100 Ω | 1.00 W |
````

数式と表は自分で計算した結果の記載です。mdEditorは数値を自動計算しません。電圧を変える場合、文章・式・表の結果を自分で再計算して書き換えてください。この例だけで実際の部品選定を決めるものではありません。

### 文章と図を編集する

最初の見出しを「抵抗の消費電力の記録」に変え、右側のプレビューにも反映されることを確認します。次に図の「仕様を確認」を「測定で検証」に変えてみます。

図の見た目を直接操作するのではなく、元になる文字を修正する操作です。文章と図の変更履歴を同じmdファイルで残せることが、この形式の扱いやすさです。

## 読む画面を別ウィンドウに出す

プレビュー側の「別ウィンドウで表示」を選ぶと、読む画面を本体から分けられます。ほかの作業と並べたり、別のディスプレイに置いたりして使います。単に読みたいときは、プレビューをウィンドウ全体に広げる操作もあります。

以下は、本体と別プレビューの実画面です。ソース版1.0.5で取得しました。Storeの提供版にこのボタンがない場合は、その版の機能・更新状況を確認してください。別ウィンドウ表示と、ウィンドウ全体のプレビュー表示はそれぞれ異なる操作です。

![本体の編集ウィンドウの実画面。Markdownだけを広く表示している。](https://5garashi.github.io/mdEditor/multichannel/illustrations/window-editor-ja.png)

![別ウィンドウのプレビューの実画面。図・数式・表が表示されている。](https://5garashi.github.io/mdEditor/multichannel/illustrations/window-preview-ja.png)

## PDFにして渡す

1. 「保存」で編集したMarkdownを保存する。
2. 「PDFに保存」を選び、PDFの保存先を指定する。
3. 保存したPDFを開く。
4. 見出し・図・数式・表が含まれること、文章の切れや不要なページがないかを確認する。

検証したソース版では、短い技術メモのPDFに末尾空白ページが付く場合がありました。本文・図・数式・表は出力されていますが、配布前にページ数を確認してください。PDFの自動更新や、数値の自動計算は行われません。

文書内に外部画像を置くと、その画像サーバーへの通信が発生します。本稿のサンプルには外部画像がなく、図・数式はアプリに同梱された部品で描画します。[アプリのプライバシーポリシー](https://github.com/5garashi/mdEditor/blob/main/PRIVACY.md)も参照してください。

## 参考資料と作成者

- [Mermaid公式資料](https://mermaid.js.org/): テキストから図を描く記法。
- [KaTeX公式資料](https://katex.org/docs/supported.html): 表示できる数式の記法。
- [mdEditorのソースと使い方](https://github.com/5garashi/mdEditor)。

本稿の手順と画像は、変更していないソース版1.0.5で確認しています。Storeの提供版番号・認定状況は未確認です。価格は所有者の確認と掲載情報に基づき無料と記載しています。

mdEditorは[5garashi.com設計事務所](https://www.5garashi.com/)の開発作品です。Markdownを普段どのように読んだり、共有したりしているか、使ってみた感想をお寄せいただけると助かります。不具合や改善案は[GitHub Issues](https://github.com/5garashi/mdEditor/issues)へお願いします。

デザイン基準出典: [Design Office Identity v4.12.0](https://5garashi.github.io/5garashi-identity/)、5garashi.com設計事務所 / 5garashi.com Design Office。公式ロゴはCC BY-ND 4.0、本文と記法例はMIT。

---

**作成者 / Author**: 5garashi.com設計事務所 / 5garashi.com Design Office
**最終更新 / Last updated**: 2026-10-13 JST
