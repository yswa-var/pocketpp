import logging
import click
import os
from sqlalchemy.orm import Session
from models import Article, Category, Session
from scraper import scrape_and_summarize
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import webbrowser

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

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


@click.group()
def cli():
    pass


@cli.command()
@click.argument("url")
@click.option("--category", default="General", help="Category for the article (default: General)")
def add(url, category):
    logger.info(
        f"Starting 'add' command with URL: {url}, Category: {category}")
    session = Session()
    try:
        logger.info("Scraping and summarizing the URL")
        data = scrape_and_summarize(url)
        logger.info(f"Scraped data: Title={data['title']}, URL={data['url']}")

        logger.info(f"Looking for category: {category}")
        cat = session.query(Category).filter_by(name=category).first()
        if not cat:
            logger.info(f"Category '{category}' not found. Creating it.")
            cat = Category(name=category)
            session.add(cat)
            session.commit()
            logger.info(f"Created category: {category}")
        category_id = cat.id
        logger.info(f"Using category ID: {category_id}")

        article = Article(
            url=url,
            title=data["title"],
            content=data["content"],
            summary=data["summary"],
            image_url=data.get("image_url"),
            category_id=category_id
        )
        session.add(article)
        session.commit()
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

        click.echo(
            f"Article saved successfully! ID: {article.id}, Title: {data['title']}, Category: {category}")
    except Exception as e:
        logger.error(f"Error in 'add' command: {e}", exc_info=True)
        session.rollback()
        click.echo("An error occurred while adding the article.")
    finally:
        logger.info("Closing session")
        session.close()


@cli.command()
def list():
    logger.info("Starting 'list' command")
    session = Session()
    try:
        articles = session.query(Article).all()
        logger.info(f"Found {len(articles)} articles")
        if not articles:
            click.echo("No articles found.")
            logger.info("No articles to display")
        for a in articles:
            category_name = a.category.name if a.category else "Uncategorized"
            click.echo(
                f"ID: {a.id} | {a.title}\nCategory: {category_name}\nSummary: {a.summary}\n---")
            logger.info(
                f"Displayed article ID: {a.id}, Title: {a.title}, Category: {category_name}")
    except Exception as e:
        logger.error(f"Error in 'list' command: {e}", exc_info=True)
        click.echo("An error occurred while listing articles.")
    finally:
        logger.info("Closing session")
        session.close()


@cli.command()
@click.argument("id", type=int)
def read(id):
    logger.info(f"Starting 'read' command for article ID: {id}")
    html_path = f"articles/{id}.html"
    try:
        if os.path.exists(html_path):
            logger.info(f"Opening HTML file: {html_path}")
            webbrowser.open(f"file://{os.path.abspath(html_path)}")
            click.echo(f"Opened article ID {id}")
        else:
            logger.error(f"Article HTML not found: {html_path}")
            click.echo("Article not found.")
    except Exception as e:
        logger.error(f"Error in 'read' command: {e}", exc_info=True)
        click.echo("An error occurred while reading the article.")


if __name__ == "__main__":
    cli()
