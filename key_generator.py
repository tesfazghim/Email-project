#------------------------------------------------------------------
# Names: Mohammed Hocho, Joshua Froese, Meron Tesfazghi
#------------------------------------------------------------------
'''The program creates public and private keys for the server and each of the 
clients then saves them in files that are stored in client and server folders'''
import os,glob
import sys
from Crypto.PublicKey import RSA

def key_gen():
    # gen server key
    server_key = RSA.generate(2048)
    server_private_key = server_key.export_key('PEM')
    server_public_key = server_key.publickey().export_key('PEM')
    #write server public and client keys
    if (os.path.exists("server")):
        private_f = open("server/server_private.pem", "wb")
        private_f.write(server_private_key)
        public_f = open("server/server_public.pem", "wb")
        public_f.write(server_public_key)
    #write server pub key to client folder
    if(os.path.exists("client")):
        serverPub = open("client/server_public.pem", "wb")
        serverPub.write(server_public_key)
        serverPub.close()
        
    #generate public and private keys for clients and store in list
    client_keys = []
    client_1 = RSA.generate(2048)
    client_1Private = client_1.export_key('PEM')
    client_1Public = client_1.publickey().export_key('PEM')
    client_keys.append(client_1Public)
    client_keys.append(client_1Private)
    
    client_2 = RSA.generate(2048)
    client_2Private = client_2.export_key('PEM')
    client_2Public = client_2.publickey().export_key('PEM')
    client_keys.append(client_2Public)  
    client_keys.append(client_2Private)
      
    
    client_3 = RSA.generate(2048)
    client_3Private = client_3.export_key('PEM')
    client_3Public = client_3.publickey().export_key('PEM')
    client_keys.append(client_3Public)
    client_keys.append(client_3Private)
    
    
    client_4 = RSA.generate(2048)
    client_4Private = client_4.export_key('PEM')
    client_4Public = client_4.publickey().export_key('PEM')
    client_keys.append(client_4Public)
    client_keys.append(client_4Private)
    
    client_5 = RSA.generate(2048)
    client_5Private = client_5.export_key('PEM')
    client_5Public = client_5.publickey().export_key('PEM')
    client_keys.append(client_5Public)
    client_keys.append(client_5Private)
    
    server_path = "server/"
    client_path = "client/"
    #clients key file names
    clientfiles = []
    for i in range (1,6):
        clientfiles.append("client"+str(i)+"_public.pem")
        clientfiles.append("client"+str(i)+"_private.pem")
    #writing client public keys to server and client directories
    #writing private keys to client directory
    for i in range(0,10,2):
        clientToServer = open(server_path+clientfiles[i], "wb")
        clientToServer.write(client_keys[i])
        clientToServer.close()
        
        
        clientPub = open(client_path + clientfiles[i], "wb")
        clientPub.write(client_keys[i])
        clientPub.close()
        clientPriv = open(client_path + clientfiles[i+1], "wb")
        clientPriv.write(client_keys[i+1])
        clientPriv.close()
         
         
key_gen()

''' some sources I used in encyption on both server and client side as well as directory operations
https://pycryptodome.readthedocs.io/en/latest/src/examples.html
https://stackoverflow.com/questions/30056762/rsa-encryption-and-decryption-in-python
https://stackabuse.com/creating-and-deleting-directories-with-python/'''