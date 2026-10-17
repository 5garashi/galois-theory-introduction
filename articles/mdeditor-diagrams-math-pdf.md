---
# ファイル名 / File: articles/mdeditor-diagrams-math-pdf.md
# 概要 / Description: mdEditor用途記事 / mdEditor use-case article
# 作成者 / Author: 5garashi.com設計事務所 / 5garashi.com Design Office
# 作成日 / Created: 2026-10-13
# 版 / Version: 1.5.0
# ライセンス / License: MIT
# SPDX-License-Identifier: MIT
title: "Markdownを読むためにVS Codeを開くのが面倒で、Windowsアプリを作った"
emoji: ""
type: "tech"
topics: ["markdown", "windows", "mermaid", "katex", "pdf"]
published: true
---

Markdownファイルの中身をちょっと読みたい。必要なら数行だけ直したい。そのためにVS Codeを開き、図や数式を見るための拡張機能を用意するのが、私には少し面倒でした。

そこで、Markdownを開いて読む、編集する、PDFで共有するためのWindowsアプリ「mdEditor」を作りました。5garashi.com設計事務所の開発作品として、Microsoft Storeで無料で公開しています。

この記事では、実画面と短い技術メモを使って、図・数式の表示、別ウィンドウのプレビュー、PDF保存を紹介します。VS Codeとの速度やメモリ使用量の比較はしていません。ここで書くのは、私が普段のMarkdown閲覧で欲しかった使い方です。

## 2026-10-18更新：図も、3Dも、動画も

@[youtube](CAi5q1c0cuo)

[English demo](https://www.youtube.com/watch?v=valiuj76iG4)

まず、文書内のSTL立方体を回転・拡大。そのあと図・数式・地図・動画を一つの文書で確認し、編集と共有へ進みます。5garashi.com設計事務所が開発する無料のWindowsアプリmdEditorの使い方を紹介します。

[ソース1.0.12の実演を見る](https://5garashi.github.io/mdEditor/#demo) · [YouTubeの入口](https://5garashi.github.io/mdEditor/youtube.html)

![mdEditorの実画面。左にSTLソース、右に赤い5が付いたクリーム色の3D立方体。](https://5garashi.github.io/mdEditor/assets/hero-3d-1.0.12-ja.png)

## 動画と同じサンプルを試す

[diagram-test.md](https://5garashi.github.io/mdEditor/samples/diagram-test.md)を保存し、mdEditorの「開く」で選びます。上から下へスクロールし、STLの画面をドラッグすると回転、ホイールで拡大・縮小できます。ネット上の画像・動画・OpenStreetMapの詳細地図は、許可したときだけ読み込みます。許可した取得先にはIPアドレスなどが伝わります。構文エラーの表示を試すための例も意図的に含まれています。

このサンプルはmdEditor向けで、STL・DOT・GeoJSONを含みます。GitHubですべて同じように直接描画されるものではありません。共通のMarkdown文書には、GitHubとmdEditorの両方で描けるMermaidを使います。

## 書きながら、横で仕上がりを確認する

見出しを直してプレビューへの反映を確認します。スクロールを連動でき、プレビューを別ウィンドウへ分けたり、ウィンドウ全体へ広げて読んだりできます。今回の録画で実際の2台目ディスプレイへの移動は試験していません。

## 必要な形式で共有する

「保存」でMarkdownを残し、「名前を付けて保存」の形式からPDF・Word・HTML・PNGなどを選びます。現行ソース1.0.12はワンクリックのPDF保存にも対応しています。配布前に、出力した文書を開いて図・文字・改ページを確認してください。Wordの色や配置、Notebookの実行結果は再現しません。数式や表の値を自動計算する機能はありません。

## 主な機能

- 書きながら横で仕上がりを確認。スクロールも連動
- プレビューを 2 台目のディスプレイに。編集中の行を表示
- ビューアーとしても。プレビューをウィンドウいっぱいに
- Mermaid・Graphviz の図と数式をオフラインで表示
- 3D モデル（STL）をマウスで回して確認
- 地図（GeoJSON）。許可すると OpenStreetMap の地図も
- 約 40 の言語のコードを色分け。PDF・Word にも色が残る
- 見出しから目次を作り、ボタン 1 つで新しくする
- GitHub と同じ注意書き・フロントマター・折りたたみ
- 文書の中の動画をプレビューで再生
- プレビューと同じ見た目の PDF をワンクリックで
- Word・HTML・メール・CSV・JSON・Jupyter Notebook・画像を開ける
- HTML・PNG・Word・CSV・JSON・Jupyter Notebook・テキストに保存
- 画像はドロップや貼り付けで、そのまま文書に
- 安全な保存と、異常終了からの自動復元
- Shift_JIS・EUC-JP・UTF-8 のファイルを正しく開ける
- ネット上の画像・動画・地図は、許可したときだけ読み込む
- 広告なし、計測なし、アカウント不要
- キーボードで全操作。ショートカットも変更できる
- 画面読み上げ・文書の読み上げ・ダークモードに対応

## 確認範囲と出典

新動画はソース版1.0.12（8ab7cef）を収録し、字幕とBGM「Light Steps」を付けています。Store配信版番号は未確認です。7形式の取り込み、PDF保存、図・数式、地図・動画、3Dの回転を録画時に確認しました。全キー操作、異常終了からの復元、全形式の書き出し、読み上げ環境を網羅的に再試験したものではありません。別窓紹介は背景を映さないため、安定した実録画1秒をアプリのウィンドウだけに切り出して繰り返しています。

[PDF・画像・サンプル](https://5garashi.github.io/mdEditor/resources.html) · [アプリのプライバシー](https://github.com/5garashi/mdEditor/blob/main/PRIVACY.md)

Design reference: [Design Office Identity 4.20.0](https://5garashi.github.io/5garashi-identity/). App, article and notation examples: MIT. Official logos: CC BY-ND 4.0.

---

**作成者 / Author**: 5garashi.com設計事務所 / 5garashi.com Design Office
**最終更新 / Last updated**: 2026-10-18 JST
