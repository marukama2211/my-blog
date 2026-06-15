from datetime import datetime
from urllib.parse import urlparse
import os
import json
import re
from bs4 import BeautifulSoup, Comment
import html


# =========================
# Block Renderer（拡張用）
# =========================
class BlockRenderer:
    def __init__(self):
        self.handlers = {
            "p": self.render_p,
            "h4": self.render_h4,
            "b": self.render_b,
            "em": self.render_em,
            "hr": self.render_hr,
            "code": self.render_code,
            "ul": self.render_ul,
            "ol": self.render_ol,
            "img": self.render_img,
            "a": self.render_a,
        }

    def get_available_tags(self):
        return "/".join(self.handlers.keys())

    def render(self, tag):

        if tag == "code":
            language = input("言語(python/js/htmlなど)：").strip()
            return self.handlers[tag](language)
    
        return self.handlers[tag]()

    def render_p(self):
        text = input("本文：")
        return f"<p>{text}</p>"

    def render_h4(self):
        text = input("見出し(h4)：")
        return f"<h4>{text}</h4>"

    def render_b(self):
        text = input("強調：")
        return f"<p><b>{text}</b></p>"

    def render_em(self):
        text = input("強調(em)：")
        return f"<p><em>{text}</em></p>"

    def render_hr(self):
        return "<hr>"

    def render_code(self, language=""):
        print("コード入力（ENDで終了）：")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
    
        code = "\n".join(lines)

        escaped = html.escape(code)

        lang_class = f' language-{language}' if language else ""
        
        return f'''<pre class="code-block"><code class="{lang_class.strip()}">{escaped}</code></pre>'''

    def render_ul(self):
        items = []
        print("リスト（空Enterで終了）")
        while True:
            i = input(" - ")
            if not i:
                break
            items.append(f"<li>{i}</li>")
        return "<ul>\n" + "\n".join(items) + "\n</ul>"

    def render_ol(self):
        items = []
        print("番号リスト（空Enterで終了）")
        while True:
            i = input(" - ")
            if not i:
                break
            items.append(f"<li>{i}</li>")
        return "<ol>\n" + "\n".join(items) + "\n</ol>"

    def render_img(self):
        while True:
            src = input("画像URLまたはファイル名：")
            if src.startswith("http"):
                break
                
            if os.path.splitext(src)[1].lower() in [".jpg", "jpeg", ".png", ".webp"]:
                src = f"images/{src}"
                break
                
        alt = input("alt：")
        return f'<img src="{src}" alt="{alt}">'

    def render_a(self):
        href = input("URL：")
        text = input("テキスト：")
        return f'<a href="{href}">{text}</a>'


# =========================
# Head
# =========================
class HeadEditor:
    def __init__(self):
        self.description = ""

    def edit(self):
        print("[head情報の編集]")
        self.description = input("ページの説明文：")


# =========================
# Meta
# =========================
class ArticleMeta:
    def __init__(self):
        self.title = ""
        self.date = ""
        self.tags = []

    def edit(self):
        print("\n[記事情報の設定]")
        self.title = input("タイトル：")
        self.date = input("日付(YYYY-MM-DD)：") or datetime.now().strftime("%Y-%m-%d")

        print("タグ（1行ずつ入力、空Enterで終了）：")
        tags = []
        while True:
            t = input()
            if not t:
                break
            tags.append(t)

        self.tags = tags if tags else ["その他"]


# =========================
# Article Editor
# =========================
class ArticleEditor:
    def __init__(self):
        self.content = []
        self.headings = []
        self.renderer = BlockRenderer()

    def create_headings(self):
        print("\n[見出しを作成（空行で終了）]")
        while True:
            h = input(f"見出し{len(self.headings)+1}：")
            if not h:
                break
            self.headings.append((h, h.replace(" ", "-")))

    def create_intro(self):
        print("\n[序文（空Enterでスキップ）]")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    
        if lines:
            self.content.append("<p>" + "<br>".join(lines) + "</p>")
    
    def input_blocks(self):
        while True:
            tag = input(f"タグ({self.renderer.get_available_tags()} / Enterで終了)：").strip().lower()
        
            if tag == "":
                break
        
            if tag not in self.renderer.handlers:
                print("無効なタグです。もう一度入力してください。")
                continue
        
            self.content.append(self.renderer.render(tag))

    def edit(self):
        self.create_intro()
        self.create_headings()

        if not self.headings:
            print("\n[本文編集]")
            print(f"使用可能タグ：{self.renderer.get_available_tags()}")
            print("Enterで次へ")
            self.input_blocks()
            return

        for i, (h, a) in enumerate(self.headings, 1):
            print(f"\n=== {i}. {h} ===")
            self.content.append(f'<section id="{a}">')
            self.content.append(f'<h3>{h}</h3>')
            self.input_blocks()
            self.content.append("</section>")

    def render(self):
        toc = ""
        if self.headings:
            toc = """
        <div class="toc">
        <h3>目次</h3>
        <ul>
        """ + "\n".join(
                [f'<li><a href="#{a}">{h}</a></li>' for h, a in self.headings]
            ) + """
        </ul>
        </div>
        """

        return (self.content[0] + "\n" + toc + "\n" + "\n".join(self.content[1:]))


# =========================
# Builder
# =========================
class ArticleBuilder:
    def __init__(self):
        self.head = HeadEditor()
        self.meta = ArticleMeta()
        self.editor = ArticleEditor()
        self.filename = ""
        self.cover = "images/default.jpg"

    def load_tag_map(self):
        path = "json/tags.json"
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def save_tag_map(self, m):
        os.makedirs("news-catalog", exist_ok=True)
        with open("json/tags.json", "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)

    def save_json(self):
        path = "json/all.json"
        os.makedirs("news-catalog", exist_ok=True)

        data = []
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except:
                print("JSONが破損しています")
                data = []

        tag_map = self.load_tag_map()
        conv = []

        for t in self.meta.tags:
            if t not in tag_map:
                tag_map[t] = input(f"{t}の英語名：")
            conv.append({"ja": t, "en": tag_map[t]})

        self.save_tag_map(tag_map)

        data.append({
            "title": self.meta.title,
            "date": self.meta.date,
            "tags": conv,
            "link": self.filename,
            "image": self.cover
        })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def build(self):
        self.head.edit()
        self.meta.edit()
        self.editor.edit()

        while True:
            name = input("ファイル名：").strip()
            if name:
                break
            print("ファイル名が空です。再入力してください。")
        
        self.filename = f"{self.meta.date}-{name}.html"

        cover = input("カバー画像：").strip()
        
        if cover:
            self.cover = cover if cover.startswith("http") else f"images/{cover}"
        else:
            self.cover = "images/default.webp"
        
        year, month, day = self.meta.date.split("-")
        tags_str = ", ".join(self.meta.tags)
        content = self.editor.render()

        with open("template.html", encoding="utf-8") as f:
            template = f.read()

        html = template.format(
            title=self.meta.title,
            description=self.head.description,
            date=f"{int(month)}/{int(day)}",
            year=year,
            tags=tags_str,
            cover=self.cover,
            coverdescription=self.meta.title,
            filename=self.filename,
            content=content
        )

        if not self.head.description:
            text = BeautifulSoup(content, "html.parser").get_text()
            self.head.description = text[:120]

        if input("保存しますか？(y/n)：") == "y":
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"保存完了：{self.filename}")
            self.save_json()
            return True
        else:
            print("保存をキャンセルしました")
            return False


# =========================
# Updater
# =========================
class SiteUpdater:
    def load(self):
        path = "json/all.json"

        if not os.path.exists(path):
            print("jsonが存在しません")
            return []

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("jsonの読み込みに失敗（フォーマット不正）")
            return []

        return data

    def normalize_tags(self, data):
        for a in data:
            if a.get("tags") and isinstance(a["tags"][0], str):
                a["tags"] = [{"ja": t, "en": t} for t in a["tags"]]
        return data

    def collect_tags(self, data):
        tags = {}
        for a in data:
            for t in a.get("tags", []):
                tags[t["ja"]] = t["en"]
        return tags

    def get_tag_counts(self, data):
        counts = {}
    
        for article in data:
            for tag in article.get("tags", []):
                counts[tag["ja"]] = counts.get(tag["ja"], 0) + 1
    
        return counts

    def generate_news(self):
        data = self.normalize_tags(self.load())

        items = ""
        for article in reversed(data):
            tag = article["tags"][0]["ja"] if article.get("tags") else ""

            items += f"""
<a href="{article['link']}" class="item">
  <div class="thumb">
    <img src="{article['image']}" alt="">
    <div class="overlay">
      <h3>{article['title']}</h3>
      <span class="tag">{tag}</span>
      <span class="date">{article['date']}</span>
    </div>
  </div>
</a>
"""

        tags = self.collect_tags(data)
        tag_counts = self.get_tag_counts(data)
        
        items_list = list(tags.items())
        items_list.sort(key=lambda x: x[0] == "その他")
        
        tag_links = "\n".join([
            f'<a href="tag_{en}.html">{ja} <span>{tag_counts.get(ja, 0)}</span></a>'
            for ja, en in items_list
        ])

        with open("news_template.html", encoding="utf-8") as f:
            template = f.read()

        soup = BeautifulSoup(template, "html.parser")
        
        tag_links_comment = soup.find(string=lambda s: isinstance(s, Comment) and s.strip() == "TAG_LINKS")
        if not tag_links_comment:
            tag_links_comment = soup.find(text=lambda s: isinstance(s, Comment) and s.strip() == "TAG_LINKS")
        if tag_links_comment:
            tag_links_comment.replace_with(BeautifulSoup(tag_links, "html.parser"))

        articles_comment = soup.find(string=lambda s: isinstance(s, Comment) and s.strip() == "ARTICLES")
        if not articles_comment:
            articles_comment = soup.find(text=lambda s: isinstance(s, Comment) and s.strip() == "ARTICLES")
        if articles_comment:
            articles_comment.replace_with(BeautifulSoup(items, "html.parser"))

        with open("news.html", "w", encoding="utf-8") as f:
            f.write(str(soup))

        print("news.html更新完了")

    def generate_tag_pages(self):
        data = self.normalize_tags(self.load())
        tags = self.collect_tags(data)

        with open("news_template.html", encoding="utf-8") as f:
            template = f.read()

            tag_counts = self.get_tag_counts(data)

            items_list = list(tags.items())
            items_list.sort(key=lambda x: x[0] == "その他")

        for ja, en in tags.items():
            articles = [a for a in data if any(t["ja"] == ja for t in a.get("tags", []))]

            tag_links = "\n".join([
                (
                    f'<a href="tag_{tag_en}.html" class="active">'
                    f'{tag_ja} <span>{tag_counts.get(tag_ja, 0)}</span></a>'
                )
                if tag_ja == ja
                else
                (
                    f'<a href="tag_{tag_en}.html">'
                    f'{tag_ja} <span>{tag_counts.get(tag_ja, 0)}</span></a>'
                )
                for tag_ja, tag_en in items_list
            ])

            items = ""
            for a in reversed(articles):
                items += f"""
<a href="{a['link']}" class="item">
  <div class="thumb">
    <img src="{a['image']}" alt="">
    <div class="overlay">
      <h3>{a['title']}</h3>
      <span class="tag">{ja}</span>
      <span class="date">{a['date']}</span>
    </div>
  </div>
</a>
"""

            soup = BeautifulSoup(template, "html.parser")
            
            tag_links_comment = soup.find(string=lambda s: isinstance(s, Comment) and s.strip() == "TAG_LINKS")
            if not tag_links_comment:
                tag_links_comment = soup.find(text=lambda s: isinstance(s, Comment) and s.strip() == "TAG_LINKS")
            if tag_links_comment:
                tag_links_comment.replace_with(BeautifulSoup(tag_links, "html.parser"))

            articles_comment = soup.find(string=lambda s: isinstance(s, Comment) and s.strip() == "ARTICLES")
            if not articles_comment:
                articles_comment = soup.find(text=lambda s: isinstance(s, Comment) and s.strip() == "ARTICLES")
            if articles_comment:
                articles_comment.replace_with(BeautifulSoup(items, "html.parser"))

            with open(f"tag_{en}.html", "w", encoding="utf-8") as f:
                f.write(str(soup))

        print("タグ別ページ生成/更新完了")

    def update_all_articles_sidebar(self):
        data = self.normalize_tags(self.load())
    
        # 新着記事
        latest = list(reversed(data))[:4]
        hot = "\n".join([
            f'<li><a href="{a["link"]}">{a["title"]}</a></li>'
            for a in latest
        ])
    
        # タグ一覧
        tags = self.collect_tags(data)
        items = list(tags.items())
        items.sort(key=lambda x: x[0] == "その他")
        cat_html = "\n".join([
            f'<li><a href="tag_{en}.html">{ja}</a></li>'
            for ja, en in items
        ])
    
        for file in os.listdir():
            if not file.endswith(".html") or file == "news.html":
                continue
    
            with open(file, encoding="utf-8") as f:
                html = f.read()
    
            soup = BeautifulSoup(html, "html.parser")
            hot_news_ul = soup.find("ul", class_="hot-news")
            sub_menu_ul = soup.find("ul", class_="sub-menu")
            
            if not hot_news_ul and not sub_menu_ul:
                continue
                
            if hot_news_ul:
                hot_news_ul.clear()
                hot_news_ul.append(BeautifulSoup(hot, "html.parser"))
                
            if sub_menu_ul:
                sub_menu_ul.clear()
                sub_menu_ul.append(BeautifulSoup(cat_html, "html.parser"))
    
            with open(file, "w", encoding="utf-8") as f:
                f.write(str(soup))
    
        print("サイドバー更新完了")

    def update_index_latest(self):
        data = self.normalize_tags(self.load())
    
        if not data:
            print("記事が存在しません")
            return
    
        latest = data[-1]  # 一番新しい記事
        link = latest["link"]
    
        with open("index.html", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        tag = soup.find("a", id="latest-link")

        if tag:
            tag["href"] = link
    
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
    
        print("index.htmlの最新記事リンク更新完了")

    def update_all(self):
        self.generate_news()
        self.generate_tag_pages()
        self.update_all_articles_sidebar()
        self.update_index_latest()
        print("サイト更新完了")


# =========================
# main
# =========================
if __name__ == "__main__":
    builder = ArticleBuilder()
    if builder.build():
        SiteUpdater().update_all()