---
# ファイル名 / File: articles/mdeditor-diagrams-math-pdf.md
# 概要 / Description: mdEditor用途記事 / mdEditor use-case article
# 作成者 / Author: 5garashi.com設計事務所 / 5garashi.com Design Office
# 作成日 / Created: 2026-10-13
# 版 / Version: 1.9.0
# ライセンス / License: MIT
# SPDX-License-Identifier: MIT
title: "Markdownを読むためにVS Codeを開くのが面倒で、Windowsアプリを作った"
emoji: ""
type: "tech"
topics: ["markdown", "windows", "mermaid", "katex", "pdf"]
published: true
---

@[youtube](AhCp_Erzfow)

Markdownファイルの中身をちょっと読みたい。必要なら数行だけ直したい。そのためにVS Codeを開き、図や数式を見るための拡張機能を用意するのが、私には少し面倒でした。

そこで、Markdownを開いて読む、編集する、PDFで共有するためのWindowsアプリ「mdEditor」を作りました。5garashi.com設計事務所の開発作品として、Microsoft Storeで無料で公開しています。

この記事では、実画面と短い技術メモを使って、図・数式の表示、別ウィンドウのプレビュー、PDF保存を紹介します。VS Codeとの速度やメモリ使用量の比較はしていません。ここで書くのは、私が普段のMarkdown閲覧で欲しかった使い方です。

## 2026-11-01更新：PDFもAIチャットの回答も、Markdownで

[English demo](https://www.youtube.com/watch?v=AkYYP5qnGDU) · [简体中文演示](https://www.youtube.com/watch?v=V60PrM1Y6pA)

PDFとWordをMarkdownとして開けます。AIチャットの回答も、書き方の癖を直して表示。プレビューどおりのPDFに、ワンクリックで保存できます。

書きながら横で仕上がりを確認。Mermaid・Graphviz・数式・3Dモデル・地図をオフラインで表示。書き間違いには波線、表は Ctrl+Shift+W で整えます。

回転する3Dモデルから始まり、AIチャットの回答の修正、PDFの取り込みと書き出し、書き方の確認を実演。そのあと、主な機能と図のサンプルを上から下へ紹介します。

Windows用・無料。PDFの取り込みはできる範囲での変換で、段組みやスキャンしたPDFは元に戻りません。AIチャットの回答は、できる範囲で再現します。収録はソースビルド1.0.20です。

開発と動画の制作に、AI（Claude・Codex）の支援を受けています。BGMはCodexで作曲・音源生成したものです。

図・数式・地図・動画を一つの文書で確認し、そのまま編集・共有できます。5garashi.com設計事務所が開発する無料のWindowsアプリmdEditorの使い方を紹介します。

[ソース1.0.20の実演を見る](https://5garashi.github.io/mdEditor/#demo) · [YouTubeの入口](https://5garashi.github.io/mdEditor/youtube.html)

![mdEditorの実画面。プレビューに、赤い台の上の緑の星形の3Dモデル。](https://5garashi.github.io/mdEditor/assets/hero-3d-1.0.20-ja.png)

## 動画と同じサンプルを試す

[diagram-test.md](https://5garashi.github.io/mdEditor/samples/diagram-test.md)を保存し、mdEditorの「開く」で選びます。上から下へスクロールし、STLの画面をドラッグすると回転、ホイールで拡大・縮小できます。ネット上の画像・動画・OpenStreetMapの詳細地図は、許可したときだけ読み込みます。許可した取得先にはIPアドレスなどが伝わります。構文エラーの表示を試すための例も意図的に含まれています。

このサンプルはmdEditor向けです。GitHubもSTL・GeoJSONを描画できますが、DOTにはmdEditorなどの対応環境が必要です。表示や操作が同じとは限りません。共通のMarkdown文書には、GitHubとmdEditorの両方で描けるMermaidを使います。

## 書きながら、横で仕上がりを確認する

見出しを直してプレビューへの反映を確認します。スクロールを連動でき、プレビューを別ウィンドウへ分けたり、ウィンドウ全体へ広げて読んだりできます。今回の録画で実際の2台目ディスプレイへの移動は試験していません。

## 画像をドロップし、サイズと中央揃えを調整する

画像を編集欄へドロップし、画像の調整で幅50％・中央揃えを選びます。文書と使用した画像は、配布用ZIPでまとめて渡せます。

![画像の調整で幅50％・中央揃えにした実画面。](https://5garashi.github.io/mdEditor/assets/image-adjust-1.0.15-ja.png)

## 必要な形式で共有する

「保存」でMarkdownを残し、「名前を付けて保存」の形式からPDF・Word・HTML・PNGなどを選びます。1.0.20はワンクリックのPDF保存（ページ番号と画面読み上げ用のタグ付き）に対応し、PDFやWordをMarkdownとして開くこともできます（できる範囲での変換）。配布前に、出力した文書を開いて図・文字・改ページを確認してください。Wordの色や配置、Notebookの実行結果は再現しません。数式や表の値を自動計算する機能はありません。

## 主な機能

- PDF や Word を Markdown として開ける。PC の中だけで変換
- PDF から見出し・箇条書き・表・コード・画像を取り出す
- ワンクリックで PDF に保存。プレビューと同じ見た目のまま
- Word・HTML・PNG・CSV・JSON・テキスト・ZIP にも保存
- 書きながら横で仕上がりを確認。スクロールも連動
- AI のチャットの Markdown も、できる範囲で再現
- プレビューを 2 台目のディスプレイに。編集中の行を表示
- 書くそばから色分けし、書き間違いに波線を引く
- 太字・斜体・リスト・表・見出しの番号をキー 1 つで
- Mermaid・Graphviz の図と数式をオフラインで表示
- 3D モデル（STL）と地図（GeoJSON）をオフラインで表示
- 約 40 の言語のコードを色分け。見出しから目次も作る
- GitHub と同じ注意書き・フロントマター・折りたたみ
- HTML・メール・CSV・JSON・Jupyter Notebook・画像も開ける
- 画像はドロップや貼り付けで、そのまま文書に
- コピーしてキーを押すと、新しい文書として開く
- 安全な保存と、異常終了からの自動復元
- Shift_JIS・EUC-JP・UTF-8 のファイルを正しく開ける
- 広告なし、計測なし、アカウント不要。ネット上の内容は許可したときだけ
- キーボード操作・画面読み上げ・文書の読み上げ・ダークモード

## 確認範囲と出典

新動画はソース版1.0.20を収録し、字幕とBGM「Light Steps」を付けています。AIチャットの回答の修正、PDFの取り込みと書き出し、書き方の確認、表の整形、図・数式・3D・地図・動画の表示を、録画時に確認しました。全キー操作、異常終了からの復元、全形式の書き出し、読み上げ環境を網羅的に再試験したものではありません。背景を覆って収録し、OSのファイル選択ダイアログは編集で除いています。

BGM：「Light Steps」5garashi.com設計事務所（作曲・音源生成：Codex）、CC BY 4.0。抜粋してくり返し、最後をフェードアウト。  
https://5garashi.github.io/5garashi-identity/ / https://creativecommons.org/licenses/by/4.0/  
サンプルの映画：「Big Buck Bunny」© 2008 Blender Foundation、CC BY 3.0。サンプル文書の中で再生（編集なし）。  
https://peach.blender.org/ / https://creativecommons.org/licenses/by/3.0/  
地図データ：© OpenStreetMap contributors（ODbL）https://www.openstreetmap.org/copyright

[PDF・画像・サンプル](https://5garashi.github.io/mdEditor/resources.html) · [アプリのプライバシー](https://github.com/5garashi/mdEditor/blob/main/PRIVACY.md)

Design reference: [Design Office Identity 4.20.0](https://5garashi.github.io/5garashi-identity/). App, article and notation examples: MIT. Official logos: CC BY-ND 4.0.

---

**作成者 / Author**: 5garashi.com設計事務所 / 5garashi.com Design Office
**最終更新 / Last updated**: 2026-11-01 JST
