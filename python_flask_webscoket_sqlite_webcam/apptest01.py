from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime
import json
import cv2
from ultralytics import YOLO
from PIL import Image
from gevent.pywsgi import WSGIServer

from db import *
from sqlite_utils import *

#names: {0: 'Lollipop', 1: 'cookie', 2: 'fruit', 3: 'noodles'}

app = Flask(__name__,static_folder='web/')

# http://127.0.0.1:3000

@app.route('/')
def index():
   #return render_template('index.html')
   return app.send_static_file('index.html')
    
 
@app.route('/video')
def goto_video():
    return render_template('html5_camera_3.html')
    


# Open the camera
camera = cv2.VideoCapture(1)
#model = YOLO('model/yolov8s.pt')
model = YOLO('model/best-m200.pt')


def detecte_objects(image_path):
    # Load image
    image = cv2.imread(image_path)

    # Perform detection+
    # model.predict("bus.jpg", save=True, imgsz=320, conf=0.5)
    results = model.predict(image, conf=0.5) 
    #print("Results structure:", results)
    
    rectangles=results[0].boxes.xyxy.tolist()
    cls=results[0].boxes.cls.tolist()
    conf=results[0].boxes.conf.tolist()
    # Add rectangles to the plot
    detected_objs={}
    id=0
    for rect,c,prob in zip(rectangles,cls,conf):
        
        print('-->',rect,c,prob)
        
        if int(c) not in class_product_tbl.keys() :  #not in the table 
            print('class id ',int(c),' is not included')
            continue
        
        detected_objs[id]={'label':class_product_tbl[int(c)]['label_name'],'conf':prob,\
        'p_id':class_product_tbl[int(c)]['p_id'],'p_name':class_product_tbl[int(c)]['p_name'],'p_price':class_product_tbl[int(c)]['p_price']}        
        
        if c==0:
            color=(0, 255, 0)
        else:
            color=(0, 255, 255)
            
        x1,y1,x2,y2= list(map(int,rect))

        #print(x1,y1,x2,y2)
        cv2.rectangle(image,(x1, y1), (x2, y2), color,2)
        id+=1
    
      # Encode image to JPEG format
    _, buffer = cv2.imencode('.jpg', image)
    # Convert to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64,detected_objs
    
    #cv2.imshow('Video with Rectangles', frame_with_rects)


#-------------websocket------------------------    
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


def save_img(msg):

    filename=datetime.now().strftime("%Y%m%d-%H%M%S")+'.png'
    base64_img_bytes = msg.encode('utf-8')
    with open('./upload/'+filename, "wb") as save_file:
        save_file.write(base64.decodebytes(base64_img_bytes))
    
    return './upload/'+filename


#user defined event 'client_event'
@socketio.on('client_event')
def client_msg(msg):
    #print('received from client:',msg['data'])
    emit('server_response', {'data': msg['data']}, broadcast=False) #include_self=False

#user defined event 'connect_event'
@socketio.on('connect_event')   
def connected_msg(msg):
    print('received connect_event')
    emit('server_response', {'data': msg['data']})
    
    
#user defined event 'capture_event'
@socketio.on('capture_event')   
def handle_capture_event(msg):
    print('received capture_event')
    #print(msg)
    filepath=save_img(msg)
    
    img_base64,objs=detecte_objects(filepath)
    
    #here we just send back the original image to browser.
    #maybe, you can do image processinges before sending back 
    emit('object_detection_event', img_base64, broadcast=False)
    emit('detected_objects',  {'objs': json.dumps(objs)}, broadcast=False)
    

    
#------SQLite stuff-----------------

from sqlite_utils import *


@socketio.on('get_allitem_event')   
def trigger_allitem_item(msg):
    print('trigger_allitem_item')
    #newitems=query_db_json(db,select_sql)
    
       
    cond = {
    'PRODUCTS.p_category': 'object',
    'Class2PID.class_id': [0, 1, 2, 3]
    }
    
    query_data = fetch_data(db, tables=['Class2PID','PRODUCTS'], conditions_dict=cond, join_on=('Class2PID.p_id', 'PRODUCTS.p_id') )
    print(f" query_data 共讀取 {len(query_data)} 筆資料")
    print(query_data)
 
    emit('new_item_event', {'data': json.dumps(query_data) }, broadcast=False)
     

@socketio.on('new_item_event')   
def  trigger_new_item(msg):
     print('trigger new_item')
     
     #newitems=[{'pid':'1234','p_name':'拿鐵咖啡','p_price':50},
      #        {'pid':'1235','p_name':'焦糖咖啡','p_price':80}]
     newitems=[{ 'p_id': 2, 'p_name': '杏仁巧克力酥片', 'p_price': 50}]
     emit('new_item_event', {'data': json.dumps(newitems) }, broadcast=False)



#carter add
# 接收前端皆漲的資料F
@socketio.on('checkout_event')
def handle_checkout(data):
    items = data['items']
    print("接收到的购物明细：", items)
    print('共給筆：',len(items))
    # 进行数据库存储或其他操作
    #insert_order(db, items:list)
    insert_order(db, items)
if __name__ == '__main__':

    #socketio.run(app, debug=True, host='127.0.0.1', port=3000)

    class_product_tbl = fetch_data(db, tables=['Class2PID','PRODUCTS'], conditions_dict=None,join_on=('Class2PID.p_id', 'PRODUCTS.p_id') )
    print(f" query_data 共讀取 {len(class_product_tbl)} 筆資料")
    print(class_product_tbl)
    
    http_server = WSGIServer(('0.0.0.0', 5000), socketio.run(app, debug=True, host='127.0.0.1', port=3000))
    http_server.serve_forever()
    
 
