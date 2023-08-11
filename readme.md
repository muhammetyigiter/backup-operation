This repo takes backups of all databases in postgresql. It zips a static file and the databases it backs up and uploads it to Google Drive at 00.00 every day. (And notify Slack with webhook)

## Installation

```bash
chmod +x install.sh
sh install.sh
```


## ENV Veriable

```ENV
DBUSER=
DBPASSWORD=
DBHOST=
DBPORT=
DBDOCKERNAME=
GDRIVEFOLDERID=
STATIC_FOLDER=
SLACK_WEBHOOK_URL=
```


You need credentials.json and token.json. 