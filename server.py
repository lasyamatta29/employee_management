from flask import Flask, request, redirect, render_template,make_response,session
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
app = Flask(__name__)
app.secret_key="employee-management-secret-key"
def get_database_connection():
    connection=sqlite3.connect("users.db")
    connection.row_factory=sqlite3.Row
    return connection
def database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

#-----Employee table------

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employeename TEXT NOT NULL,
        email TEXT NOT NULL,
        phonenumber TEXT NOT NULL,
        department TEXT NOT NULL,
        salary INTEGER NOT NULL,
        joiningdate TEXT NOT NULL,
        address TEXT) 
         """)
    connection.commit()
    connection.close()
# -----login check-----
def login_required():
    return "user_id" in session

#-----Set Theme -----

@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in["light","dark"]:
        theme="light"
    previous_page=request.referrer or "/"
    response=make_response(
             redirect(previous_page)
    )
    response.set_cookie(
            "theme",
            theme,
            max_age= 60 * 60 * 24 * 365
    )
    return response

@app.route("/")
def home():
    if not login_required():
        return redirect("/login1")
    theme=request.cookies.get(
        "theme","light"
    )   
    username=session.get("username")
    fullname=session.get("fullname")
    return render_template("nav.html",
                           theme=theme,
                           username=username,
                           fullname=fullname)

#------Register Page------
@app.route("/register",methods=["GET"])
def register1():
    theme=request.cookies.get(
        "theme","light"
    )
    return render_template("register.html",theme=theme)
@app.route("/register", methods=["POST"])
def register():
    fullname = request.form.get("fullname"," ").strip()
    username = request.form.get("username"," ").strip()
    password = request.form.get("password"," ")
    if not fullname:
        return render_template(
            "register.html",
            theme=request.cookies.get("theme","light"),
            error="fullname is required"
        )
    if not username:
        return render_template(
                "register.html",
                theme=request.cookies.get("theme","light"),
                error="username is required"
            )
    if not password:
        return render_template(
            "register.html",
            theme=request.cookies.get("theme","light"),
            error="password is required"
        )
    #-----hash password-----
    hashed_password=generate_password_hash(password)

    #-----insert user-----
    connection=get_database_connection()
    cursor=connection.cursor()
    try:
       cursor.execute("""INSERT INTO users(fullname, username, password) VALUES (?,?,?)""",
                   (fullname, username, hashed_password))
       connection.commit()
    except sqlite3.IntegrityError:
       connection.close()
       return render_template("register.html",theme=request.cookies.get("theme","light"),
                           error="username already existed")
    connection.commit()
    return redirect("/login1")
# -------Home Page-------
@app.route("/home",methods=["get"])
def homepage():
    theme=request.cookies.get(
            "theme","light"
        )
    return render_template("home.html",theme=theme)

#------Login Page-------
@app.route("/login1", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/")
    theme=request.cookies.get("theme","light")
    return render_template("login1.html",theme=theme)

@app.route("/login1", methods=["POST"])
def login_user():
    username = request.form.get("username"," ").strip()
    password = request.form.get("password"," ")
    if not username or not password:
        return render_template("login1.html",theme=request.cookies.get("theme","light"),
                               error="username or password are required")
    connection=get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT id,fullname,username,password
                    FROM users
                      WHERE username=?""",
                   (username,))
    user = cursor.fetchone()
    connection.close()
    
    if user is None:
        return render_template("login1.html",theme=request.cookies.get("theme","light"),
                               error="username or password is incorrect" )
    password_correct=check_password_hash(user["password"],password)
    if not password_correct:
        return render_template("login1.html",theme=request.cookies.get("theme","light"),
                                       error="username or password is incorrect" )
    session.clear()
    session["user_id"]=user["id"]
    session["username"]=user["username"]
    session["fullname"]=user["fullname"]
    return redirect("/")
# ------Logout------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login1")



#-----Add Employee--------  
  
@app.route("/addemployee",methods=["get"])    
def addemployee_page():
    if not login_required():
        return redirect("/login1")
    theme=request.cookies.get("theme","light")
    return render_template("addemployee.html",theme=theme)

#--------Add employee post--------
@app.route("/addemployee",methods=["post"])
def addemployee():
    if not login_required():
        return redirect("/login1")
    employeename=request.form.get("employeename"," ").strip()
    email=request.form.get("email"," ").strip()
    phonenumber=request.form.get("phonenumber"," ").strip()
    department=request.form.get("department"," ").strip()
    salary=request.form.get("salary"," ").strip()
    joiningdate=request.form.get("joiningdate"," ").strip()
    address=request.form.get("address"," ").strip()
    # ---validation------

    if not employeename:
        return "Employeename is required"
    if not email:
            return "Email is required"
    if not phonenumber:
            return "phonenumber is required"
    if not department:
            return "department is required"
    if not salary:
            return "salary is required"
    if not joiningdate:
            return "joiningdate is required"
    try:
        salary=int(salary)
    except ValueError:
        return "salary must be an number!"    
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO employees(
                    employeename,
                    email,
                    phonenumber,
                    department,
                    salary,
                    joiningdate,
                    address) VALUES(?,?,?,?,?,?,?)""",
                    (employeename,email,phonenumber,department,salary,joiningdate,address))
    connection.commit()
    connection.close()
    return redirect("/employees")

#------Employees--------

@app.route("/employees")
def employees():
    if not login_required():
        return redirect("/login1")
    connection= get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id ASC
    """)
    employees=cursor.fetchall()
    connection.close()
    theme=request.cookies.get("theme","light")
    return render_template("employees.html",employees=employees,theme=theme)


#------edit employee get------
@app.route("/editemployee/<int:id>",methods=["get"])
def edit_employee_page(id):
         if not login_required():
             return redirect("/login1")
         connection=get_database_connection()
         cursor=connection.cursor()
         cursor.execute("""
                         select * from employees
                         where id=?""",(id,))
         employee=cursor.fetchone() 
         connection.close()
         if employee is None:
             return"""
              <h2>employee not found</h2>
              <a href="/employees">
              Back to employees
              </a>"""
         theme=request.cookies.get("theme","light")
         return render_template(
             "editemployee.html",
             employee=employee,
             theme=theme
         )

#------edit employee post------         
@app.route("/editemployee/<int:id>",methods=["post"])
def edit_employee(id):
    if not login_required():
        return redirect("/login1")
    employeename =request.form.get("employeename"," ").strip()
    email =request.form.get("email"," ").strip()
    phonenumber =request.form.get("phonenumber"," ").strip()
    department =request.form.get("department"," ").strip()
    salary =request.form.get("salary"," ").strip()
    joiningdate =request.form.get("joiningdate"," ").strip()
    address =request.form.get("address"," ").strip()

    # ---validation------
    
    if not employeename:
        return "Employeename is required"
    if not email:
        return "Email is required"
    if not phonenumber:
        return "phonenumber is required"
    if not department:
        return "department is required"
    if not salary:
        return "salary is required"
    if not joiningdate:
        return "joiningdate is required"
    try:
        salary=int(salary)
    except ValueError:
        return "salary must be an number!"    
        
    # ------update employee------
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
         update employees
         set  
         employeename=?,
         email=?,
         phonenumber=?,
         department=?,
         salary=?,
         joiningdate=?,
         address=?
         where id=?
        """,(employeename,email,phonenumber,department,salary,joiningdate,address,id))
    connection.commit()
    connection.close()
    return redirect("/employees")

#------delete employee------   
   
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    if not login_required():
        return redirect("/login1")
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
           DELETE FROM employees
            WHERE id=? """,
            (id,))
    connection.commit()
    connection.close()
    return redirect("/employees")

# -------Search Employee---------
@app.route("/employees")
def employees_list():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    connection.close()
    return render_template("employees.html", employees=employees)
@app.route("/search", methods=["GET","POST"])
def search():
    employees = []
    searchname = ""

    if request.method == "POST":
        searchname = request.form.get("searchname","").strip()

        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, employeename, email, department, phonenumber,salary,joiningdate,address
            FROM employees
            WHERE employeename LIKE ?
        """, ("%"+searchname+"%",))
        employees = cursor.fetchall()
        connection.close()

    theme = request.cookies.get("theme", "light")
    return render_template("search.html",
                           employees=employees,
                           searchname=searchname,
                           theme=theme)

if __name__ == "__main__":
    database()
    app.run(debug=True)




