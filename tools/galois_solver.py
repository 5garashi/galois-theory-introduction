#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
# Windows コンソールで UTF-8 出力を強制
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
galois_solver.py
ガロア理論に基づいた代数方程式の解法

PDF「可解な代数方程式のガロア理論に基づいた解法」の
MathematicaプログラムをPythonで忠実に実装。

[第1部] ガロア群の計算
  § 1  根と係数の関係
  § 2  多項式の次数低減
  § 3  n!個の置換
  § 4  原始要素 v と最小多項式 g(x)
  § 5  分解体の基底
  § 6  X[i] の v による多項式表現 (LU分解)
  § 7  ガロア群 G
  § 8  G の乗積表と逆元
  § 9  G の組成列

[第2部] 可解な代数方程式の解法
  §11  分解体の元の積・商の計算
  §12  体の拡大と g(x) の次数低減
  §13  根の計算

使い方:
    python galois_solver.py
"""

from sympy import (
    Symbol, symbols, Poly, factor_list, expand, simplify, cancel,
    Add, Mul, Rational, Integer, gcd, div, rem, diff, degree,
    isprime, Matrix, eye, solve, together, fraction, sympify,
    root, sqrt, cbrt, Abs
)
from itertools import permutations as _iter_perms
from math import factorial
import sys
import time as _time
import datetime as _datetime
import json as _json
import os as _os

# ============================================================
#  グローバル状態
# ============================================================
_x = Symbol('x')   # 多項式の変数（方程式の変数）
_v = Symbol('v')   # 原始元

n   = 0      # 方程式の次数
nn  = 0      # n! (置換の総数 → ガロア群計算後は |G|)
fx  = None   # 対象多項式（sympy式、最高次係数=1）

X   = {}     # 根の記号変数 X[1]..X[n]
r   = {}     # 根と係数の関係 r[1]..r[n]
sigma = []   # n! 個の置換（1-indexed タプルのリスト、ソート済み）
m   = {}     # 原始要素の係数 m[1]..m[n]
V   = {}     # V[1]..V[nn] (各種の v の候補)
gx  = None   # 原始元 v の最小多項式
w   = []     # 分解体の基底（各要素: 長さnの整数リスト [j1,j2,...,jn]）
G   = []     # ガロア群（1-indexed の置換タプルのリスト）
Gs  = []     # 組成列 （各要素: 1-indexed インデックスのリスト）
pro = []     # 乗積表 pro[i][j] = G[i]°G[j] の1-indexedインデックス
inv_G = []   # 逆元 inv_G[i] = G[i]^{-1} の1-indexedインデックス

# Part 2 用
list_of_alpha = []  # [(symbol, 条件式), ...] 例: (alpha1, alpha1^p - A1)


# ============================================================
#  ユーティリティ
# ============================================================
def _poly_rem(f_expr, g_expr, var):
    """f mod g (var の一変数多項式として剰余を求める)"""
    f_exp = expand(f_expr)
    g_exp = expand(g_expr)
    if g_exp == 0:
        return f_exp
    fp = Poly(f_exp, var, domain='EX')
    gp = Poly(g_exp, var, domain='EX')
    _, rp = div(fp, gp, var, domain='EX')
    return expand(rp.as_expr())


def _poly_nth(f_expr, var, k):
    """f の var^k の係数を返す"""
    return Poly(expand(f_expr), var, domain='EX').nth(k)


def _poly_deg(f_expr, var):
    """var についての次数 (f=0 なら -1 を返す)"""
    try:
        d = degree(expand(f_expr), var)
        if d == float('-inf') or str(d) == '-oo':
            return -1
        return int(d)
    except Exception:
        return -1


# ============================================================
#  高速多項式演算: v 次数を乗算中に逐次縮減するヘルパー
# ============================================================
def _reduce_xpoly_v_coeffs(expr, gkm1_v_poly):
    """x の多項式 expr の各 v-係数を gkm1_v_poly で縮減する。"""
    gkm1_deg = int(gkm1_v_poly.degree())
    try:
        p_x = Poly(expand(expr), _x, domain='EX')
        deg_x = int(p_x.degree())
        terms = []
        for k in range(deg_x + 1):
            ck = p_x.nth(k)
            if _poly_deg(ck, _v) >= gkm1_deg:
                ck = expand(Poly(ck, _v, domain='EX').rem(gkm1_v_poly).as_expr())
            if ck != 0:
                terms.append(expand(ck) * _x ** k)
        return Add(*terms) if terms else Integer(0)
    except Exception:
        return expand(expr)


def _poly_mul_reduce_v(p1_expr, p2_expr, gkm1_v_poly):
    """
    x の多項式 p1, p2 を掛け合わせ、各 v-係数を gkm1_v_poly で逐次縮減する。
    expand() より前に縮減するため、n≥4 の大規模多項式で大幅に高速。
    """
    gkm1_deg = int(gkm1_v_poly.degree())
    try:
        p1 = Poly(expand(p1_expr), _x, domain='EX')
        p2 = Poly(expand(p2_expr), _x, domain='EX')
    except Exception:
        result = expand(expand(p1_expr) * expand(p2_expr))
        return _reduce_xpoly_v_coeffs(result, gkm1_v_poly)
    d1 = int(p1.degree())
    d2 = int(p2.degree())
    result = [Integer(0)] * (d1 + d2 + 1)
    for i in range(d1 + 1):
        ci = p1.nth(i)
        if ci == 0:
            continue
        for j in range(d2 + 1):
            cj = p2.nth(j)
            if cj == 0:
                continue
            prod = expand(ci * cj)
            if _poly_deg(prod, _v) >= gkm1_deg:
                try:
                    prod = expand(
                        Poly(prod, _v, domain='EX').rem(gkm1_v_poly).as_expr()
                    )
                except Exception:
                    pass
            result[i + j] = expand(result[i + j] + prod)
    terms = [result[k] * _x ** k for k in range(len(result)) if result[k] != 0]
    return Add(*terms) if terms else Integer(0)


def _poly_pow_reduce_v(expr, exp, gkm1_v_poly):
    """expr^exp を x 多項式として計算し、各ステップで v 次数を縮減する。"""
    if exp == 0:
        return Integer(1)
    if exp == 1:
        return _reduce_xpoly_v_coeffs(expand(expr), gkm1_v_poly)
    result = Integer(1)
    for _ in range(exp):
        result = _poly_mul_reduce_v(result, expr, gkm1_v_poly)
    return result


# ============================================================
#  § 1  根と係数の関係  (RootAndCoefficient)
# ============================================================
def root_and_coefficient():
    """
    f(x) - (x-X[1])…(x-X[n]) を展開して x^(n-i) の係数 r[i] を求め、
    r[j]=0 を使って X[n-j+1] を消去する。
    """
    global r
    product_roots = Mul(*[(_x - X[i]) for i in range(1, n + 1)])
    temp = expand(fx - product_roots)
    p_temp = Poly(temp, _x, domain='EX')
    for i in range(1, n + 1):
        r[i] = expand(p_temp.nth(n - i))
    # 次数低減: r[j]=0 を使って X[n-j+1] の次数を下げる
    for i in range(2, n + 1):
        for j in range(1, i):
            r[i] = _poly_rem(r[i], r[j], X[n - j + 1])


# ============================================================
#  § 2  多項式の次数低減  (ReductionOfX)
# ============================================================
def reduction_of_X(f):
    """
    X[1],...,X[n] からなる多項式 f について、r[i]=0 を使って次数を低減する。
    """
    temp = expand(f)
    for i in range(1, n + 1):
        var = X[n - i + 1]
        if _poly_deg(r[i], var) > 0:
            temp = _poly_rem(temp, r[i], var)
        temp = expand(temp)
    return expand(temp)


# ============================================================
#  § 3  置換  (build_sigma)
# ============================================================
def build_sigma():
    """x[1]..x[n] の n! 個の置換をソート済みで生成する（1-indexed タプル）。"""
    global sigma
    sigma = sorted(_iter_perms(range(1, n + 1)))


# ============================================================
#  § 4  原始要素 v と最小多項式 g(x)
# ============================================================
def _update_V():
    """V[i] = Σ m[j] * X[sigma[i-1][j-1]] を更新する。"""
    for i in range(1, nn + 1):
        perm = sigma[i - 1]
        V[i] = Add(*[m[j] * X[perm[j - 1]] for j in range(1, n + 1)])


def _build_gx_from_indices(indices):
    """
    指定されたインデックスリスト indices に対して
    g(x) = Π_{j in indices} (x - reduction_of_X(V[j])) を構築する。
    Mathematica の「gx の逐次更新」と同等。
    """
    curr = Integer(1)
    for j in indices:
        vj = reduction_of_X(V[j])
        # curr = (x - vj) * curr を項別に計算（ReductionOfX のコスト分散）
        deg_curr = _poly_deg(curr, _x)
        new_curr = _x * curr
        for k in range(deg_curr + 1):
            ck = _poly_nth(curr, _x, k)
            if ck != 0:
                term = reduction_of_X(V[j] * ck)
                new_curr = new_curr - term * _x ** k
        curr = expand(new_curr)
    return curr


def primitive_element():
    """
    § 4: m[1],...,m[n] を決めて V[1] が原始要素となるようにする。
    g(x) = Π (x - V[i]) を計算する。
    """
    global gx, m
    # 初期化
    for i in range(1, n + 1):
        m[i] = 0
    m[1] = 1
    _update_V()

    # m[2],...,m[n-1] を順に決める
    for k in range(2, n):
        m[k] = -m[k - 1] if m[k - 1] > 0 else 1 - m[k - 1]
        step = factorial(n - k)
        while True:
            _update_V()
            indices = list(range(1, nn + 1, step))
            curr_gx = _build_gx_from_indices(indices)
            g_diff = diff(curr_gx, _x)
            try:
                pg = Poly(curr_gx, _x, domain='EX')
                pd = Poly(g_diff, _x, domain='EX')
                g_gcd = gcd(pg, pd)
                if int(g_gcd.degree()) <= 0:
                    break
            except Exception:
                break
            m[k] = -m[k] if m[k] > 0 else 1 - m[k]

    m[n] = 0
    _update_V()
    # 全体の g(x) = Π_{i=1}^{nn} (x - V[i])
    gx = _build_gx_from_indices(list(range(1, nn + 1)))


def minimal_polynomial_select():
    """g(x) を因数分解し、ユーザーに因数を選ばせる。"""
    global gx
    try:
        pg = Poly(expand(gx), _x, domain='QQ')
        fl = factor_list(pg)
    except Exception:
        pg = Poly(expand(gx), _x, domain='EX')
        fl = factor_list(pg)

    irred = [(fi.as_expr(), mult) for fi, mult in fl[1] if fi.degree() > 0]

    if len(irred) == 0:
        return
    if len(irred) == 1:
        gx = irred[0][0]
        return

    print("\ng(x) の因数分解:")
    for idx, (fi, _) in enumerate(irred, 1):
        print(f"  ({idx}) {fi}")
    while True:
        try:
            choice = int(input("因数を選んでください (番号): ")) - 1
            if 0 <= choice < len(irred):
                gx = irred[choice][0]
                break
        except (ValueError, EOFError):
            gx = irred[0][0]
            print(f"  (EOF: 自動で (1) を選択)")
            break
        print("  有効な番号を入力してください。")


# ============================================================
#  § 5  分解体の基底  (BasisOfSplittingField)
# ============================================================
def basis_of_splitting_field():
    """
    w[i] = X[1]^j[1] * X[2]^j[2] * ... * X[n]^j[n] の指数リストを生成。
    各 w[i] (0-indexed) は長さ n の整数リスト。
    """
    global w
    w = []
    for i in range(1, nn + 1):
        wi = []
        for j in range(1, n + 1):
            exp = ((i - 1) // factorial(n - j)) % (n - j + 1)
            wi.append(exp)
        w.append(wi)  # 0-indexed: w[i-1]


# ============================================================
#  § 6  X[i] の v による多項式表現  (PowerOfV + XOfV)
# ============================================================
def _extract_basis_coef(poly_expr, basis_idx):
    """
    poly_expr (X[1],...,X[n] の多項式) から
    w[basis_idx] (0-indexed) に対応するモノミアルの係数を抽出する。
    w[basis_idx] = [j1, j2, ..., jn] (jn=0 常)
    """
    exponents = w[basis_idx]  # 長さ n のリスト
    temp = expand(poly_expr)
    # 高次の変数から順に係数を取り出す
    for k in range(n - 1, -1, -1):
        var = X[k + 1]
        pw = exponents[k]
        try:
            temp = Poly(expand(temp), var, domain='EX').nth(pw)
        except Exception:
            temp = Integer(0)
        temp = expand(temp)
    return temp


def power_of_v():
    """
    V[1]^0, V[1]^1, ..., V[1]^(nn-1) を基底 w[1]..w[nn] の線形結合で表す。
    A[i][j] = V[1]^i の w[j+1] 成分 (どちらも 0-indexed)。
    """
    A = []
    curr = Integer(1)
    total = nn
    for i in range(total):
        if i > 0:
            curr = reduction_of_X(V[1] * curr)
        row = []
        for j in range(total):
            coef = _extract_basis_coef(curr, j)
            row.append(coef)
        A.append(row)
        sys.stdout.write(f"\r  [6] V[1]のべき乗: {i+1}/{total}")
        sys.stdout.flush()
    print()
    return A


def x_of_v(A_mat):
    """
    LU 分解法（行列の逆行列）で X[1],...,X[n] を v の多項式として求める。

    §6 より: X[j] = w_{(n-j)!+1} (1-indexed) = A^{-1} の行 (n-j)! を
    [1, v, v^2, ..., v^{nn-1}] と内積をとったもの。
    """
    print("  [6] 行列 A を構築中...")
    M = Matrix([[expand(A_mat[i][j]) for j in range(nn)] for i in range(nn)])

    print("  [6] 行列の逆行列を計算中... (nn={})".format(nn))
    try:
        Minv = M.inv()
    except Exception as e:
        print(f"  逆行列計算エラー: {e}")
        return {}

    gv = expand(gx.subs(_x, _v))
    gv_poly = Poly(gv, _v, domain='EX')

    X_poly = {}
    for j in range(1, n):
        row_idx = factorial(n - j)  # 0-indexed: w_{(n-j)!+1} は行インデックス (n-j)!
        xi = Add(*[Minv[row_idx, k] * _v ** k for k in range(nn)])
        xi = expand(xi)
        # g(v) による次数低減
        xi = expand(Poly(xi, _v, domain='EX').rem(gv_poly).as_expr())
        X_poly[j] = xi

    # X[n] = -a_{n-1} - Σ X[i]  (ビエタの公式)
    an1 = Poly(fx, _x, domain='EX').nth(n - 1)  # x^{n-1} の係数
    xn = expand(-an1 - Add(*[X_poly[i] for i in range(1, n)]))
    xn = expand(Poly(xn, _v, domain='EX').rem(gv_poly).as_expr())
    X_poly[n] = xn

    # V[i] を v の多項式として整理
    for i in range(1, nn + 1):
        perm = sigma[i - 1]
        vi = Add(*[m[j] * X_poly[perm[j - 1]] for j in range(1, n + 1)])
        V[i] = simplify(vi)

    return X_poly


# ============================================================
#  § 7  ガロア群  (GaloisGroup)
# ============================================================
def galois_group(X_poly):
    """
    g(x) の根となる V[i] を選び、それに対応する置換をガロア群 G とする。
    V[i] が g(x) の根 ⟺ g(V[i]) mod g(v) = 0。
    """
    global G, nn, V

    gv = expand(gx.subs(_x, _v))
    gv_poly = Poly(gv, _v, domain='EX')
    deg_gx = _poly_deg(gx, _x)

    if deg_gx == nn:
        # g(x) の次数が n! → G = 対称群全体
        G = list(sigma)
        return

    G_indices = []
    for i in range(1, nn + 1):
        # V[i] は既に v の多項式として計算済み
        vi = V[i]
        # Horner 法で g(V[i]) mod g(v) を計算
        temp = Integer(0)
        for d in range(deg_gx, -1, -1):
            coef_d = _poly_nth(gx, _x, d)
            prod_vd = expand(temp * vi + coef_d)
            temp = expand(Poly(prod_vd, _v, domain='EX').rem(gv_poly).as_expr())

        if expand(temp) == 0:
            G_indices.append(i)

    new_nn = len(G_indices)
    new_V = {}
    new_G = []
    for new_i, old_i in enumerate(G_indices, 1):
        new_V[new_i] = V[old_i]
        new_G.append(sigma[old_i - 1])

    nn = new_nn
    for i in range(1, nn + 1):
        V[i] = new_V[i]
    G = new_G


# ============================================================
#  § 8  G の乗積表と逆元  (ProductOfG)
# ============================================================
def product_of_G():
    """
    ガロア群 G の乗積表 pro と逆元 inv_G を求める。
    pro[i][j] (0-indexed) = G[i] ∘ G[j] の G 内 1-indexed インデックス。
    """
    global pro, inv_G
    pro = []
    for i in range(nn):
        row = []
        for j in range(nn):
            # G[i] ∘ G[j]: k → G[j][k] → G[i][G[j][k]]
            composed = tuple(G[i][G[j][k] - 1] for k in range(n))
            try:
                idx = G.index(composed) + 1  # 1-indexed
            except ValueError:
                idx = -1
            row.append(idx)
        pro.append(row)

    inv_G = []
    for i in range(nn):
        for j in range(nn):
            if pro[i][j] == 1:
                inv_G.append(j + 1)  # 1-indexed
                break


# ============================================================
#  § 9  G の組成列  (CompositionSeries)
# ============================================================
def composition_series():
    """
    ガロア群 G の組成列 Gs を求める。
    Gs[k] は G の部分群（1-indexed インデックスのリスト）。
    """
    global Gs
    Gs = []
    G1 = list(range(1, nn + 1))
    Gs.append(G1[:])

    while True:
        G2 = [1]  # 単位元のみ
        for i in range(len(G1)):
            Hi = [G1[i]]
            L1 = 1
            while True:
                # (1) g^{-1} h g の形を Hi に追加（正規性の確認）
                for j in range(len(Hi)):
                    for k in range(len(G1)):
                        gk = G1[k]
                        gk_inv = inv_G[gk - 1]           # 1-indexed
                        inner = pro[Hi[j] - 1][gk - 1]   # 1-indexed
                        temp = pro[gk_inv - 1][inner - 1] # 1-indexed 結果
                        if temp not in Hi:
                            Hi.append(temp)
                # (2) Hi 内の積を Hi に追加（閉性の確認）
                for j in range(len(Hi)):
                    for k in range(len(Hi)):
                        temp = pro[Hi[j] - 1][Hi[k] - 1]
                        if temp not in Hi:
                            Hi.append(temp)
                L2 = len(Hi)
                if L1 == L2:
                    break
                L1 = L2

            if len(G1) > L2 > len(G2):
                G2 = sorted(Hi)

        Gs.append(G2[:])
        if len(G2) == 1:
            break
        G1 = G2[:]


# ============================================================
#  § 11  体の元の次数低減と分数式の多項式化
# ============================================================
def reduction_of_alpha(f):
    """
    list_of_alpha の条件式を使って alpha[k], z[p] の次数を低減する。
    逆順（最後に付加したものから）処理する。
    変数が分母に現れる場合はそのステップをスキップする。
    """
    temp = expand(f)
    for alp_sym, fa_expr in reversed(list_of_alpha):
        fa = expand(fa_expr)
        if _poly_deg(fa, alp_sym) > 0:
            # 分母に alp_sym が含まれる場合はスキップ
            _, den = fraction(temp)
            if _poly_deg(expand(den), alp_sym) > 0:
                temp = expand(temp)
                continue
            try:
                temp = _poly_rem(temp, fa, alp_sym)
            except Exception:
                pass
        temp = expand(temp)
    return expand(temp)


def frac_to_poly(f):
    """
    分数式 f を list_of_alpha の元の多項式に書き換える。
    Mathematica の FracToPoly に対応。
    逆順に処理: P/Q = c0 + c1*alp + ... として
    Numerator(Together(P/Q - ga)) = 0 の係数から c を決める。
    ループ内では reduction_of_alpha を呼ばない（Mathematica 版と同じ）。
    """
    temp = expand(f)
    for alp_sym, fa_expr in reversed(list_of_alpha):
        fa = expand(fa_expr)
        k_deg = int(_poly_deg(fa, alp_sym))
        if k_deg <= 0:
            continue
        c_syms = [Symbol(f'_fc{d}') for d in range(k_deg)]
        ga = Add(*[c_syms[d] * alp_sym ** d for d in range(k_deg)])
        # Mathematica: PolynomialRemainder[Numerator[Together[temp-ga]], fa, alp]
        combined = together(expand(temp - ga))
        num_expr = fraction(combined)[0]
        try:
            # 重要: 分子を fa で割った余りを使う（Mathematica と同じ）
            num_poly = Poly(expand(num_expr), alp_sym, domain='EX')
            fa_poly  = Poly(fa, alp_sym, domain='EX')
            _, rem_poly = div(num_poly, fa_poly, alp_sym, domain='EX')
            eq_poly = rem_poly  # 余りの次数は < k_deg
        except Exception:
            continue
        eqs = [eq_poly.nth(d) for d in range(k_deg)]
        sol = solve(eqs, c_syms)
        if sol:
            if isinstance(sol, list):
                sol = sol[0]
            temp = ga.subs(sol)
        # ループ内では reduction_of_alpha を呼ばない (Mathematica と同じ)
    return expand(simplify(temp))


# ============================================================
#  § 12  p 乗根の計算  (PthRoot)
# ============================================================
def pth_root(poly_f, p):
    """
    poly_f^(1/p) を x の多項式として求める。
    poly_f = q(x)^p から q(x) を決定する。
    """
    deg_f = int(_poly_deg(poly_f, _x))
    m_deg = deg_f // p
    c_syms = [Symbol(f'_cr{d}') for d in range(m_deg)]
    fi = _x ** m_deg + Add(*[c_syms[d] * _x ** d for d in range(m_deg)])
    temp = expand(poly_f - fi ** p)
    temp_poly = Poly(expand(temp), _x, domain='EX')
    eqs = [temp_poly.nth(k) for k in range(m_deg * p - m_deg, m_deg * p)]
    sol = solve(eqs, c_syms)
    # solve の戻り値の型に応じて dict に変換
    if isinstance(sol, list):
        if not sol:
            sol = {}
        elif isinstance(sol[0], dict):
            sol = sol[0]
        else:
            # list of tuples or list of values
            if c_syms:
                first = sol[0]
                if hasattr(first, '__iter__'):
                    sol = dict(zip(c_syms, first))
                else:
                    sol = {c_syms[0]: first} if len(c_syms) == 1 else {}
            else:
                sol = {}
    elif not isinstance(sol, dict):
        sol = {}
    fi_solved = reduction_of_alpha(fi.subs(sol))
    return fi_solved


# ============================================================
#  § 12 + § 13  体の拡大による根の計算  (Part 2 メインループ)
# ============================================================
def solve_by_galois(X_poly):
    """
    組成列に従って体を拡大し、g(x) の次数を段階的に下げて v を求め、
    X[i] に代入して根を得る。
    """
    global list_of_alpha
    list_of_alpha = []

    gx_current = gx  # 現在の最小多項式
    X_current = {i: X_poly[i] for i in range(1, n + 1)}

    num_steps = len(Gs) - 1

    for step in range(1, num_steps + 1):
        G_cur = Gs[step - 1]   # インデックスリスト（1-indexed）
        H_next = Gs[step]
        p = len(G_cur) // len(H_next)

        print(f"\n━━━ ステップ {step}/{num_steps}  p={p}  "
              f"|G_{{k-1}}|={len(G_cur)} → |G_k|={len(H_next)} ━━━")

        # G_cur に属し H_next に属さない置換 s を探す
        s_idx = None
        for idx in G_cur:
            if idx not in H_next:
                s_idx = idx
                break

        # z[p] の処理
        if p == 2:
            z_p = Integer(-1)
        else:
            z_p = Symbol(f'z{p}')
            z_cond = Add(*[z_p ** i for i in range(p)])  # z^p + ... + 1 = 0
            list_of_alpha.append((z_p, z_cond))
            print(f"  z[{p}] を付加: {z_p}^{p} + ... + 1 = 0")

        # h[0], h[1], ..., h[p-1] を計算
        # h[i] = Π_{j in H_i} (x - V[j])  (V[j] は v の多項式)
        H_cur = list(H_next)
        h = []
        gkm1_v = gx_current.subs(_x, _v)
        gkm1_v_poly = Poly(expand(gkm1_v), _v, domain='EX')

        # ────────────────────────────────────────────────────
        # 早期縮減①: V[i] を現在の g_{k-1}(v) で事前縮減する
        # n≥4 では V[i] が高次（最大 deg(g0)-1 次）になるため、
        # この時点で使える最小多項式で v 次数を下げておく。
        # ────────────────────────────────────────────────────
        gkm1_deg = int(gkm1_v_poly.degree())
        if gkm1_deg > 0:
            for i_v in range(1, nn + 1):
                try:
                    v_deg = _poly_deg(V[i_v], _v)
                    if v_deg >= gkm1_deg:   # 縮減の余地がある場合のみ
                        V[i_v] = expand(
                            Poly(V[i_v], _v, domain='EX').rem(gkm1_v_poly).as_expr()
                        )
                except Exception:
                    pass

        # ────────────────────────────────────────────────────
        # 早期縮減②: _poly_mul_reduce_v で乗算中に v 次数を縮減する
        # expand() 前に縮減するため n≥4 の大規模多項式で高速。
        # ────────────────────────────────────────────────────
        for i in range(p):
            hi = Integer(1)
            total_j = len(H_cur)
            for jj, j in enumerate(H_cur):
                vj = V[j]
                hi = _poly_mul_reduce_v(hi, _x - vj, gkm1_v_poly)
                sys.stdout.write(f"\r  h[{i}] 構築中: {jj+1}/{total_j}")
                sys.stdout.flush()
            print()
            h.append(hi)
            if i < p - 1:
                H_cur = [pro[s_idx - 1][j - 1] for j in H_cur]

        # θ_i(x) = (1/p) Σ_j ζ_p^{i*j} h[j]
        # h[j] の係数は既に v 縮減済み; alpha 条件でさらに縮減
        theta = []
        for i in range(p):
            th_i = expand(Add(*[z_p ** (i * j) * h[j] for j in range(p)]) / p)
            th_i = _reduce_xpoly_v_coeffs(th_i, gkm1_v_poly)
            th_i = reduction_of_alpha(th_i)
            theta.append(th_i)
            print(f"  θ[{i}](x) = {theta[i]}")

        # α の決定
        alpha_k = None
        al_val = None
        A1_val = None

        for i in range(1, p):
            # θ[i]^p を計算して A_i, Q_i を求める
            # _poly_pow_reduce_v で各乗算ステップで v 次数を縮減する
            print(f"  θ[{i}]^{p} を計算中...")
            temp_i = reduction_of_alpha(
                _poly_pow_reduce_v(theta[i], p, gkm1_v_poly)
            )
            deg_temp = _poly_deg(temp_i, _x)
            if deg_temp < 0:
                A_i = temp_i
            else:
                A_i = Poly(temp_i, _x, domain='EX').LC()

            Q_i_raw = simplify(temp_i / A_i)
            Q_i = frac_to_poly(Q_i_raw)

            a_i_deg = _poly_deg(theta[i], _x)
            if a_i_deg < 0:
                a_i = theta[i]
            else:
                a_i = Poly(theta[i], _x, domain='EX').LC()

            q_i = pth_root(Q_i, p)

            if i == 1:
                A1_val = A_i
                al_val = a_i
                alpha_k = Symbol(f'alpha{step}')
                theta[i] = alpha_k * q_i
                list_of_alpha.append((alpha_k, alpha_k ** p - A1_val))
                print(f"  α[{step}] を付加: {alpha_k}^{p} = {A1_val}")
            else:
                # b_i = (a_1^(p-i) * a_i) / A_1
                num_bi = reduction_of_alpha(
                    Poly(expand(al_val ** (p - i) * a_i), _v, domain='EX')
                    .rem(gkm1_v_poly).as_expr()
                )
                b_i = frac_to_poly(simplify(num_bi / A1_val))
                theta[i] = alpha_k ** i * reduction_of_alpha(b_i * q_i)

        # g_k(x) = Σ θ[i]
        gx_current = reduction_of_alpha(expand(Add(*theta)))
        print(f"  g[{step}](x) = {gx_current}")

        # X[i] を g_k(v) で次数低減
        gk_v = gx_current.subs(_x, _v)
        gk_v_poly = Poly(expand(gk_v), _v, domain='EX')
        for i in range(1, n + 1):
            X_current[i] = reduction_of_alpha(
                Poly(X_current[i], _v, domain='EX').rem(gk_v_poly).as_expr()
            )

    # 最後の g_s(x) は 1次式: g_s(x) = x + c  →  v = -c
    v_value = -_poly_nth(gx_current, _x, 0)
    v_value = reduction_of_alpha(simplify(v_value))
    print(f"\n  v = {v_value}")

    # X[i] に v = v_value を代入して根を求める
    roots = {}
    for i in range(1, n + 1):
        xi = X_current[i].subs(_v, v_value)
        xi = reduction_of_alpha(expand(xi))
        roots[i] = xi

    return roots


# ============================================================
#  α → 根号への展開表示
# ============================================================
def _show_radical_forms(roots, list_of_alpha, fx_expr, deg_n):
    """
    ガロア理論式の alpha[k], z[p] を具体的な根号式に置き換えて表示する。
    2通りの方法を試みる:
      [方法1] sympy の直接代数解法 (Cardano など) による表現
      [方法2] 条件式から alpha → root(A, p) を代入した展開形
    """
    from itertools import product as _iproduct
    from sympy import RootOf

    # ── solve(fx) を1回だけ呼んで方法1・方法2照合の両方に使う ─────
    print("  [方法1] sympy の代数解法 (Cardano 公式など) による根号表現:")
    sym_sols = []
    try:
        sym_sols = solve(fx_expr, _x)
        for i, s in enumerate(sym_sols, 1):
            s_nice = simplify(s)
            if not s_nice.has(RootOf):
                print(f"    x[{i}] = {s_nice}")
            else:
                print(f"    x[{i}] ~= {complex(s_nice.evalf()):.6f}  (代数閉形式は複雑)")
    except Exception as e:
        print(f"    (計算エラー: {e})")

    # 方法2照合用（方法1の結果を再利用、solve を再呼び出しない）
    m1_exprs = []
    try:
        m1_exprs = [simplify(s) for s in sym_sols if not s.has(RootOf)]
    except Exception:
        pass

    # ── 方法2: alpha[k] → root(A, p) を代入した展開形 ──────────────
    print("  [方法2] ガロア理論式の α を root(A,p) に置き換えた展開形:")
    print("          ※ 根号の枝 (±) を適切に選ぶと方法1と一致します")

    def _build_rad_subs(sign_vec):
        """sign_vec[k] ∈ {1, -1} を使って alpha[k] → (±)root(A,p) を構築する。"""
        rsubs = {}
        for k, (alp_sym, cond) in enumerate(list_of_alpha):
            cond_sub = expand(cond.subs(rsubs))
            p = Poly(cond_sub, alp_sym, domain='EX')
            pd = int(p.degree())
            if pd == 2 and p.nth(1) == 1 and p.nth(0) == 1:
                rsubs[alp_sym] = Rational(-1, 2) + sqrt(Integer(-3)) / 2
            elif all(p.nth(j) == 0 for j in range(1, pd)):
                A = expand(-p.nth(0))
                rsubs[alp_sym] = sign_vec[k] * root(A, pd)
            else:
                return None
        return rsubs

    def _simplify_radical(xi):
        """
        方法2の展開式をより簡潔にする。
        (1) 方法1の根号式と数値照合 → 一致すれば方法1の式を使用（最も簡潔）
        (2) powsimp / cancel / simplify を順に試して短い表現を採用
        """
        try:
            xi_num = complex(xi.evalf())
        except Exception:
            return xi

        # 方法1の根との数値照合
        for m1 in m1_exprs:
            try:
                if abs(xi_num - complex(m1.evalf())) < 1e-5:
                    return m1   # 方法1の簡潔な形を流用
            except Exception:
                pass

        # powsimp → cancel → simplify の順で試行
        from sympy import powsimp, cancel as _cancel
        best = xi
        for fn in [lambda e: powsimp(e, force=True),
                   lambda e: _cancel(e),
                   lambda e: simplify(e)]:
            try:
                s = fn(best)
                if len(str(s)) < len(str(best)):
                    best = s
            except Exception:
                pass
        return best

    try:
        found = False
        # 符号の組み合わせを試して非縮退の枝を選ぶ
        for sign_vec in _iproduct([1, -1], repeat=len(list_of_alpha)):
            rsubs = _build_rad_subs(list(sign_vec))
            if rsubs is None:
                continue
            xi_raw_list = [simplify(roots[i].subs(rsubs)) for i in range(1, deg_n + 1)]
            # 縮退チェック（全て 0 になるケースをスキップ）
            if all(xi == 0 for xi in xi_raw_list):
                continue
            # 簡略化して表示
            for i, xi in enumerate(xi_raw_list, 1):
                xi_nice = _simplify_radical(xi)
                print(f"    x[{i}] = {xi_nice}")
            found = True
            break
        if not found:
            # 全符号で縮退する場合は符号なしでそのまま表示
            rsubs0 = _build_rad_subs([1] * len(list_of_alpha))
            if rsubs0:
                for i in range(1, deg_n + 1):
                    xi = simplify(roots[i].subs(rsubs0))
                    print(f"    x[{i}] = {_simplify_radical(xi)}")
            else:
                print("    (自動展開できませんでした)")
        if m1_exprs:
            print("    ※ 方法1と一致する根は方法1の表現で表示しています")
    except Exception as e:
        print(f"    (展開エラー: {e})")


# ============================================================
#  キャッシュ・タイマーユーティリティ
# ============================================================
_CACHE_FILE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'galois_cache.json')


def _cache_load():
    """galois_cache.json を読み込む。失敗時は空 dict を返す。"""
    if not _os.path.exists(_CACHE_FILE):
        return {}
    try:
        with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
            return _json.load(f)
    except Exception:
        return {}


def _cache_save(cache):
    """galois_cache.json に書き込む。"""
    try:
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            _json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  (キャッシュ保存エラー: {e})")


def _cache_key(fx_expr):
    """方程式の正規化文字列をキャッシュキーとして返す。"""
    return str(expand(fx_expr))


def _cache_save_part1(cache, key, X_poly, solvable, ratios, t_start, t_end):
    """グローバル変数から第1部の結果を収集してキャッシュに保存する。"""
    entry = cache.setdefault(key, {})
    entry['part1'] = {
        'timestamp_start': _datetime.datetime.fromtimestamp(t_start).strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp_end':   _datetime.datetime.fromtimestamp(t_end  ).strftime('%Y-%m-%d %H:%M:%S'),
        'elapsed':  round(t_end - t_start, 2),
        'n': n, 'nn': nn,
        'm':     {str(k): int(v)  for k, v in m.items()},
        'gx':    str(gx),
        'G':     [list(perm)      for perm in G],
        'Gs':    [list(gs)        for gs   in Gs],
        'pro':   pro,
        'inv_G': list(inv_G),
        'r':     {str(k): str(v) for k, v in r.items()},
        'V':     {str(k): str(v) for k, v in V.items()},
        'X_poly':   {str(k): str(v) for k, v in X_poly.items()},
        'solvable': solvable,
        'ratios':   list(ratios),
    }
    _cache_save(cache)


def _cache_save_part2(cache, key, roots, t_start, t_end):
    """第2部の結果をキャッシュに保存する。list_of_alpha はグローバルから参照。"""
    entry = cache.setdefault(key, {})
    entry['part2'] = {
        'timestamp_start': _datetime.datetime.fromtimestamp(t_start).strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp_end':   _datetime.datetime.fromtimestamp(t_end  ).strftime('%Y-%m-%d %H:%M:%S'),
        'elapsed': round(t_end - t_start, 2),
        'roots':        {str(k): str(v) for k, v in roots.items()},
        'list_of_alpha': [(str(a), str(c)) for a, c in list_of_alpha],
    }
    _cache_save(cache)


def _cache_restore_part1(entry):
    """
    第1部のキャッシュをグローバル変数に復元する。
    復元した X_poly を返す（キャッシュになければ None）。
    """
    global nn, gx, m, G, Gs, pro, inv_G, r, V
    p1 = entry['part1']
    nn       = p1['nn']
    gx       = sympify(p1['gx'])
    m        = {int(k): int(v)    for k, v in p1['m'].items()}
    G[:]     = [tuple(perm)       for perm  in p1['G']]
    Gs[:]    = [list(gs)          for gs    in p1['Gs']]
    pro[:]   = p1['pro']
    inv_G[:] = p1['inv_G']
    r.update({int(k): sympify(v)  for k, v in p1['r'].items()})
    V.update({int(k): sympify(v)  for k, v in p1['V'].items()})
    if 'X_poly' in p1:
        return {int(k): sympify(v) for k, v in p1['X_poly'].items()}
    return None


def _cache_restore_part2(entry):
    """
    第2部のキャッシュを復元して roots を返す。
    グローバル list_of_alpha も更新する。
    """
    global list_of_alpha
    p2 = entry['part2']
    roots = {int(k): sympify(v) for k, v in p2['roots'].items()}
    list_of_alpha = [(Symbol(a), sympify(c)) for a, c in p2['list_of_alpha']]
    return roots


def _ask(prompt, default=''):
    """
    input() の EOF 安全ラッパー。
    常にプロンプトを表示する。stdin が枯渇した場合は
    default を自動選択してその旨を表示する。
    """
    try:
        return input(prompt).strip().lower()
    except EOFError:
        print(f"(自動選択: {default})")
        return default.lower()


def _fmt_complex(c, decimals=6):
    """
    複素数 c を 2 形式でフォーマットして返す。
      ri_str  : 'R ± I·i' 形式  例: -1.287815 + 0.857897i
      pair_str: '(R, I)' 形式   例: (-1.287815, 0.857897)
    """
    fmt = f".{decimals}f"
    r, im = float(c.real), float(c.imag)
    sign = "+" if im >= 0 else "-"
    ri_str   = f"{r:{fmt}} {sign} {abs(im):{fmt}}i"
    pair_str = f"({r:{fmt}}, {im:{fmt}})"
    return ri_str, pair_str


_GROUP_LABEL = {
    'C2': 'C₂ (巡回群 Z₂)',  'S2': 'S₂ (対称群)',
    'C3': 'C₃ (巡回群 Z₃)',  'S3': 'S₃ (対称群)',
    'C4': 'C₄ (巡回群 Z₄)',  'V':  'V₄ (Klein 四元群)',
    'D4': 'D₄ (二面体群)',   'A4': 'A₄ (交代群)',
    'S4': 'S₄ (対称群)',
    'C5': 'C₅ (巡回群 Z₅)',  'D5': 'D₅ (二面体群)',
    'M20':'M₂₀ (フロベニウス群)', 'A5': 'A₅ (交代群)',
    'S5': 'S₅ (対称群)',
}


def _fast_galois_compute(fx_expr):
    """
    Poly.galois_group() でガロア群を高速計算する（sympy 1.11+）。
    Returns dict or None.
    """
    try:
        from sympy import Poly, QQ
        p = Poly(expand(fx_expr), _x, domain=QQ)
        name_enum, is_alt = p.galois_group(by_name=True)
        G, _             = p.galois_group(by_name=False)
        order    = G.order()
        solvable = bool(G.is_solvable)
        raw_name = str(getattr(name_enum, 'value', name_enum))
        label    = _GROUP_LABEL.get(raw_name, raw_name)
        # 組成列は可解群のみ（不可解群では composition_series が NotImplementedError）
        orders = None
        ratios = []
        if solvable:
            try:
                comp   = G.composition_series()
                orders = [g.order() for g in comp]
                ratios = [orders[i] // orders[i + 1] for i in range(len(orders) - 1)]
            except Exception:
                pass
        return {
            'name': label, 'raw': raw_name,
            'order': order, 'solvable': solvable,
            'ratios': ratios, 'comp_orders': orders,
        }
    except Exception:
        return None


def _show_sympy_roots(fx_expr):
    """
    sympy.solve() で f(x)=0 の根を直接求めて表示する。
    v（原始元）を使わない閉形式の根号表現 + 数値を併記。
    """
    from sympy import RootOf as _RootOf
    print("\n■ 根（sympy 直接解法 — v を使わない表現）:")
    try:
        sym_roots = solve(fx_expr, _x)
        for i, sr in enumerate(sym_roots, 1):
            sr_nice = simplify(sr)
            if not sr_nice.has(_RootOf):
                print(f"  x[{i}] = {sr_nice}")
            else:
                print(f"  x[{i}]  (代数閉形式は複雑)")
            try:
                ri, pair = _fmt_complex(complex(sr_nice.evalf()))
                print(f"       ≈ {ri}  = {pair}")
            except Exception:
                pass
    except Exception as e:
        print(f"  (計算エラー: {e})")


def _print_timing(dt_start, t_start, t_p1, t_p2, p1_cached, p2_cached):
    """処理開始・終了・所要時間を表示する。"""
    t_end  = _time.time()
    dt_end = _datetime.datetime.now()
    print("\n" + "=" * 65)
    print("  処理時間")
    print("=" * 65)
    print(f"  処理開始: {dt_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  処理終了: {dt_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  所要時間: {round(t_end - t_start, 2)} 秒")
    if t_p1 is not None:
        tag = "（キャッシュ）" if p1_cached else ""
        print(f"    第1部: {t_p1} 秒 {tag}")
    if t_p2 is not None:
        tag = "（キャッシュ）" if p2_cached else ""
        print(f"    第2部: {t_p2} 秒 {tag}")
    elif t_p1 is not None:
        print( "    第2部: スキップ")


# ============================================================
#  メインプログラム
# ============================================================
def main():
    global n, nn, fx, X

    print("=" * 65)
    print("  ガロア理論に基づいた代数方程式の解法")
    print("  (可解な代数方程式のガロア理論に基づいた解法)")
    print("=" * 65)
    print()
    print("方程式 f(x) = 0 を入力してください。")
    print("例: x**3 - x - 1")
    print("    x**3 + a2*x**2 + a1*x + a0  (記号係数も可)")
    print("    x**4 + 2*x**3 + 3*x**2 + 4*x + 5")
    print()
    try:
        fx_str = input("f(x) = ").strip()
    except EOFError:
        print()
        print("入力がありません。")
        return

    if '=' in fx_str:
        fx_str = fx_str.split('=', 1)[-1].strip()
    if '#' in fx_str:
        fx_str = fx_str[:fx_str.index('#')].strip()

    if not fx_str:
        print("式が空です。例: x**3 - x - 1")
        return

    try:
        fx = sympify(fx_str)
        fx = expand(fx)
    except Exception as e:
        print(f"入力エラー: {e}")
        print("例: x**3 - x - 1  (右辺の式だけを入力してください)")
        return

    lc = Poly(fx, _x, domain='EX').LC()
    if lc != 1:
        fx = expand(fx / lc)
        print(f"モニック化: f(x) = {fx}")

    n = int(degree(fx, _x))
    nn = factorial(n)

    print(f"\nf(x) = {fx}")
    print(f"次数 n = {n},  n! = {nn}")

    if n < 1:
        print("次数が 0 以下です。")
        return
    if n == 4:
        print("注意: 次数4の場合、計算に数分以上かかることがあります（n!=24の行列演算）。")
    elif n >= 5:
        print("警告: 次数 >= 5 の場合は実用的でない程度に時間がかかります（n!≥120）。")

    for i in range(1, n + 1):
        X[i] = Symbol(f'X{i}')

    # ── モード選択 ────────────────────────────────────────
    print()
    print("  ┌─ モード選択 ───────────────────────────────────────────────────────┐")
    print("  │ (1) PDF 準拠モード  §1〜§13 全手順（ガロア群→体の拡大→根）教育的  │")
    print("  │ (2) 高速モード      §1〜§9（ガロア群・組成列）+ sympy 直接根        │")
    print("  └────────────────────────────────────────────────────────────────────┘")
    mode = _ask("  モード選択 [1/2]: ", '1').strip()
    if mode not in ('1', '2'):
        mode = '1'

    # キャッシュとキーはどちらのモードでも使う
    cache = _cache_load()
    ckey  = _cache_key(fx)

    # ── タイマー開始 ──────────────────────────────────────
    t_prog_start  = _time.time()
    dt_prog_start = _datetime.datetime.now()
    t_p1_elapsed = t_p2_elapsed = None
    p1_from_cache = p2_from_cache = False

    # ── キャッシュ確認 ────────────────────────────────────
    cached = cache.get(ckey, {})
    has_p1 = 'part1' in cached
    has_p2 = 'part2' in cached

    # ── 高速モード: Part 1 も Poly.galois_group() で高速化 ────
    if mode == '2' and not has_p1:
        print("\n" + "─" * 55)
        print("  第1部: ガロア群の計算（高速モード — Poly.galois_group）")
        print("─" * 55)
        t_p1_s = _time.time()
        fast_res = _fast_galois_compute(fx)
        t_p1_elapsed = round(_time.time() - t_p1_s, 2)

        if fast_res is not None:
            solvable_fast = fast_res['solvable']
            print(f"\n  ガロア群: {fast_res['name']}  (位数 {fast_res['order']})")
            if fast_res['comp_orders'] is not None:
                orders_str = " → ".join(f"[{o}]" for o in fast_res['comp_orders'])
                print(f"  組成列:   {orders_str}")
                print(f"  商の素数列: {fast_res['ratios']}")
            else:
                print(f"  組成列:   (不可解群のため組成列の計算は省略)")
            print(f"\n  f(x) は {'[可解]' if solvable_fast else '[可解でない — 根号では解けません]'}")
            print(f"  第1部所要時間: {t_p1_elapsed} 秒")

            print("\n" + "─" * 55)
            print("  根の計算（高速モード — sympy 直接解法）")
            print("─" * 55)
            _show_sympy_roots(fx)
            _print_timing(dt_prog_start, t_prog_start, t_p1_elapsed, None, False, False)
            return
        else:
            print("  (Poly.galois_group() 利用不可 → 従来手法で継続)")
            # fall through to traditional Part 1

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  第1部: ガロア群の計算
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    X_poly = None

    if has_p1:
        p1info = cached['part1']
        print(f"\n  [キャッシュ] 第1部の結果が保存されています。")
        print(f"    計算日時: {p1info.get('timestamp_end', '不明')}")
        print(f"    所要時間: {p1info.get('elapsed', '?')} 秒")
        ans = _ask("  キャッシュを使用しますか？ [Y/n]: ", 'y')
        if ans != 'n':
            try:
                X_poly = _cache_restore_part1(cached)
                p1_from_cache = True
                t_p1_elapsed  = p1info.get('elapsed', 0)
                print("  → 復元完了")
            except Exception as e:
                print(f"  → 復元失敗 ({e}): 再計算します。")

    if not p1_from_cache:
        print("\n" + "─" * 55)
        print("  第1部: ガロア群の計算")
        print("─" * 55)
        t_p1_s = _time.time()

        print("\n[§1] 根と係数の関係を計算中...")
        root_and_coefficient()
        for i in range(1, n + 1):
            print(f"  r[{i}] = {r[i]}")

        print("\n[§3] 置換 σ を生成中...")
        build_sigma()
        print(f"  {nn} 個の置換を生成しました。")

        print("\n[§4] 原始要素 v を計算中... (時間がかかることがあります)")
        primitive_element()
        print(f"  m = {[m[i] for i in range(1, n + 1)]}")

        print("  g(x) を因数分解中...")
        minimal_polynomial_select()
        print(f"  g(x) = {gx}")
        print(f"  deg(g) = {_poly_deg(gx, _x)}")

        print("\n[§5] 分解体の基底を計算中...")
        basis_of_splitting_field()

        print("\n[§6] V[1] のべき乗を計算中... (時間がかかることがあります)")
        A_matrix = power_of_v()

        print("\n[§6] LU分解で X[i] を v の多項式として計算中...")
        X_poly = x_of_v(A_matrix)
        if not X_poly:
            print("  X[i] の計算に失敗しました。")
            return
        for i in range(1, n + 1):
            print(f"  X[{i}] = {X_poly[i]}")
        _show_sympy_roots(fx)

        print("\n[§7] ガロア群 G を計算中...")
        galois_group(X_poly)
        print(f"  |G| = {nn}")
        print("  G =")
        for perm in G:
            print(f"    {perm}")

        print("\n[§8] G の乗積表と逆元を計算中...")
        product_of_G()

        print("\n[§9] G の組成列を計算中...")
        composition_series()
        print("  組成列:")
        for k, Gk in enumerate(Gs):
            perms = [G[idx - 1] for idx in Gk]
            print(f"    G{k}: {perms}  (|G{k}| = {len(Gk)})")

        t_p1_e = _time.time()
        t_p1_elapsed = round(t_p1_e - t_p1_s, 2)
    else:
        print("\n" + "─" * 55)
        print("  第1部: ガロア群の計算 [キャッシュ]")
        print("─" * 55)
        print("\n[§1] 根と係数の関係:")
        for i in range(1, n + 1):
            print(f"  r[{i}] = {r.get(i, '?')}")
        print(f"\n  g(x) = {gx}")
        print(f"  m = {[m.get(i, '?') for i in range(1, n + 1)]}")
        print(f"\n  |G| = {nn}")
        print("  G =")
        for perm in G:
            print(f"    {perm}")
        print("\n  組成列:")
        for k, Gk in enumerate(Gs):
            perms = [G[idx - 1] for idx in Gk]
            print(f"    G{k}: {perms}  (|G{k}| = {len(Gk)})")

    # ── 可解性の判定 ─────────────────────────────────────
    solvable = True
    ratios = []
    for k in range(1, len(Gs)):
        ratio = len(Gs[k - 1]) // len(Gs[k])
        ratios.append(ratio)
        if not isprime(ratio):
            solvable = False

    print(f"\n  商の素数列: {ratios}")
    print(f"  f(x) は {'[可解]' if solvable else '[可解でない — 根号では解けません]'}")

    if not p1_from_cache:
        try:
            _cache_save_part1(cache, ckey, X_poly, solvable, ratios, t_p1_s, t_p1_e)
            print(f"  [キャッシュ] 第1部を保存しました → {_CACHE_FILE}")
        except Exception as e:
            print(f"  (キャッシュ保存エラー: {e})")

    if not solvable:
        print("\n根号による解を求めることができません。")
        print("参考: 数値解（ sympy.solve を使用）:")
        num_sols = solve(fx, _x)
        for i, s in enumerate(num_sols, 1):
            print(f"  x[{i}] = {s}")
        _print_timing(dt_prog_start, t_prog_start, t_p1_elapsed, None, p1_from_cache, False)
        return

    # ── 高速モード: Part 2 をスキップして sympy で根を表示 ─────
    if mode == '2':
        print("\n" + "─" * 55)
        print("  根の計算（高速モード — sympy 直接解法）")
        print("─" * 55)
        _show_sympy_roots(fx)
        _print_timing(dt_prog_start, t_prog_start, t_p1_elapsed, None,
                      p1_from_cache, False)
        return

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  第2部: 根の計算（PDF 準拠モード）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    roots = None

    if has_p2:
        p2info = cached['part2']
        print(f"\n  [キャッシュ] 第2部の結果も保存されています。")
        print(f"    計算日時: {p2info.get('timestamp_end', '不明')}")
        print(f"    所要時間: {p2info.get('elapsed', '?')} 秒")
        ans = _ask("  キャッシュを使用しますか？ [Y/n]: ", 'y')
        if ans != 'n':
            try:
                roots = _cache_restore_part2(cached)
                p2_from_cache = True
                t_p2_elapsed  = p2info.get('elapsed', 0)
                print("  → 復元完了")
            except Exception as e:
                print(f"  → 復元失敗 ({e}): 再計算します。")

    if not p2_from_cache:
        if n >= 4:
            print(f"\n注意: 次数 {n} の根の計算（第2部）は中間多項式が非常に大きくなります。")
            print("  次数3以下: 数十秒で完了")
            print("  次数4以上: 数時間以上かかる可能性があります")
            ans = _ask("  第2部（根号表現の計算）を実行しますか？ (y/N): ", 'n')
            if ans != 'y':
                print("\n第2部をスキップしました。")
                print("第1部の結果（ガロア群・組成列・可解性判定）をご参照ください。")
                _show_sympy_roots(fx)
                _print_timing(dt_prog_start, t_prog_start, t_p1_elapsed, None,
                              p1_from_cache, False)
                return

        print("\n" + "─" * 55)
        print("  第2部: 根の計算（体の拡大）")
        print("─" * 55)

        t_p2_s = _time.time()
        roots  = solve_by_galois(X_poly)
        t_p2_e = _time.time()
        t_p2_elapsed = round(t_p2_e - t_p2_s, 2)

        try:
            _cache_save_part2(cache, ckey, roots, t_p2_s, t_p2_e)
            print(f"  [キャッシュ] 第2部を保存しました → {_CACHE_FILE}")
        except Exception as e:
            print(f"  (キャッシュ保存エラー: {e})")
    else:
        print("\n" + "─" * 55)
        print("  第2部: 根の計算（体の拡大）[キャッシュ]")
        print("─" * 55)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  結果の表示（高コスト部分を display_text としてキャッシュ）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    _disp_cached = cached.get('part2', {}).get('display_text') if p2_from_cache else None

    if _disp_cached is not None:
        # キャッシュ済みの表示テキストをそのまま出力
        print(_disp_cached, end='')
    else:
        # 表示を計算しながら stdout を StringIO にキャプチャする
        import io as _io_mod
        _buf = _io_mod.StringIO()
        _real_stdout = sys.stdout
        sys.stdout = _buf
        try:
            print("\n" + "=" * 65)
            print("  結果")
            print("=" * 65)

            print("\n■ 体の拡大に使った α と z の定義:")
            for alp_sym, cond in list_of_alpha:
                print(f"  {alp_sym} の条件式: {cond} = 0")

            print("\n■ 根（α, z を含む根号表現）:")
            print("  ─── ガロア理論による段階的な体の拡大で得られた表現 ───")
            for i in range(1, n + 1):
                print(f"  x[{i}] = {roots[i]}")

            print("\n■ 根（α を根号で展開した表現）:")
            _show_radical_forms(roots, list_of_alpha, fx, n)

            print("\n■ 数値確認:")

            print("  [参考] sympy 直接解法による数値根:")
            try:
                direct_roots = solve(fx, _x)
                for i, dr in enumerate(direct_roots, 1):
                    ri, pair = _fmt_complex(complex(dr.evalf()))
                    print(f"    r{i} = {ri}  = {pair}")
            except Exception:
                pass

            print("\n  [検証] α, z に数値を代入して f(x[i]) ≈ 0 を確認:")
            try:
                import numpy as _np_ver

                def iter_alpha_combos(idx, subs_dict):
                    """numpy.roots で alpha を数値列挙する（sympy.solve より高速）。"""
                    if idx >= len(list_of_alpha):
                        yield dict(subs_dict)
                        return
                    alp_sym, cond = list_of_alpha[idx]
                    cond_sub = expand(cond.subs(
                        {k: sympify(v) for k, v in subs_dict.items()}
                    ))
                    try:
                        p_poly = Poly(cond_sub, alp_sym, domain='EX')
                        deg = int(p_poly.degree())
                        if deg <= 0:
                            return
                        coeffs = [complex(p_poly.nth(k).evalf())
                                  for k in range(deg, -1, -1)]
                        sols_num = _np_ver.roots(coeffs).tolist()
                    except Exception:
                        return
                    for val in sols_num:
                        val_c = complex(val)
                        if idx > 0 and abs(val_c) < 1e-10:
                            continue
                        new_dict = dict(subs_dict)
                        new_dict[alp_sym] = val_c
                        yield from iter_alpha_combos(idx + 1, new_dict)

                found_roots = []
                checked = 0
                for subs_d in iter_alpha_combos(0, {}):
                    if checked >= 30:
                        break
                    subs_eval = {str(k): complex(v) for k, v in subs_d.items()}
                    for i in range(1, n + 1):
                        try:
                            xi_v = complex(roots[i].evalf(subs=subs_eval))
                            f_xi = complex(fx.evalf(subs={str(_x): xi_v}))
                            if abs(f_xi) < 1e-4:
                                found_roots.append((i, xi_v, f_xi))
                        except Exception:
                            pass
                    checked += 1

                unique_roots = {}
                for i, xi_v, f_xi in found_roots:
                    key_r = round(xi_v.real, 4) + round(xi_v.imag, 4) * 1j
                    if key_r not in unique_roots:
                        unique_roots[key_r] = (i, xi_v, f_xi)

                if unique_roots:
                    print("  根号表現が正しく根を表していることを確認:")
                    for key_r, (i, xi_v, f_xi) in sorted(unique_roots.items(),
                                                           key=lambda kv: kv[1][1].real):
                        ri, pair = _fmt_complex(xi_v)
                        print(f"    x = {ri}  = {pair}  (|f(x)| = {abs(f_xi):.2e}  ✓)")
                else:
                    print("  (数値的に根を確認できませんでした)")
            except Exception as e:
                print(f"  (数値評価エラー: {e})")
        finally:
            sys.stdout = _real_stdout

        _disp_text = _buf.getvalue()
        print(_disp_text, end='')

        # display_text をキャッシュに保存
        try:
            _upd = cache.setdefault(ckey, {}).setdefault('part2', {})
            _upd['display_text'] = _disp_text
            _cache_save(cache)
            print("  [キャッシュ] 表示結果を保存しました。")
        except Exception as _e:
            print(f"  (表示キャッシュ保存エラー: {_e})")

    _print_timing(dt_prog_start, t_prog_start, t_p1_elapsed, t_p2_elapsed,
                  p1_from_cache, p2_from_cache)


if __name__ == '__main__':
    main()
