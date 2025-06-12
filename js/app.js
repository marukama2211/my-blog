document.addEventListener('DOMContentLoaded', () => {
  const content = document.getElementById('content');

  async function loadPage(page) {
    let path = `contents/${page}.html`;
    const res = await fetch(path);
    content.innerHTML = await res.text();

    if (page === 'posts') {
      loadPosts();
    }
  }

    async function loadPosts() {
      const res = await fetch('posts.json');
      const posts = await res.json();
    
      const loading = document.getElementById('posts-loading');
      if (loading) loading.remove(); // 読み込み中メッセージ削除
    
      const listContainer = document.getElementById('posts-list');
      listContainer.innerHTML = ''; // ← ここでリストを毎回初期化！
    
      const list = document.createElement('ul');
    
      posts.forEach(post => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = post.url;
        a.textContent = `${post.date}: ${post.title}`;
        a.addEventListener('click', async (e) => {
          e.preventDefault();
          const res = await fetch(post.url);
          document.getElementById('content').innerHTML = await res.text();
          attachNavEvents();
        });
        li.appendChild(a);
        list.appendChild(li);
      });
    
      listContainer.appendChild(list);
    }


  function attachNavEvents() {
    document.querySelectorAll('a[data-page]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        loadPage(link.dataset.page);
      });
    });
  }

  attachNavEvents();
  loadPage('home');
});
