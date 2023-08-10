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

# Cron job oluşturma
echo "Cron job oluşturuluyor..."
cron_command="/usr/bin/python3 ./backup.py"
cron_job="0 0 * * * $cron_command"
(crontab -l ; echo "$cron_job") | crontab -

echo "İşlem tamamlandı."
