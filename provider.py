from flask import Flask, request, render_template
import sys, os, logging, time, datetime, json, uuid, requests, ast
from werkzeug import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_restful import Resource, Api

app = Flask(__name__)

api = Api(app)

app.debug = True

class OPERATIONS(Resource):
        # @app.route('/',methods=['GET', 'POST'])
        # def hello_world(self):
        #     return 'Hello World!'

        @app.route('/',methods=['GET','POST'])
        def customerupdate():
            print ("************DEBUG 1 ***********")
            RequestValues = request.values
            print (RequestValues)
            # print ("************DEBUG 2 ***********")
            # RequestForm = request.form
            # print (RequestForm)
            # print ("************DEBUG 2-1 ***********")
            # so = RequestForm
            # json_of_metadatas = so.to_dict(flat=False)
            # print (json_of_metadatas)
            # print ("************DEBUG 2-2 ***********")
            # MetdatasFromJSON = json_of_metadatas['json']
            # print (MetdatasFromJSON)          
            # print ("************DEBUG 2-3 ***********")
            # MetdatasFromJSON0 = MetdatasFromJSON[0]
            # print (MetdatasFromJSON0)
            # print ("************DEBUG 3-5 ***********")
            # strMetdatasFromJSON0 = str(MetdatasFromJSON0)
            # MetdatasDICT = ast.literal_eval(strMetdatasFromJSON0)
            # print (MetdatasDICT)
            # print ("************DEBUG 3-5 ***********")
            # for key in MetdatasDICT :
            #     print ("key: %s , value: %s" % (key, MetdatasDICT[key]))
            # print ("************DEBUG 4 ***********")
            # f = request.files['file']
            # f.save(secure_filename(f.filename))
            # print ("FILE SAVED LOCALY")
            return 'JSON of customer posted'


app.run(host='0.0.0.0', port=5000)