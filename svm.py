# -*- coding: utf-8 -*-
"""
Created on Fri May 06 20:52:23 2016

@author: ajain24
"""


import os
import glob
import cv2
from sklearn import preprocessing
import csv
from sklearn import cross_validation
from numpy import *

from scipy.cluster.vq import *
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from skimage import feature
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
from sklearn import ensemble
from sklearn.preprocessing import StandardScaler


csvPath = "C:\\Users\\ajain24\\Desktop\\project\\"
#csvPath = "G:\\pp\\"

    
def generateOutputCSV(YTestId, pred_out, damaged_test_Image,path):
    
    distortedImg = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
    pred_prob =[]
   
    for i in range(len(YTestId)):
        pred_prob.append(pred_out[i][0])
        
    id_arr = []
    for i in range(len(YTestId)):
        id_arr.append(YTestId[i])
               
    for i, row in enumerate(YTestId):
        for j in range(len(pred_prob[i])):
            row.append(pred_prob[i][j])
                
    with open(csvPath+path, 'wb') as fp:
        writer = csv.DictWriter(fp, fieldnames = ["id","col1","col2","col3","col4","col5","col6","col7","col8"])
        writer.writeheader()
        csv_file = csv.writer(fp, delimiter=',')
        csv_file.writerows(id_arr)      
   

def getTrainY():

    fileData = []
    file_name = csvPath +'train.csv'
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            fileData.append(row)        
    data = array(fileData)
    data = data[1:,].astype(int32, copy=False)
    return data

def generatesURFFeatures(data):
    
    data_size = len(data)
    surf = cv2.SURF(400)
    flatten_desc_arr = empty((0,128))
    big_desc_arr = empty((0,128))
   
    temp = []
    counter  = 0
    prev_Des =[]
    for i in range(data_size):
        counter = counter + 1
        _, desc = surf.detectAndCompute(data[i], None)
        
        if (desc is not None and len(desc) > 0):
            prev_Des= desc
            temp.append(desc)
            if logical_or(counter % 1000 == 0 , i == data_size-1):
                print counter
                big_desc_arr = concatenate((big_desc_arr, flatten_desc_arr))
                flatten_desc_arr = empty((0,128))
            flattenDesc = array(desc)
            flatten_desc_arr = concatenate((flatten_desc_arr, flattenDesc))
        else:
            irand = randrange(0, i-3)
            temp.append(temp[irand])
          
    return big_desc_arr, temp
    

def generateTrainKmeans(big_desc_arr, temp):
    k =5
    histo = zeros((len(temp),k))
    big_desc_arr = whiten(big_desc_arr)
    centroids,_ = kmeans(big_desc_arr, k,1)
    for i in range(len(temp)):
        code, _ = vq(temp[i], centroids)
        for c in code:
            histo[i][c] = histo[i][c] + 1
    return centroids, histo 


def generateTestKmeans(big_desc_arr, centroids, temp):
     k =5
     histo = zeros((len(temp), k))
     for i in range(len(temp)):   
        code, dist = vq(temp[i], centroids)
        for c in code:
            histo[i][c] = histo[i][c] + 1
     return  histo


damaged_test_Image = []




def getY(data):
    label = 0
   
    if data[0][1] == 1:
        label=1
    if data[0][2] == 1:
        label=2
    if data[0][3] == 1:
        label=3        
    if data[0][4] == 1:
        label=4
    if data[0][5] == 1:
        label=5
    if data[0][6] == 1:
        label=6        
    if data[0][7] == 1:
        label=7
    if data[0][8] == 1:
        label=8
    return label;
    

def prepareData(path,  train_csv_data):
    trainY=[]
    id = []
    cv_img = []
    newx,newy = 200,200
    i = 0
    damaged_test_Image = []
  
    for img in glob.glob(path+"*.jpg"):
       n = cv2.imread(img, 0)
       i = i+1 
       newimage =[]
       head, tail = os.path.split(img)
       data_id = int(tail.rstrip(".jpg"))
       match_pics_id = where(train_csv_data[:,0] == data_id)
       co = train_csv_data[match_pics_id[0],:]
       trainY.append(getY(co))
       
       id.append([data_id])  
       
       if n is not None:   
            newimage = cv2.resize(n,(newx,newy),interpolation = cv2.INTER_AREA)
       else:
            damaged_test_Image.append(id)
            newimage = cv_img[i-2]   
       cv_img.append(newimage) 
       
    return id , cv_img, damaged_test_Image, trainY


def prepareTestData(path):
    
    id = []
    cv_img = []
    newx,newy = 200,200
    i = 0
    damaged_test_Image = []
   
    for img in glob.glob(path+"*.jpg"):
       n = cv2.imread(img, 0)
       i = i+1 
       newimage =[]
       head, tail = os.path.split(img)
       data = int(tail.rstrip(".jpg"))
       id.append([data])  
       if n is not None:   
            newimage = cv2.resize(n,(newx,newy),interpolation = cv2.INTER_AREA)
       else:
           damaged_test_Image.append(id)
           irand = randrange(0, i-1)
           newimage = cv_img[irand] 
       cv_img.append(newimage) 
       
    return id , cv_img, damaged_test_Image
    
def main():

    train_path = csvPath + "train\\";   
    test_path = csvPath +"test\\"
    
    data = getTrainY()
    
    # Read Train Data
    train_id, Xtrain_data, damaged_train_Image, Ytrain = prepareData(train_path, data)
    print "Read Train Data"
   
   # Generated Train Model
    surfFeatures, temp = generateSURFFeatures(Xtrain_data)
    centroids, histo_tr = generateTrainKmeans(surfFeatures, temp)
    
    print "Generated Train Model"

    # Read Test Data
    test_id, test_data, damaged_test_Image = prepareTestData(test_path)
    print "Read Test Data"    
    
    surfTestFeatures, temp1 = generateSURFFeatures(test_data)
    histo_te = generateTestKmeans(surfTestFeatures, centroids,temp1 )    
     
    print "Generated Test Model"
    
    
    print "Get Y"
    clf3 = SVC(probability=True, decision_function_shape='ovr')
      
    standard_scaler = StandardScaler()
    svm_tr = standard_scaler.fit(histo_tr)
    svm_trf = svm_tr.transform(histo_tr)
    
    svm_tr1 = standard_scaler.fit(histo_te)    
    svm_tef = svm_tr1.transform(histo_te)
    
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(svm_trf, Ytrain, test_size=0.3, random_state=0)
       
    clf3.fit(X_train, y_train)
    print clf3.score(X_test, y_test)
    pred_out = []

    for j in range(len(test_data)):
        pred_out.append(clf3.predict_proba([svm_tef[j]]))
     
    generateOutputCSV(test_id, pred_out, damaged_test_Image,'output.csv')
      
    print "Done!!!!!!"
       
main()
