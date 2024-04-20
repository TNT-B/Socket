import socket
import base64
import re 
import secrets
import os
import json
import time 
import threading
import sys
with open('config.json', 'r') as config_file:
        config = json.load(config_file)
def generate_boundary_string():
    # Generate a random string 16 characters long
    return secrets.token_urlsafe(16)
def split_base64_string(base64_string, chunk_size=76):
    return [base64_string[i:i+chunk_size] for i in range(0, len(base64_string), chunk_size)]
def sendMail():
    userEmail =config['General']['Username']
    print("This is the email confirmation information: (If the address is not available, please press enter to pass)")
    userTo = input("To: ")
    userCc=input("Cc:")
    userBcc=input("Bcc: ")
    userSubject = input("Enter Subject: ")
    userBody = input("Enter Message: ")
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver
    mailserver =config['General']['MailServer']
    mailPort = config['General']['SMTP']
    # Create socket called clientSocket and establish a TCP connection with mailserver
    #Fill in start
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientSocket.connect((mailserver, mailPort))
    #Fill in end
    recv = clientSocket.recv(1024).decode()
    #print(recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')
    # Send HELO command and print server response.
    heloCommand = 'HELO HCMUS\r\n'
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024).decode()
    #print(recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')

    # Send MAIL FROM command and print server response.
    # Fill in start
    mailFrom = "MAIL FROM: <{}>\r\n".format(userEmail)
    clientSocket.send(mailFrom.encode())
    recv5 = clientSocket.recv(1024).decode()
    #print(recv5)
    
    # Fill in start
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern,userTo)
    if userTo !='':
        for match in matches:
            rcptto = "RCPT TO: <{}>\r\n".format(match)
            clientSocket.send(rcptto.encode())
            response = clientSocket.recv(1024).decode()
            #print(response)
    
    # Gửi lệnh RCPT TO để chỉ định người nhận (Cc)
    matches = re.findall(email_pattern,userCc)
    if userCc !='':
        for match in matches:
            rcptCc = "RCPT TO: <{}>\r\n".format(match)
            clientSocket.send(rcptCc.encode())
            response = clientSocket.recv(1024)
            #print(response)

    # Gửi lệnh RCPT TO để chỉ định người nhận (Bcc)
    matches = re.findall(email_pattern,userBcc)
    if userBcc != '':
        for match in matches:
            rcptBcc = "RCPT TO: <{}>\r\n".format(match)
            clientSocket.send(rcptBcc.encode())
            response = clientSocket.recv(1024)
            #print(response)
    
    data = 'DATA\r\n'
    clientSocket.send(data.encode())
    response=clientSocket.recv(1024)
    if userTo :
        To_send="To: {}\r\n".format(userTo)
        clientSocket.send(To_send.encode())
    if userCc:
        Cc_send="Cc: {}\r\n".format(userCc)
        clientSocket.send(Cc_send.encode())
    User_address=f'From: {userEmail}\r\n'
    clientSocket.send(User_address.encode())
    
    #Gui file bang giao thuc MIME
    sendfile=input("Co gui kem file dinh kem khong(1 co 2 khong): ")

    if sendfile=='2':   
        clientSocket.send(f"Subject: {userSubject}\r\n\r\n{userBody}".encode())
        clientSocket.send(endmsg.encode())
        response=clientSocket.recv(1024)
        #print(response)    
    elif sendfile =='1':
        number_file=input('So luong luong file muon gui: ')
        if int(number_file) >=1:
            i=1
            boundary_string = generate_boundary_string()
            # Thêm thông tin về tệp đính kèm vào nội dung email
            email_content = f'Subject: {userSubject}\r\n'
            email_content += f'MIME-Version: 1.0\r\n'
            email_content += f'Content-Type: multipart/mixed; boundary={boundary_string}\r\n\r\n'
            email_content += f'--{boundary_string}\r\nContent-Type: text/plain\r\n\r\n{userBody}\r\n\r\n'
            while i<=int(number_file):
                # Tên tệp cần đính kèm
                attachmentpath=input(f"Cho biet duong dan thu {i}:")
                # Đọc nội dung tệp
                attachmentpath=attachmentpath.replace('"','')
                max_attachment_size_mb=3
                file_size_mb = os.path.getsize(attachmentpath) / (1024 * 1024)
                if file_size_mb > max_attachment_size_mb:
                    print(f"Kich thuoc tep vuot qua {max_attachment_size_mb} MB. Khong the gui")
                    print("Vui long nhap lai duong dan\n")      
                else:
                    # Sử dụng os.path.basename() để lấy tên tệp
                    filename = os.path.basename(attachmentpath)
                    with open(attachmentpath, 'rb') as file:
                        attachment_data = file.read()
                    base64_encoded_data = base64.b64encode(attachment_data).decode()
                    # Chia base64 thành các dòng nhỏ
                    chunks = split_base64_string(base64_encoded_data)
                    email_content += f'--{boundary_string}\r\nContent-Type: application/octet-stream\r\n'
                    email_content += f'Content-Transfer-Encoding: base64\r\n'
                    email_content += f'Content-Disposition: attachment;\r\n filename="{filename}"\r\n\r\n'
                    for chunk in chunks:
                        email_content += f'{chunk}\r\n'
                    i+=1
            email_content += f'--{boundary_string}--'
            # Gửi nội dung email
            clientSocket.sendall(email_content.encode())
            end='\r\n.\r\n'
            clientSocket.send(end.encode())
            response = clientSocket.recv(1024)
            #print(response.decode()) 
    
    print("Da gui email ")
    # Send QUIT command and get server response.
    # Fill in start
    quitCMD = 'QUIT\r\n'
    clientSocket.send(quitCMD.encode())
    recv9 = clientSocket.recv(1024).decode()
    #print(recv9)
    clientSocket.close()
    
def receive_data(sock,skip_ok=True):
    data = b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
        if b"\r\n" in data:
            break
    return data

def pop3_login(sock, username, password):
    username=config['General']['Username']
    password=config['General']['Password']
    receive_data(sock)  # Nhận banner từ máy chủ
    sock.sendall(b"USER " + username.encode() + b"\r\n")
    receive_data(sock)
    sock.sendall(b"PASS " + password.encode() + b"\r\n")
    receive_data(sock)

def pop3_list(sock):
    sock.sendall(b"LIST\r\n")
    response = receive_data(sock)
    lines = response.decode("utf-8").split("\r\n")[0:-2]
    email_info = [line.split()[0] for line in lines]
    return email_info

def pop3_retr(sock, email_number,skip_ok=True):
    sock.sendall(f"RETR {email_number}\r\n".encode())
    response = sock.recv(1024).decode()
    # Đọc phần nội dung email
    
    email_content = response
    if response.startswith("+OK"):
        while True:
            if response.startswith(".\r\n"):
                break
            if len(response)<1024:
                break
            response = sock.recv(1024).decode()
            email_content += response
    #xoa ca dong +OK ....
    email_content = re.sub(r'.*OK.*\n?', '', email_content)
    
    return email_content
def pop3_stat(sock):
    # Gửi lệnh STAT đến máy chủ
    sock.sendall(b"STAT\r\n")
    # Nhận và giải mã phản hồi từ máy chủ
    response = sock.recv(1024).decode("utf-8").strip()
    # In thông tin trạng thái
    #print(f"Server Response: {response}")
    # Phân tích phản hồi để lấy số lượng email và tổng kích thước
    if response.startswith("+OK"):
        #_ la ki tu +OK 
        _, num_emails,_= response.split()#response.split()=['+OK', '2', '940']
    else:
        print("Failed to retrieve status information.")
    return int(num_emails)

def save_email_to_file(email_content, filename):
    with open(filename, "wb") as file:
        file.write(email_content)

def decode_base64(encoded_data):
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data  
     
def extract_email_info(email_content):
    # Decode the "To", "From" and "Subject" headers
    to_index= email_content.find('To:')
    endTo_index = email_content.find("\r\n",to_index)
    from_index = email_content.find("From:")
    end_from = email_content.find("\r\n",from_index)
    from_header = email_content[from_index:end_from].replace("From:", "").strip()
    subject_index = email_content.find("Subject:")
    end_index = email_content.find("\r\n",subject_index)
    subject_header = email_content[subject_index:end_index].replace("Subject:", "").strip()
    To_header =email_content[to_index:endTo_index].replace("To:", "").strip()
    Cc_header=''
    boundary=""
    if email_content.find('Cc:')!=-1:
        Cc_index=email_content.find('Cc:')
        endCc_index = email_content.find("\r\n",Cc_index)
        Cc_header=email_content[Cc_index:endCc_index].replace("Cc:","").strip()
    
    main_body=""
    #Tim Vi tri cua Main body
    if email_content.find('Content-Type: multipart') != -1:
        first_boundary = email_content.find('boundary=')
        end_boundary=email_content.find('\r\n',first_boundary)
        boundary=email_content[first_boundary:end_boundary].replace("boundary=", "").replace('"','').strip()
        boundary=f"--{boundary}"
        main_body = email_content.split(boundary)[1]
        main_body= ''.join(main_body)
        start_body=main_body.find('Content-Type: text/plain')
        end_body=main_body.find('\r\n',start_body)
        main_body=main_body[end_body:].strip('\r\n\r\n')

    else:
        main_body=email_content.split("\r\n\r\n")[1]
    return To_header,from_header,subject_header,main_body,Cc_header,boundary
def apply_filters(email, filters):
    for filter_rule in filters["filters"]:
        criteria = filter_rule["criteria"]
        destination = filter_rule["destination"]
        # Kiểm tra tiêu chí từ địa chỉ nguồn
        if "from" in criteria and email["from"] in criteria["from"]:
            return destination
        
        # Kiểm tra tiêu chí từ chủ đề
        if "subject" in criteria and any(keyword in email["subject"] for keyword in criteria["subject"]):
            return destination
        
        # Kiểm tra tiêu chí từ nội dung
        if "content" in criteria and any(keyword in email["content"] for keyword in criteria["content"]):
            return destination
        
        # Kiểm tra tiêu chí từ chủ đề hoặc nội dung
        if "$or" in criteria and any(keyword in email["subject"] or keyword in email["content"] for keyword in criteria["$or"]):
            # Thực hiện các hành động khi điều kiện đúng
            return destination
    return "Inbox"

def autoloadEmail(interval):
    interval=config['General']['Autoload']
    while True:
        downloadEmail()
        time.sleep(interval)

def downloadEmail():
    server=config['General']['MailServer']
    port=config['General']['POP3']
    with socket.create_connection((server, port)) as sock:
        username=config['General']['Username']
        password=config['General']['Password']
        pop3_login(sock, username, password)
        num_messages=pop3_stat(sock)
        for i in range(1,num_messages+1):
            folder_path=config['Email']['Inbox']
            email_content=pop3_retr(sock,i)
            to_header,from_header,subject_header,main_body,Cc_header,_=extract_email_info(email_content)
            # Lưu trữ nội dung email
            filename=f'email_{i}.eml'
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern,from_header)
            # Áp dụng filter cho email
            email = {
                "from": f'{from_header}',
                "subject": f'{subject_header}',
                "content": f'{main_body}'
            }
            result = apply_filters(email, config)
            if result == 'Project':
                folder_path = config['Email']['Project']
            elif result== 'Spam':
                folder_path = config['Email']['Spam']
            elif result == 'Work':
                folder_path = config['Email']['Work']
            elif result == 'Important':
                folder_path = config['Email']['Important']
            else:
                folder_path = config['Email']['Inbox']
            #print(result)    
            folder_path+=f'\\{matches[0]}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            else:
                if not os.path.exists(folder_path+f'\\{filename}'):
                    file_path =folder_path+f'\\{filename}'
                    #email_content = re.sub(r'.*\..*\n?', '', email_content)
                    with open(file_path, 'w') as file:
                        file.write(email_content)
    
def readEmail(username=config['General']['Username'], password=config['General']['Password']):
    # Đọc thông tin cấu hình từ file JSON
    server=config['General']['MailServer']
    port=config['General']['POP3']
    with socket.create_connection((server, port)) as sock:
        #Dang nhap vao gmail de doc email
        pop3_login(sock, username, password)
        # Lấy số lượng email
        num_messages=pop3_stat(sock)
        print("Day la danh sach folder trong mailbox: ")
        # Retrieve the "From" and "Subject" headers for the first email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        print('1.Inbox')
        print('2.Project')
        print('3.Important')
        print('4.Work')
        print('5.Spam')
        choose=input("Ban muon xem Email trong folder nao:(Nhap enter de thoat ra ngoai) ") 
        while choose =='1' or choose =='2' or choose == '3' or choose == '4' or choose == '5':
            INBOX=[]
            PROJECT=[]
            IMPORTANT=[]
            WORK=[]
            SPAM=[]
            for i in range(1,num_messages+1):
                email_content=pop3_retr(sock,i)
                to_header,from_header,subject_header,main_body,Cc_header,boundary=extract_email_info(email_content)
                email = {
                    "from": f'{from_header}',
                    "subject": f'{subject_header}',
                    "content": f'{main_body}'
                }
                #add email tu server thanh cac thu muc cu the
                result = apply_filters(email, config)
                if result=='Inbox':
                    INBOX.append(email_content)
                elif result=='Project':
                    PROJECT.append(email_content)
                elif result=='Important':
                    IMPORTANT.append(email_content)
                elif result=='Work':
                    WORK.append(email_content)
                elif result=='Spam':
                    SPAM.append(email_content)
            if choose == '1':
                folder=INBOX
            elif choose == '2':
                folder=PROJECT
            elif choose == '3':
                folder =IMPORTANT
            elif choose == '4':
                folder= WORK
            elif choose== '5':
                folder=SPAM

            if(len(folder))>0:
                boundary=""
                for i in range(1,len(folder)+1):
                    to_header,from_header,subject_header,main_body,Cc_header,boundary=extract_email_info(folder[i-1])
                    matches = re.findall(email_pattern,from_header)
                    print(f"{i}<{matches[0]}>, <{subject_header}>")
                    #rint(main_body)
                choose=(input("Ban muon doc email thu may: "))
                try:
                    choose = int(choose)
                except ValueError:
                    print("Gia tri khong hop le chuong trinh da thoat.")
                    sys.exit()
                choose=int(choose)
                print(f"Noi dung cua email thu {choose} la: ")
                #email_content=pop3_retr(sock,choose)
                if choose<=len(folder) and choose>0:
                    to_header,from_header,subject_header,main_body,Cc_header,boundary=extract_email_info(folder[choose-1])
                    print("Day la noi dung email ban muon doc: ")
                    print(f"\r\nTo: {to_header}")
                    if Cc_header!='':
                        print(f'Cc: {Cc_header}')
                    print(f"Subject: {subject_header}")
                    print(f"From: {from_header}\r\n")
                    print(f"{main_body}\r\n")
                    
                    if folder[choose-1].find('Content-Type: multipart/mixed;')!=-1:
                        #lay phan tep dinh kem da duoc ma hoa
                        parts=folder[choose-1].split(f'{boundary}')[2:] 
                        choose=input('Trong email nay co attached file ban co muon luu khong(y/n)')
                        if choose == 'y'or choose=='Y':
                            for part in parts:
                                if part.find('Content-Disposition: attachment;') !=-1:
                                    lines=part.split('\r\n')
                                    # Vòng lặp qua các dòng trong danh sách lines
                                    for line in lines:
                                        if line.startswith(' filename'):
                                            start_filename=line.find('filename=')+len('filename=')
                                            end_filename=line.find('\r\n',start_filename)
                                            filename=line[start_filename:end_filename].replace('"','').strip()
                                            start_index = lines.index(line) + 2
                                            # Gộp các dòng chứa dữ liệu mã hóa Base64 thành một chuỗi
                                            base64_data = ''.join(lines[start_index:])
                                            # Giải mã dữ liệu và lưu vào biến attachment_data
                                            attachment_data = base64.b64decode(base64_data)
                                            folder_path=input('Nhap duong dan muon luu:')
                                            folder_path=folder_path.replace('"','').strip()
                                            # Ghi dữ liệu vào tệp tin
                                            folder_path+=f'\\{filename}'
                                            with open(folder_path, 'wb') as f:
                                                f.write(attachment_data)
                                            print(f"attached file '{filename}' Da luu thanh cong")                
                else:
                    print("Khong hop le vui long nhap lai ")
            else:
                print(" Thu muc rong ")
            print('1.Inbox')
            print('2.Project')
            print('3.Important')
            print('4.Work')
            print('5.Spam')
            choose=input('Ban muon xem trong folder nao: (Nhan enter de thoat ra ngoai) ')
        sock.sendall(b"QUIT\r\n")
        response=sock.recv(1024).decode()
        #print(response)
# Fill in end
def main():
    # Tạo một luồng để thực hiện việc tải email định kỳ
    thread = threading.Thread(target=autoloadEmail, args=(10,))
    thread.start()
    print("Vui long chon menu:")
    print("1.De gui Email")
    print("2.De xem danh sach email da nhan")
    print("3.Thoat ")
    choose=input("Ban chon: ")
    if choose.strip() == "":
        print("Ban chua nhap gia tri chuong trinh da thoat")
        sys.exit()
    try:
        choose = int(choose)
        if choose ==3:
                print("Chuong trinh da thoat ") 
                sys.exit()
    except ValueError:
        print("Gia tri khong hop le chuong trinh da thoat.")
        sys.exit()
    while True :
        
        if choose == 1:
            sendMail()
        elif choose==2:
            readEmail() 
        print("Vui long chon menu:")
        print("1.De gui Email")
        print("2.De xem danh sach email da nhan")
        print("3.Thoat ")
        choose=input("Ban chon: ")
        try:
            choose = int(choose)
            # Xử lý logic với giá trị đã nhập
            if choose ==3:
                print("Chuong trinh da thoat ") 
                sys.exit()
        except ValueError:
            print("Gia tri khong hop le chuong trinh da thoat.")
            thread.join()
            sys.exit()
    
if __name__=="__main__":
    main()
