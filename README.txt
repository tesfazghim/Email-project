
A) ASSUMPTION:
1. for option 3, first of all the programs assume that there is an inbox to look at
2. also if you try to view an email that doesn't exisit, the program hangs
3. for option 1, if the user enters anything other than 'y' or 'Y' or 'n' or 'N' while asking if user wants to use file or
   enter text for the email, the program hangs; so I assume that the user enters only 'y' or 'Y' or 'n' or 'N'
4. I did test only on localhost and didn't test my programs on the student server lab machines, so fingers crossed on

The project as it is now can run well on command prompt. 
Steps to run the project:
1. Open a cmd window in server folder
2. Open another cmd window in client folder. Open multpiple client cmd windows to view the communications between 
   the known clients. 
   Use "localhost" as server name for ease of run.
   The client user names and passowrds can be found in the user_pass.json file.
3. Use the '''python3 fileName.py''' to run the python programs. Run server.py first followed by client.py
   in their respective cmd windows.
4. Use the client cmd windows to use the program.

