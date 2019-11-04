#!/usr/bin/env python
# coding: utf-8

# # Step 1 - Scraping the pokedex

# ## Step 1.1 Use BeautifulSoup to extract all the table rows as a list. 


#Use BeautifulSoup to extract all the table rows as a list. 
#Create an HTTP request for the page 
import requests
from bs4 import BeautifulSoup
url='https://pokemondb.net/pokedex/all'
import re

page = requests.get(url)
# Response code is returned
page



page_soup = BeautifulSoup(page.text, 'html.parser')
#page_soup.prettify()


import sys
sys.getsizeof(page)

header_raw=page_soup.find_all(name="div", class_="sortwrap")
header=[]
for i in header_raw:
    header.append(i.text)


header


body = page_soup.find_all('tbody')
print("Number of results: " + str(len(body)))
#page_list[0].find_all("tr")
content=[]
for each in page_soup.findAll(name = 'td'):
    content.append(each.contents)
rows=[content[i:i+10] for i in range(0, len(content), 10)]   


rows.append(header)
rowsfinal=[]
for row in rows:
    row=list(row)
    rowsfinal.append(row)


len(rowsfinal)


# There are 927 rows in the extracted list, including the header

# ## Step 1.2 Extract name,url, types,total points and statistics of the first pokemon as a test


bulbasaur=rowsfinal[0]
string=''.join(str(e) for e in bulbasaur)
string


#The name of the pokemon
regexName = r'/pokedex/(.*)"\stitle'
Name = re.findall(regexName, string)
print(Name)


#The url of the pokemon
regexLink = r'href="(.*)"\stitle'
Link = re.findall(regexLink, string)
print(Link)


#The types of the pokemon
regexType1 = r'(?<=/type/).*>(\w+)(?=</a>\,)'
regexType2 =  r'(?<=/type/).*>(\w+)(?=</a>\])'
Type1 = re.findall(regexType1, string)
Type2 = re.findall(regexType2, string)
Type_List=Type1+Type2
Type=[' '.join(str(t) for t in Type_List)]
print(Type)



#The total points of the pokemon
regexTotal = r'(?<=\[\')(\d{3})'
Total = re.findall(regexTotal, string)
print(Total)



#The list of ID Number, HP, Attack, Defense, Sp. Atk, Sp. Def, Speed of the pokemon
regexID = r'(\d+)</span>'
ID = re.findall(regexID, string)

regexNumeric = r'(?<=[\d+]\'\]\[\')(\d+)'
Numeric = re.findall(regexNumeric, string)

statistics=ID+Numeric
print(statistics)


# ## Step 1.3 Define a function that takes in a row of the pokedex table and returns it as a DataFrame with a single row. 


#Create a single DataFrame by appending these rows. 
def pokedex(rowsfinal):
    import pandas as pd
    statistics=[]
    Name=[]
    Link=[]
    Type=[]
    Total=[]
    regexName = r'/pokedex/(.*)"\stitle'
    regexLink = r'href="(.*)"\stitle'
    regexType1 = r'(?<=/type/).*>(\w+)(?=</a>\,)'
    regexType2 =  r'(?<=/type/).*>(\w+)(?=</a>\])'
    regexTotal = r'(?<=\[\')(\d{3}?)'
    regexID = r'(\d+)</span>'
    regexNumeric = r'(?<=[\d+]\'\]\[\')(\d+)'
    for i in range(len(rowsfinal)-1):
        string=''.join(str(e) for e in rowsfinal[i])
        Name.append(re.findall(regexName, string))
        ID = re.findall(regexID, string)
        Numeric = re.findall(regexNumeric, string)
        statistics.append(ID+Numeric)
        Link.append(re.findall(regexLink, string))
        Type1 = re.findall(regexType1, string)
        Type2 = re.findall(regexType2, string)
        Type_List=Type1+Type2
        Type.append([' '.join(str(t) for t in Type_List)])
        Total.append(re.findall(regexTotal, string)[0])
    df=pd.DataFrame((list(zip(statistics,Name,Link,Type,Total))))
    return df
        


df=pokedex(rowsfinal)
df.head()


# # Step 2 - Cleaning the Pokedex

# ## Step 2.1 Add column names to the DataFrame. Convert strings to numeric where appropriate. Make the ID number the first column in the DataFrame




df.columns = ['statistics','Name','URL','Type','Total']




df['statistics']=df['statistics'].apply(', '.join)




df['Name'] = df['Name'].str.get(0)
df['URL'] = df['URL'].str.get(0)
df['Type'] = df['Type'].str.get(0)




df.head()




new = df['statistics'].str.split(",", n = 6, expand = True) 


df['ID Number']=new[0]
df['HP']=new[1]
df['Attack']=new[2]
df['Defense']=new[3]
df['Sp.Atk']=new[4]
df['Sp.Def']=new[5]
df['Speed']=new[6]




df=df.drop('statistics', axis=1) 




df['Total']=df['Total'].astype(float)
df['HP']=df['HP'].astype(float)
df['Attack']=df['Attack'].astype(float)
df['Defense']=df['Defense'].astype(float)
df['Sp.Atk']=df['Sp.Atk'].astype(float)
df['Sp.Def']=df['Sp.Def'].astype(float)
df['Speed']=df['Speed'].astype(float)




df=df.set_index('ID Number')




df.head()


# ## Step 2.2 Create 18 dummy variables for each type of pokemon. 



import pandas as pd
dummy=df['Type'].str.get_dummies(sep=' ')




df1=pd.concat([df,dummy],axis=1)
len(df1.columns)


# ## Step 2.3 Remove duplicate values of pokemon based on the URL




df1.drop_duplicates(subset ="URL", 
                     keep = 'first', inplace = True) 
len(df1)


# ## Step 2.4 create a sample of the pokemon.



#Add a dummy variable to the DataFrame called "sample" that tags every 4th pokemon to be included in the sample
df1['sample']=(df1.index.astype('int64') % 4==0).astype('int64')




samples=df1['Name'][df1['sample']==1]


# # Step 3 - Scraping Individual Pages

# ## Step 3.1 Scrape the main image for Bulbasaur in a general way that could be applied to other pokemon pages by searching for the relevant tag and extracting the image URL. 



from IPython.display import Image



urlimage='https://pokemondb.net/pokedex/bulbasaur'
image = requests.get(urlimage)
# Response code is returned
image_soup = BeautifulSoup(image.text, 'html.parser')
#image_soup.prettify()

image_string=''.join(str(e) for e in image_soup.find_all('img'))
print(image_string)


#Display image
image= re.findall('https://.*/.*/.*.jpg', image_string)
image[0]

import requests
import IPython.display as Disp
Disp.Image(requests.get(image[0]).content)


# ## Step 3.2 Extract the location table.


url='https://pokemondb.net/pokedex/bulbasaur'
tables = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)


#table that contains the locations for Bulbasaur
tables[15]


# ## Step 3.3 Transpose the DataFrame such that each column is a video game and each row/cell is the location 

table=tables[15].T
table.columns = table.iloc[0]
table=table.drop(table.index[0])

table


# ## Step 3.4 Extract the location table and transpose it for all the pokemon in the sample 

#Set up the pokeman route names
import time
samples=df1['Name'][df1['sample']==1]
route_names=list(map(lambda x:x.lower(),samples))
del route_names[-1]


#Extract the location table and transpose it for all the pokemon in the sample 
dfs = []
for route_name in route_names:
    url='https://pokemondb.net/pokedex/'+route_name
    tables = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)
    tables=tables[-2].T
    tables.columns = tables.iloc[0]
    tables=tables.drop(tables.index[0])
    tables['Name']=route_name
    time.sleep(0.5)
    dfs.append(tables)
print("Finished")



#Get the size of the table list we just created
import sys
sys.getsizeof(dfs)


# ## Because the location table is not in the same format for every page, so we will be extracting only the information for the X and Y games


#Check if the the column 'XY' is in the DataFrame.create a new DataFrame with only the name for the pokemon and the 'XY' column. 
#Append that DataFrame to a list to concatenate with the other pokemon that have the XY location column. 
dfs1=[]
for df in dfs:
    if 'XY' in df.columns:
        dfs1.append(df[['Name','XY']])

#Create a single DataFrame that contains the name or URL of the pokemon and the XY location.
#Append all the sample pokemon and their XY locations to a single DataFrame.
XY=pd.DataFrame()
XY=XY.append(dfs1,ignore_index=True)
XY.head()


#test length of the new dataframe
len(XY)


# # Step 4 - Analysis

# ## Step 4.1 Which type has the highest and lowest average attack? Average defense? 

#Create a table that shows the average  attack and defense for each type. 
sampleDF=df1[df1['sample']==1]

dummies=list(sampleDF.columns[10:28])
dummies


pivot=[]
for dummy in dummies:
    pivot.append(sampleDF.pivot_table(values=['Attack','Defense'],columns=dummy,aggfunc='mean'))

pivot_table=pd.concat(pivot, axis=1)

pivot_table.drop(0, axis=1, inplace=True)

pivot_table.columns=dummies

#Each type should be a row. Average attack and defense should be columns.
pivot_table=pivot_table.T


MeanAttackDefense=pivot_table.plot(kind='bar', stacked=True, width=0.5,figsize=(20,10)).get_figure()
MeanAttackDefense.savefig('MeanAttackDefense.pdf')


# get the index position of max values in every column
maxValueType = pivot_table.idxmax()
 
print("Max values of columns are at row index position :")
print(maxValueType)

# get the index position of min values in every column
minValueType = pivot_table.idxmin()
 
print("Min values of columns are at row index position :")
print(minValueType)


# The Pokemon type that has the maximum average attack is Dragon, the type that has the maximum avaerage defense is steel

# The Pokemon type that has the minimum average attack is Fairy, the type that has the minimum avaerage defense is Normal

# ## Step 4.2 For the locations in pokemon X/Y, which location has the highest average total point score?

#Join the pokedex data to the  location DataFrame created in Step 3.4. 
merged=pd.merge(XY, df1, on='Name', how='inner')
merged.head()

XY_table=merged.set_index('XY').groupby(by='XY').mean()['Total']

#XY_table.plot.bar(rot=270)
MaxAverageTotal_in_XY=XY_table.plot(kind='bar', stacked=True, width=0.5,figsize=(20,80)).get_figure()
MaxAverageTotal_in_XY.savefig('MaxAverageTotal_in_XY.pdf')


maxValuelocation = XY_table.idxmax()
 
print("Location has the highest average total point score :")
print(maxValuelocation)


XY_table[maxValuelocation]


# Location has the highest average total point score is Sea Spirit's Den, Roaming Kalos; the highest average total points is 580
