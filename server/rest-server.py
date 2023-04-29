#!flask/bin/python
################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------                                                                                                                             
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches 
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #                                                                                                                                  	       
#-------------------------------------------------------------------------------------------------------------------------------                                                                                                                              
################################################################################################################################
from flask import Flask, jsonify, abort, request, make_response, url_for,redirect, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import shutil 
import numpy as np
from search import recommend
import tarfile
from datetime import datetime
from scipy import ndimage
#from scipy.misc import imsave

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
from tensorflow.python.platform import gfile
app = Flask(__name__, static_url_path = "")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth = HTTPBasicAuth()

#==============================================================================================================================
#                                                                                                                              
#    Loading the extracted feature vectors for image retrieval                                                                 
#                                                                          						        
#                                                                                                                              
#==============================================================================================================================
extracted_features=np.zeros((2955,2048),dtype=np.float32)
with open('saved_features_recom.txt') as f:
    		for i,line in enumerate(f):
        		extracted_features[i,:]=line.split()
print("loaded extracted_features") 


#==============================================================================================================================
#                                                                                                                              
#  This function is used to do the image search/image retrieval
#                                                                                                                              
#==============================================================================================================================
@app.route('/imgUpload', methods=['GET', 'POST'])
#def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_img():
    print("image upload")
    result = 'static/result'
    if not gfile.Exists(result):
          os.mkdir(result)
    shutil.rmtree(result)
 
    if request.method == 'POST' or request.method == 'GET':
        print(request.method)
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
           
            print('No selected file')
            return redirect(request.url)
        if file:# and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 将图片存入static下的文件夹upload
            uploadloc = os.path.join("static/upload", filename)
            # 防止重名,若有则删除
            if os.path.exists(uploadloc):
                os.remove(uploadloc)
            # 保存图片
            file.save(uploadloc)

            recommend(uploadloc, extracted_features)
            image_path = "/result"
            image_list =[os.path.join(image_path, file) for file in os.listdir(result)
                              if not file.startswith('.')]
            image_list = get_tag_for_image(image_list)
            return jsonify(image_list)

def get_tag_for_image(image_list):
    image_index_list = []
    for i in range(len(image_list)):
        image_name = image_list[i]
        # 获取字符串中的数字
        index = int(''.join([x for x in image_name if x.isdigit()]))
        image_index_list.append(index)
        # 转为列表
        image_list[i] = [image_list[i]]
    # 循环遍历database/tags文件夹下的所有txt文件
    for file in os.listdir("database/tags"):
        # 获取文件名，不带后缀，作为tag名称
        tag_name = os.path.splitext(file)[0]
        # 读取文件内容,若内容包含图片序号，则将tag加入到对应的图片列表中
        with open(os.path.join("database/tags", file), 'r') as f:
            for line in f.readlines():
                if(line=='\n'):
                     break
                index = int(line.strip())
                if index in image_index_list:
                    image_list[image_index_list.index(index)].append(tag_name)
                    print("将"+tag_name+"存入"+image_list[image_index_list.index(index)][0])
    return image_list

#==============================================================================================================================
#                                                                                                                              
#                                           Main function                                                        	            #						     									       
#  				                                                                                                
#==============================================================================================================================
@app.route("/")
def main():
    return render_template("temp.html")
if __name__ == '__main__':
    app.run(debug = True, host= '0.0.0.0')
