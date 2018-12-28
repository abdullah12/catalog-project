# Prerequiste:  

install virtualbox  
install vagrant  
run the following:
```
git clone https://github.com/udacity/fullstack-nanodegree-vm.git fullstack  
cd fullstack/vagrant  
vagrant up  
vagrant ssh  
```
Inside the vagrant machine:
```
cd vagrant/catalog  
clone https://github.com/abdullah12/CategoryItems.git .  
```
run the following:  
```
python database-setup.py
python seeder.py
python app.py
```
navigate to localhost:5000
