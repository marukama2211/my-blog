from datetime import datetime
import json
import os

class HeadEditor:
    def __init__(self):
        self.meta = {}

    def edit(self):
        print("[head情報の編集]")
        self.meta['description'] = input('ページの説明文：')


class ArticleMeta:
    def __init__(self):
        self.title = ""
        self.date = ""
        self.tags = []

    def edit(self):
        print("[記事情報の設定]")
        self.title = input('タイトル：')
        self.date = input('日付(YYYY-MM-DD)：') or datetime.now().strftime("%Y-%m-%d")
        tags_raw = input("タグ(カンマ区切り)：")
        self.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]


class ArticleEditor:
    def __init__(self):
        self.content = []
        self.toc = []

    def handle_paragraph(self):
        line = input("段落：")
        self.content.append(f"<p>{line}</p>")

    def handle_heading(self):
        level = input("見出しレベル(h1〜h6)：") or "h2"
        heading = input("見出しテキスト：")
        anchor = heading.lower().replace(" ", "-")
        self.content.append(f"<{level} id=\"{anchor}\">{heading}</{level}>")
        self.toc.append(f"<li><a href=\"#{anchor}\">{heading}</a></li>")

    def handle_list(self, list_type):
        items = []
        print("リスト項目を入力（空行で終了）：")
        while True:
            item = input(" - ")
            if item == "":
                break
            items.append(f"<li>{item}</li>")
        self.content.append(f"<{list_type}>\n" + "\n".join(items) + f"\n</{list_type}>")

    def handle_table(self):
        headers = input("ヘッダ（カンマ区切り）：").split(',')
        self.content.append("<table>\n<tr>" + "".join([f"<th>{h.strip()}</th>" for h in headers]) + "</tr>")
        print("行データを入力（カンマ区切り、空行で終了）：")
        while True:
            row = input("行：")
            if row == "":
                break
            cells = row.split(',')
            self.content.append("<tr>" + "".join([f"<td>{c.strip()}</td>" for c in cells]) + "</tr>")
        self.content.append("</table>")

    def handle_image(self):
        src = input("画像パス：")
        alt = input("代替テキスト：")
        self.content.append(f"<img src=\"{src}\" alt=\"{alt}\">")

    def handle_link(self):
        href = input("リンクURL：")
        link_text = input("リンクテキスト（または画像・HTML）：")
        self.content.append(f"<a href=\"{href}\">{link_text}</a>")

    def edit(self):
        print("[記事本文を入力。空行で終了。見出し=h、リスト=ul/ol、表=table、画像=img、リンク=a、段落=p]")
        handlers = {
            "p": self.handle_paragraph,
            "h": self.handle_heading,
            "ul": lambda: self.handle_list("ul"),
            "ol": lambda: self.handle_list("ol"),
            "table": self.handle_table,
            "img": self.handle_image,
            "a": self.handle_link,
        }
        while True:
            element_type = input("要素タイプ(p/h/ul/ol/table/img/a/END)：").lower()
            if element_type == "end":
                break
            handler = handlers.get(element_type)
            if handler:
                handler()
            else:
                print("未対応の要素タイプです。")

    def render(self):
        toc_html = "<ul>" + "\n".join(self.toc) + "</ul>" if self.toc else ""
        return toc_html + "\n" + "\n".join(self.content)


class ArticleBuilder(HeadEditor, ArticleMeta, ArticleEditor):
    def __init__(self):
        HeadEditor.__init__(self)
        ArticleMeta.__init__(self)
        ArticleEditor.__init__(self)
        self.cover = "images/default.jpg"
        self.coverdescription = "cover image"
        self.filename = ""
        self.last_post = ""
        self.next_post = ""
        self.hot_news = ""
        self.sub_menu = ""

    def build(self):
        self.edit()
        self.filename = input("保存ファイル名(拡張子なし)：") + ".html"
        self.cover = input("カバー画像パス(images/...)：") or self.cover
        self.coverdescription = input("カバー画像の説明：") or "cover"

        with open("template.html", encoding="utf-8") as f:
            template = f.read()

        html = template.format(
            title=self.title,
            description=self.meta['description'],
            date=self.date.split('-'),
            tags=", ".join(self.tags),
            cover=self.cover,
            coverdescription=self.coverdescription,
            filename=self.filename,
            content=self.render(),
            last_post=self.last_post,
            next_post=self.next_post,
            hot_news=self.hot_news,
            sub_menu=self.sub_menu
        )

        print("[記事のプレビュー]")
        print(html[:500], "... (略)...")

        if input("保存しますか？(y/n)：") == 'y':
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"保存完了: {self.filename}")
        else:
            print("保存をキャンセルしました")
