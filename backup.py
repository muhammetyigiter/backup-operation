from datetime import datetime
import json
import os
import shutil
import psycopg2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from decouple import config
from oauth2client import file, client, tools
import requests


db_params = {
    "database": config("DB"),
    "user": config("DBUSER"),
    "password": config("DBPASSWORD"),
    "host": config("DBHOST"),
    "port": config("DBPORT"),
}

CREDENTIALS_FILE = "../credentials.json"


def sendSlack(channel, senderName, message, icon_emoji=":large_green_circle:"):
    url = config("SLACK_WEBHOOK_URL")
    data = {
        "channel": channel,
        "username": senderName,
        "text": message,
        "icon_emoji": icon_emoji,
    }
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    requests.post(url, data=json.dumps(data), headers=headers)


def backup_postgresql_databases(backup_folder):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = [row[0] for row in cursor.fetchall()]

    for database in databases:
        backup_file = os.path.join(backup_folder, f"{database}.backup")
        os.system(
            "docker exec -it {} pg_dump -U {} -d {} > {}_backup.sql".format(
                config("DBDOCKERNAME"), config("DBUSER"), database, database
            )
        )

    cursor.close()
    conn.close()


def upload_file_to_google_drive(file_path):
    try:
        SCOPES = "https://www.googleapis.com/auth/drive"
        store = file.Storage("token.json")
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(CREDENTIALS_FILE, SCOPES)
            creds = tools.run_flow(flow, store)
            print("Credentials saved.")
        else:
            print(
                "Credentials seem to be valid. Remove credentials.json to renew them anyways."
            )

        drive_service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": file_path, "parents": [config("GDRIVEFOLDERID")]}
        media = MediaFileUpload(file_path, mimetype="application/zip")
        file2 = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        sendSlack(
            "#backup-logs",
            "Backup - OK",
            "Dosya yüklendi. Dosya ID'si: {}".format(file2.get("id")),
            ":white_check_mark:",
        )
    except Exception as e:
        sendSlack(
            "#backup-logs",
            "Backup - ERROR",
            "Dosya yüklenirken hata oluştu. Hata: {}".format(e),
            ":red_circle:",
        )


def delete_files_with_extension(directory, extension):
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"{filename} is deleted.")


def main():
    sendSlack(
        "#backup-logs",
        "Backup Job - Started",
        "Yedekleme Scripti Başladı",
        ":white_check_mark:",
    )
    static_folder = config("STATIC_FOLDER")
    backup_folder = "backup_folder"
    db_backup_folder = "backup_folder/databases"
    os.makedirs(backup_folder, exist_ok=True)
    os.makedirs(db_backup_folder, exist_ok=True)
    os.chdir(db_backup_folder)

    backup_postgresql_databases(db_backup_folder)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.chdir("../../")

    file_name = "{}_backup".format(now)
    shutil.copytree(static_folder, backup_folder + "/" + static_folder.split("/")[-1])
    shutil.make_archive(file_name, "zip", backup_folder)
    upload_file_to_google_drive("{}.zip".format(file_name))
    delete_files_with_extension(".", ".zip")
    try:
        shutil.rmtree(backup_folder)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
