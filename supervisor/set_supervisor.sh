rm -rf /etc/supervisor/conf.d/exorde.conf
rm -rf /etc/supervisor/conf.d/watcher.conf
cp ./*.conf /etc/supervisor/conf.d/.
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start exorde
sudo supervisorctl start watcher
