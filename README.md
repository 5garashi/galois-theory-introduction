# ガロア理論入門

このリポジトリは、ガロア理論の初心者向け資料
「なぜ一般の5次方程式にはべき根による解の公式がないのか」
を公開・更新するためのものです。

## 資料の目的

本資料は、厳密な証明を目的とした専門書ではなく、
ガロア理論の入口を直観的に理解するための入門資料です。

主なテーマは次の通りです。

- ガロア群を「根の入れ替え」として見る
- 体が拡大すると、許される入れ替えが減ることを見る
- 方程式がべき根で解ける条件を、群の縮小鎖として見る
- 一般の5次方程式で何が壁になるのかを見る

## 構成

```
pdf/     PDF本体(日本語版・英語版)
source/  元データ(PowerPoint)
tools/   ガロア理論に基づく代数方程式ソルバー(Python)
docs/    初心者向け解説・手法まとめ
```

## PDF

- 日本語版: `pdf/galois_theory_intro_ja_v1_11.pdf`
- English: `pdf/galois_theory_intro_en_v1_11.pdf`

## ソルバー

`tools/galois_solver.py` は、PDF「可解な代数方程式のガロア理論に基づいた解法」に
掲載されたMathematicaプログラムをPython/sympyで実装したものです。
詳細は `tools/galois_solver_README.md` を参照してください。

## 解説文書

- `docs/galois_theory_beginner.md` : 初心者向け解説
- `docs/galois_pdf_method_chat_summary.md` / `.pdf` : 手法まとめ

## 誤り報告・改善提案

数学的な誤り、説明の分かりにくい箇所、表記の改善案は、
GitHub Issues からご連絡ください。

## ライセンス

本リポジトリの内容(PDF・スライド・解説文書・コードを含む)は
`LICENSE` ファイルに記載の条件に従います。

Copyright 2026 5garashi.com設計事務所

---

**作成者**: 5garashi.com設計事務所
**最終更新**: 2026-07-25 JST
