from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
warnings.filterwarnings('ignore')
from feature import FeatureExtraction
import math

file = open("model.pkl","rb")
gbc = pickle.load(file)
file.close()


app = Flask(__name__,template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30) 

        y_pred =gbc.predict(x)[0]
        #0 - unsafe       
        #1 - safe
        y_pro_phishing = gbc.predict_proba(x)[0,0]
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]
        print("phi ",y_pro_phishing)
        print("non phi ",y_pro_non_phishing)
        x = math.floor(y_pro_non_phishing*1000)/10
        print(x)
        return render_template('index.html',xx =x,url=url )
    
    #home page render
    return render_template("index.html", xx =-1)


if __name__ == "__main__":
    app.run(debug=True,port=2002)
