# To run UWSGI: Make sure to point --virtualenv to this current directory's virtualenv
sudo uwsgi --http-socket :5000 --plugin python38 --module wsgi:app  --virtualenv myenv/ 
# or
sudo uwsgi myapp.ini --http-socket :5000

# To Kill processes:
pkill -9 uwsgi

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

# Seal the Deal?
cd /var/www/myapp
nohup uwsgi myapp.ini &

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

# Probably do this:
sudo nohup uwsgi myapp.ini --http-socket :5000