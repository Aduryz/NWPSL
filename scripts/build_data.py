# -*- coding: utf-8 -*-
"""깃허브 페이지가 읽을 docs/data.json 을 만든다 (GitHub Actions 에서 주기 실행)."""

import datetime
import json
import pathlib
import sys

import naver_paid_core as core

OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "data.json"


def main():
    try:                       # 윈도우 cmd 는 기본이 cp949 라 한글·기호에서 죽는다
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    data = core.collect()
    kst = datetime.timezone(datetime.timedelta(hours=9))
    data["fetchedAt"] = datetime.datetime.now(kst).isoformat(timespec="seconds")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    hot = sum(1 for r in data["rows"]
              if r["favorite"] is not None and r["favorite"] >= data["threshold"])
    print(f"{OUT} 작성 완료 — 작품 {len(data['rows'])}편, "
          f"관심수 {data['threshold']:,} 이상 {hot}편")
    print(f"공지: {data['notice']['subject']}")
    if not data["rows"]:
        print("작품을 하나도 못 찾았습니다.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
