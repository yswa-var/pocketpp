document.addEventListener('DOMContentLoaded', () => {
    loadArticles();

    const form = document.getElementById('add-article-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const url = document.getElementById('url').value;
        const category = document.getElementById('category').value;

        try {
            const response = await fetch('/articles/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, category }),
            });
            if (!response.ok) {
                throw new Error('Failed to add article');
            }
            const data = await response.json();
            alert(data.message);
            loadArticles(); // Refresh the article list
        } catch (error) {
            alert(error.message);
        }
    });
});

async function loadArticles() {
    try {
        const response = await fetch('/articles/');
        if (!response.ok) {
            throw new Error('Failed to load articles');
        }
        const articles = await response.json();
        const articleList = document.getElementById('article-list');
        articleList.innerHTML = ''; // Clear existing list
        articles.forEach(article => {
            const li = document.createElement('li');
            li.innerHTML = `
                <strong>${article.title}</strong> (Category: ${article.category})<br>
                Summary: ${article.summary}<br>
                <a href="/articles/${article.id}/read" target="_blank">Read</a>
            `;
            articleList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading articles:', error);
    }
}