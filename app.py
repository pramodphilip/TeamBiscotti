# import dependancies
import numpy as np
import sqlalchemy
import json
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
from flask import Flask, jsonify, render_template
from operator import itemgetter
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
@app.route("/")

def welcome():
    return render_template('index.html')
    # """List all available api routes."""
    # return (
    #     f'Available Routes:<br/>'
    #     f'/api/v1.0/quote<br/>'
    #     f'/api/v1.0/author<br/>'
    #     f'/api/v1.0/author/<author_name><br/>'
    #     f'/api/v1.0/tags<br/>'
    #     f'/api/v1.0/tags/<tag>'
    #     f'/api/v1.0/top10tags'
    # )
###########################################################################

#	1. This route will dispaly all the available quotes in the database

@app.route("/api/v1.0/quote")
def quote():
    # start new session
    session = Session(bind=engine)

    # Total # of quotes
    tot_num_quotes = session.query(Quotes).group_by(Quotes.quote_id).count() #100

    # Queries postgres tables to get data on all quotes
    all_quotes = engine.execute(f"\
                                SELECT quote.quote_text, quote.author_name,\
                                    STRING_AGG (tags.tags_list,', ' \
                                    ORDER BY quote.author_name) \
                                FROM quote INNER JOIN tags USING (quote_id) \
                                GROUP BY quote.quote_text, quote.author_name").fetchall()
    
    # close session    
    session.close()

    # Create list of dicts for easy use with json
    quote_list = []
    for i in range(0,len(all_quotes)):
        quote_dict = {}
        quote_dict["quote"] = all_quotes[i][0].replace('\u201d','').replace('\u201c','')
        quote_dict['auth'] = all_quotes[i][1]
        quote_dict['tags'] = all_quotes[i][2]
        quote_list.append(quote_dict)

    # add total number of Quotes and the quote_list to one dict for easier return statement
    quote_json = [f"Total Number of Quotes: {tot_num_quotes}", quote_list]

    return jsonify(Quotes=quote_list, Number_of_Quotes=tot_num_quotes)
    
#############################################################################

# 2. This route will display the information about all the authors available in the database

@app.route("/api/v1.0/author")
def author():
    session = Session(bind=engine) 

    # Total # of authors
    tot_num_authors = session.query(Author).group_by(Author.author_id).count() #100

    # run grouping query for all the author info
    all_author = engine.execute(f"\
        SELECT quote.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text, \
            (SELECT COUNT(quote_text) \
            FROM quote \
            WHERE quote.author_name = author.author_name GROUP BY quote.author_name, author.author_name), \
        STRING_AGG (tags.tags_list,', ' ORDER BY quote.author_name) tags \
        FROM quote \
        INNER JOIN tags \
        USING (quote_id) \
        INNER JOIN author \
        USING (author_name) \
        GROUP BY quote.author_name, author.author_name, author.description, author.birth_date, author.birth_place, quote.quote_text").fetchall()

    session.close()

    # initialize empty list to hold all dicts  
    all_author_list = []

    # for loop layer 1 to gather each author info
    for a in range(0,len(all_author)):
        # check is current auth = previous? no then gather all data
        if all_author[a][0] != all_author[a-1][0]:
            # initialize empty dict to hold only auth info
            all_author_dict = {}
            all_author_dict["author_name"] = all_author[a][0]
            all_author_dict["description"] = all_author[a][1].replace('\u2013','').replace('\u00e9','')
            all_author_dict["birth_date"] = all_author[a][2] 
            all_author_dict["birth_place"] = all_author[a][3] 
            all_author_dict["num_quotes"] = all_author[a][5]

            # initialize empty list to hold quotes and tags data
            quote_tag_list = []

            # for loop to gather only quotes and tags data
            for q in range(0,len(all_author[a])):
                # initialize empty dict for quotes and tags data 
                quote_tag_dict={}
                quote_tag_dict["quote_text"] = all_author[q][4].replace('\u201d','').replace('\u201c','')
                quote_tag_dict["tags"] = all_author[q][6]
                # append quotes and tags data to list outside of loop layer 2 
                quote_tag_list.append(quote_tag_dict)

            # add all the quote tags from layer 2 into dict
            all_author_dict["quotes"] = quote_tag_list

            # append auth info dict to list outside of all the loops
            all_author_list.append(all_author_dict)  

    true_author_dict = {'total':tot_num_authors,'detail':all_author_list}      
    
    return jsonify(true_author_dict)

#############################################################################

# 3.This route will display the information about a particular author

@app.route("/api/v1.0/author/<author_name>")
def one_author(author_name):

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
    
    # add if statement for returning no value message
    if len(one_author)==0:
        one_auth_dict = {"name" : author_name,
                        "description" : 'does not exist', 
                        }
    # if tag value found then return actual result
    else:                   

        # Create a dict with the static values     
        one_auth_dict = {"author_name" : one_author[0][0],
                        "description" : one_author[0][1], 
                        "birth_date" : one_author[0][2], 
                        "birth_place" : one_author[0][3], 
                        "num_quotes" : one_author[0][5],
                        }
        # Initialize a list with for the dict     
        quote_tag_list = []

        # for loop to get the related tags and quote info into sing dict   
        for i in range(0,len(one_author)):
            quote_tag_dict={}
            quote_tag_dict["text"] = one_author[i][4]
            quote_tag_dict["tags"] = one_author[i][6]
            quote_tag_list.append(quote_tag_dict)

        # add list with little dicts to big dict   
        one_auth_dict['quotes']=quote_tag_list

    return jsonify(one_auth_dict)

#############################################################################

#	4. this route will dispaly all the available tags in the database

@app.route("/api/v1.0/tags")
def tags():

    # start new session
    session = Session(bind=engine)

    # Total # of quotes
    tot_num_tags = session.query(Tags).group_by(Tags).count() #232

    # run grouping query for all the author info
    all_tags = engine.execute(f"\
        SELECT tags.tags_list, quote.quote_text \
        FROM tags \
        INNER JOIN quote \
        USING (quote_id) \
        GROUP BY tags.tags_list, quote.quote_id \
        ORDER BY tags_list  ASC").fetchall()

    all_tag_lists = engine.execute(f"select quote.quote_text, \
            STRING_AGG (tags.tags_list, ', '  ORDER BY quote.author_name) tags \
            from quote, tags \
            Group by quote.author_name, quote.quote_text")
    # close session          
    session.close()
    
    # create a df to isolate tags & quote info
    df = pd.DataFrame(all_tags, columns=['tag', 'quotes'])

    # create a second df to isolate quote info and list of tags for each quote
    df_2 = pd.DataFrame(all_tag_lists, columns=['quotes','tag_lists'])

    # isolate only the unique tags
    tags = df.tag.unique()

    # create list to hold all the dicts
    all_tag_list = []

    # for loop to iterate the unique tags list and return the df values for those 
    for tag in tags:
        quotes = list(df[df['tag'] == tag]['quotes'])
        #quote_tags_list = []
        #for quote in quotes:
        #    tag_list = df_2[df['quotes'] == quote]['tag_lists']
        #    quote_tlist_dict = {'text':quote,'tags':tag_list}
        #    quote_tags_list.append(quote_tlist_dict)
        tag_dict = {'name': tag, 'number_of_quotes': len(quotes), 'quotes': quotes}
        all_tag_list.append(tag_dict)
            
    true_tags_dict = {'count':tot_num_tags,'details':all_tag_list}

    return jsonify(true_tags_dict)

#############################################################################

#	5. this route will display the information about a particual tag only

@app.route("/api/v1.0/tags/<tag>")
def one_tag(tag):

    # run grouping query for all the author info
    one_tag = engine.execute(f"\
        SELECT tags.tags_list, quote.quote_text, \
            (SELECT COUNT(quote_id) \
            FROM tags \
            WHERE tags_list = '{tag}') \
        FROM tags \
        INNER JOIN quote \
        USING (quote_id) \
        WHERE tags_list = '{tag}' \
        GROUP BY tags.tags_list, quote.quote_id \
        ORDER BY tags_list  ASC").fetchall()

    # add if statement for returning no value message
    if len(one_tag)==0:
        one_tag_dict = {'tag' : tag , 'value' : 'Does not exist'}

    # if tag value found then return result
    else:
        # initialize empty list to hold all dicts  
        one_tag_list = []

        # initialize dict for one tag info
        one_tag_dict = {'name_of_tag' : one_tag[0][0], 'count' : one_tag[0][2]}

        # for loop to get all quote info
        for q in range(len(one_tag)):
            quote_dict={}
            quote_dict["quote"] = one_tag[q][1]
            one_tag_list.append(quote_dict)
            
        # add one tag list to the bigger dict of all quotes for single tag    
        one_tag_dict['quotes']=one_tag_list    

    return jsonify(one_tag_dict)

#############################################################################

#	6. This route will display the information about top10 tags

@app.route("/api/v1.0/top10tags")
def top_ten_tag():

    # run grouping query for all the author info
    all_tags = engine.execute(f"\
    SELECT tags.tags_list, quote.quote_text \
    FROM tags \
    INNER JOIN quote \
    USING (quote_id) \
    GROUP BY tags.tags_list, quote.quote_id \
    ORDER BY tags_list  ASC").fetchall()

    df = pd.DataFrame(all_tags, columns=['tag', 'quotes'])

    tags = df.tag.unique()

    all_tag_list = []
    for tag in tags:
        quotes = list(df[df['tag'] == tag]['quotes'])
        tag_dict = {'name_of_tag': tag, 'quote_count': len(quotes)}
        all_tag_list.append(tag_dict)

        
    top_10 = sorted(all_tag_list,key=itemgetter('quote_count'), reverse=True)
    top_10 = top_10[0:10]

    return jsonify(top_10)
#############################################################################

engine.dispose()

if __name__ == '__main__':
    app.run(debug=True)