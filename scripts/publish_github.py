# -*- coding: utf-8 -*-
"""깃허브 저장소로 올리는 도우미 — 사용자명·저장소·이메일을 묻고 git 을 대신 실행한다."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(*args, check=True, quiet=False):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not quiet:
        for s in (r.stdout, r.stderr):
            if s and s.strip():
                print("    " + s.strip().replace("\n", "\n    "))
    if check and r.returncode != 0:
        raise SystemExit(r.returncode)
    return r.returncode


def ask(label):
    try:
        return input(f"  {label} : ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("\n  ── 깃허브 저장소로 올립니다 ─────────────────────────────\n")
    print("  먼저 https://github.com/new 에서 빈 저장소를 만들어 두세요.")
    print("    - Public 으로 (무료 계정은 Public 이어야 깃허브 페이지가 켜집니다)")
    print("    - README / .gitignore / license 는 모두 체크 해제\n")

    user = ask("깃허브 사용자명")
    repo = ask("저장소 이름 (예: naver-webtoon-paid)") or "naver-webtoon-paid"
    mail = ask("깃허브에 등록된 이메일")
    if not user or not mail:
        print("\n  입력이 비어 있어서 그만둡니다.\n")
        return 1

    print()
    if run("git", "rev-parse", "--git-dir", check=False, quiet=True) != 0:
        run("git", "init")
    run("git", "config", "user.name", user)
    run("git", "config", "user.email", mail)
    run("git", "add", "-A")
    run("git", "commit", "-m", "네이버 웹툰 유료화 전환 작품 관심수/별점", check=False)
    run("git", "branch", "-M", "main")
    run("git", "remote", "remove", "origin", check=False, quiet=True)
    run("git", "remote", "add", "origin", f"https://github.com/{user}/{repo}.git")

    print("\n  올리는 중입니다. 로그인 창이 뜨면 깃허브 계정으로 로그인하세요.\n")
    if run("git", "push", "-u", "origin", "main", check=False) != 0:
        print("\n  올리기에 실패했습니다. 저장소 이름이 맞는지, 그 저장소가 비어 있는지 보세요.")
        print("  이미 내용이 있는 저장소라면 먼저:  git pull --rebase origin main\n")
        return 1

    print("\n  ── 올렸습니다. 이제 깃허브 페이지를 켜세요 ──────────────\n")
    print(f"  1) https://github.com/{user}/{repo}/settings/pages")
    print("     Source = Deploy from a branch / Branch = main / 폴더 = /docs / Save\n")
    print(f"  2) https://github.com/{user}/{repo}/settings/actions")
    print("     맨 아래 Workflow permissions = Read and write permissions / Save")
    print("     (매일 자동 갱신이 커밋할 수 있게 하는 설정입니다)\n")
    print(f"  1~2분 뒤 주소 :  https://{user}.github.io/{repo}/\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
