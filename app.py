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
import datetime
from datetime import date, timedelta
import os

app = Flask(__name__, static_folder='static', static_url_path='')

def get_user():
    login = 'user_id' in session
    if login:
        return db_fectf['users'].find_one(id=session['user_id'])

    return None

def dbQueryArticlesLimit():
    print("Зашел в функцию статьи")
    news = db_fectf.query("SELECT * FROM articles ORDER BY id DESC LIMIT 3")
    news = list(news)
    print('news= ', news)
    return(news)

def dbQueryArticles():
    print("Зашел в функцию статьи")
    news = db_fectf.query("SELECT * FROM articles ORDER BY id DESC")
    news = list(news)
    print('news= ', news)
    return(news)

def dbQueryPartners():
    partners = db_fectf.query("SELECT * FROM partners")
    partners = list(partners)
    return(partners)

@app.route('/')
def index():
    user = get_user()
    articles=dbQueryArticlesLimit()
    partners = dbQueryPartners()
    return render_template('main_page.html', user=user, articles=articles, partners=partners)

@app.route('/news_list')
def news_list():
    articles=dbQueryArticles()
    return render_template('news_list.html',articles=articles)

@app.route('/article/<string:id>')
def article(id):
    article = db_fectf['articles'].find_one(id=id)
    other_articles = dbQueryArticlesLimit()
    return render_template('article.html', article=article, other_articles=other_articles)

# PrivateRoom
@app.route('/private_room')
def private_room():
    user = get_user()
    if user['isAdmin']:
        articles = dbQueryArticles()
        partners = dbQueryPartners()
        return render_template('private_room.html', user=user, articles=articles, partners=partners)
    else:
        return render_template('private_room.html', user=user)
    


def session_login(email):
    print("Зашли в функцию session_login")
    user = db_fectf['users'].find_one(email=email)
    print("Выводим переменную user ", user)
    print(user['id'])
    session['user_id'] = user['id']
    print("Выводим сессию:")
    print("session['id']=", session['user_id'])


#РЕГИСТРАЦИЯ
@app.route('/register/submit', methods = ['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        print(username)
        email = request.form['email']
        print(email)
        password = request.form['password']
        print(password)
        #from register import register_submit
        url = register_submit(db_fectf, username, email, password)
        if url:
            #print("Отправляет письмо")
            #from emailSend import emailRegistrationSend
            #emailRegistrationSend(username, password)
            #print("Письмо отправленно")
            return redirect(url)
        else:
            print("Ошибка регистрации")
            return redirect(url_for('register'))
        
def register_submit(db_fectf, username, email, password):
    """Попытки зарегистрировать нового пользователя"""
    print('зашел в регистрацию')        
    if not username:
        print("Пустое поле логина")
        return None

    user_found = db_fectf['users'].find_one(username=username)
    if user_found:
        print("Такой уже есть")
        return None
    
    email_found = db_fectf['users'].find_one(email=email)
    if email_found:
        print("Такой email уже есть")
        return None

    isAdmin = 0
    userCount = db_fectf['users'].count()
    #if no users, make first user admin
    if userCount == 0:
        isAdmin = 1
        print("Теперь ты ", username, " админ!!")
    elif userCount > 0:
        print("Регистрация прошла успешно")
        
    print(username, type(username), "\n", password, type(password), "\n", isAdmin, type(isAdmin))
    #Создание словаря
    new_user = dict(username=username, password=password, email=email, isAdmin=isAdmin)
    db_fectf['users'].insert(new_user)

    #Изменил должен переходить на /category 
    #redirect перенаправляет пользователя на другую страницу
    return url_for('index')
    
    
#АВТОРИЗАЦИЯ
@app.route('/login/submit', methods = ['GET', 'POST'])
def author():
    if request.method == 'POST':
        email = request.form['email']
        print(email)
        password = request.form['password']
        print(password)
        
        #Вся информация о пользователе из базы
        user = db_fectf['users'].find_one(email=email)
        print("Найденый юзер ", user)
        if user is None:
            print("Нет такого юзера!")
            #return redirect(url_for('index'))
        if user['password'] == password:
            session_login(email)
            return redirect(url_for('index'))
            print("Вход произведен")
        else:
            print("Что то не так")
            #return redirect(url_for('index'))

@app.route('/logout')
def logout():
    print("Зашел в функцию выхода")
    print(session['user_id'])
    del session['user_id']
    return redirect('/')


@app.route('/addArticle', methods = ['GET', 'POST'])
def addArticle():
    user = get_user()
    newArticle_name = request.form['new_article_name']
    new_short_articles = request.form['new_short_articles']
    newArticle = request.form['new_articles']
    data_article = request.form['data_article']
    file = request.files['main_img_article']
    filename = file.filename
    file.save(os.path.join("static/article_img/", filename))
    db_fectf['articles'].insert(dict(header=newArticle_name, article_text=newArticle, main_img=filename, data=data_article, article_short_text=new_short_articles))
    print("Статью вставили")
    return redirect(url_for('private_room'))


@app.route('/addPartners', methods = ['GET', 'POST'])
def addPartners():
    user = get_user()
    name_partner = request.form['name_partner']
    link_partner = request.form['link_partner']
    height = request.form['height']
    width = request.form['width']
    file = request.files['logo_partners']
    filename = file.filename
    file.save(os.path.join("static/partner_img/", filename))
    db_fectf['partners'].insert(dict(name=name_partner, image_partners=filename, link=link_partner, height=height, width=width))
    print("Партнера вставили")
    return redirect(url_for('private_room'))



@app.route('/deleteArticles/<string:id>')
def deleteArticles(id):
    print("Зашел в функцию удаления статьи")
    query = db_fectf.query('''DELETE FROM articles WHERE id = :id''', id=id)    
    return redirect(url_for('private_room'))


@app.route('/deletePartner/<string:id>')
def deletePartner(id):
    print("Зашел в функцию удаления статьи")
    query = db_fectf.query('''DELETE FROM partners WHERE id = :id''', id=id)    
    return redirect(url_for('private_room'))


@app.route('/EditHeight_partner/<string:id>', methods = ['GET', 'POST'])
def EditHeight(id):
    height = request.form['partner_height']
    update = db_fectf.query("UPDATE partners SET height=:height WHERE id=:id", height=height, id=id)    
    return redirect(url_for('private_room'))


@app.route('/EditWidth_partner/<string:id>', methods = ['GET', 'POST'])
def EditWidth(id):
    width = request.form['partner_width']
    update = db_fectf.query("UPDATE partners SET width=:width WHERE id=:id", width=width, id=id)    
    return redirect(url_for('private_room'))


    
@app.route('/editArticles/<string:id>')
def editArticles(id):
    user = get_user()
    article = db_fectf['articles'].find_one(id=id)
    print("Функция изменения статьи", article)
    return render_template('editArticles.html', user=user, article=article)

# Необходимо добавить AJAX!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route('/edit/<string:id>', methods = ['GET', 'POST'])
def edit(id):
    user = get_user()
    article = db_fectf['articles'].find_one(id=id)
    if user["isAdmin"]:
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
    
    #НЕ ДОДЕЛАЛ
@app.route('/addTodayComp', methods = ['GET', 'POST'])
def addTodayComp():
    user = get_user()
    newArticle_name = request.form['new_article_name']
    new_short_articles = request.form['new_short_articles']
    newArticle = request.form['new_articles']
    data_article = request.form['data_article']
    file = request.files['main_img_article']
    filename = file.filename
    file.save(os.path.join("static/article_img/", filename))
    db_fectf['articles'].insert(dict(header=newArticle_name, article_text=newArticle, main_img=filename, data=data_article, article_short_text=new_short_articles))
    print("Статью вставили")
    return redirect(url_for('private_room'))


#SISTEM SETINGS
db_fectf = dataset.connect('sqlite:///db/fectf.db')
app.secret_key = 'avesomefareastctf'
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

