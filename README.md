General LLM functionality for real scale projects.


1. First install postgress using brew: 
2. `brew install postgresql`
3. next `brew install make`
4. Then clone pgvector. Run the following in the terminal: 
   
* `/tmp % git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git`
*  `cd pgvector`
*  `make install`

Then let's create a postgres DB with PGVector extension. In the terminal run:

* `brew services start postgresql`

* `createdb vectortutorial` . vectortutorial is the name of our db.
*  Then in the terminal run: `/opt/homebrew/bin/createuser -s postgres` or `/usr/local/opt/postgresql\@14/bin/createuser -s postgres`
* And finally: `psql --host localhost --username postgres --dbname vectortutorial`

To enable my DB to support vectors I run the following inside the db terminal:

* `CREATE EXTENSION IF NOT EXISTS vector;`

Now I can create a TAble with items that can store vectors: 
