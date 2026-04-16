import subprocess
import sys


# =========================
# util
# =========================
def run(cmd):
    print(f"\n>>> {cmd}")
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)

    if r.stdout:
        print(r.stdout.strip())
    if r.stderr:
        print(r.stderr.strip())

    if r.returncode != 0:
        # git diff系は許容する場合があるので例外は呼び出し側で制御
        return r.stdout.strip(), r.stderr.strip(), r.returncode

    return r.stdout.strip(), r.stderr.strip(), r.returncode


print("=== deploy_blog ===")


# =========================
# fetch
# =========================
run("git fetch")


# =========================
# 状態取得
# =========================
status_out, _, _ = run("git status --porcelain")
local_head, _, _ = run("git rev-parse HEAD")
remote_head, _, _ = run("git rev-parse @{u}")


has_local_changes = len(status_out.strip()) > 0
remote_updated = local_head != remote_head


# =========================
# 変更ファイル抽出
# =========================
def get_local_changed_files():
    out, _, _ = run("git status --porcelain")
    files = set()
    for line in out.splitlines():
        if line.strip():
            # " M file.html" or "A file"
            parts = line.strip().split()
            if len(parts) == 2:
                files.add(parts[1])
            elif len(parts) > 2:
                files.add(parts[-1])
    return files


def get_remote_changed_files():
    out, _, _ = run("git diff --name-only HEAD @{u}")
    return set(out.splitlines()) if out else set()


# =========================
# 衝突推定
# =========================
def estimate_conflicts():
    local_files = get_local_changed_files()
    remote_files = get_remote_changed_files()

    conflict = local_files & remote_files

    print("\n--- 状態分析 ---")
    print("ローカル変更:", local_files)
    print("リモート変更:", remote_files)
    print("衝突候補:", conflict)

    return conflict


# =========================
# ケース①
# ローカル変更なし & remote更新あり
# =========================
if (not has_local_changes) and remote_updated:
    print("\n📥 remote更新あり → pullのみ実行")
    run("git pull")
    sys.exit(0)


# =========================
# ケース②
# ローカル変更あり & remote更新あり
# =========================
if has_local_changes and remote_updated:
    print("\n⚠ 未同期状態（ローカル + リモート両方変更）")

    conflict = estimate_conflicts()

    if conflict:
        print("\n⚠ 衝突可能性があるファイル:", conflict)
    else:
        print("\n✔ 衝突可能性は低い")

    ans = input("\nstashして統合しますか？ (yes/no): ").strip().lower()

    if ans != "yes":
        print("中断しました")
        sys.exit(1)

    print("\n📦 stash → pull → pop 実行")

    run("git stash")
    run("git pull")

    pop_out, pop_err, _ = run("git stash pop")

    if "CONFLICT" in pop_out or "CONFLICT" in pop_err:
        print("\n⚠ 競合発生：手動修正が必要")
        sys.exit(1)

    print("\n✔ 統合完了")
    sys.exit(0)


# =========================
# ケース③
# ローカル変更のみ
# =========================
if has_local_changes and not remote_updated:
    print("\n✔ ローカル変更あり（push実行）")

    run("git add .")
    run('git commit -m "update"')
    run("git push")

    sys.exit(0)


# =========================
# ケース④
# 完全同期
# =========================
print("\n✔ 完全同期状態（何もしない）")