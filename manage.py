from os import environ
from os.path import dirname, join

from dotenv import load_dotenv

from app import app

load_dotenv(join(dirname(__file__), ".env"))


if __name__ == "__main__":
    app.run(
        host=environ.get("HOST"),
        port=environ.get("PORT"),
        debug=eval(environ.get("DEBUG")),
    )
