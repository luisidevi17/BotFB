#!/bin/bash
# Instalar Google Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update -qq
apt-get install -yqq ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Instalar ChromeDriver
CHROME_VER=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
DRIVER_VER=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VER)
wget -q https://chromedriver.storage.googleapis.com/$DRIVER_VER/chromedriver_linux64.zip
unzip -q chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
