import sys
sys.path.append(r'C:\Users\YIFAN\Documents\GitHub\FridgeViewer')

activate_this = r'C:\Users\YIFAN\Documents\GitHub\FridgeViewer\venv\Scripts\activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application