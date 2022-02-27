## How to restore a production database from Heroku:

 - List the existing backups:

```sh
heroku pg:backups --app personalized-time-capsule
```

 - Download a chosen backup:

```sh
heroku pg:backups:url <backup_id(for example b001)> --app personalized-time-capsule
```

- Restore to any Postgres:

```sh
pg_restore -d <db_name> -1 ~/Downloads/<dump_file_name>
```

### For more restoring and backup options:
https://devcenter.heroku.com/articles/heroku-postgres-backups



## How to upgrade chrome driver locally (for e2e test):

 - Download the new chromedriver from the website
 - Create directory for the new version:

```sh
cd /usr/local/Caskroom/chromedriver
mkdir 98.0.4758.102
```

 - Copy the new chromedriver to there:

```sh
cp ~/Downloads/chromedriver ./98.0.4758.102/
```

 - Link the new chromedriver to the cli

```sh
cdp
ln -s /usr/local/Caskroom/chromedriver/98.0.4758.102/chromedriver chromedriver
```