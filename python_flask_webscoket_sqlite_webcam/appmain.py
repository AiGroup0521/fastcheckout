'''
 SELECT 
            M.o_id, M.o_date, M.o_total, D.o_no, D.p_id, D.p_name, D.p_price, D.p_qty
        FROM 
            ORDER_M M
        JOIN 
            ORDER_D D ON M.o_id = D.o_id
        WHERE
            M.o_date BETWEEN ? AND ?
            ['訂單編號', '訂單日期', '結帳金額', '商品序號', '商品編號', '商品名稱', '商品單價', '商品數量']
'''

from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime
import json
import cv2
from ultralytics import YOLO
from PIL import Image
from gevent.pywsgi import WSGIServer
import pandas as pd
from db import *
from sqlite_utils import *
import os
#names: {0: 'Lollipop', 1: 'cookie', 2: 'fruit', 3: 'noodles'}

app = Flask(__name__,static_folder='web/')

# http://127.0.0.1:3000

@app.route('/')
def index():
   #return render_template('index.html')
   return app.send_static_file('index.html')
    
 
@app.route('/video')
def goto_video():
    return render_template('html5_camera_1_1.html')
    
@app.route('/item')
def get_item():
   #return render_template('index.html')
  return render_template('viewreport02.html')

# Open the camera
camera = cv2.VideoCapture(1)
#model = YOLO('model/yolov8s.pt')
model = YOLO('model/best-m400.pt')


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
     newitems=[{ 'p_id': 2, 'p_name': '杏仁巧克力酥片', 'p_price': 50}]
     emit('new_item_event', {'data': json.dumps(newitems) }, broadcast=False)



#carter add
# 接收前端皆漲的資料F
@socketio.on('checkout_event')
def handle_checkout(data):
    items = data['items']
    print("接收到的購物明细：", items)
    print('共給筆：',len(items))
    # 进行数据库存储或其他操作
    #insert_order(db, items:list)
    insert_order(db, items)
    emit('order_saved', {'status': '訂單已成功存檔！'}, broadcast=True)
    
#carter add
@app.route('/download', methods=['GET'])
def download():
    global current_order_details
    if not current_order_details:
        return "No order details available to download.", 400
    
    try:
        order_id = current_order_details['order_id']
        order_date = current_order_details['order_date']
        details_df = current_order_details['details']
        total_amount = current_order_details['total_amount']
        
        filename = f"order_{order_id}.xlsx"
        filepath = os.path.join('downloads', filename)
        
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('OrderDetails')
            
            # Format for bold text
            bold = workbook.add_format({'bold': True})
            
            # Write order ID and date
            worksheet.write(0, 0, f'訂單編號: {order_id}', bold)
            worksheet.write(1, 0, f'訂單日期: {order_date}', bold)
            
            # Write the dataframe to the worksheet, starting from row 3 to avoid overlap
            details_df.to_excel(writer, sheet_name='OrderDetails', startrow=3, index=False)
            
            # Format the header row
            for col_num, value in enumerate(details_df.columns.values):
                worksheet.write(3, col_num, value, bold)
            
            # Write the total amount
            worksheet.write(len(details_df) + 4, 0, '結帳金額', bold)
            worksheet.write(len(details_df) + 4, 1, total_amount)
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        print(f"Error generating Excel file: {e}")
        return f"Error generating Excel file: {e}", 500

@socketio.on('search')
def handle_search(data):
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    conn = sqlite3.connect(DataBase)
    query = '''
        SELECT 
            M.o_id, M.o_date, M.o_total
        FROM 
            ORDER_M M
        JOIN 
            ORDER_D D ON M.o_id = D.o_id
        WHERE
            M.o_date BETWEEN ? AND ?
        GROUP BY M.o_id, M.o_date, M.o_total
    '''
    try:
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        
        df.columns = ['訂單編號', '訂單日期', '金額']
        
        if df.empty:
            emit('search_results', {'results': []})
        else:
            orders = df.to_dict('records')
            emit('search_results', {'results': orders})
    except Exception as e:
        print(f"Error executing query: {e}")
        emit('search_results', {'results': f"Error executing query: {e}"})
    finally:
        conn.close()
current_order_details = {}
@socketio.on('get_order_details')
def handle_order_details(data):
    global current_order_details
    o_id = data['o_id']
    conn = sqlite3.connect(DataBase)
    query = '''
        SELECT p_id, p_name, p_price, SUM(p_qty) as total_qty
        FROM ORDER_D
        WHERE o_id = ?
        GROUP BY p_id, p_name, p_price
    '''
    try:
        df = pd.read_sql_query(query, conn, params=(o_id,))
        df['商品序號'] = df.index + 1  # Adding a new column for '商品序號'
        df['金額'] = df['p_price'] * df['total_qty']  # Calculating the amount for each item
        total_amount = df['金額'].sum()
        
        df = df[['商品序號', 'p_id', 'p_name', 'p_price', 'total_qty', '金額']]  # Reordering columns
        
        df.columns = ['商品序號', '商品編號', '商品名稱', '商品單價', '商品數量', '金額']  # Renaming columns
        
        if df.empty:
            emit('order_details', {'details': 'No data found.'})
        else:
            details_html = df.to_html(index=False)
            details_html += f'<p>結帳金額: {total_amount}</p>'
            # Fetching order date
            order_query = 'SELECT o_date FROM ORDER_M WHERE o_id = ?'
            order_date = pd.read_sql_query(order_query, conn, params=(o_id,)).iloc[0, 0]
            current_order_details = {'order_id': o_id, 'order_date': order_date, 'details': df, 'total_amount': total_amount}
            emit('order_details', {'details': details_html, 'order_id': o_id, 'order_date': order_date})
    except Exception as e:
        print(f"Error executing query: {e}")  # Debug line
        emit('order_details', {'details': f"Error executing query: {e}"})
    finally:
        conn.close()


if __name__ == '__main__':

    #socketio.run(app, debug=True, host='127.0.0.1', port=3000)

    class_product_tbl = fetch_data(db, tables=['Class2PID','PRODUCTS'], conditions_dict=None,join_on=('Class2PID.p_id', 'PRODUCTS.p_id') )
    print(f" query_data 共讀取 {len(class_product_tbl)} 筆資料")
    print(class_product_tbl)
    
    http_server = WSGIServer(('0.0.0.0', 5000), socketio.run(app, debug=True, host='127.0.0.1', port=3000))
    http_server.serve_forever()
    
 

