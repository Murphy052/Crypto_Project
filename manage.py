import typer

app = typer.Typer()


@app.command()
def run():
    import uvicorn

    uvicorn.run("src.main:app", port=8000, reload=True)


@app.command()
def migrate():
    from src.db import db
    with open("src/db/migrations/init.sql") as f:
        query: str = f.read()
        try:
            queries = query.split(";")
            for query in queries:
                db.conn.cursor().execute(query)
            db.conn.commit()
        except Exception as e:
            print(e)

    db.close()


if __name__ == '__main__':
    app()
