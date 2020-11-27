from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('div',attrs={'class':'lister-list'})
lister=table.find_all('div',attrs={'class':'lister-item-content'})
temp = [] #initiating a tuple

#insert the scrapping process here
for i in range(0, len(lister)):
    row = lister[i]
    
    #get title
    title = row.find_all('a')[0].text.strip()

    #get imdb rating
    imdb_rating = row.find_all('strong')[0].text.strip()
    
    #get metacritic score
    if row.find('span',attrs={'class':'metascore mixed'}) == None:
        metascore = 0
    else:
        metascore = row.find('span',attrs={'class':'metascore mixed'}).text.strip()

    #get votes
    votes = row.find_all('span',attrs={'name':'nv'})[0].text.strip().replace(',','')
    
#     print(title,imdb_rating,metascore,votes)
    
    temp.append((title,imdb_rating,metascore,votes))

temp

#change into dataframe
df = pd.DataFrame(temp, columns = ('title','imdb_rating','metascore','votes'))

#insert data wrangling here
df['imdb_rating']=df['imdb_rating'].astype('float64')
df[['metascore','votes']]=df[['metascore','votes']].astype('int64')
top7popular=df.set_index('title').sort_values('votes',ascending=False).head(7)
top7popular_votes=top7popular['votes']
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = top7popular_votes.max()

	# generate plot
	ax = top7popular_votes.plot.barh(figsize = (20,9))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
