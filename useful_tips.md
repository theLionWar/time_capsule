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