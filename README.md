# pg-vector-demo
install PG Vector:

Ensure C++ support in Visual Studio is installed, and run:

call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
Note: The exact path will vary depending on your Visual Studio version and edition

Then use nmake to build:

set "PGROOT=C:\Program Files\PostgreSQL\16"
cd %TEMP%
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install


via  Docker 
docker run --name pgvector-container -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16


Connect SQL 
DB_NAME = "langchain"
DB_USERNAME = "langchain"
DB_PASSWORD = "langchain"
DB_PORT = "6024"
DB_HOST = "localhost"

install extension:
CREATE EXTENSION IF NOT EXISTS vector;



check if pgVector is installed:
SELECT * FROM pg_extension;
