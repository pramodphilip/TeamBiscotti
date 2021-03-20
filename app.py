# import dependancies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
from flask import Flask, jsonify
# postgres pasword
from config import postgres_password as password

# create engine to postgres
engine = create_engine(f'postgresql://postgres:{password}@localhost:5432/quotes_db')

# use engine to connect to existing tables/db
Database = automap_base( )
Database.prepare(engine, reflect=True)

# View all of the classes/tables that automap found
Database.classes.keys( )

# Save references to each table (capital because they are considered classes) 
Tags = Database.classes.tags
Quotes = Database.classes.quote
Author = Database.classes.author

# Create our session (link) from Python to the DB
session = Session(bind=engine)
#inspector = inspect(engine)

# Use  get_columns in order write queries later
#inspector.get_columns('table_name')

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# create the homepage with the links:
#	1. This route will dispaly all the available quotes in the database
#		- select all from the quotes tables
#		- select count * from the quotes tables 
@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/quote<br/>'
        f'/api/v1.0/author<br/>'
        f'/api/v1.0/author/<author_name><br/>'
        f'/api/v1.0/tags<br/>'
        f'/api/v1.0/tags/<tag>'
        f'/api/v1.0/top10tags'
    )
###########################################################################

@app.route("/api/v1.0/quote")
def quote():
    # start new session
    session = Session(bind=engine)

    # Total # of quotes
    tot_num_quotes = session.query(Quotes).group_by(Quotes.quote_id).count() #100

    # Getting all quotes, author, tags for quote
    all_quotes = engine.execute("SELECT quote.quote_text, quote.author_name, STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags FROM quote INNER JOIN tags USING (quote_id) GROUP BY quote.quote_text, quote.author_name").fetchall()

    return( f'Total number of quotes: {tot_num_quotes}',
            f'QUOTES: {all_quotes}'
        )

    # close session    
    session.close()
    
#############################################################################

@app.route("/api/v1.0/author")
def author():

# start new session
session = Session(bind=engine)

# run grouping query for all the author info
all_author = engine.execute("SELECT quote.author_name, author.description, author.birth_date, author.birth_place, COUNT(quote.quote_text), quote.quote_text, STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags FROM quote INNER JOIN tags USING (quote_id) INNER JOIN author USING (author_name) GROUP BY quote.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text").fetchall()

return(all_author)

# close session          
session.close()

#############################################################################

@app.route("/api/v1.0/author/<author_name>")
def one_author():
# start new session
session = Session(bind=engine)

# run grouping query for all the author info
all_author = engine.execute("SELECT quote.author_name, author.description, author.birth_date, author.birth_place, (SELECT COUNT(quote_text) FROM quote WHERE quote.author_name = (SELECT author_name FROM author)), STRING_AGG (quote.quote_text,', '), STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags FROM quote INNER JOIN tags USING (quote_id) INNER JOIN author USING (author_name) GROUP BY quote.author_name, author.description, author.birth_date, author.birth_place").fetchall()

print(all_author)
           
session.close()

#############################################################################
#@app.route("/api/v1.0/tags")
#def tags():




#############################################################################
#@app.route("/api/v1.0/tags/<tag>")
#def one_tag():





#############################################################################
#@app.route("/api/v1.0/top10tags")
#def top_ten_tag():

engine.dispose
if __name__ == '__main__':
    app.run(debug=True)