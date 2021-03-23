import sqlite3
import pandas as pd
from pandas import DataFrame
import csv
import re

# Pandas display options
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Used for just making application prettier
formatting = "--------------------------------------------------------------------------------------" \
         "-------------------------------------------------------------------" \
         "---------------------------------------"

# Establishing a connection to the database
conn = sqlite3.connect('./students.sqlite')  # establish connection
mycursor = conn.cursor()

# Function to get read in data from the csv
def loadData(filename):
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        # going through each row
        count = 0
        for record in reader:
            # This will skip the first iteration because we do not want the column names as a record
            if count == 0:
                count += 1
                continue
            else:
                # inserting each record from the csv file into our Student database
                # also entering 0 for each of the isDeleted records
                # leaving the FacultyAdvisor as null in case we want to check for null in the future
                mycursor.execute(
                    "INSERT INTO Student(FirstName, LastName, Address, City, State, ZipCode, "
                    "MobilePhoneNumber, Major, GPA, isDeleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], 0))
                conn.commit()

# Checking to see if the user need to input the data
print("Do you need to import the student.csv data? (1)Yes (2)No")
get_data = int(input("Answer: "))
if get_data == 1:
    loadData("students.csv")
    print("Data imported.")

# Loop to run our student database application
while True:
    print("\n\n|-------------------------|")
    print("| Menu:                   |\n| (1)Print all students   "
          "|\n| (2)Add a student        |\n| (3)Update a student     |\n"
          "| (4)Delete a student     |\n| (5)Search for a student |\n| (6)Exit Application     |")
    print("|-------------------------|\n")
    choice = int(input("Choose the number you want: \n"))

    # Prints out all students
    if choice == 1:
        print("\nAll Students: ")
        print(formatting)
        mycursor.execute("Select * from Student;")
        myrecords = mycursor.fetchall()
        df = DataFrame(myrecords)
        df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City', 'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']
        print(df)
        print(formatting)

    # Allows user to add a student to the database
    elif choice == 2:
        first = input("Enter the students first name: ")
        last = input("Enter the students last name: ")

        # Making sure the user GPA input is valid and less than 4.0
        while True:
            try:
                gpa = float(input("Enter the students GPA: "))
            except ValueError:
                print("This is not a valid GPA. Try again.")
            try:
                if isinstance(gpa, float) and gpa <= 4.0:
                    break
            except:
                continue
        # converting back to string type just in case
        gpa = str(gpa)
        major = input("Enter the students major: ")
        advisor = input("Enter the students advisor: ")
        address = input("Enter the students address: ")
        city = input("Enter the students city: ")
        state = input("Enter the students state: ")

        # Making sure the user zipcode input is valid
        # Checks to make sure it is only numbers and 5 number long
        while True:
            try:
                zipcode = int(input("Enter the students zipcode: "))
            except ValueError:
                print("This zipcode is not valid. It must only contain numbers.")
            try:
                if isinstance(zipcode, int) and len(str(zipcode)) == 5:
                    break
            except:
                print("This zipcode is not valid. It must contain only 5 digits. ")
                continue

        # Converting back to string type just in case
        zipcode = str(zipcode)

        # Making the correct pattern for entering a phone number
        pattern = "\(\d{3}\) \d{3}-\d{4}"
        while True:
            phone = input("Enter the students phone number (xxx) xxx-xxxx: ")
            isphone = re.match(pattern, phone)
            if isphone:
                break
            else:
                print("This is not a valid number. Try again. ")
        mycursor.execute("INSERT INTO Student(FirstName, LastName, GPA, Major, FacultyAdvisor, "
                         "Address, City, State, ZipCode, MobilePhoneNumber, isDeleted) "
                         "VALUES (?,?,?,?,?,?,?,?,?,?,?);",
                         (first, last, gpa, major, advisor, address, city, state, zipcode, phone, 0,))
        conn.commit()

    # Allows user to update a student in the database by selecting their student id
    elif choice == 3:
        id = int(input("Enter the id of the student you would like to update: "))

        # Continues to ask for input until update is done successfully or they exit
        while True:
            print("(1)Major\n(2)Advisor\n(3)Phone Number\n(4)Exit")
            select = (int(input("Enter what you want to update about this student: ")))
            if select == 1:
                major = input("\nEnter the major you want to switch this student to: ")
                mycursor.execute("UPDATE Student SET Major = ? WHERE StudentId = ?;", (major, id))
                conn.commit()
                break
            elif select == 2:
                advisor = input("\nEnter the advisor you want to switch this student to: ")
                mycursor.execute("UPDATE Student SET FacultyAdvisor = ? WHERE StudentId = ?;", (advisor, id))
                conn.commit()
                break
            elif select == 3:
                pattern = "\(\d{3}\) \d{3}-\d{4}"
                while True:
                    phone = input("\nEnter the phone number you want to switch this student to (xxx) xxx-xxxx: ")
                    isphone = re.match(pattern, phone)
                    if isphone:
                        break
                    else:
                        print("This is not a valid number. Try again. ")
                mycursor.execute("UPDATE Student SET MobilePhoneNumber = ? WHERE StudentId = ?;", (phone, id))
                conn.commit()
                break
            elif select == 4:
                break
            else:
                print("\nYour choice was invalid. Please try again. ")

    # Allows user to soft delete a student in the database
    elif choice == 4:
        id = input("Enter the id of the student you would like to delete: ")
        mycursor.execute("Update Student set isDeleted = 1 WHERE StudentID = ?;", (id,))
        conn.commit()

    # Allows user to search database based on different criteria
    elif choice == 5:
        while True:
            print("(1)Major\n(2)GPA\n(3)City\n(4)State\n(5)Advisor\n(6)Exit")
            select = int(input("Enter how you want to search this students by: "))
            if select == 1:
                major = input("\nEnter the major you would like to search for: \n")
                mycursor.execute("SELECT * FROM Student WHERE Major = ?;", (major,))
                myrecords = mycursor.fetchall()
                df = DataFrame(myrecords)
                df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City',
                              'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']

                print("Students with " + major + " as their major:\n" + formatting)
                print(df)
                print(formatting)
            elif select == 2:
                gpa = input("\nEnter the gpa you would like to search for: \n")
                mycursor.execute("SELECT * FROM Student WHERE GPA = ?;", (gpa,))
                myrecords = mycursor.fetchall()
                df = DataFrame(myrecords)
                df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City',
                              'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']
                print("Students with a " + gpa + " GPA:\n" + formatting)
                print(df)
                print(formatting)
            elif select == 3:
                city = input("\nEnter the city you would like to search for: \n")
                mycursor.execute("SELECT * FROM Student WHERE City = ?;", (city,))
                myrecords = mycursor.fetchall()
                df = DataFrame(myrecords)
                df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City',
                              'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']
                print("Students from " + city + ":\n" + formatting)
                print(df)
                print(formatting)
            elif select == 4:
                state = input("\nEnter the state you would like to search for: \n")
                mycursor.execute("SELECT * FROM Student WHERE State = ?;", (state,))
                myrecords = mycursor.fetchall()
                df = DataFrame(myrecords)
                df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City',
                              'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']
                print("Students from " + state + ":\n" + formatting)
                print(df)
                print(formatting)
            elif select == 5:
                advisor = input("\nEnter the advisor you would like to search for: \n")
                mycursor.execute("SELECT * FROM Student WHERE FacultyAdvisor = ?;", (advisor,))
                myrecords = mycursor.fetchall()
                df = DataFrame(myrecords)
                df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor', 'Address', 'City',
                              'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted']
                print("Students with " + advisor + " as their advisor:\n" + formatting)
                print(df)
                print(formatting)
            else:
                print("Exiting Program.")
                break

    # Exits the database
    else:
        print("\nExiting Application. Goodbye.")
        break

