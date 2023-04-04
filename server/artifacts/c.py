import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="ap04av2796@3621",
  database="svcet"
)

mycursor = mydb.cursor()

def get_student_details(roll_number):
    sql = "SELECT * FROM details WHERE roll_number= %s"
    val = (roll_number,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    return result

roll_number = input("Enter roll number: ")
student_details = get_student_details(roll_number)

if student_details:
    print(student_details)
else:
    print("No student found with the given roll number.")