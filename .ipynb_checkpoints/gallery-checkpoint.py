import requests
from bs4 import BeautifulSoup
import re


HTML_PATH = "gallery.html"


def scrape_tumblr_images(base_url, max_pages=100):
    """
    Tumblr から画像リンクを取得し、画像URLリストを返す
    ページに画像がない・エラー時は終了
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    image_urls = []

    for page_num in range(1, max_pages + 1):
        if page_num == 1:
            page_url = base_url.rstrip('/')
        else:
            page_url = f"{base_url.rstrip('/')}/page/{page_num}"

        print(f"📄 Fetching: {page_url}")

        response = requests.get(page_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ ページ {page_num} が存在しない → 終了")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")

        # 2ページ目以降で画像がなくなったら終了
        if page_num > 1 and not images:
            print(f"⚠️ ページ {page_num} に画像なし → 終了")
            break

        new_images = 0

        for img in images:
            src = img.get("src")
            if src and src.startswith("https://64.media.tumblr.com/"):
                if src not in image_urls:
                    image_urls.append(src)
                    new_images += 1
                    print(f"[{len(image_urls)}] {src}")

        if new_images == 0 and page_num > 1:
            print("⚠️ 新しい画像なし → 終了")
            break

    print("\n--- 📌 取得完了 ---")
    print(f"合計 {len(image_urls)} 枚取得済み\n")

    return image_urls



def update_gallery_html(image_urls):
    """
    gallery.html の grid 内画像ブロックをすべて削除し
    最新画像が上になる順序で再構築
    """
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 廃棄対象:
    # <div class="item"> ～ </div> の繰り返しを全削除
    html_cleaned = re.sub(
        r'<div class="item">[\s\S]*?<img[\s\S]*?</div>',
        '',
        html
    )

    # 追加対象の挿入位置を検索
    marker = '<div class="wrapper grid">'
    idx = html_cleaned.find(marker)

    if idx == -1:
        raise ValueError("gallery.html 内に grid 要素が見つかりません")

    # markerの直後に挿入する
    before = html_cleaned[:idx + len(marker)]
    after = html_cleaned[idx + len(marker):]

    # 既に image_urls は取得順で古 → 新なので逆にしないこと！
    # ※ 新しい画像ほど後ろに append されている
    addition = ""

    for url in image_urls:  # ← ここが順番のポイント
        addition += (
            '\n            <div class="item">\n'
            f'                <img src="{url}" alt="">\n'
            '            </div>'
        )

    new_html = before + addition + after

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("✨ gallery.html を更新しました")
    print("👆 画像の上ほど新しい順番です")


if __name__ == "__main__":
    blog_url = "https://marucama.tumblr.com"  # ←変更する

    images = scrape_tumblr_images(blog_url)

    update_gallery_html(images)
