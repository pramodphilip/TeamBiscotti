 you will scrape the following information from http://quotes.toscrape.com/

- quote text
- tags
- Author name
- Author Details
  - born
  - description

# import splinter,beautifulsoup, webdriver, pandas, pymongo
# create path and open browser window
# establish url
# visit site and grab page html
# create soup object
# create the initial list to store the data, creating a small dictionary for each quote box inside a larger dictionary
	quotes_dictionary=[]
# create a for loop to cycle through each quote box
	# create click function for the about link to access Author Details and grab the specific html tag for : author name, born, description
        #store that data as the following variables: author_name, born, decription
    # create back function to get back to main quotes page into to pull the next author information
    # quote text, tags - these are on the same page, grab the specific html tag for these
        #storing data into the following variable: quote_text, tags
        # tags: findall on the <a> tag where the class=tag -do .text to just pull the text( if the .text doesn't work use get_text)
	#append to the mini dictionary for each quote box to the full Quotes_Dictionary
        #looks kinda quotes_dictionary=[{"author_name": author_name, "born": born, "description": description,
                                            "quote_text": quote_text}, "tags": [tags]}]
	# create a while loop to click to the next page
		# create click function for the next button
	
--------------------------------------------------------------------------------------------------
## Store the collected information into MongoDB( either local mongoDB or Atlas mongoDB)
    # create a database and collection
    # create a connection
    # create a client
    # define the database
    # define the collections (db.collection name)
    # insert_many using data from Quotes_Dictionary; if that does not work, then try loop through Quotes_Dictionary and insert_one
# switched to pandas: 
    # use .dataframe to covert the quotes_dictionary into a dataframe
    # .replace to replace "," in the born variable with ""
    #.split the born variable on spaces
    # drop index[3]
	# set index - this will be used as the quote_id
    # create a loop to loop through the born column
        # set variables: birth_month, birth_day, birth_year, birth_city, birth_country
        # set each variable to equal the corresponding born index
            #birth_month= born[0], birth_day = born[1], birth_year=born[2] birth_city=born[3], birth_country=born[4]
        #create new column and add the new variables to the column
            df["Birth_Month"]=birth_month
            df["Birth_Day"]=birth_day 
            df["Birth_Year"]= birth_year
            df["Birth_City"]= birth_city
            df["Birth_Country"]= birth_country

    #drop the born column
    #break the large dataframe into 3 smaller dataframes that will match up to the postgres tables
    #drop duplicates on the author table
   *# To be solved: Tags are in a list for each row, how do we pull each tag out so that we can have a full list to count with**
        

----------------------------------------------------------------------------------------

## Design the following three tables, Extract the data from mongoDB and load it into postgres
# create tables in PGadmin
	#use the quick db for the schema

	- one table for quotes, this table can have the quote and author relationship (id, author_name, text )
	- one table for author information (name, born , description)
	- one table to store quote and tag relation (quote_id , tag)
# connection string
# establish the engine
# engine.tablesname - to confirm that we have the schemas established
# to_sql for all three tables

---------------------------------------------------------------------------------------------
## Create a FLASK application with the following endpoints

# import flask, jsonify, sqlalchelmy, pandas
	from sqlalchemy.ext.automap import automap_base
	from sqlalchemy.orm import Session
	from sqlalchemy import create_engine, func
	import datetime as dt
# app=Flask(__name__)
# @app.route("/") -homepage
#f???Available Routes:<br/>???
        f???/api/v1.0/quotes<br/>???
        f???/api/v1.0/authors<br/>???
        f???/api/v1.0/authors/<author_name><br/>???
        f???/api/v1.0/tags<br/>???
        f???/api/v1.0/tags/<tag>???
f???/api/v1.0/top10tags???
# build function
# end the flask---
if __name__ == '__main__':
    app.run(debug=True)

# create the homepage with the links:
	1. This route will dispaly all the available quotes in the database
		- select all from the quotes tables
		- select count * from the quotes tables 
	2. This route will display the information about all the authors available in the database
		-select count * from authors table
		-select all from authors table
	3.This route will display the information about a particular author
		- Select all from author where author_name=Albert 
		- select count quote_id from quotes table where author_name=Albert
		-select all from tags, quotes tables where tags.quote_id=quotes.quote_id
	4. this route will dispaly all the available tags in the database - TBD until we figure out how to break out the tags list
	5. this route will display the information about a particual tag only -TBD until we figure out how to break out the tags list
	6. This route will display the information about top10 tags -TBD until we figure out how to break out the tags list