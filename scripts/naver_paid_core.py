# -*- coding: utf-8 -*-
"""
네이버 웹툰 '유료화 전환 작품' 공지 → 작품별 관심수 · 별점

1) comic.naver.com 공지 목록에서 '유료화'로 검색한 결과의 가장 위(최신) 글을 연다
2) 그 공지 본문에 적힌 작품명들을 순서대로 뽑는다
3) 작품마다 네이버 웹툰에서 검색해 관심수(favoriteCount)와 별점을 읽는다

별점은 작품 단위 값이 API에 없어서 회차 별점을 쓴다
 - star     = 최신 회차의 별점
 - starAvg  = 최신 20개 회차의 평균
"""

import concurrent.futures as futures
import html
import json
import re
import urllib.parse
import urllib.request

SEARCH_WORD = "유료화"        # 공지 목록에서 검색할 말
THRESHOLD = 100_000           # 이 값 이상이면 핑크색
TIMEOUT = 15                  # 요청 하나당 최대 대기(초)
WORKERS = 4                   # 동시 요청 수

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

API = "https://comic.naver.com/api"


def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://comic.naver.com/",
        "Accept": "application/json, text/plain, */*",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def clean(s):
    """BOM·제로폭 문자·겹공백을 없앤다 (공지 본문에 종종 섞여 있다)."""
    s = re.sub("[\ufeff\u200b-\u200d\xa0]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def key(s):
    """제목 비교용 — 공백·대소문자 무시."""
    return re.sub(r"\s+", "", clean(s)).lower()


# ── 1) 최신 공지 찾기 ────────────────────────────────────────
def latest_notice():
    url = f"{API}/notice/list?searchWord={urllib.parse.quote(SEARCH_WORD)}&page=1"
    d = get_json(url)
    rows = list(d.get("bestNoticeList") or []) + list(d.get("generalNoticeList") or [])
    if not rows:
        raise RuntimeError(f"'{SEARCH_WORD}' 검색 결과가 비어 있습니다.")
    return rows[0]          # 목록 가장 위 = 최신 공지


def notice_content(notice_id):
    return get_json(f"{API}/notice/detail?noticeId={notice_id}")["notice"]["content"]


# ── 2) 공지 본문에서 작품명 뽑기 ─────────────────────────────
TAG = re.compile(r"<[^>]+>")
ANCHOR = re.compile(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.I | re.S)
NUMBERED = re.compile(r"^\s*\d+\s*[.)]\s*(.+)$")


def strip_tags(s):
    return clean(html.unescape(TAG.sub("", s)))


def parse_titles(content_html):
    """[(작품명, 공지에 걸린 titleId 또는 None), ...] 를 공지 순서대로."""
    def mark(m):
        tid = re.search(r"titleId=(\d+)", m.group(1))
        return f"{strip_tags(m.group(2))}\x01{tid.group(1) if tid else ''}\x02"

    s = ANCHOR.sub(mark, content_html)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|tr)>", "\n", s)
    s = "\n".join(strip_tags(x) for x in s.split("\n"))

    items, seen = [], set()
    for line in s.split("\n"):
        m = NUMBERED.match(line.strip())
        if not m:
            continue
        body = m.group(1).strip()
        hit = re.search(r"([^\x01]*)\x01(\d*)\x02", body)
        if hit:
            name, tid = clean(hit.group(1)), (hit.group(2) or None)
        else:
            name, tid = clean(body.replace("\x01", "").replace("\x02", "")), None
        name = re.sub(r"\s*\(\s*(완결|휴재|재연재)\s*\)\s*$", "", name).strip()
        if name and key(name) not in seen:
            seen.add(key(name))
            items.append((name, tid))

    if not items:      # 번호가 없는 형식이면 본문의 링크를 전부 쓴다
        for m in ANCHOR.finditer(content_html):
            tid = re.search(r"titleId=(\d+)", m.group(1))
            name = strip_tags(m.group(2))
            if tid and name and key(name) not in seen:
                seen.add(key(name))
                items.append((name, tid.group(1)))
    return items


# ── 3) 네이버 웹툰에서 검색 → 관심수 · 별점 ──────────────────
def search_webtoon(name):
    """검색 결과에서 (titleId, 실제 제목). 제목이 정확히 같은 것을 우선."""
    d = get_json(f"{API}/search/all?keyword={urllib.parse.quote(name)}")
    views = (d.get("searchWebtoonResult") or {}).get("searchViewList") or []
    if not views:
        return None, None
    for v in views:
        if key(v.get("titleName", "")) == key(name):
            return v.get("titleId"), v.get("titleName")
    return views[0].get("titleId"), views[0].get("titleName")


def fetch_stars(tid):
    """(최신화 별점, 최근 20화 평균). 작품 단위 별점 API가 없어 회차 별점을 쓴다."""
    try:
        d = get_json(f"{API}/article/list?titleId={tid}&page=1&sort=DESC")
        s = [a["starScore"] for a in (d.get("articleList") or [])
             if isinstance(a.get("starScore"), (int, float))]
        if not s:
            return None, None
        return round(s[0], 2), round(sum(s) / len(s), 2)
    except Exception:
        return None, None


def fetch_one(name, linked_id):
    """작품 하나의 결과 dict."""
    row = {"name": name, "titleId": None, "favorite": None,
           "star": None, "starAvg": None, "note": ""}
    try:
        tid, info = linked_id, None
        if tid:
            info = get_json(f"{API}/article/list/info?titleId={tid}")
            # 공지에 잘못된 링크가 걸려 있는 경우가 있어 제목을 대조한다
            if key(info.get("titleName", "")) != key(name):
                found, found_name = search_webtoon(name)
                if found and key(found_name or "") == key(name):
                    row["note"] = f"공지 링크가 다른 작품({info.get('titleName')})을 가리켜 검색으로 보정"
                    tid, info = found, None
        if not tid:
            tid, _ = search_webtoon(name)
        if not tid:
            row["note"] = "검색 결과 없음"
            return row
        if info is None:
            info = get_json(f"{API}/article/list/info?titleId={tid}")

        row["titleId"] = tid
        row["name"] = info.get("titleName") or name
        fav = info.get("favoriteCount")
        row["favorite"] = int(fav) if fav is not None else None
        if row["favorite"] is None and not row["note"]:
            row["note"] = "관심수 없음(성인/비공개?)"
        row["star"], row["starAvg"] = fetch_stars(tid)
    except Exception as e:
        row["note"] = f"조회 실패({type(e).__name__})"
    return row


# ── 전체 실행 ────────────────────────────────────────────────
def collect():
    """공지 정보 + 작품별 결과를 한 번에."""
    notice = latest_notice()
    items = parse_titles(notice_content(notice["noticeId"]))
    with futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        rows = list(ex.map(lambda it: fetch_one(*it), items))
    return {
        "threshold": THRESHOLD,
        "notice": {
            "id": notice["noticeId"],
            "subject": notice["subject"],
            "url": f"https://comic.naver.com/notice/detail?noticeId={notice['noticeId']}",
            "registerDate": notice.get("registerDate"),
        },
        "rows": rows,
    }
