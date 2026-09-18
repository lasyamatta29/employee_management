from flask import Flask,request,redirect,render_template
import sqlite3
app=Flask(__name__)
def get_database_connection():
    connection=sqlite3.connect("users.db")
    connection.row_factory=sqlite3.Row
    return connection
def create_database():
    #connect to database
     connection=sqlite3.connect("users.db")
    #store databse in some object
     cursor=connection.cursor()
    #write query using that object
     cursor.execute("""
                             CREATE TABLE IF NOT EXISTS users(
                             id integer PRIMARY KEY AUTOINCREMENT,
                             fullname text NOT NULL,
                             username text UNIQUE NOT NULL,
                             password text NOT NULL)""")
    #-----employee table----
     cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees(
                    id integer PRIMARY KEY AUTOINCREMENT,
                    employeename text NOT NULL,
                    email text UNIQUE NOT NULL,
                    phonenumber TEXT NOT NULL,
                    department text NOT NULL,
                    salary INTEGER NOT NULL,
                    joiningdate TEXT NOT NULL,
                    address TEXT
                    )""")
     
     
     
    #commit query
     connection.commit()
    #close connection
     connection.close()   
@app.route("/")
def home():
    return render_template("nav.html")
#----register page-----
@app.route("/register",methods=["get"])
def register_page():
    return render_template("register.html")

@app.route("/register",methods=["post"])
def register():
    fullname=request.form["fullname"]
    username=request.form["username"]
    password=request.form["password"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
        INSERT INTO users(fullname,username,password)
        VALUES(?,?,?)
         """,(fullname,username,password)
         )
    connection.commit()
    connection.close()
    return redirect("/login1")
#----login page get----

@app.route("/login1" ,methods=["get"]) 
def login_page():
    return render_template("login1.html")

# -------login page post-------
@app.route("/login1",methods=["post"])
def login():
    username=request.form["username"]
    password=request.form["password"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
         SELECT * FROM users
         WHERE username=? AND password=?
         """,(username,password))
    user=cursor.fetchone()
    connection.close()
    if  user:
        return "<h2>login successfull </h2><p>welcome,"+ username +"!</p>"
    else:  
        return "<h2>login failed </h2> <p>username or passwords is incorrect </p>"
 
 #----add employee get-----

@app.route("/addemployee",methods=["get"])
def addemployee_page():
    return render_template("addemployee.html")


# -----add employee post------ 

@app.route("/addemployee",methods=["post"])
def addemployee():
    employeename=request.form["employeename"]
    email=request.form["email"]  
    phonenumber=request.form["phonenumber"]  
    department=request.form["department"]  
    salary=request.form["salary"]  
    joiningdate=request.form["joiningdate"]  
    address=request.form["address"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""INSERT INTO employees(
        employeename,
        email,
        phonenumber,
        department,
        salary,
        joiningdate,
        address) VALUES(?,?,?,?,?,?,?)
        """,(employeename,email,phonenumber,department,salary,joiningdate,address)) 
    connection.commit()
    connection.close()
    return redirect("/employees")


  
#-----employee page------
@app.route("/employees")
def employees():
    connection=get_database_connection() 
    cursor=connection.cursor()
    cursor.execute("""
                  SELECT *
                  from employees
                  ORDER BY id ASC
                  """)
    employees=cursor.fetchall()
    connection.close()
    return render_template("employees.html",employees=employees)


#-----edit employee -----
@app.route("/editemployee/<int:id>")
def edit_employee_page(id):
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
                   select * from employees
                   where id=?""",
                   (id,))
    employee=cursor.fetchone()
    connection.cursor()
    if employee is None:
        return"""
        <h2>employee not found</h2>
        <a href="/employees>
        Back to employees
        </a>"""
    return render_template("editemployee.html",employee=employee)
#------Edit Employee update(post)-------
@app.route("/editemployee/<int:id>",methods=["post"])
def edit_employee(id):
    employeename=request.form["employeename"]
    email=request.form["email"]
    phonenumber=request.form["phonenumber"]
    department=request.form["department"]
    salary=request.form["salary"]
    joiningdate=request.form["joiningdate"]
    address=request.form["address"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
                   UPDATE employees
                   SET
                   employeename=?,
                    email=?,
                    phonenumber=?,
                    department=?,
                    salary=?,
                    joiningdate=?,
                    address=?
                    WHERE id=?
                    """,(employeename,email,phonenumber,department,salary,joiningdate,address,id))
    connection.commit()
    connection.close()
    return redirect("/employees")
#-----delete employee------
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
                   DELETE FROM employees
                   WHERE id=?
                   """,(id,))
    connection.commit()
    connection.close()
    return redirect("/employees")


if __name__=="__main__":
    create_database()
    app.run(debug=True)