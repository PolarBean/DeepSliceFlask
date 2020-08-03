# To run UWSGI: Make sure to point --virtualenv to this current directory's virtualenv
sudo uwsgi --http-socket :5000 --plugin python38 --module wsgi:app  --virtualenv myenv/ 
# or
sudo uwsgi myapp.ini --http-socket :5000

# To Kill processes:
sudo pkill -9 uwsgi

# No Module Named Encodings? Wrong Virtualenv!
virtualenv = myenv // Something like this

# First Removes folder from myapp, then copies contents from test folder to working myapp folder
sudo rm -rf /var/www/myapp; sudo cp -R "/mnt/d/Documents/Github Projects/test" /var/www/myapp 

# Then: (Note: http-socket for local running)
sudo uwsgi myapp.ini --http-socket :5000

# Edit Config:
sudo nano /etc/nginx/sites-available/myapp.conf
# To replace config:
sudo ln -sf /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/myapp.conf
# Then restart with
sudo service nginx restart

# Activate environment:
source myenv/bin/activate

# Seal the Deal? (ACTIVATE ENV FIRST!)
cd /var/www/myapp
sudo nohup uwsgi myapp.ini &

# Probably do this for running UWSGI:
sudo nohup uwsgi myapp.ini  --http-socket :5000

# Folders
cd "/mnt/d/Documents/Github Projects/test"
cd "/var/www/myapp"

# Activate environment:
source myenv/bin/activate

# Upgrade pip:
pip install -U pip
# Install Tensorflow after upgrading pip:
pip install tensorflow
# Also need to install other libraries:
pip install numpy pandas scikit-learn scikit-image

# List processes on port 80
sudo lsof -t -i:80
# Kill Process
sudo kill -9 <pid>

# Check Errors on NGINX
sudo tail -15 /var/log/nginx/error.log

# To run in emperor
sudo uwsgi --emperor /etc/uwsgi/apps-enabled/


# -- APACHE -- #
sudo nano /etc/apache2/sites-enabled/myapp.conf

# To restart:
sudo apache2ctl restart

# For Error Logs:
sudo nano /var/log/apache2/error.log


/var/www/myapp/myenv/lib/python3.8/site-packages
