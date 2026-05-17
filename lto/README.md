## Team Git Workflow

To keep our repository organized and stable, please follow these steps:  

### 1. **Clone the repository**
   git clone https://github.com/eeveevv/127-FinalProject.git
   cd 127-FinalProject

### 2. create your own branch
    git checkout -b yourname
    git push -u origin yourname

### 3. work only on your branch
    git add .
    git commit -m "Describe your changes"
    git push

### 4. Keep main stable  
Do not commit directly to main.  

All merges into main must go through a Pull Request.  

### 5. Open a Pull Request  
On GitHub, open a PR from your branch into main.  

Merge only if there are no errors or conflicts.  

### 6. Stay updated  
    git checkout yourname
    git pull origin main
    ```