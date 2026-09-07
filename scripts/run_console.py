# -*- coding: utf-8 -*-
"""콘솔에서 바로 보기 — 관심수 10만 이상은 핑크색 글자."""

import sys
import unicodedata

import naver_paid_core as core

PINK = "\x1b[38;2;255;105;180m"   # 핫핑크
GRAY = "\x1b[38;2;150;150;150m"
BOLD = "\x1b[1m"
OFF = "\x1b[0m"


def enable_ansi():
    """cmd 창에서도 색이 나오도록 VT 처리를 켠다."""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        for handle in (-11, -12):                 # STDOUT, STDERR
            h = k.GetStdHandle(handle)
            mode = ctypes.c_uint32()
            if k.GetConsoleMode(h, ctypes.byref(mode)):
                k.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:
        pass


def disp_len(s):
    """한글은 터미널에서 두 칸을 먹으므로 표 맞춤용 길이를 따로 센다."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def main():
    enable_ansi()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(f"\n{BOLD}네이버 웹툰 유료화 전환 작품 — 관심수 · 별점{OFF}")
    print(f"{GRAY}공지 검색어: {core.SEARCH_WORD} / 핑크 기준: 관심수 {core.THRESHOLD:,} 이상{OFF}\n")
    print(f"  {GRAY}공지를 읽는 중...{OFF}")

    data = core.collect()
    n = data["notice"]
    print(f"\r  최신 공지 : {BOLD}{n['subject']}{OFF}")
    print(f"  주소      : {GRAY}{n['url']}{OFF}\n")

    rows = data["rows"]
    if not rows:
        print("  공지 본문에서 작품명을 찾지 못했습니다.\n")
        return

    width = max(disp_len(r["name"]) for r in rows) + 2
    hot = 0
    for i, r in enumerate(rows, 1):
        pad = " " * max(0, width - disp_len(r["name"]))
        fav = f"관심 {r['favorite']:>9,}" if r["favorite"] is not None else f"관심 {'-':>9}"
        sc = f"별점 {r['star']:>5.2f}" if r["star"] is not None else f"별점 {'-':>5}"
        sc += f" (최근20화 {r['starAvg']:.2f})" if r["starAvg"] is not None else " " * 15
        line = f"{i:>2}. {r['name']}{pad}{fav}  {sc}"
        note = f"  {GRAY}{r['note']}{OFF}" if r["note"] else ""
        if r["favorite"] is not None and r["favorite"] >= core.THRESHOLD:
            hot += 1
            print(f"  {PINK}{line}{OFF}{note}")
        else:
            print(f"  {line}{note}")

    print(f"\n  {PINK}관심수 {core.THRESHOLD:,} 이상: {hot}편{OFF} / 전체 {len(rows)}편")
    print(f"  {GRAY}별점 = 최신 회차 기준 (작품 단위 별점은 네이버가 제공하지 않음){OFF}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  오류: {type(e).__name__}: {e}\n")
