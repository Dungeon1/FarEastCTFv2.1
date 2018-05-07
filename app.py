#!/usr/bin/env python
import dataset
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from flask import escape
from flask import jsonify
import json
import datetime
from datetime import date, timedelta
import os
import urllib.request
import random
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='')

def get_user():
    login = 'user_id' in session
    if login:
        return db_fectf['users'].find_one(id=session['user_id'])

    return None

def session_login(email):
    user = db_fectf['users'].find_one(email=email)
    session['user_id'] = user['id']

def dbQueryArticlesLimit():
    news = db_fectf.query("SELECT * FROM articles ORDER BY id DESC LIMIT 3")
    news = list(news)
    return(news)

def dbQueryArticles():
    news = db_fectf.query("SELECT * FROM articles ORDER BY id DESC")
    news = list(news)
    return(news)

def dbQueryPartners():
    partners = db_fectf.query("SELECT * FROM partners")
    partners = list(partners)
    return(partners)

def dbQueryDocuments():
    documents = db_fectf.query("SELECT * FROM documents")
    documents = list(documents)
    return(documents)

def dbQueryTodayComp():
    today_competition = db_fectf.query("SELECT * FROM today_competition")
    today_competition = list(today_competition)
    return(today_competition)

def dbQueryUserEmail():
    UserEmail = db_fectf.query("SELECT username, email FROM users")
    UserEmail = list(UserEmail)
    return(UserEmail)

#def dbQueryAdminsContacts():
#    AdminsContacts = db_fectf.query("SELECT * FROM admin_contacts")
#    AdminsContacts = list(AdminsContacts)
#    #print(AdminsContacts)
#    phone_name=[]
#    telegram=[]
#    email=[]
#    address=[]
#    #распихаем все по спискам
#    for string in AdminsContacts:
#        if string['phone_name']:
#            phone_name.append(string['phone_name'])
#        if string['telegram']:
#            telegram.append(string['telegram'])
#        if string['email']:
#            email.append(string['email'])
#        if string['address']:
#            address.append(string['address'])

#    return(phone_name, telegram, email, address)


@app.route('/')
def index():
    user = get_user()
    articles=dbQueryArticlesLimit()
    partners = dbQueryPartners()
    today_comp = dbQueryTodayComp()
    return render_template('main_page.html', user=user, articles=articles, partners=partners, today_comp=today_comp, SITE_KEY=SITE_KEY)

@app.route('/news_list')
def news_list():
    articles=dbQueryArticles()
    return render_template('news_list.html',articles=articles)

@app.route('/documents')
def documents():
    documents = dbQueryDocuments()
    return render_template('documents.html', documents=documents)

@app.route('/who')
def who():
    return render_template('who.html')

@app.route('/error/<msg>')
def error(msg):
    if msg in errors['error']:
        message = errors['error'][msg]
    else:
        message = errors['error']['unknown']
    user = get_user()
    return render_template('error.html', message=message, user=user, SITE_KEY=SITE_KEY)

@app.route('/massage/<msg>')
def massage(msg):
    if msg in errors['massage']:
        message = errors['massage'][msg]
    else:
        message = errors['error']['unknown']
    if msg =='registration_complete'or msg =='forgot_pass':
        user = get_user()
        return render_template('massage.html', message=message, user=user, buttom='home')
    if msg =='email_send' or msg=='pass_complete':
        user = get_user()
        return render_template('massage.html', message=message, user=user, buttom='pr_room')
    else:
        return render_template('massage.html', message=message, user=user)


@app.route('/404')
def none():
    return render_template('404.html')

@app.route('/article/<string:id>')
def article(id):
    article = db_fectf['articles'].find_one(id=id)
    if article:
        other_articles = dbQueryArticlesLimit()
        return render_template('article.html', article=article, other_articles=other_articles)
    else:
        return render_template('404.html')

# PrivateRoom
@app.route('/private_room')
def private_room():
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif user['isAdmin']:
        articles = dbQueryArticles()
        partners = dbQueryPartners()
        documents = dbQueryDocuments()
        today_comp = dbQueryTodayComp()
        useremail = dbQueryUserEmail()
        return render_template('private_room.html', user=user, articles=articles, partners=partners, documents=documents, today_comp=today_comp, useremail=useremail)
    else:
        return render_template('private_room.html', user=user, SITE_KEY=SITE_KEY)

    
#РЕГИСТРАЦИЯ
@app.route('/register/submit', methods = ['GET', 'POST'])
def reg():
    if request.method == 'POST':
        print("Зашел")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        response = request.form.get('g-recaptcha-response')
        if checkRecaptcha(response,SECRET_KEY):
            print("капча тут")
            if not username:
                return redirect(url_for('error', msg='empty_user')) 
            #если пользователь найден
            elif db_fectf['users'].find_one(username=username):
                return redirect(url_for('error', msg='already_exist_login'))
            #если email найден
            elif db_fectf['users'].find_one(email=email):
                return redirect(url_for('error', msg='already_exist_email'))
            else:
                #from emailSend import emailRegistrationSend
                #emailSend = emailRegistrationSend(username, password, email, myEmail, myEmailPass)
                #if not emailSend:
                #    return redirect(url_for('error', msg='email_errorSend'))
                #else:
                if register_submit(db_fectf, username, email, password):
                    return redirect(url_for('massage', msg='registration_complete'))
                else: 
                    return redirect(url_for('error', msg='error_register'))
        else:
            return redirect(url_for('error', msg='bot'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))


def checkRecaptcha(response, secretkey):
    url = 'https://www.google.com/recaptcha/api/siteverify?'
    url = url + 'secret=' +secretkey
    url = url + '&response=' +response
    try:
        jsonobj = json.loads((urllib.request.urlopen(url).read()).decode("utf-8"))
        if jsonobj['success']:
            return True
        else:
            return False
    except Exception as e:
        return False
    
    

def register_submit(db_fectf, username, email, password): 
    isAdmin = 0
    userCount = db_fectf['users'].count()
    #if no users, make first user admin
    if userCount == 0:
        isAdmin = 1
    #Случальное число аватарки
    avatar_num = random.randrange(1, 26)        
    #Создание словаря
    new_user = dict(username=username, password=generate_password_hash(password), email=email, isAdmin=isAdmin, avatar_num=avatar_num)
    if db_fectf['users'].insert(new_user):
        return True
    else:
        return False

    
    
    
#АВТОРИЗАЦИЯ
@app.route('/login/submit', methods = ['GET', 'POST'])
def author():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        #Вся информация о пользователе из базы
        user = db_fectf['users'].find_one(email=email)
        if user is None:
            return redirect(url_for('error', msg='invalid_login'))
        #if user['password'] == password:
        if check_password_hash(user['password'], password):
            session_login(email)
            return redirect(url_for('index'))
            #Вход произведен
        else:
            return redirect(url_for('error', msg='invalid_credentials'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))

    
@app.route('/logout')
def logout():
    del session['user_id']
    return redirect('/')

#В _modal_window удалил HTML сброс пароля и ссылку Забыли пароль
#СБРОС ПАРОЛЯ
#@app.route('/forgot_pass/submit', methods = ['GET', 'POST'])
#def forgot_pass():
#    if request.method == 'POST':
#        username = request.form['reset_username']
#        email = request.form['reset_email']
#        response = request.form.get('g-recaptcha-response')
#        if checkRecaptcha(response,SECRET_KEY):
#            #Найдем пользователя
#            user = db_fectf['users'].find_one(username=username)
#            if user:
#                if email == user['email']:
#                    randomPassword = id_generator()
#                    #генерируем хэш и вставляем его в бд
#                    randomPasswordHash=generate_password_hash(randomPassword)
#                    newPas = db_fectf.query('''UPDATE users SET password = :newPass WHERE username= :username''', newPass=randomPasswordHash, username=username)
#                    from emailSend import emailForgotPassword
#                    #####################################
#                    emailSend = emailForgotPassword(username, email, randomPassword, myEmail, myEmailPass)
#                    if emailSend:
#                        return redirect(url_for('massage', msg='forgot_pass')) 
#                        #return redirect(url_for('index'))
#                    else:
#                        return redirect(url_for('error', msg='email_errorSend'))
#                else:
#                    return redirect(url_for('error', msg='invalid_email')) 
#            else:
#                return redirect(url_for('error', msg='invalid_login'))
#        else:
#            return redirect(url_for('error', msg='bot'))
#    else:
#        #Метод не POST
#        return redirect(url_for('error', msg='method_error'))
    
            

def id_generator():   
    pas = ''
    for x in range(16): #Количество символов (16)
        pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ@!$&*^')) #Символы, из которых будет составлен пароль
    return pas


#СМЕНА ПАРОЛЯ
@app.route('/refresh_pass/submit', methods = ['GET', 'POST'])
def refresh_pass():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return render_template('404.html')
        old_pass = request.form['old_pass']
        new_pass = request.form['new_pass']
        repeat_new_pass = request.form['repeat_new_pass']
        response = request.form.get('g-recaptcha-response')
        if user:
            if checkRecaptcha(response,SECRET_KEY):
                    #Найдем пользователя
                    user_in_db = db_fectf['users'].find_one(username=user['username'])
                    username = user['username']
                    if user_in_db:
                        print(old_pass, user_in_db['password'])
                        #if old_pass == user_in_db['password']:
                        if check_password_hash(user_in_db['password'], old_pass):
                            if new_pass == repeat_new_pass:
                                update = db_fectf.query("UPDATE users SET password=:new_pass WHERE username=:username", new_pass=generate_password_hash(new_pass), username=username)
                            else:
                                #Введенные пароли не совпадают
                                return redirect(url_for('error', msg='pass_error')) 
                        else:
                            #Введенный старый пароль не совпадает с тем, что в базе
                            return redirect(url_for('error', msg='old_pass_error')) 
                    else:
                        #Не найден пользователь
                        return redirect(url_for('error', msg='invalid_login')) 
            else:
                #Капча не правильная
                return redirect(url_for('error', msg='bot'))
        else:
            #Вы не залогинены
            return redirect(url_for('error', msg='login_required'))
        
        #return redirect(url_for('private_room'))
        return redirect(url_for('massage', msg='pass_complete'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    


#Отправка письма оргам из личного кабинета
#@app.route('/send_email_to_org/submit', methods = ['GET', 'POST'])
#def send_email_to_org():
#    if request.method == 'POST':
#        user = get_user()
#        print(user)
#        if user:
#            print('проверил пользователя')
#            text_of_massage = request.form['emailForOrg']
#            response = request.form.get('g-recaptcha-response')
#            if checkRecaptcha(response,SECRET_KEY):
#                print('Капча норм')
#                from emailSend import emailToOrg
#                print("Подготовка к отправке письма")
#                #####################################
#                emailSend = emailToOrg(user['username'], user['email'], text_of_massage, EmailSenderToOrg, EmailSenderToOrgPass, EmailReceiverOrg)
#                if emailSend:
#                    print("Письмо отправлено")
#                    #return redirect(url_for('private_room'))
#                    return redirect(url_for('massage', msg='email_send'))
#                else:
#                    return redirect(url_for('error', msg='email_errorSend'))
#            return redirect(url_for('error', msg='bot'))
#        else:
#            #Вы не залогинены
#            return redirect(url_for('error', msg='login_required'))
#    else:
#        #Метод не POST
#        return redirect(url_for('error', msg='method_error'))
                    
        
        
@app.route('/addArticle', methods = ['GET', 'POST'])
def addArticle():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user['isAdmin']:
            newArticle_name = request.form['new_article_name']
            new_short_articles = request.form['new_short_articles']
            newArticle = request.form['new_articles']
            data_article = request.form['data_article']
            file = request.files['main_img_article']
            filename = file.filename
            file.save(os.path.join("static/article_img/", filename))
            db_fectf['articles'].insert(dict(header=newArticle_name, article_text=newArticle, main_img=filename, data=data_article, article_short_text=new_short_articles))
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    #Добавить ответ что типо все ок (ajax?)


@app.route('/addPartners', methods = ['GET', 'POST'])
def addPartners():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user['isAdmin']:
            name_partner = request.form['name_partner']
            link_partner = request.form['link_partner']
            height = request.form['height']
            width = request.form['width']
            file = request.files['logo_partners']
            filename = file.filename
            file.save(os.path.join("static/partner_img/", filename))
            db_fectf['partners'].insert(dict(name=name_partner, image_partners=filename, link=link_partner, height=height, width=width))
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    
@app.route('/addDocument', methods = ['GET', 'POST'])
def addDocument():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user['isAdmin']:
            name_on_site = request.form['name_on_site']
            file = request.files['document']
            fullDocName = file.filename
            lists = fullDocName.split('.')
            DocName = lists[0]
            DocExtension = lists[1]
            file.save(os.path.join("static/documents/", fullDocName))
            db_fectf['documents'].insert(dict(name=fullDocName, extension=DocExtension, name_on_site=name_on_site))
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))



@app.route('/deleteArticles/<string:id>', methods = ['GET', 'POST'])
def deleteArticles(id):
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif not user['isAdmin']:
        return redirect(url_for('error', msg='admin_required'))
    elif user['isAdmin']:
        query = db_fectf.query('''DELETE FROM articles WHERE id = :id''', id=id)    
        return redirect(url_for('private_room'))


@app.route('/deletePartner/<string:id>', methods = ['GET', 'POST'])
def deletePartner(id):
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif not user['isAdmin']:
        return redirect(url_for('error', msg='admin_required'))
    elif user['isAdmin']:
        query = db_fectf.query('''DELETE FROM partners WHERE id = :id''', id=id)    
        return redirect(url_for('private_room'))
    
@app.route('/deleteDocument/<string:id>', methods = ['GET', 'POST'])
def deleteDocument(id):
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif not user['isAdmin']:
        return redirect(url_for('error', msg='admin_required'))
    elif user['isAdmin']:
        query = db_fectf.query('''DELETE FROM documents WHERE id = :id''', id=id)    
        return redirect(url_for('private_room'))


@app.route('/EditHeight_partner/<string:id>', methods = ['GET', 'POST'])
def EditHeight(id):
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user['isAdmin']:
            height = request.form['partner_height']
            update = db_fectf.query("UPDATE partners SET height=:height WHERE id=:id", height=height, id=id)    
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))


@app.route('/EditWidth_partner/<string:id>', methods = ['GET', 'POST'])
def EditWidth(id):
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user['isAdmin']:
            width = request.form['partner_width']
            update = db_fectf.query("UPDATE partners SET width=:width WHERE id=:id", width=width, id=id)    
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))


@app.route('/editArticles/<string:id>', methods = ['GET', 'POST'])
def editArticles(id):
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif not user['isAdmin']:
        return redirect(url_for('error', msg='admin_required'))
    elif user['isAdmin']:
        article = db_fectf['articles'].find_one(id=id)
        return render_template('editArticles.html', user=user, article=article)


@app.route('/edit/<string:id>', methods = ['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            article = db_fectf['articles'].find_one(id=id)
            header = request.form['new_article_name']
            article_short_text = request.form['new_short_articles']
            article_text = request.form['new_articles']
            main_img = request.files['main_img_article']
            main_img_name= main_img.filename
            data = request.form['data_article']
            #-------------------------------------------------
            if not main_img:
                print("Новой картинки нет, меняем все остальное")
                update = db_fectf.query("UPDATE articles SET header=:header, article_short_text=:article_short_text, article_text=:article_text, data=:data WHERE id=:id", header=header, article_short_text=article_short_text, article_text=article_text, data=data, id=id)
            else:
                if article["main_img"] == main_img_name:
                    print("Наименование картинки то же меняем все кроме ее")
                    update = db_fectf.query("UPDATE articles SET header=:header, article_short_text=:article_short_text, article_text=:article_text, data=:data WHERE id=:id", header=header, article_short_text=article_short_text, article_text=article_text, data=data, id=id)
                else:
                    print("Меняем картинку")
                    #С заменой имени картинки
                    update = db_fectf.query("UPDATE articles SET header=:header, article_text=:article_text, main_img=:main_img_name, data=:data,  article_short_text=:article_short_text WHERE id=:id", header=header, article_text=article_text, main_img_name=main_img_name, data=data, article_short_text=article_short_text, id=id)
                    #Загрузка новой картинки
                    main_img.save(os.path.join("static/article_img/", main_img_name))
            #print("Имя изменили")
            #return render_template('editArticles.html', user=user, article=article)
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))



@app.route('/addTodayComp', methods = ['GET', 'POST'])
def addTodayComp():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            todayCompName = request.form['todayCompName']
            header_comp = request.form['header_comp']
            text_comp = request.form['text_comp']
            buttom_name = request.form['buttom_name']
            file = request.files['image_comp']
            image_name = file.filename
            file.save(os.path.join("static/article_img/", image_name))
            db_fectf['today_competition'].insert(dict(todayCompName=todayCompName, header=header_comp, image_name=image_name, text=text_comp, buttom_name=buttom_name))
            print("Новый чемпионат вставили")
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    

@app.route('/updateTodayCompMainName', methods = ['GET', 'POST'])
def updateTodayCompMainName():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            compMainName = request.form['updatetodayCompMainName']
            update = db_fectf.query("UPDATE today_competition SET todayCompName=:compMainName", compMainName=compMainName)
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    


@app.route('/updateTodayCompText', methods = ['GET', 'POST'])
def updateTodayCompText():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            newtext_comp = request.form['newtext_comp']
            update = db_fectf.query("UPDATE today_competition SET text=:newtext_comp", newtext_comp=newtext_comp)
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))

    
@app.route('/updateTodayCompImageHeight', methods = ['GET', 'POST'])
def updateTodayCompImageHeight():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            new_image_height = request.form['new_image_height']
            update = db_fectf.query("UPDATE today_competition SET image_height=:new_image_height", new_image_height=new_image_height)
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    

@app.route('/updateTodayCompImage', methods = ['GET', 'POST'])
def updateTodayCompImage():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            file = request.files['newimage_comp']
            image_name = file.filename
            file.save(os.path.join("static/article_img/", image_name))

            update = db_fectf.query("UPDATE today_competition SET image_name=:image_name", image_name=image_name)
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    
    
@app.route('/deleteTodayComp', methods = ['GET', 'POST'])
def deleteTodayComp():
    if request.method == 'POST':
        user = get_user()
        if not user:
            return redirect(url_for('error', msg='login_required'))
        elif not user['isAdmin']:
            return redirect(url_for('error', msg='admin_required'))
        elif user["isAdmin"]:
            query = db_fectf.query("DELETE FROM today_competition")    
            return redirect(url_for('private_room'))
    else:
        #Метод не POST
        return redirect(url_for('error', msg='method_error'))
    

@app.route('/deleteUser/<string:username>', methods = ['GET', 'POST'])
def deleteUser(username):
    user = get_user()
    if not user:
        return redirect(url_for('error', msg='login_required'))
    elif not user['isAdmin']:
        return redirect(url_for('error', msg='admin_required'))
    elif user["isAdmin"]:
        query = db_fectf.query("DELETE FROM users WHERE username=:username", username=username)    
        return redirect(url_for('private_room'))


#SISTEM SETINGS
db_fectf = dataset.connect('sqlite:///db/fectf.db')
app.secret_key = 'avesomefareastctf'
#SITE_KEY = '6LdfkFEUAAAAAMIBbg3UU2QkwhS0IkwhebH9CQBo' #-локальный
#SECRET_KEY = '6LdfkFEUAAAAAJlMq7rStntNXyorsTjVkyEDtQY9' #-локальный
SITE_KEY = '6LcNrFUUAAAAAHhEyGtpHaWM8Yb_LprumlnEpOHt' #-удаленный
SECRET_KEY = '6LcNrFUUAAAAADFeTdzIyBh_2SwrPzVBvXn4yR87' #-удаленный

#С этого адреса отправляется письмо при регистрации и при забытом пароле
myEmail = 'fareastctf@mail.ru'
myEmailPass = 'qwerty1234567890'

#Отсюда отправляется письмо из личного кабинета для организаторов
EmailSenderToOrg = 'autoemailfromusers@mail.ru'
EmailSenderToOrgPass = 'FarEastCTF2017'

#Адрес принимает письма из личного кабинета для организаторов
EmailReceiverOrg = 'fareastctf@mail.ru'

#fareastctf@yandex.ru - метрика
#fareastctf@gmail.com - google analytics

# Load error_list
errors_str = open('static/errors.json', 'r').read()
errors = json.loads(errors_str)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

#СПИСОК ДЕЛ
#Трен площадку замутить