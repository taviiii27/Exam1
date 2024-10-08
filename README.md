This is a python program that allows monitoring the hours worked by a company's employees. The data you receive as a parameter comes from access points in an office building. Any person, to enter or leave the building, must validate the access card. Through validation, the id of the person holding the card, the time of validation and the meaning (entry or exit) are obtained. 
In the building there can be 2 types of gates through which access is made. The first type saves all this data in a text or csv file that has the same structure as the attached examples. The second type of gate transmits in real time to the server the inputs and outputs via the Internet, in json format. 
Requirements: 
• Create a repository on github (you need to make it public to start a portfolio of applications that will be useful in future job interviews). Upload all the code you develop there. A pull request will be needed for each implemented functionality. 
• In development, use OOP concepts (encapsulation, inheritance, polymorphism, abstraction)
• Create a functionality through which an administrator can register users. Users will be saved in a database table where we will record ID, Name, Surname, Company, IdManager. These details are sent through a request through which all the necessary details are sent. 
• The first type of gate: Within the project there will be a folder called "entries" where the building administrators will upload the files generated by the first type of gates. The program will read each file in that directory, load the data into the database, in the "access" table and then move the file into a directory called backup_entries. The file names will have the format Gate[gate_number].[file_type] (eg Gate1.csv). The name of the port on which each entry is made must be saved in the database. The program must read the file as soon as it appears. (Check at each iteration if there are new files in the entries folder).
• The second type of gate: At the program level, you create an endpoint that receives as a parameter a json with the following format and saves it in the database: 
{
     "date":"2023-05-21T13:49:51.141Z",
     "meaning": "in",
     "idPersona":10,
     "idPorta":3
}
• Create a functionality that runs daily and calculates the number of hours worked by each employee, based on the entries and exits recorded at the gates. For each employee who did not work 8 hours in a day, an email will be sent to his manager. Also, the list with the names of the employees will be written in the backup directory with the names <data_curenta>_chiulangii.csv and <data_curenta>_chiulangii.txt and will contain the employees in the format Name, Working Hours both in csv and in txt (in txt it will not had header). 
Analogue, I did for the workers who did an extra-work, to receive an email too and promise them a bonification to the salary.
