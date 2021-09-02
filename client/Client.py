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
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

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
#return encrypted rsa message
def encryptToServerRSA(message):
    serverPub = RSA.import_key(open("server_public.pem", "rb").read())
    RSA_cipher = PKCS1_OAEP.new(serverPub)
    encrypted_RSA = RSA_cipher.encrypt(message.encode('ascii'))
    return encrypted_RSA    
#def decryptFromServerRSA(message):

def client():
    serverPort = 13000 #Server port
    serverName = input("Enter the server IP or name: ")

    #Create client socket
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in client socket creation:',e)
        sys.exit(1)

    try:
        #Client connect with the server
        clientSocket.connect((serverName, serverPort))
        
        #get username, encrypt with RSA and send to server
        username = input("Enter your username: ")
        clientName = username
        file = os.getcwd()+"/"+str(username)+"_private.pem" #private key file name
        username = encryptToServerRSA(username)
        clientSocket.send(username)
        
        clientSocket.recv(2048) #sync
        
        #get password, encrypt and send to server
        password = input("Enter your password: ")
        password = encryptToServerRSA(password)
        clientSocket.send(password)
        
        #get message to check if invalid or sym key 
        message = clientSocket.recv(2048)
        if message[0:7] == b'Invalid':
            print("Invalid username or password\nTerminating.")
            clientSocket.close()
            sys.exit(1)
            return
        
        #decrypt symmetric key
        clientPrivKey = RSA.import_key(open(file, "rb").read())
        clientCipher = PKCS1_OAEP.new(clientPrivKey)
        sym_key = clientCipher.decrypt(message)
        
        #send ok msg
        ok_msg = encryptMessage(sym_key, "OK")
        clientSocket.send(ok_msg)
        #receive menu and ask for input of choice
        menu = decryptMessage(sym_key, clientSocket.recv(2048))
        choice = input(menu)
        encrypted_choice = encryptMessage(sym_key, choice)
        clientSocket.send(encrypted_choice)
        
        while choice in '123':
            if choice == '1':
                decryptMessage(sym_key, clientSocket.recv(2048))
                #get destination
                dst = input("Enter destinations (separated by ;): ")
                title = input ("Enter Title: ")
                while len(title) > 100:
                    title = input("  Enter shorter title: ")
                
                option = input("Would you like to load contents from a file?(Y/N) ")
                if option in 'nN':
                    content = input("Enter message contents: ")                    
                    while len(content)>1000000:
                        content = input("  Too long, enter shorter email: ")
                                      
                        
                elif option in 'yY':
                    filename = input('Enter filename: ')
                    if os.path.isfile(os.getcwd()+'/'+filename):
                        with open(filename, "r") as file:
                            content = file.read()
                            while len(content)>1000000:
                                filename = input('  Too long, Enter filename: ')
                                if os.path.isfile(os.getcwd()+'/'+filename):
                                    with open(filename, "r") as file:
                                        content = file.read()
                    else:
                        print("file not found")
                        sys.exit(1)
                data = {}
                data['From'] = clientName
                data['To'] = dst.split(';')
                data['Title'] = title
               
                data['Content Length'] = len(content)
                data['Content'] = content
                serialised = json.dumps(data)                
                encrypted_data = encryptMessage(sym_key, serialised)
                
                clientSocket.send(encryptMessage(sym_key, str(len(encrypted_data))))
                clientSocket.recv(2048)
                
                current = 0
                filepart = encrypted_data[current:current + BUFFER_SIZE]
                current = len(filepart)
                clientSocket.send(filepart)
                while current < len(encrypted_data):
                    if current == len(encrypted_data):
                        break
                    filepart = encrypted_data[current:current + BUFFER_SIZE]
                    clientSocket.send(filepart)
                    current += len(filepart)   
                
                print("The message is sent to the server\n")                
                
            elif choice == '2':
                encryptedMessage = clientSocket.recv(2048)
                message = decryptMessage(sym_key, encryptedMessage)
                if message[0:2] == 'No':
                    print(message)
                else:
                    print("Index    From      Date Time              Title")
                    index = 1
                    print()
                    inbox = json.loads(message)
                    for i in range(len(inbox['inbox'])):
                        print(f" {index}    {inbox['inbox'][i]['From']}     ", end="")
                        print(f"{inbox['inbox'][i]['Time and date']}              {inbox['inbox'][i]['Title']}")
                        index += 1
                clientSocket.send(encryptMessage(sym_key, "OK"))
            
            elif choice == '3':
                request = clientSocket.recv(2048)
                decryptMessage(sym_key, request)
                index = input("Enter the email index you wish to view: ")
                clientSocket.send(encryptMessage(sym_key, index))
                
                length = int(decryptMessage(sym_key, clientSocket.recv(2048)))
                clientSocket.send(encryptMessage(sym_key, "length received"))
                data = b''
                filepart = clientSocket.recv(BUFFER_SIZE)
                data += filepart
                current = len(filepart)
                while current<length:
                    filepart = clientSocket.recv(BUFFER_SIZE)
                    data += filepart
                    current+= len(filepart)
                    if current==length:
                        break
                data = decryptMessage(sym_key, data)
                print(data)
                data = json.loads(data)
                print(f"From: {data['From']}\nTo: {';'.join(data['To'])}")
                print(f"Time and Date received: {data['Time and date']}\nTitle: {data['Title']}")
                print(f"Content Length: {data['Content Length']}\nContents:\n{data['Content']}")
                
                clientSocket.send(encryptMessage(sym_key, "received info"))
                
                
            
            menu = decryptMessage(sym_key, clientSocket.recv(2048))
            choice = input(menu)
            encrypted_choice = encryptMessage(sym_key, choice)
            clientSocket.send(encrypted_choice)            
            
        if choice == '4':
            clientSocket.close()
            print("Terminating connection with server")
    except socket.error as e:
        print('An error occured:',e)
        clientSocket.close()
        sys.exit(1)

client()

