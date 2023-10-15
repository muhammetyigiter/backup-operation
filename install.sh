#!/bin/bash

# Python 3 kurulumunu kontrol et
if ! command -v python3 &> /dev/null; then
    echo "Python 3 kurulu değil. Kurulum yapılıyor..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Paketleri kurma
echo "Paketler yükleniyor..."
pip3 install -r ./requirements.txt

crontab -r

script_dir=$(pwd)
cron_command="/usr/bin/python3 $script_dir/backup.py"
cron_job="0 */2 * * * $cron_command"
(crontab -l ; echo "$cron_job") | crontab -

echo "Cron job oluşturuldu."
