# Welcome to my swile case study

## prerequisite:
- having a running docker-compose environment

## instructions:
run:  
`sudo docker compose up -d`
  
after seeing the containers being created, you can go to http://localhost:9001/ (username: minio, password: password) to connect to the Minio server. And see that the data has been upload.  
    
The result should be bucket "bucket" containing a folder "transactions" containing the json files.  
  
Go to http://localhost:3000/asset-groups , a dag of 4 jobs should already be present.  
Just click on the up-right located button "materialize all".  
The pipeline can be a bit long, it is a good idea to keep the Minio connected by refreshing the Minio's page.  
  
After the pipeline succeeded, there should be a resulting CSV file called "export.csv" onto the Minio bucket.

## Improvements:
Here's some possible ameliorations to continue this project even further:
- having unit tests
- having a CI/CD pipeline with github actions or Gitlab CI
- having a proper secret manager so they are not written into the docker-compose file
- having a Rate Limiter for the INSEE API
- having standard dev tools like a linter and code checker integrated into the CI
- improve the daily_spend_per_naf_code.sql file
- improve db integration with the SqlAlchemy models with alembic migrations
