import logging
import os
import webbrowser
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession
from .models import Article, Category, Session
from .scraper import scrape_and_summarize
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static",
          StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Serve the index.html as the root page


@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


# Jinja2 setup
template_dir = os.path.join(os.path.dirname(__file__), "templates")
try:
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("article.html")
    logger.info(
        f"Jinja2 template 'article.html' loaded successfully from {template_dir}")
except TemplateNotFound as e:
    logger.error(f"Template not found in {template_dir}: {e}")
    raise
except Exception as e:
    logger.error(f"Error initializing Jinja2 environment: {e}")
    raise

# Pydantic models


class AddArticleRequest(BaseModel):
    url: str
    category: str = "General"

# Dependency to provide a database session


def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()


@app.post("/articles/")
def add_article(request: AddArticleRequest, db: DBSession = Depends(get_db)):
    """
    Add an article by scraping the given URL and saving it to the database.
    """
    logger.info(
        f"Starting 'add' endpoint with URL: {request.url}, Category: {request.category}")
    try:
        logger.info("Scraping and summarizing the URL")
        data = scrape_and_summarize(request.url)
        logger.info(f"Scraped data: Title={data['title']}, URL={data['url']}")

        logger.info(f"Looking for category: {request.category}")
        cat = db.query(Category).filter_by(name=request.category).first()
        if not cat:
            logger.info(
                f"Category '{request.category}' not found. Creating it.")
            cat = Category(name=request.category)
            db.add(cat)
            db.commit()
            logger.info(f"Created category: {request.category}")
        category_id = cat.id
        logger.info(f"Using category ID: {category_id}")

        article = Article(
            url=request.url,
            title=data["title"],
            content=data["content"],
            summary=data["summary"],
            image_url=data.get("image_url"),
            category_id=category_id
        )
        db.add(article)
        db.commit()
        logger.info(f"Saved article with ID: {article.id}")

        try:
            html = template.render(article=article.__dict__)
            html_path = f"articles/{article.id}.html"
            os.makedirs("articles", exist_ok=True)
            with open(html_path, "w") as f:
                f.write(html)
            logger.info(f"Generated HTML at: {html_path}")
        except Exception as e:
            logger.error(f"Failed to generate HTML: {e}", exc_info=True)
            raise

        return {"message": "Article saved successfully!", "id": article.id, "title": data["title"], "category": request.category}
    except Exception as e:
        logger.error(f"Error in 'add' endpoint: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while adding the article.")
    finally:
        logger.info("Closing session")
        db.close()


@app.get("/articles/")
def list_articles(db: DBSession = Depends(get_db)):
    """
    List all saved articles.
    """
    logger.info("Starting 'list' endpoint")
    try:
        articles = db.query(Article).all()
        logger.info(f"Found {len(articles)} articles")
        if not articles:
            return {"message": "No articles found."}
        result = []
        for a in articles:
            category_name = a.category.name if a.category else "Uncategorized"
            result.append({
                "id": a.id,
                "title": a.title,
                "category": category_name,
                "summary": a.summary
            })
            logger.info(
                f"Displayed article ID: {a.id}, Title: {a.title}, Category: {category_name}")
        return result
    except Exception as e:
        logger.error(f"Error in 'list' endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while listing articles.")
    finally:
        logger.info("Closing session")
        db.close()


@app.get("/articles/{article_id}/read")
def read_article(article_id: int):
    """
    Read an article by opening its HTML file in the browser.
    """
    logger.info(f"Starting 'read' endpoint for article ID: {article_id}")
    html_path = f"articles/{article_id}.html"
    try:
        if os.path.exists(html_path):
            logger.info(f"Opening HTML file: {html_path}")
            webbrowser.open(f"file://{os.path.abspath(html_path)}")
            return {"message": f"Opened article ID {article_id}"}
        else:
            logger.error(f"Article HTML not found: {html_path}")
            raise HTTPException(status_code=404, detail="Article not found.")
    except Exception as e:
        logger.error(f"Error in 'read' endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while reading the article.")
