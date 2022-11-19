from flask import Flask, request, render_template 
import numpy as np 
import pandas as pd 
from sklearn import metrics 
import warnings 
import pickle 
import requests 
warnings.filterwarnings('ignore') 
from feature import FeatureExtraction 
import math 

file = open("model.pkl","rb") 
gbc = pickle.load(file) 
file.close() 


API_KEY = "<YOUR_API_KEY>" 
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": 
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'}) 
mltoken = token_response.json()["access_token"] 
header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken} 


app = Flask(__name__, template_folder="templates") 
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
        
        payload_scoring = {"input_data": [{"fields": ["UsingIP","LongURL","ShortURL","Symbol@","Redirecting//","PrefixSuffix-","SubDomains","HTTPS","DomainRegLen","Favicon","NonStdPort","HTTPSDomainURL","RequestURL","AnchorURL","LinksInScriptTags","ServerFormHandler","InfoEmail","AbnormalURL","WebsiteForwarding","StatusBarCust","DisableRightClick","UsingPopupWindow","IframeRedirection","AgeofDomain","DNSRecording","WebsiteTraffic","PageRank","GoogleIndex","LinksPointingToPage","StatsReport" 
        ], "values": [1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,-1,-1,1,1,1,0,1,1,1,1,-1,-1,-1,-1,1,0,1]}]} 
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/27c47874-fd3f-4c1c-aefa-afa3d1738374/predictions?version=2022-11-17', json=payload_scoring, 
        headers={'Authorization': 'Bearer ' + mltoken}) 
        print("Scoring response for given input") 
        print(response_scoring.json()) 
        predictions=response_scoring.json() 

        x = math.floor(y_pro_non_phishing*1000)/10 
        pred=print(predictions['predictions'][0]['values'][0][0]) 
        if(pred == -1): 
            print("The Website is unsafe") 
        else: 
            print("The Website is safe") 
        return render_template('index.html',xx =x,url=url ) 
    return render_template("index.html", xx =-1) 

if __name__ == "__main__": 
    app.run(debug=True,port=2020)
