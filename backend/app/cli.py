import typer
from app.db.session import SessionLocal
from app.db.init_db import init_db

app = typer.Typer()

@app.command()
def initdb():
    """Initialize the database with required tables and default data."""
    try:
        db = SessionLocal()
        init_db(db)
        typer.echo("Database initialized successfully!")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    finally:
        db.close()

if __name__ == "__main__":
    app() 