class HeadEditor: #1 <head>要素を編集
    def __inint__(self):
        self.meta = {}

    def edit(self):
        print("[head情報の編集]")
        self.mata['description'] = input('ページの説明文：')
    
class ArticleMeta: #2 記事のタイトル、日付、タグを編集
    def __inint__(self):
        self.title = ""
        self.date = ""
        self.tags = []

    def edit(self):
        from datetime import datetime
        print("[記事情報の設定}")
        self.title = input('タイトル：')
        self.date = input('日付(YY-MM-DD)：') or datetime.noe().strftime("%Y-%m-%d") # 空白なら当日
        tags_raw = input("タグ(カンマ区切り)：")
        self.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    
class ArticleEditor: #3 記事の作成
    def __init__(self):
        self.content = []

    def edit(self):
        # 動作終了の確認もして、入れ子構造もできるようにする(例：<p>リンクは<a href="https://example.com">ここ<</a><をクリック/p>)

    def p(self, content): # 本文の関数
        # 見出し
        # 目次リスト(見出し対応)
        # 箇条書きリスト
        # 表
        # 画像
        # リンク
        # 適宜追加可能
    
class ArticleBuilder(HeadEditor, ArticleMeta, ArtickeEditor): #4 記事を組み立てる
    # クラス1~3を実行し、テンプレートを読み込み、htmlを作成→プレビューを表示、良ければ保存
    # 日付とinput()でファイル名を作成→og:urlを更新、
    # タグごとにファイル名、タイトル, urlをjsonに保存
    html = # template.html
    
class IndexUpdater: #5 記事のメタデータをもとに記事一覧ページを追加・更新する(タグと一覧ページ名をjson保存)
    # 記事一覧のjsonを基に、全記事一覧→タグごと一覧のjsonを作成(タグが新しければ新規作成), jsonを基に各一覧ページを作成
    # タグに対応するjsonおよび一覧htmlファイルの名前はユーザに尋ねる
    
class RecentUpdater: #6 個別記事の最新記事リンクを全更新する、最新記事はひとつ前へのリンク、ひとつ前の記事は最新へのリンクを追加する
    # 記事一覧のjsonをもとに各ファイルごとに更新
    
class TopPageUpdater: #7 トップページの最新記事リンクを更新する
    # index.htmlを読み込み更新

# とりあえずここまで----------------------スクレイピングはあとで
# class GalleryUpdater: #8 Tumblrをスクレイピングし最近投稿の画像を数枚並べる(ページ下部にTumblrへのリンクを置く)
    
class SiteUpDater(IndexUpdater, RecentUpdater, TopPageUpdater): #9 アップデート
    
class SiteGenerator(ArticleBuilder, SiteUpDater): #10 すべての処理を実行