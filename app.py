
import pyodbc
from flask import Flask,request,render_template,redirect,session,jsonify,url_for
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import os
import base64
from PIL import Image 
from flask_session import Session
from to_encrypt_decrypt import to_encrypt_string,to_decrypt_string
from datetime import datetime,timedelta 





app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



app=Flask(__name__,template_folder='template') #CHANGE WHEN ADDING FRONTPAGE
app.secret_key="A1S2D3F4"
app.permanent_session_lifetime= timedelta(minutes=2)

ALLOWED_EXTENSIONS={'png','jpg','jpeg','gif'}



#CONNECTION STRING  SQL 
#driver= '{ODBC Driver 13 for SQL Server}'
driver= '{ODBC Driver 17 for SQL Server}'
server = 'tcp:secure-programming-server.database.windows.net,1433'
database = 'Secure_Programming_SQLDB'
username = 'abhyudai'
password = 'HR26dc0590#'
#cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor() #cursor 


#login & Register
@app.route('/',methods=['GET','POST'])
def homepage():
    return render_template('login.html')

@app.route('/user_register_page',methods=['GET','POST'])
def user_register_page():
    return render_template('user_register.html')

@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        details = request.form.get
        fname= details('fname')
        fname = fname.strip()
        fname_encrypted = to_encrypt_string(fname)
        print(fname_encrypted)
        lname= details('lname')
        lname = lname.strip()
        lname_encrypt = to_encrypt_string(lname)
        email= details('email')
        email = email.strip()
        password=details('password')
        password = password.strip()
        password_encrypted = to_encrypt_string(password)
        is_admin=0
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(filename)
        image = open(filename, 'rb')
        image_read = image.read()
        image_64_encode = base64.b64encode(image_read)
        profileimage =image_64_encode.decode("UTF-8")
        username =details('username')
        username = username.strip()
        cursor.execute('''Select username from users where username= ?''',username)
        check_username=cursor.fetchall()
        print(len(check_username))
        if len(check_username) == 1:
            error="Incorrect details try again"
            return render_template("login.html",error=error)
        else:
            cursor.execute('''INSERT INTO users (firstname,lastname,email,password,is_admin,profileimage,username) VALUES (?,?,?,?,?,?,?)''',fname_encrypted, lname_encrypt, email,password_encrypted,is_admin,profileimage,username)
            cnxn.commit()
        return render_template('login.html')


@app.route('/admin_register_page',methods=['GET','POST'])
def admin_register_page():
    return render_template('admin_register.html')

@app.route('/admin_register',methods=['GET','POST'])
def admin_register():
    if request.method=='POST':
        details = request.form.get
        fname= details('fname')
        fname = fname.strip()
        fname_encrypted = to_encrypt_string(fname)
        print(fname_encrypted)
        lname= details('lname')
        lname = lname.strip()
        lname_encrypt = to_encrypt_string(lname)
        email= details('email')
        email = email.strip()
        password=details('password')
        password = password.strip()
        password_encrypted = to_encrypt_string(password)
        is_admin=1
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(filename)
        image = open(filename, 'rb')
        image_read = image.read()
        image_64_encode = base64.b64encode(image_read)
        profileimage =image_64_encode.decode("UTF-8")
        username =details('username')
        username = username.strip()
        cursor.execute('''INSERT INTO users (firstname,lastname,email,password,is_admin,profileimage,username) VALUES (?,?,?,?,?,?,?)''',fname_encrypted, lname_encrypt, email,password_encrypted,is_admin,profileimage,username)
        cnxn.commit()
    return render_template('login.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        session.permanent=True
        details = request.form.get
        username= details("username")
        session["username"]=username
        print(session["username"])
        password=details('password')
        password= password.strip()
        cursor.execute('''SELECT username,password from users where username =?;''', session["username"])
        valid=cursor.fetchall()
        valid_length=len(valid)
        if valid_length== 0:
            return render_template('homepage.html')
        else:
            x=valid.pop(0)
            x1= to_decrypt_string(x[1])
            print("#"*40)
            print(x1)
            if x[0]== username and x1==password:
                cursor.execute('''SELECT firstname,profileimage,lastname,username,email from users where username =?;''', session["username"])
                valid=cursor.fetchall()
                x=valid.pop(0)
                fname = x[0]
                decrypt_fname = to_decrypt_string(fname)
                profilepic = x[1]
                lname = x[2]
                username =x[3]
                session['username']= username
                email= x[4]
                print("#"*40)
                session['email']=email
                print(session['email'])
                lname= to_decrypt_string(lname)
                return render_template('homepage.html',fname=decrypt_fname,profilepic=profilepic,lname=lname)
            else:
                return render_template('login.html')


@app.route('/uploadfile',methods=['GET','POST'])
def uploadfile():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(filename)
        image = open(filename, 'rb')
        image_read = image.read()
        image_64_encode = base64.b64encode(image_read)
        readyimage =image_64_encode.decode("UTF-8")
        return render_template("test.html", test =readyimage)
    

@app.route('/create_group_page',methods=['GET','POST'])
def create_group_page():
    if request.method == 'POST':
        return render_template("create_group.html")

@app.route('/delete_group_page',methods=['GET','POST'])
def delete_group_page():
    if request.method == 'POST':
        if "username" in session:
            username = session["username"]
            print(username)
            cursor.execute('''SELECT is_admin  from users  where username =?''',username)
            get_is_admin=cursor.fetchone()
            if get_is_admin[0] == 1: 
                cursor.execute('''SELECT email  from users  where username =?''',username)
                get_email_to_del=cursor.fetchone()
                cursor.execute('''SELECT DISTINCT groupname from group_members_status where email =?''',get_email_to_del[0])
                group_names=cursor.fetchall()
                group_names_list=[]
                for x in group_names:
                    group_names_list.append(x[0])     
                return render_template("delete_group.html",group_names_list=group_names_list)
            else:    
                return render_template("delete_group.html")


@app.route('/delete_group',methods=['GET','POST'])
def delete_group():
    if request.method == 'POST':
        hidden_skills = request.form['hidden_skills']    
        emails_hidden_skills = hidden_skills.split(",")
        for x in emails_hidden_skills:
            print("_"*50)
            print(x)
            print("_"*50)
            cursor.execute('''delete from groups where groupname = ?''',x)
            cursor.execute('''delete from group_members_status where groupname = ?''',x)
        return jsonify("Delted")


@app.route('/create_group',methods=['GET','POST'])
def create_group():
    if request.method=='POST':
        details = request.form.get
        gname = details('gname')
        gname = gname.strip()
        session['gname']=gname
        gdescription = details('gdescription')
        gdescription = gdescription.strip()
        encrypt_gdescription = to_encrypt_string(gdescription)
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(filename)
        image = open(filename, 'rb')
        image_read = image.read()
        image_64_encode = base64.b64encode(image_read)
        groupimage =image_64_encode.decode("UTF-8")
        cursor.execute('''INSERT INTO groups(groupname,groupdesription ,date ,is_admin,groupimage,username,email) VALUES (?,?,?,?,?,?,?)''',gname, encrypt_gdescription,datetime.now() ,session['email'],groupimage,session['username'],session['email'])
        cnxn.commit()
        cursor.execute('''SELECT email from users''')
        members=cursor.fetchall()
        members_list=[]
        for x in members:
            y = x[0]
            print(y)
            members_list.append(y)
        return render_template("add_groupmemebers.html",members=members_list)


@app.route("/ajax_add",methods=["POST","GET"])
def ajax_add():
    if request.method == 'POST':
        hidden_skills = request.form['hidden_skills']
        print(hidden_skills)     
        emails_hidden_skills = hidden_skills.split(",")
        for x in emails_hidden_skills:
            print(x)
            cursor.execute('''INSERT INTO group_members_status(groupname,email,status) VALUES (?,?,?)''',session['gname'],x,"Requested")
        cursor.commit()
        message = "Request sent"
        return jsonify(message)

@app.route('/homepage_link',methods=['GET','POST'])
def homepage_link():
    if "username" in session:
        username = session["username"]
        cursor.execute('''SELECT firstname,profileimage,lastname,username,email from users where username =?;''', session["username"])
        valid=cursor.fetchall()
        x=valid.pop(0)
        fname = x[0]
        decrypt_fname = to_decrypt_string(fname)
        profilepic = x[1]
        lname = x[2]
        username =x[3]
        session['username']= username
        email= x[4]
        print("#"*40)
        session['email']=email
        print(session['email'])
        lname= to_decrypt_string(lname)
        return render_template('homepage.html',fname=decrypt_fname,profilepic=profilepic,lname=lname)
    else:
        return render_template('login.html')


@app.route('/checkposts',methods=['GET','POST'])
def checkposts():
    if request.method=='POST':
        if "username" in session:
            username = session["username"]
            print(username)
            cursor.execute('''SELECT email from users where username =?;''', username)
            get_eamil=cursor.fetchall()
            cursor.execute('''select DISTINCT groupname from group_members_status where email=?;''',get_eamil[0])
            gnames_list=cursor.fetchall()
            ##LIST TO ZIP AFTER APPEND 
            guuid_valid_list=[]
            decrypted_valid_gdescription=[]
            group_details_image=[]
            gname_valid_list=[]
            gdate_valid_list=[]
            gusername_valid_list=[]
            for x in gnames_list:
                g_name=x[0]
                cursor.execute('''SELECT groupname from groups where username =? and groupname=?;''', username,g_name)
                gname_valid=cursor.fetchall()
                if len(gname_valid)==0:
                    pass
                else:
                    gname_valid_list.append(x[0])##list1
                    cursor.execute('''SELECT groupimage from groups where username =? and groupname=?;''', username,g_name)
                    validimage=cursor.fetchall()
                    for x in validimage:
                        group_details_image.append(x[0])#list4
                    cursor.execute('''SELECT groupdesription from groups where username =? and groupname=?;''', username,g_name)
                    gdescription_valid=cursor.fetchall()
                    for x in gdescription_valid:
                        gdescription_valid_1= to_decrypt_string(x[0])
                        decrypted_valid_gdescription.append(gdescription_valid_1)##list2
                    cursor.execute('''SELECT uuid from groups where username =? and groupname=?;''', username,g_name)
                    guuid_valid=cursor.fetchall() 
                    for x in guuid_valid:
                        guuid_valid_list.append(x[0])##list3
                    cursor.execute('''SELECT date from groups where username =? and groupname=?;''', username,g_name)
                    gdate_valid=cursor.fetchall() 
                    for x in gdate_valid:
                        gdate_valid_list.append(x[0])##list4
                    cursor.execute('''SELECT username from groups where username =? and groupname=?;''', username,g_name)
                    gusername_valid=cursor.fetchall() 
                    for x in gusername_valid:
                        gusername_valid_list.append(x[0])##list5
            print("_"*50)
            print(gusername_valid_list)
            print("_"*50)
            group_details_test=list(zip(gname_valid_list,decrypted_valid_gdescription,guuid_valid_list,group_details_image,gdate_valid_list,gusername_valid_list))
            return render_template("posts.html",gdescription=group_details_test)


@app.route('/delete_post',methods=['GET','POST'])
def delete_post():
    if request.method=='POST':
        details = request.form.get
        img_uuid= details('uuid')
        print(img_uuid)
    if "username" in session:
        username = session["username"]
        print(username)
    cursor.execute('''DELETE FROM groups WHERE username=? and uuid = ?''',session['username'],img_uuid)
    cursor.commit
    return ("<h2>Deleted</H2>")


@app.route('/approval_requests',methods=['GET','POST'])
def approval_requests():
    if "username" in session:
        username = session["username"]
        print(username)
        cursor.execute('''Select is_admin from users where username=?''',username)
        check_username=cursor.fetchall()
        print(check_username)
        check_user_admin=check_username.pop()
        if check_user_admin[0] == 1:
            cursor.execute('''Select groupname from group_members_status where status=?''',"Requested")
            validate_users = cursor.fetchall()
            cursor.execute('''Select email from group_members_status where status=?''',"Requested")
            validate_users_groups = cursor.fetchall()
            validate_users_groups_list=[]
            validate_users_list=[]
            for x in validate_users:
                validate_users_1= x[0]
                validate_users_list.append(validate_users_1)
            for x in validate_users_groups:
                validate_users_groups_1=x[0]
                validate_users_groups_list.append(validate_users_groups_1)
            group_request_list= list(zip(validate_users_list,validate_users_groups_list))
            return render_template('group_request.html',group_request_list=group_request_list)
        else:
            return render_template('group_request.html')


@app.route('/share_new_post_page',methods=['GET','POST'])
def share_new_post_page():
    return render_template('share_post.html')

@app.route('/share_new_post',methods=['GET','POST'])
def share_new_post():
     if "username" in session:
        username = session["username"]
        if request.method=='POST':
            details = request.form.get
            gname = details('gname')
            gname = gname.strip()
            session['gname']=gname
            gdescription = details('gdescription')
            gdescription = gdescription.strip()
            encrypt_gdescription = to_encrypt_string(gdescription)
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(filename)
            image = open(filename, 'rb')
            image_read = image.read()
            image_64_encode = base64.b64encode(image_read)
            groupimage =image_64_encode.decode("UTF-8")
            cursor.execute('''INSERT INTO groups(groupname,groupdesription ,date ,is_admin,groupimage,username,email) VALUES (?,?,?,?,?,?,?)''',gname, encrypt_gdescription,datetime.now() ,session['email'],groupimage,session['username'],session['email'])
            cnxn.commit()
            cursor.execute('''SELECT firstname,profileimage,lastname,username,email from users where username =?;''', session["username"])
            valid=cursor.fetchall()
            x=valid.pop(0)
            fname = x[0]
            decrypt_fname = to_decrypt_string(fname)
            profilepic = x[1]
            lname = x[2]
            username =x[3]
            session['username']= username
            email= x[4]
            print("#"*40)
            session['email']=email
            print(session['email'])
            lname= to_decrypt_string(lname)
            return render_template('homepage.html',fname=decrypt_fname,profilepic=profilepic,lname=lname)


@app.route("/request_approved",methods=["POST","GET"])
def request_approved():
    if request.method == 'POST':
        hidden_skills = request.form['hidden_skills']
        hidden_skills=hidden_skills.split(",")
        print(hidden_skills)
        alternate_groups= hidden_skills[1::2]
        print(alternate_groups)
        alternate_email=hidden_skills[0::2]
        approved_email=list(zip(alternate_email,alternate_groups))
        print(approved_email)
        for x in approved_email:
            print(x[0])
            print(x[1])
            cursor.execute('''UPDATE group_members_status SET status=? where groupname=? and email=?;''',"Approved",x[1],x[0])
            cursor.commit()
        return ("Approved")


        
        
















@app.route('/logout',methods=['GET','POST'])
def logout():
    if request.method=='POST':
        session['email']=None
        session['username']=None
        session['gname']=None
        return render_template("login.html")


if __name__== "__main__":
    app.run(debug=True)

