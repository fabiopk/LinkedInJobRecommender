# LinkedInJobRecommender
A (personal) recommendation system for LinkedIn jobs. Data scraping, feature creation, modeling and frontend deployment.

Demo: https://linkedinjob.herokuapp.com/

## What is it?

This projet shows the creation of a job recommendation system. 
It starts with data scraping of LinkedIn jobs by query and location.
The job pages are downloaded and the useful information is scraped and saved in a MongoDDB database.
The target user has to label some of the samples manually; either by the frontend application of through the jupyter notebook.
The job title and description are processed as as bag-of-words and, with ohter features, some models are tested.
There is a server with an accesible api to retrieve the scores for a list of jobs and to label a given sample.
There is a frontend application that shows the best jobs based on some filters.
Isolated scripts are used to automate the process of data scraping and prediciting scores for the production server.

## What is the stack used?

Python + scikit_learn + pandas + numpy for data modeling
MongoDB as the database
Flask + Guinicorn for the backend portion
React for the frontend application

## How can I use it for recommending ME jobs?

You can either follow the jupyter notebooks or the python scripts, and chage the query and city as you like.
You'll have to setup your own database (I recommend using MongoDB locally with docker for development).
Manually label at least a 100 or so jobs before checking the results. You'll probably need a lot more to see a good performing model



