from os import access
from pkgutil import get_data
import socket 
import json 
import threading
from datetime import datetime
import time
import requests
import os 

#----------------SERVER------------------------------------------------------------------------------
HOST = '127.0.0.1'
PORT = 65432
FORMAT = 'utf8'

#global var 
status = ""
table_number = 0
cp = []
cop = []
total = 0
cardNumber = 0

#-------------------------------Data base------------------------------------
#Get information in menu from Json and print 
def upload_menu_to_drive():
    headers = {"Authorization": "Bearer ya29.A0ARrdaM_0cmaSfSu_CDu5cemdkqyCRFrT4rR1EJXxzKHqE_pVD8EdsgIHpzSr8NyNp0KUqo7dCMIIjWN_W0jvFqeWTj9LXBCazrVD7us_wg41TFrODGRBfS0z04aOxYeNqfYvCDRVG5qcA6Dce3j-Y6EIN4ltYUNnWUtBVEFTQVRBU0ZRRl91NjFWS1JoQ2ZzSy1RRVkzdlhVWkxraWpiUQ0163"}
    para = {
        "name": "menu.json",
        "parents": ["1IDTkOkKY4bfFrZQGlIJ7CqBZniyf-fQU"]
    }
    files = {
        'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
        'file': open("./menu.json", "rb")
    }
    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )
    r.text

#---------------TCP SERVER-----------------------
def handle_client(conn: socket, addr):    #conn, addr
        global table_number, cp, cop, total, cardNumber
        print(addr , "connnected")
        click = conn.recv(1024).decode(FORMAT)
        print(addr, click)
        if click == "menu":
            msg = "download"
            conn.sendall(msg.encode(FORMAT))
            #RECV TABLE NUMBER 
            msg = conn.recv(1024).decode(FORMAT)
            table_number = int(msg)
            conn.sendall(str(msg).encode(FORMAT))
            #RECV CP
            cp = recv_cp(conn)
            #RECV COP
            cop = recv_cop(conn)
            #RECV TOTAL
            msg = conn.recv(1024).decode(FORMAT)
            total = int(msg)
            conn.sendall(str(msg).encode(FORMAT))
            #RECV CARD NUMBER
            msg = conn.recv(1024).decode(FORMAT)
            cardNumber = int(msg)
            conn.sendall(str(msg).encode(FORMAT))
            #sau khi thuc hien xong, chuong trinh dang gui tin nhan
        
        click = conn.recv(1024).decode(FORMAT)
        print(addr, click)
        if click == "exit":
            global status
            status = "unpaid"
        elif click == "money" or click == "cash":
            status = "paid"

        #Kiểm tra số bàn, nếu đặt lại trong 2h sẽ được dặt thêm
        valid, data = check_file(table_number)
        if valid == True:
            update_data_after_2hours(data, table_number)
        else:
            data_base()
        if click:
            print(addr, "end")
         


#-------------------------get data from client-----------------------
def recv_cp(conn):
    cp = []
    msg = None
    while msg != "x":
        msg = conn.recv(1024).decode(FORMAT)
        if msg != "x":
            cp.append(int(msg))
        conn.sendall(str(msg).encode(FORMAT))
    return cp

def recv_cop(conn):
    cop = []
    msg = None
    while msg != "x":
        msg = conn.recv(1024).decode(FORMAT)
        if msg != "x":
            cop.append(int(msg))
        conn.sendall(str(msg).encode(FORMAT))
    return cop


#----------------------data base----------------------
#Get date and time currently
def get_time():
    now = datetime.now()
    date = datetime.today()

    curr_time = {}
    curr_time['hour'] = now.hour
    curr_time['minutes'] = now.minute
    curr_time['second'] = now.second

    curr_date = {}
    curr_date['day'] = date.day
    curr_date['month'] = date.month  
    curr_date['year'] = date.year

    return curr_time, curr_date

def update_data():
    with open ('order.json', 'r') as f:
        data = json.load(f)
        f.close()
    global status, cardNumber, cp, cop, total, table_number
    data["bill"]["status"] = status
    data["bill"]["total money"] = total
    data["bill"]["card number"] = cardNumber
    data["bill"]["id"] = table_number
    index = 0
    for item in data["bill"]["milk tea"]:
        if (index > 3):
            break
        item["amount"] = cp[index]
        item["into money"] = cop[index]
        index += 1
    
    index = 4
    for item in data["bill"]["topping"]:
        if (index > 7):
            break
        item["amount"] = cp[index]
        item["into money"] = cop[index]
        index += 1

    return data

#Save data to Json 
def save_data_to_Json(): 
    update_time, update_date = get_time()
    new_data = update_data()
    global table_number
    new_data["bill"]["date"] = update_date
    new_data["bill"]["time"] = update_time
    filename=f"Data/{table_number}_{update_date['day']}.{update_date['month']}.{update_date['year']}.json"
    with open (filename, 'w') as write_file:
        json.dump(new_data, write_file, indent= 2)
        write_file.close()

#kiểm tra xem file có tồn tại hay không
def check_file(tableNumber):
    time, date = get_time()

    filename = f"Data/{tableNumber}_{date['day']}.{date['month']}.{date['year']}.json"
    if os.path.isfile(filename) == True:
        with open (filename, "r") as read_file:
            data = json.load(read_file)
            read_file.close()
        return True, data
    else:
        data = None
        return False, data

#kiểm tra xem nếu thời gian nhỏ hơn 2h, thì sẽ được đặt thêm và lưu vào cơ sở dữ liệu
def update_data_after_2hours(data, tableNumber):
    time, date = get_time()
    hour_in_data = data["bill"]["time"]["hour"]
    hour_real_time = time["hour"]
    
    gap_time = abs(hour_real_time - hour_real_time)

    filename =  f"Data/{tableNumber}_{date['day']}.{date['month']}.{date['year']}_update.json"
    
    global cp, cop, total, cardNumber
    if gap_time < 2:
        data["bill"]["total money"] += total
        data["bill"]["card number"] += cardNumber
        index = 0
        for item in data["bill"]["milk tea"]:
            if (index > 3):
                break
            item["amount"] += cp[index]
            item["into money"] += cop[index]
            index += 1
        index = 4
        for item in data["bill"]["topping"]:
            if (index > 7):
                break
            item["amount"] += cp[index]
            item["into money"] += cop[index]
            index += 1
        
        with open (filename, "w") as write_file:
            json.dump(data, write_file, indent=2)
            write_file.close()
    else:
        data_base()


def data_base():
    update_data()
    save_data_to_Json()

def main():
    #config server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)

    print("WATING TO CLIENT")
    print("Ready to get order")
    try:
        nClient = 0
        while True:
            if nClient == 5:
                break
            conn, addr = s.accept()
            thr = threading.Thread(target=handle_client, args=(conn, addr))
            thr.daemon = False
            thr.start()
            nClient+=1
    except:
        conn.close()
        print("Error")
    finally:
        print("End app")
        conn.close()
    s.close()


if __name__ == "__main__":
    main()