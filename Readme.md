This is a project that shows how to create a database sample web app that containt multiple tables(parent child tables) using flask framework

# Prerequiste:  

install virtualbox  
install vagrant
clone the vagrant machine fullsack-nanodegree:
```
git clone https://github.com/udacity/fullstack-nanodegree-vm.git fullstack  
```
run the vagrant machine:
```
cd fullstack/vagrant  
vagrant up  
vagrant ssh  
```
# Installation
Inside the vagrant machine:
```
cd vagrant/catalog  
clone https://github.com/abdullah12/CategoryItems.git .  
```
# Run
run the following:  
```
python database-setup.py
python seeder.py
python app.py
```
# See The Result
navigate to localhost:5000
