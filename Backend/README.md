# Fresh machine or deploy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Add all the installed packages to requirements.txt
pip freeze > requirements.txt

export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"

#DATABASE
docker run --name shrinkr-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=shrinkr -p 5432:5432 -d postgres