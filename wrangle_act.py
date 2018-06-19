
# coding: utf-8

# In[1]:


#mentioning all the libraries
import numpy as np
import pandas as pd
import requests
import tweepy
import json
import matplotlib.pyplot as plt
import warnings


# ## GATHER

# In[2]:


#reading and loading a csv file 
twitter=pd.read_csv('twitter_archive_enhanced.csv')


# In[3]:


#loading a tsv file 
url="https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv"
response = requests.get(url)

with open('image_predictions.tsv', 'wb') as file:
    file.write(response.content)

image = pd.read_csv('image_predictions.tsv', sep='\t')


# In[4]:


#creating API object. I have removed original values of consumer_key, consumer_secret,OAUTH_TOKEN,OAUTH_TOKEN_SECRET
consumer_key = 'my consumer key'
consumer_secret = 'my consumer secret'
OAUTH_TOKEN = 'my oauth token'
OAUTH_TOKEN_SECRET = 'my token secret'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)


# In[5]:


#writing json data to tweet_json.txt file
with open('tweet_json.txt', 'a', encoding='utf8') as file:
    for tweet_id in twitter['tweet_id']:
        try:
            tweet = api.get_status(tweet_id, tweet_mode='extended')
            json.dump(tweet._json, file)
            file.write('\n')
        except:
            continue


# In[6]:


#append each data to tweet_list line by line
tweet_list = []

file = open('tweet_json.txt', "r")

for line in file:
    try:
        data = json.loads(line)
        tweet_list.append(data)
    except:
        continue
        
file.close()


# In[7]:


#creating dataframe for tweet_data
tweet_data = pd.DataFrame()
tweet_data['id'] = list(map(lambda tweet: tweet['id'], tweet_list))
tweet_data['retweet_count'] = list(map(lambda tweet: tweet['retweet_count'], tweet_list))
tweet_data['favorite_count'] = list(map(lambda tweet: tweet['favorite_count'], tweet_list))



# ** We have three dataframes named as :twitter , tweet_data , image **

# ##  ASSESS 

# In[8]:


# first ten entries of twitter dataframe
twitter.head(10)


# In[9]:


# first 10 entries of image dataframe
image.head(10)


# In[10]:


# first 10 entries of tweet_data dataframe
tweet_data.head(10)


# In[11]:


twitter.info()


# In[12]:


image.info()


# In[13]:


tweet_data.info()


# In[14]:


# checking for null values in twitter dataframe for each column
twitter.isnull().sum()


# In[15]:


# checking for null values in image dataframe for each column
image.isnull().sum()


# In[16]:


#checking for null values in tweet_data dataframe for each column
tweet_data.isnull().sum()


# In[17]:


# inspecting the name column of twitter dataframe
twitter['name'].value_counts()


# In[18]:


#checking those texts which contain any decimal rating as rating_numerator values can be wrong for those particular rows
twitter[twitter['text'].str.contains(r"(\d+\.\d*\/\d+)")]


# In[19]:


#Checking if any dog has 0 as its rating_denominator value as that value is wrong
twitter[twitter['rating_denominator']==0]


# In[20]:


#checking for those rows in which rating denominator is not having value 10
twitter[twitter['rating_denominator']!=10]


# In[21]:


image.head(3)


# In[22]:


#checking for duplicate values in tweet_data dataframe
tweet_data.duplicated().sum()


# In[23]:


#checking for duplicate values in twitter dataframe
twitter.duplicated().sum()


# In[24]:


#checking for duplicate values in image dataframe
image.duplicated().sum()


# ** QUALITY ISSUES WITH DATAFRAMES **
# 
#  -> data type conflicts (time_stamp, in_reply_to_user_id, in_reply_to_status_id,tweet_id , etc...)
#  
#  
#  
#  
#  
#  
# 
# 
# 
#  
#  

# -> duplicacy of records( In tweet_data dataframe)

# -> dataframe consists of retweets

# -> Incorrect dog names in twitter dataframe

# -> tweets with no images are present

# -> record containing wrong value of rating_denominator as 0

# -> some columns such as retweeted_status_id and retweeted_status_user_id are not required 

# -> the rating_numerator value of records having decimal rating in their text is not written properly
# 

# ** TIDINESS ISSUES **

# -> The distinct dog type columns ( can be resolved by combining dog type columns into one column)

# -> merging all the three dataframes together to get a new dataframe 

# # CLEAN

# In[25]:


# creating copies of dataframes for cleaning purpose
twitter_clean=twitter.copy()
image_clean=image.copy()
tweet_data_clean=tweet_data.copy()



# ** DEFINE **

# Removing retweets from twitter_clean dataframe

# ** CODE **

# In[26]:


# if retweet status id is null then there is no retweet
twitter_clean=twitter_clean[twitter_clean['retweeted_status_id'].isnull()]


# In[27]:


twitter_clean


# ** TEST **

# In[28]:


# Through info we can observe that there is no non null value present for retweeted_status_id
twitter_clean.info()


# **  DEFINE  **

# removing columns related to retweets from twitter_clean dataframe

# ** CODE **

# In[29]:


columns=['retweeted_status_id','retweeted_status_user_id','retweeted_status_timestamp']
twitter_clean.drop(columns,inplace=True,axis=1)


# ** TEST **

# In[30]:


# to check if the columns related to retweets are deleted
twitter_clean.info()


# ** DEFINE **

# Removing the invalid names of dogs (We observed while assessing that the dog names having all lowercase letters are wrong names)

# ** CODE **

# In[31]:


# replacing invalid names with None 
for name in twitter_clean['name']:
    if name.islower()==True:
        twitter_clean.replace(name,'None',inplace=True)


# ** TEST **

# In[32]:


# to check whether invalid dog names are removed and replaced with None 
twitter_clean['name'].value_counts()


# ** DEFINE **

# to replace invalid ratings with the decimal rating present in the text (if present)

# ** CODE **

# In[33]:


#column width is adjusted to make the full text visible
pd.set_option('display.max_colwidth', -1)
twitter_clean[twitter_clean['text'].str.contains(r"(\d+\.\d*\/\d+)")]



# In[34]:


# replacing the invalid ratings with the correct decimal ratings
twitter_clean.loc[twitter_clean['tweet_id']==883482846933004288,"rating_numerator"]=13.5
twitter_clean.loc[twitter_clean['tweet_id']==786709082849828864,"rating_numerator"]=9.75
twitter_clean.loc[twitter_clean['tweet_id']==778027034220126208,"rating_numerator"]=11.27
twitter_clean.loc[twitter_clean['tweet_id']==681340665377193984,"rating_numerator"]=9.5
twitter_clean.loc[twitter_clean['tweet_id']==680494726643068929,"rating_numerator"]=11.26


# ** TEST **

# In[35]:


# checking whether updation of rating_denominator and rating_numerator is done 
twitter_clean[twitter_clean['text'].str.contains(r"(\d+\.\d*\/\d+)")]


# ** DEFINE **

# correcting the rating_numerator and rating_denominator values where the value of rating_denominator is 0

# ** CODE **

# In[36]:


#checking for the rows having rating_denominator = 0
twitter_clean[twitter_clean['rating_denominator']==0]


# In[37]:


#inspecting the text to check whether rating is available or not
twitter_clean.loc[twitter_clean['rating_denominator']==0].text


# In[38]:


# changing the invalid rating values to valid values
twitter_clean.loc[twitter_clean['tweet_id']==835246439529840640,"rating_numerator"]=13
twitter_clean.loc[twitter_clean['tweet_id']==835246439529840640,"rating_denominator"]=10


# ** TEST**

# In[39]:


# checking whether changes are performed for the particular tweet_id 
twitter_clean.loc[twitter_clean['tweet_id']==835246439529840640]


# ** DEFINE **

# Merging the columns of dog type into one column

# ** CODE **

# In[40]:


#defining a new column dog_type and removing the columns which are not required
twitter_clean['dog_type']=twitter_clean.text.str.extract('(puppo|pupper|floofer|doggo)',expand=True)
columns=['doggo','floofer','pupper','puppo']
twitter_clean=twitter_clean.drop(columns,axis=1)


# ** TEST **

# In[41]:


#to check whether the columns are merged into one column dog_type
twitter_clean.info()


# ** DEFINE **

# changing data types of columns of twitter_clean dataframe

# **CODE **

# In[42]:


#changing data type of rating_numerator and rating_denominator to float
twitter_clean['rating_numerator']=twitter_clean.rating_numerator.astype('float')
twitter_clean['rating_denominator']=twitter_clean.rating_denominator.astype('float')


# In[43]:


#changing data type of dog_type to category data type
#changing data type of timestamp to datetime data type
twitter_clean['dog_type']=twitter_clean['dog_type'].astype('category')
twitter_clean['timestamp']=pd.to_datetime(twitter_clean['timestamp'])


# In[44]:


#changing datatype of mentioned columns to string
twitter_clean['in_reply_to_status_id'] = twitter_clean['in_reply_to_status_id'].astype('str')
twitter_clean['in_reply_to_user_id'] = twitter_clean['in_reply_to_user_id'].astype('str')
twitter_clean['tweet_id'] = twitter_clean['tweet_id'].astype('str')



# **TEST**

# In[45]:


twitter_clean.info()


# ** DEFINE **

# changing the rating_numerator and rating_denominator where rating denominator is not equal to 10

# **CODE**

# In[46]:


# checking for those records where rating_denominator is not equal to 10
twitter_clean[twitter_clean['rating_denominator']!=10]


# In[47]:


#changing incorrect values by inspecting the text in which the correct rating is available
twitter_clean.loc[twitter_clean['tweet_id']=='722974582966214656',"rating_numerator"]=13
twitter_clean.loc[twitter_clean['tweet_id']=='722974582966214656',"rating_denominator"]=10


# In[48]:


#one more record found whose rating was available in text
twitter_clean.loc[twitter_clean['tweet_id']=='716439118184652801',"rating_numerator"]=11
twitter_clean.loc[twitter_clean['tweet_id']=='716439118184652801',"rating_denominator"]=10


# we observed that when ratings are done for group of dogs then rating_denominator is of other value than 10. We can ignore those records

# **TEST**

# In[49]:


#checking if values of rating_numerator and rating_denominator is changed
twitter_clean.loc[twitter_clean['tweet_id']=='716439118184652801']


# In[50]:


#checking that value of rating_numerator and rating_denominator is changed  for another tweet_id also
twitter_clean.loc[twitter_clean['tweet_id']=='722974582966214656']


# ** DEFINE **

# removing rows that does not contain expanded_urls for images

# **code**

# In[51]:


#removing rows not containing images
twitter_clean = twitter_clean.dropna(subset=['expanded_urls'])


# **TEST**

# In[52]:


#to check whether records not having image urls are removed from the dataframe
twitter_clean.info()


# ** DEFINE **

# removing duplicated records from tweet_data_clean dataframe

# **CODE**

# In[53]:


#checking duplicated records
tweet_data_clean.duplicated().sum()


# In[54]:


#removing duplicated records
tweet_data_clean=tweet_data_clean.drop_duplicates()


# **TEST**

# In[55]:


#checking whether duplicated rows are deleted
tweet_data_clean.duplicated().sum()


# **DEFINE**

# changing column name and data type of column named 'id' of tweet_data_clean dataframe 

# **CODE**

# In[56]:


#renaming the id column of tweet_data_clean as tweet_id
tweet_data_clean=tweet_data_clean.rename(columns={'id':'tweet_id'})


# In[57]:


# changing the data type
tweet_data_clean['tweet_id'] = tweet_data_clean['tweet_id'].astype('str')


# **TEST**

# In[58]:


#to check the change in data type and name of column
tweet_data_clean.info()


# **DEFINE**

# changing data type of columns of image_clean dataframe

# **CODE**

# In[59]:


#information about data types
image_clean.info()


# In[60]:


#changing data type of tweet_id column to string
image_clean['tweet_id'] = image_clean['tweet_id'].astype('str')


# **TEST**

# In[61]:


image_clean.info()


# **DEFINE**

# merging dataframes tweet_data_clean, image_clean,twitter_clean

# **CODE**

# In[62]:


#merging dataframes on the basis of tweet_id  
master_df = pd.merge(twitter_clean, tweet_data_clean,on='tweet_id', how='inner')
master_df= pd.merge(master_df, image_clean,on='tweet_id', how='inner')



# **TEST**

# In[63]:


#final dataframe is master_df
master_df.info()


# In[64]:


master_df.head()


# ## STORING DATA

# In[84]:


#writing data to twitter_archive_master.csv
master_df.to_csv('twitter_archive_master.csv',index=False)


# ## ANALYZING

# In[85]:


data=pd.read_csv('twitter_archive_master.csv')


# In[86]:


data.head(3)


# In[87]:


#making a new column named rating ratio for further analysis

data['rating ratio']=data['rating_numerator']/data['rating_denominator']


# In[77]:


#again displaying the dataframe
data.head()


# In[88]:


#plotting rating ratio
get_ipython().run_line_magic('matplotlib', 'inline')
data['rating ratio'].value_counts()


# In[89]:


data['rating ratio'].value_counts().plot(kind='bar')
plt.title('rating ratio analysis')


# This graph gives the insight of how rating ratio differs and which rating ratio is the highest 

# In[90]:


data.info()


# In[91]:


data.dog_type.value_counts()


# In[92]:


data['dog_type'].value_counts().plot(kind='bar')
plt.title('dog_type analysis')


# **We observe through this graph pupper is more in number that is pupper is more common dog type **

# In[98]:


#extracting month
data['timestamp']=pd.to_datetime(data['timestamp'])
data['month'] = data['timestamp'].dt.month


# In[101]:


data.head(3)


# In[102]:


#extracting year
data['year'] = data['timestamp'].dt.year


# In[103]:


data.head(3)


# In[114]:


plotting_detail = pd.DataFrame(data.groupby('month')['retweet_count'].count())


# In[115]:


plotting_detail


# In[119]:


plotting_detail.plot(kind='bar',title='month vs retweet count')


# we observed that in 12th month retweet count is maximum

# In[138]:


plotting_detail1 = pd.DataFrame(data.groupby('year')['retweet_count'].count())


# In[139]:


plotting_detail1


# In[127]:


plotting_detail1.plot(kind='bar',title='year vs retweet count')


# From above bar graph we noticed that 2016 year witnessed maximum retweet count

# In[133]:


data.plot(x="retweet_count",y="favorite_count",kind="scatter")
plt.xlabel("Retweet count")
plt.ylabel("Favorite count")
plt.title("favorite Count vs Retweet Count")
plt.figure(figsize=(10,10))


# above graph shows strong correlation between favorite tweets and retweets

# In[145]:


data.dog_type.value_counts()
data.boxplot(column='rating ratio', by='dog_type')
plt.xlabel("Dog type")
plt.ylabel("Rating Ratio")
plt.suptitle("")
plt.title("Distribution of rating ratio vs Dog Type")


# puppo dog type has highest median rating ratio and pupper has the lowest median rating ratio
