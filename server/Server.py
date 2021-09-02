#------------------------------------------------------------------
# Names: Mohammed Hocho, Joshua Froese, Meron Tesfazghi
#------------------------------------------------------------------

import json
import socket
import os,glob
import sys
import datetime
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
def store(data):
    source = data['From']
    dst = data['To']
    replicate = dict(data)
    #store the content in a file
    for i in range(len(dst)):
        clientFolder = os.getcwd() + '/' + dst[i]
        if os.path.exists(clientFolder) == False:
            os.mkdir(clientFolder)
        
        contentFile = clientFolder + '/' + source + '_' + data['Title']  + '.txt'
        contentWrite = open(contentFile, 'w')
        contentWrite.write(data['Content'])
    
    for j in range(len(dst)):
        clientFolder = os.getcwd() + '/' + dst[j]
        
        inboxFile = clientFolder + '/' + 'inbox.txt'
        
        replicate = dict(data)
        del replicate['Content']
        #replicate ['To'] = dst[j]
        
        inboxDict = {}
        inboxDict['inbox'] = []         
        if os.path.exists(inboxFile):
            openInbox = open(inboxFile, 'r').read()
            if len(openInbox) > 0:
                inboxDict = json.loads(openInbox)        
            print('exists')
                        
        inboxDict['inbox'].append(replicate)
        
        try:
            inboxWrite = open(inboxFile, 'w')
            dictToStr = json.dumps(inboxDict)
            inboxWrite.write(dictToStr)
        except:
            print("error writing")
    
# returns an encrypted message
def encryptMessage(key, message):
    # Generate Cyphering Block
    cipher = AES.new(key, AES.MODE_ECB)
    # Encrypt the message
    return cipher.encrypt(pad(message.encode('ascii'),16))

# returns an decrypted message
def decryptMessage(key, ct_bytes):
    # Generate Cyphering Block
    cipher = AES.new(key, AES.MODE_ECB)
    # Decrypting the message
    Padded_message = cipher.decrypt(ct_bytes)
    Encodedmessage = unpad(Padded_message,16)
    return Encodedmessage.decode('ascii')

#decrypt RSA using server private key
def decryptFromClientRSA(message):
    privateKey = RSA.import_key(open("server_private.pem", "rb").read())
    privateCipher = PKCS1_OAEP.new(privateKey)
    decrptedMsg = privateCipher.decrypt(message)
    return decrptedMsg.decode('ascii')

#generate 256bit AES key
def generate_sym():
    KeyLen = 256
    key = get_random_bytes(int(KeyLen/8))
    return key

def server():

    serverPort = 13000 #Server port
    menuMessage = "Select the operation:\n\
    1) Create and send an email\n\
    2) Display the inbox list\n\
    3) Display the email contents\n\
    4) Terminate the connection\n\n\
    choice: "

    #Create server socket
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Associate port number to the server socket
        serverSocket.bind(('', serverPort))
    except socket.error as e:
        print('Error in server socket creation or binding: ',e)
        sys.exit(1)

    #server is now ready to listen to five clients at the same time
    serverSocket.listen(5)
    print("The server is ready to accept connections")

    while 1:
        try:
            #Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            id = os.fork()
            if id == 0: #child process
                serverSocket.close()
                
                #receive username from client and decrypt
                username = connectionSocket.recv(2048)
                username = decryptFromClientRSA(username)
                
                
                connectionSocket.send("username".encode('ascii'))#sync
                
                #receive password from client and decrypt
                password = connectionSocket.recv(2048)
                password = decryptFromClientRSA(password)
                try:
                    f = open("user_pass.json", "r") #open json file
                    data = json.load(f) # get json file as a dict
                    f.close()
                    if username in data:
                        if data[username] != password:
                            invalid = "Invalid username or password"
                            connectionSocket.send(invalid.encode('ascii'))
                            print(f"The received client information: {username} is invalid (Connection Terminated).")
                            connectionSocket.close() #Server terminates client connection
                            return                            
                        #generate sym keyencrypt
                        sym_key = generate_sym() 
                        file = os.getcwd()+"/"+str(username)+"_public.pem"
                        clientPub = RSA.import_key(open(file, 'rb').read())
                        rsa_cipher = PKCS1_OAEP.new(clientPub)
                        encrypted_sym = rsa_cipher.encrypt(sym_key)
                        connectionSocket.send(encrypted_sym)
                       
                        print(f"Connection Accepted and Symmetric Key Generated for client: {username}")
                        
                              
                    else:
                        invalid = "Invalid username or password"
                        connectionSocket.send(invalid.encode('ascii'))                        
                        print(f"The received client information: {username} is invalid (Connection Terminated).")
                        connectionSocket.close() #Server terminates client connection
                        return   
                    #wait for OK message
                    encrypted_OK = connectionSocket.recv(2048)
                    OK_msg = decryptMessage(sym_key, encrypted_OK)
                    if OK_msg != "OK":
                        print("OK message not received")
                    #encrypt menu and send
                    menu = encryptMessage(sym_key, menuMessage)
                    connectionSocket.send(menu)
                    encrypted_choice = connectionSocket.recv(2048)
                    #choice option
                    choice = decryptMessage(sym_key, encrypted_choice)
                    #loop through choices
                    while choice in '123':
                       
                        if choice == '1':
                            connectionSocket.send(encryptMessage(sym_key, "Send the email"))
                            
                            length = int(decryptMessage(sym_key, connectionSocket.recv(2048)))                            
                            connectionSocket.send(encryptMessage(sym_key, "Length received"))
                            
                            data = b''
                            filepart = connectionSocket.recv(BUFFER_SIZE)
                            data += filepart
                            current = len(filepart)
                            while current < length:
                                if current == length:
                                    break                                
                                filepart = connectionSocket.recv(BUFFER_SIZE)
                                data += filepart
                                current += len(filepart)
                                
                            data = decryptMessage(sym_key, data)
                            data = json.loads(data)
                            now = datetime.datetime.now()
                            date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
                            data['Time and date'] = date_time
                            
                            store(data)
                            statement = (f'''An email from {data['From']} is sent to {";".join(data['To'])} has a content length of {data['Content Length']}.''')
                            print(statement)
                            
                            
                        #choice to check inbox
                        elif choice == '2':
                            clientFolder = os.getcwd() + '/' + username + '/inbox.txt'
                            if os.path.exists(clientFolder) == False:
                                connectionSocket.send(encryptMessage(sym_key, "No emails in your inbox"))
                            else:
                                inboxFile = open(clientFolder, 'r')
                                inbox = json.load(inboxFile)
                                inboxSend = json.dumps(inbox)
                                encryptedInbox = encryptMessage(sym_key, inboxSend)
                                connectionSocket.send(encryptedInbox)
                            connectionSocket.recv(2048)
                                
                        #choice to view email       
                        elif choice == '3':
                            connectionSocket.send(encryptMessage(sym_key, "the server request email index"))
                            index = int(decryptMessage(sym_key, connectionSocket.recv(2048)))
                            inboxFile = os.getcwd() + '/' + username + '/inbox.txt'
                            if os.path.exists(inboxFile):
                                inbox = open(inboxFile,'r').read()
                                inbox = json.loads(inbox)
                                email = inbox['inbox'][index-1]
                                emailTitle = email['Title']
                                mailFileName = os.getcwd() + '/' + username + '/' + email['From'] + '_' + email['Title']  + '.txt'
                                
                                if os.path.exists(mailFileName):
                                    
                                    content = open(mailFileName, 'r')
                                    content = content.read()
                                    email['Content'] = content
                                    serialisedEmail = json.dumps(email)
                                    
                                    encryptedData = encryptMessage(sym_key,serialisedEmail)
                                    connectionSocket.send(encryptMessage(sym_key, str(len(encryptedData))))
                                    connectionSocket.recv(2048)
                                    
                                    current = 0
                                    data = b''
                                    filepart = encryptedData[current:current+BUFFER_SIZE]
                                    
                                    current = len(filepart)
                                    connectionSocket.send(filepart)
                                    while current<len(encryptedData):
                                        
                                        filepart = encryptedData[current:current+BUFFER_SIZE]
                                        connectionSocket.send(filepart)
                                        if current == len(encryptedData):
                                            break
                                        current += len(filepart)
                                else:
                                    print("index doesn't exsist")
                                    sys.exit(1)
                            else:
                                print("Inbox empty")
                                sys.exit(1)                                
                                
                            connectionSocket.recv(2048)
                                   
                        
                        connectionSocket.send(menu)
                        choice = decryptMessage(sym_key, connectionSocket.recv(2048))
                    if choice == '4':
                        connectionSocket.close()
                        print(f"Terminating connection with {username}")
                    
                except:
                    print("error with opening json file")
                    sys.exit(1)
        except socket.error as e:
            print('An error occured:',e)
            sys.exit(1)
                    
server()