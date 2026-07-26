---
title: "Galois Theory as Permitted \"Permutations\" and \"Rotation Division\""
emoji: "📘"
type: "idea"
topics: ["Mathematics", "GaloisTheory", "Algebra", "Beginner"]
published: true
---

[🇯🇵 日本語](https://zenn.dev/5garashi_com/articles/galois-theory-roots-permutation) | 🇺🇸 English

Galois theory tends to be intimidating right at the entrance, with terms like fields, groups, automorphisms, and normal subgroups appearing one after another.

So, for beginners, I wrote a PDF resource that explains the theory along the following line of thought:

- View the Galois group as the "permitted permutations" that preserve the relations among values of rational expressions formed from the roots
- See that as the field extends, the permitted permutations decrease. In other words, the group shrinks
- View the degree n of the radical adjoined at each step of the field extension as the number of its conjugates (n). The conjugates sit at positions dividing 360° into n equal parts
- View the condition for the equation to be solvable by radicals as a descending chain of groups that reaches {e}
- See that for the general quintic equation, A₅ becomes the obstruction

## What this material aims to convey

This material is not meant as a rigorous, proof-oriented textbook, but as an introductory resource for grasping the overall picture of Galois theory intuitively.

Viewing the Galois group as "permitted permutations," and field extension as "equal division of the rotation," is what reveals the real point: not that "the quintic equation has no solution," but that **"there is no single formula, using only the four arithmetic operations and radicals, that solves the general quintic equation"** (individual quintic equations can still be solvable by radicals).

## Intended audience

This is written for readers who know the quadratic formula (high-school level) but have little to no background in abstract algebra (university level).

## Where this is published

The PDF, the PowerPoint source, the changelog, and an issue tracker for error reports are all published on GitHub.

- PDF (Japanese, opens in browser): https://5garashi.github.io/galois-theory-introduction/pdf/galois_theory_intro_ja_v1_12.pdf
- PDF (English, opens in browser): https://5garashi.github.io/galois-theory-introduction/pdf/galois_theory_intro_en_v1_12.pdf
- Repository: https://github.com/5garashi/galois-theory-introduction

If you notice any mathematical errors, unclear explanations, or ideas for a better presentation, please let us know via GitHub Issues.
