from lzma import FORMAT_ALONE
import socket
import json 
import time 
import requests
from datetime import datetime
from operator import index
from tkinter import*

#-----------------CLIENT--------------------
HOST = '127.0.0.1'
PORT = 65432
FORMAT = 'utf8'

#connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

#global var to continue client
click = ""

def connect_to_server():
    global click
    msg = "menu"
    s.sendall(msg.encode(FORMAT))
    msg = s.recv(1024).decode(FORMAT)
    if msg == "download":
        download_file()
        cp, cop, Total, cardNumber, numberTable = UI()

        #send table number
        msg = str(numberTable)
        s.sendall(msg.encode(FORMAT))
        s.recv(1024)
        #SEND CP
        send_cp(cp)
        #SEBD COP
        send_cop(cop)
        #SEND TOTAL
        msg = str(Total)
        s.sendall(msg.encode(FORMAT))
        s.recv(1024)
        #SEND CARD NUMBER
        msg = str(cardNumber)
        s.sendall(msg.encode(FORMAT))
        s.recv(1024)
        #sau khi thuc hien xong ,chuong trinh dang nhan tin nhan
        s.sendall(click.encode(FORMAT))
        
    s.close()  

def send_cp(cp): 
    for item in cp:
        s.sendall(str(item).encode(FORMAT))
        s.recv(1024)
    msg = "x"
    s.sendall(msg.encode(FORMAT))
    s.recv(1024)

def send_cop(cop):
    for item in cop:
        s.sendall(str(item).encode(FORMAT))
        s.recv(1024)
    msg = "x"
    s.sendall(msg.encode(FORMAT))
    s.recv(1024)

#Get data in file json
def get_menu():
    with open ('menu.json', 'r') as get_file:
        getData = json.load(get_file)
        get_file.close()
    return getData

def get_data_from_menu():
    menu = get_menu()
    milk_tea = []
    topping = [] 
    pr_milk_tea = []
    pr_topping = []
    note = []
    
    for item in menu["menu"]["milk tea"]:
        milk_tea.append(item["type"])
        pr_milk_tea.append(item["price"])
        note.append(item["note"])
    for item in menu["menu"]["topping"]:
        topping.append(item["type"])
        pr_topping.append(item["price"])

    return milk_tea, note, topping, pr_milk_tea, pr_topping

#---------------download menu from drive-------------------------------
def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_file():
    file_id = '1UmBCJsI5QChqJ6CkrzaqsAg-O3rSIbF2'
    destination = './menu.json'
    download_file_from_google_drive(file_id, destination)

#-------------GUI Client--------------------------------
def UI():
    #cái này là đống biến được server gửi qua nè
    milk_tea, note, topping, pr_milk_tea, pr_topping = get_data_from_menu()
    root = Tk()
    
    #variable in menu
    varTraSuaTruyenThong = StringVar()
    varTraSuaTranChau = StringVar()
    varTraSuaMatcha = StringVar()
    varTraSuaOreo = StringVar()
    varTranChau = StringVar()
    varRauCau = StringVar()
    varFlan = StringVar()
    varPudding = StringVar()
    varNumber=StringVar()
    varNumberTable=StringVar()

    varTraSuaTruyenThong.set(0)
    varTraSuaTranChau.set(0)
    varTraSuaMatcha.set(0)
    varTraSuaOreo.set(0)
    varTranChau.set(0)
    varRauCau.set(0)
    varFlan.set(0)
    varPudding.set(0)

    cardNumber = 0

    #set the menu
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')
    root.resizable(width=False,height=False)
    root.configure(background='light green')
    root.title("Food Order")

    # FRAMES                        
    Tops = Frame(root, width=1350, height=70, bd=12, relief="raise")
    Tops.pack(side=TOP)
    lblTitle = Label(Tops, font=("arial", 50, 'bold'), text="             Restaurant          ")
    lblTitle.grid(row=0, column=0)


    #   Date and Time  
    localtime = time.asctime(time.localtime(time.time()))
    lblInfo = Label(Tops, font=('arial', 20, 'bold'), text=localtime, bd=10, anchor='w')
    lblInfo.grid(row=1, column=0)

    BottomMainFrame = Frame(root, width=1200, height=1000, bd=12, relief=SUNKEN)
    BottomMainFrame.place(x=100,y=280)

    f1left = Frame(BottomMainFrame, width=500, height=550, bd=4, relief='raise')
    f1middle= Frame(BottomMainFrame,width=500,height=550,bd=4,relief='raise')
    f1right=Frame(BottomMainFrame,width=500,height=550,bd=4,relief='raise')
    f1temp=Frame(width=500,height=550,bd=4,relief='raise')
    f1temp1=Frame(width=500,height=550,bd=4,relief='raise')
    f1temp2=Frame(root,width=500,height=550,bd=4,relief='raise')
    f1menu=Frame(BottomMainFrame,width=500,height=550,bd=4,relief="raise")
    f1menu1=Frame(BottomMainFrame,width=500,height=550,bd=4,relief="raise")
    f1menu2=Frame(BottomMainFrame,width=500,height=550,bd=4,relief="raise")
    f1temp2.pack(side=TOP)
    #Nhaạp số bàn
   
    lblTable= Label(f1temp2, font=('arial', 22, 'bold'),text="Enter table number",bd=12,anchor="w")
    lblTable.grid(row=5, column=0)
    txtTable=Entry(f1temp2, font=('arial',22,'bold'),textvariable=varNumberTable,bd=12,insertwidth=8,bg="white",justify='right',width=16)
    txtTable.grid(row=5,column=1)
    lblWel= Label(f1temp2, font=('arial', 22, 'bold'),text="Welcome to my Restaurant",bd=12,anchor="w")
    lblWel.grid(row=2, column=1)
        
    #Số tài khoản
    def check():
        global click
        textvariable=varNumber
        if(len(varNumber.get())!=10):
            global cardNumber
            cardNumber = int(varNumber)
            print("Check again, Invalid account number")
        else :
            click = "card"
            root.destroy()
        
        
    #Trả bằng tiền
    def money():
        global click
        click = "money"
        root.destroy()
    # Total
    def total():
        if (varTraSuaTruyenThong.get() == ""):
            cp1 = 0
        else:
            cp1 = int(varTraSuaTruyenThong.get())

        if (varTraSuaTranChau.get() == ""):
            cp2 = 0
        else:
            cp2 = int(varTraSuaTranChau.get())

        if (varTraSuaMatcha.get() == ""):
            cp3 = 0
        else:
            cp3 = int(varTraSuaMatcha.get())

        if (varTraSuaOreo.get() == ""):
            cp4 = 0
        else:
            cp4 = int(varTraSuaOreo.get())

        if (varTranChau.get() == ""):
            cp5 = 0
        else:
            cp5 = int(varTranChau.get())

        if (varRauCau.get() == ""):
            cp6 = 0
        else:
            cp6 = int(varRauCau.get())

        if (varFlan.get() == ""):
            cp7 = 0
        else:
            cp7 = int(varFlan.get())

        if (varPudding.get() == ""):
            cp8 = 0
        else:
            cp8 = int(varPudding.get())

        cop1 = cp1 * 30000
        cop2 = cp2 * 35000
        cop3 = cp3 * 35000
        cop4 = cp4 * 40000

        cop5 = cp5 * 5000
        cop6 = cp6 * 5000
        cop7 = cp7 * 5000
        cop8 = cp8 * 10000

        subtotal = (cp1 + cp2 + cp3 + cp4 + cp5  +cp6 + cp7 + cp8)

        Total = (cop1 + cop2 + cop3 + cop4 + cop5 + cop6 + cop7 + cop8)

        varsubtotal.set(subtotal)
        varTotal.set(Total)

        cp = [cp1, cp2, cp3, cp4, cp5, cp6, cp7, cp8]
        cop = [cop1, cop2, cop3, cop4, cop5, cop6, cop7, cop8]
        return cp, cop, Total

    varsubtotal = StringVar()
    varTotal = StringVar()

    # Reset
    def reset():
        varTraSuaTruyenThong.set(0)
        varTraSuaTranChau.set(0)
        varTraSuaMatcha.set(0)
        varTraSuaOreo.set(0)
        varTranChau.set(0)
        varRauCau.set(0)
        varFlan.set(0)
        varPudding.set(0)
        varsubtotal.set(0)
        varTotal.set(0)
    # Exit
    def qexit():
        global click
        click = "exit" #request to exit
        root.destroy()

    def Cash():
        f1temp1.pack()
    
    # Pay
    def pay():
        f1temp.pack()
        btnCash=Button(f1temp,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Card",bg="aqua",command=Cash).grid(row=6,column=1)
        btnMoney=Button(f1temp,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Money",bg="pink",command=money).grid(row=7,column=1)

    
    def appear():
        f1menu.pack(side=LEFT)
        f1menu1.pack(side=LEFT)
        f1menu2.pack(side=RIGHT) 
        f1temp2.destroy()

        
       
    def order():
        f1left.pack(side=LEFT)
        f1middle.pack(side=LEFT)
        f1right.pack(side=RIGHT)
        f1menu.destroy()
        f1menu1.destroy()
        f1menu2.destroy()

    
    def number_table():
        if varNumberTable.get() != "":
            numberTable = int(varNumberTable.get())
        else:
            numberTable = 0

        return numberTable
    # Nhập số bàn  
    lblTable= Label(f1temp2, font=('arial', 22, 'bold'),text="Enter table number",bd=12,anchor="w")
    lblTable.grid(row=5, column=0)
    txtTable=Entry(f1temp2, font=('arial',22,'bold'),textvariable=varNumberTable,bd=12,insertwidth=8,bg="white",justify='right',width=16)
    txtTable.grid(row=5,column=1)
    lblWel= Label(f1temp2, font=('arial', 22, 'bold'),text="Welcome to my Restaurant",bd=12,anchor="w")
    lblWel.grid(row=2, column=1)

    starterscat= Label(f1left,text='        MILK TEA',font=('arial',30,'bold'))
    starterscat.grid()
    lblTraSuaTruyenThong= Label(f1left, font=('arial', 16, 'bold'),text= milk_tea[0],bd=5,anchor="w")
    lblTraSuaTruyenThong.grid(row=1, column=0)
    txtTraSuaTruyenThong=Entry(f1left, font=('arial',16,'bold'),textvariable=varTraSuaTruyenThong,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtTraSuaTruyenThong.grid(row=1,column=1)

    lblTraSuaTranChau= Label(f1left, font=('arial', 16, 'bold'),text=milk_tea[1],bd=5,anchor="w")
    lblTraSuaTranChau.grid(row=2, column=0)
    txtTraSuaTranChau=Entry(f1left, font=('arial',16,'bold'),textvariable=varTraSuaTranChau,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtTraSuaTranChau.grid(row=2,column=1)

    lblTraSuaMatcha= Label(f1left, font=('arial', 16, 'bold'),text=milk_tea[2],bd=5,anchor="w")
    lblTraSuaMatcha.grid(row=3, column=0)
    txtTraSuaMatcha=Entry(f1left, font=('arial',16,'bold'),textvariable=varTraSuaMatcha,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtTraSuaMatcha.grid(row=3,column=1)

    lblTraSuaOreo= Label(f1left, font=('arial', 16, 'bold'),text=milk_tea[3],bd=5,anchor="w")
    lblTraSuaOreo.grid(row=4, column=0)
    txtTraSuaOreo=Entry(f1left, font=('arial',16,'bold'),textvariable=varTraSuaOreo,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtTraSuaOreo.grid(row=4,column=1)

    maincoursecat= Label(f1middle,text='       TOPPING',font=('arial',30,'bold'))
    maincoursecat.grid()

    lblTranChau= Label(f1middle, font=('arial', 16, 'bold'),text=topping[0],bd=5,anchor="w")
    lblTranChau.grid(row=1, column=0)
    txtTranChau=Entry(f1middle, font=('arial',16,'bold'),textvariable=varTranChau,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtTranChau.grid(row=1,column=1)

    lblRauCau= Label(f1middle, font=('arial', 16, 'bold'),text=topping[1],bd=5,anchor="w")
    lblRauCau.grid(row=2, column=0)
    txtRauCau=Entry(f1middle, font=('arial',16,'bold'),textvariable=varRauCau,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtRauCau.grid(row=2,column=1)

    lblFlan= Label(f1middle, font=('arial', 16, 'bold'),text=topping[2],bd=5,anchor="w")
    lblFlan.grid(row=3, column=0)
    txtFlan=Entry(f1middle, font=('arial',16,'bold'),textvariable=varFlan,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtFlan.grid(row=3,column=1)

    lblPudding= Label(f1middle, font=('arial', 16, 'bold'),text=topping[3],bd=5,anchor="w")
    lblPudding.grid(row=4, column=0)
    txtPudding=Entry(f1middle, font=('arial',16,'bold'),textvariable=varPudding,bd=5,insertwidth=5,bg="white",justify='right',width=6)
    txtPudding.grid(row=4,column=1)


    cash=Label(f1temp,font=('arial', 30, 'bold'),text="Payment options",bd=2,anchor="w")
    cash.grid(row = 1,column =1)

    number=Label(f1temp1,font=('arial', 16, 'bold'),text="Enter account number: ",bd=3,anchor="w")
    number.grid(row=1, column=1)
    number=Entry(f1temp1, font=('arial',16,'bold'),textvariable=varNumber,bd=5,insertwidth=5,bg="wheat",justify='right',width=15)
    number.grid(row=1,column=2)

    #Menu
    starterscat1= Label(f1menu,text='        MILK TEA',font=('arial',30,'bold'))
    starterscat1.grid()
    lblTraSuaTruyenThong1= Label(f1menu, font=('arial', 16, 'bold'),text= milk_tea[0]+".....("+str(pr_milk_tea[0])+" VND)",bd=5,anchor="w")
    lblTraSuaTruyenThong1.grid(row=2, column=0)
   
    lblTraSuaTranChau1= Label(f1menu, font=('arial', 16, 'bold'),text=milk_tea[1]+".....("+str(pr_milk_tea[1])+" VND)",bd=5,anchor="w")
    lblTraSuaTranChau1.grid(row=3, column=0)
    
    lblTraSuaMatcha1= Label(f1menu, font=('arial', 16, 'bold'),text=milk_tea[2]+".....("+str(pr_milk_tea[2])+" VND)",bd=5,anchor="w")
    lblTraSuaMatcha1.grid(row=4, column=0)
    
    lblTraSuaOreo1= Label(f1menu, font=('arial', 16, 'bold'),text=milk_tea[3]+".....("+str(pr_milk_tea[3])+" VND)",bd=5,anchor="w")
    lblTraSuaOreo1.grid(row=5, column=0)
    
    maincoursecat1= Label(f1menu1,text='      TOPPING',font=('arial',30,'bold'))
    maincoursecat1.grid()

    lblTranChau1= Label(f1menu1, font=('arial', 16, 'bold'),text=topping[0]+".....("+str(pr_topping[0])+" VND)",bd=5,anchor="w")
    lblTranChau1.grid(row=2, column=0)
    
    lblRauCau1= Label(f1menu1, font=('arial', 16, 'bold'),text=topping[1]+".....("+str(pr_topping[1])+" VND)",bd=5,anchor="w")
    lblRauCau1.grid(row=3, column=0)
   
    lblFlan1= Label(f1menu1, font=('arial', 16, 'bold'),text=topping[2]+".....("+str(pr_topping[2])+" VND)",bd=5,anchor="w")
    lblFlan1.grid(row=4, column=0)
   
    lblPudding1= Label(f1menu1, font=('arial', 16, 'bold'),text=topping[3]+".....("+str(pr_topping[3])+" VND)",bd=5,anchor="w")
    lblPudding1.grid(row=5, column=0)
    




    #Total
    totalcat= Label(f1right,text='           Bill',font=('arial',30,'bold'))
    totalcat.grid()

    lblsubtotal= Label(f1right, font=('arial', 16, 'bold'),text="Amount",bd=5,anchor="w")
    lblsubtotal.grid(row=1, column=0)
    txtsubtotal=Entry(f1right, font=('arial',16,'bold'),textvariable=varsubtotal,bd=5,insertwidth=5,bg="white",justify='right',width=12)
    txtsubtotal.grid(row=1,column=1)

    lblTotal= Label(f1right, font=('arial', 16, 'bold'),text="Total",bd=5,anchor="w")
    lblTotal.grid(row=3, column=0)
    txtTotal=Entry(f1right, font=('arial',16,'bold'),textvariable=varTotal,bd=5,insertwidth=5,bg="white",justify='right',width=12)
    txtTotal.grid(row=3,column=1)

    # Button
    btnTotal=Button(f1right,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Total",bg="powder blue",command=total).grid(row=4,column=1)
    btnReset=Button(f1right,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Reset",bg="aquamarine",command=reset).grid(row=5,column=1)
    btnPay=Button(f1right,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Pay",bg="yellow",command=pay).grid(row=6,column=1)
    btnExit=Button(f1right,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=10,text="Exit",bg="red",command=qexit).grid(row=7,column=1)
    btnEnter=Button(f1temp1,padx=6,pady=6,bd=8,fg="black",font=('arial',16,'bold'),width=8,text="Enter",bg="orange",command=check).grid(row=1,column=3)
    btnEnterTable=Button(f1temp2,padx=16,pady=8,bd=16,fg="black",font=('arial',16,'bold'),width=12,text="Enter",bg="pink",command=appear).grid(row=5,column=3)
    btnOrder=Button(f1menu2,padx=16,pady=8,bd=16,fg="white",font=('arial',16,'bold'),width=8,text="Order",bg="black",command=order).grid(row=0,column=1)

    root.mainloop()
    cp, cop, Total = total()
    numberTable = number_table()
    return cp, cop, Total, cardNumber, numberTable


def main():
    connect_to_server()
    
if __name__ == "__main__":
    main()
    