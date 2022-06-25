## What is required need to do?

The objective is to read JSON data containing user login behavior from an AWS SQS Queue that is made available via [localstack](https://github.com/localstack/localstack). Fetch wanted me to hide the personal identifiable information (PII). The fields `device_id` and `ip` should be masked, but in a way where it is easy for data analysts to identify duplicate values in those fields.

Once I parsed the JSON data object and hashed the two fields, I wrote each record to a Postgres database that is made available via [Postgres's docker image](https://hub.docker.com/_/postgres). 

```sql
-- Creation of user_logins table

CREATE TABLE IF NOT EXISTS user_logins(
    user_id             varchar(128),
    device_type         varchar(32),
    masked_ip           varchar(256),
    masked_device_id    varchar(256),
    locale              varchar(32),
    app_version         varchar(64),
    create_date         date
);
```

## Installation:
#
This document is for Ubuntu 22.04
1. start by downloading the template files given in the repository
2. Next, install virtualbox with Ubuntu to setup my development environment (the image file can be downloaded from Ubuntu's website)
3. Install docker  the terminal command: \
    `sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin`
4. Install pip  the terminal command \
    `python -m ensurepip --upgrade` \
    `sudo apt-get install python3-pip`
5. Installed a virtualenv  pip3 so that it doesn't mess with Ubuntu's default package manager  the terminal command \
    `sudo pip3 install virtualenv`
    
## Project Setup
#

## Virtual environtment setup with pip and awslocal
1. Make a project folder that will keep all of your files
2. Move all downloaded template files into the new folder
3. Go into the template folder and run the file
    `01_call_python_scripts.sh` 
4. Create the virtual environment  \
    `python3 -m venv /path/to/new/virtual/environment`
5. Activated/Deactivated the virtual environment  \
    `source venv/bin/activate` \
    `deactivate (in the env)`
6. Install awslocal in the virtualenv  the terminal command \
    `pip install awscli-local`

## Docker setup
1. Start the docker service by  \
    `sudo systemctl start docker.service`
2. Once your docker-compose.yml are in your project folder, run the `make start` command. This executes `docker-compose up` which creates the localstack container for the AWS SQS queue and Postgres database container. 
3. Check to see if all containers are running and check the their ID by the command
    `docker ps`
## Test local access
#
## Receive message from awslocal
1. Activate the virtualenv \
    `source venv/bin/activate`

2. Read the messages from the queue with awslocal \
`awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue` 
## Connect to postgres database
1. Check postgres container ID with \
    `docker ps`
2. Connect to Postgres container  \
    `docker exec -it hostname:/bin/bash`
3. Once in the Postgres container, to connect to the postgres database \
    `psql -d postgres -U postgres  -p 5432 -h localhost -W`
4. To verify a table is created use \
    `select * from user_logins;`
## Using python to ETL of a SQS Queue
#
## Receive messages from Queue and porting to postgres
1. Run in the virtualenv \
    `receiveQueue.py`
2. Take the generated json file and send it over to the postgres docker container  the command \
    `docker cp qdata.json [postgresContainerID]:/home/`
3. Connect to postgres container  \
    `docker exec -it hostname:/bin/bash`
4. Once in the Postgres container, to connect to the postgres database \
    `psql -d postgres -U postgres  -p 5432 -h localhost -W`
5. Create a temp table  \
    `create temp table user_logins_info(info json);`
6. Import json file into variable 'content' \
    \set content \`cat /home/qdata.json`
7. Insert json values into the temp table \
    `insert into user_logins_info values(:'content');`
8. Populate user_logins database with json info \
`\i insertion.sql`

```sql 
-- Inserts into user_logins using our temp postgres table to cross join laterally and populate it

insert into user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
select p.* from user_logins_info l cross join lateral json_populate_recordset(null::user_logins, info) as p

```

```sql


               user_id                | device_type |      masked_ip       |   masked_device_id   | locale | app_version | create_date 
--------------------------------------+-------------+----------------------+----------------------+--------+-------------+-------------
 607a0bff-c282-4d3b-9b57-b0f1dba212a3 | android     | 2757490101077010937  | -8359013604816752496 | IR     | 8.3         | 
 c24b628c-1afd-4f59-a0f0-3db2ae71fd5c | ios         | -6211284796857948575 | 5946580104296178583  | BR     | 0.2.4       | 
 a0c70e0d-6dad-4bf2-b26e-a9f39d2cc69f | android     | -3045012191054737559 | -3400218713126740300 |        | 0.4.8       | 
 27843453-3ecd-46d5-bf1c-43a137c214b5 | ios         | -2977210858651311076 | -8220529927155568948 | CA     | 0.6.6       | 
 868f5cea-ab60-4c83-bda0-51ac318ef89d | ios         | 8077639694476901068  | 6309648547739530680  | VN     | 0.7.9       | 

```

## Ways to improve project
#
1. Using a cleaner method of insertions without needing the use of a temp table. 
2. Find a way to embed the SQL commands into the python scripts.

## Tools used
1. Virtualbox (Ubuntu)
2. Docker
3. awslocal/awscli
4. Python3
5. PostgresSQL
6. pip3
7. virtualenv
8. VSCode

Comments were left in both the receiveQueue.py and insertion.sql files explaining further what each line of code is doing.
