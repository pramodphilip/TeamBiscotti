# import dependancies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
from flask import Flask, jsonify, render_template
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

    # Quesry postgres tables to get data on all quotes
    all_quotes = engine.execute(f"\
                                SELECT quote.quote_text, quote.author_name,\
                                    STRING_AGG (tags.tags_list,', ' \
                                    ORDER BY quote.author_name) \
                                FROM quote INNER JOIN tags USING (quote_id) \
                                GROUP BY quote.quote_text, quote.author_name").fetchall()

    # Create list of dicts for easy use with json
    quote_list = []
    for i in range(0,len(all_quotes)):
        quote_dict = {}
        quote_dict["quote"] = all_quotes[i][0]
        quote_dict['auth'] = all_quotes[i][1]
        quote_dict['tags'] = all_quotes[i][2]
        quote_list.append(quote_dict)

    # add total number of Quotes and the quote_list to one dict for easier return statement
    quote_json = [f"Total Number of Quotes: {tot_num_quotes}", quote_list]

    return jsonify(Quotes=quote_list, Number_of_Qoutes=tot_num_quotes)

    # close session    
    session.close()
    
#############################################################################

# @app.route("/api/v1.0/author")
# def author():

    # start new session
    #session = Session(bind=engine)

    # run grouping query for all the author info
    #all_author = engine.execute("SELECT quote.author_name, author.description, author.birth_date, author.birth_place, COUNT(quote.quote_text), quote.quote_text, STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags FROM quote INNER JOIN tags USING (quote_id) INNER JOIN author USING (author_name) GROUP BY quote.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text").fetchall()

    #return(all_author)

    # close session          
    #session.close()

#############################################################################

@app.route("/api/v1.0/author/<author_name>")
def one_author(author_name):
    # start new session
    session = Session(bind=engine)

    # run grouping query for all the author info
    one_author = engine.execute(f"\
        SELECT quote.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text, \
            (SELECT COUNT(quote_text) \
            FROM quote \
            WHERE author_name = '{author_name}'), \
        STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags \
        FROM quote \
        INNER JOIN tags USING (quote_id) \
        INNER JOIN author USING (author_name) \
        WHERE author_name = '{author_name}' \
        GROUP BY quote.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text").fetchall()
    one_author

    # Create a dict with the static values     
    one_auth_dict = {"a_name" : one_author[0][0],
                    "b_description" : one_author[0][1], 
                    "c_birth_date" : one_author[0][2], 
                    "d_birth_place" : one_author[0][3], 
                    "e_num_quotes" : one_author[0][5],
                    }
    # Initialize a list with for the dict     
    quote_tag_list = []

    # for loop to get the related tags and quote info into sing dict   
    for i in range(0,len(one_author)):
        quote_tag_dict={}
        quote_tag_dict["quote"] = one_author[i][4]
        quote_tag_dict["tags"] = one_author[i][6]
        quote_tag_list.append(quote_tag_dict)

    # add list with little dicts to big dict   
    one_auth_dict['f_quote_tags']=quote_tag_list

    return jsonify(one_auth_dict)
            
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