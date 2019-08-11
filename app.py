from flask import Flask,render_template,g,request
import sqlite3
from datetime import datetime
app = Flask(__name__)


def connect_db():
  sql = sqlite3.connect('food_log.db')
  sql.row_factory = sqlite3.Row
  return sql

def get_db():
  if not hasattr(g,'sqlite3_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
  if hasattr(g,'sqlite3_db'):
    g.sqlite_db.close()

@app.route('/', methods = ['GET','POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form["date"]
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date (entry_date) values(?)',[database_date])
        db.commit()
    cur = db.execute('''select log_date.entry_date ,sum(food.protein) as protein ,sum(food.carbohydrates) as carbohydrates , sum(food.fat)as fat,sum(food.calories)as calories
                        from log_date left
                        join food_data on food_data.log_date_id = log_date.id left
                        join food on food.id = food_data.food_id group by log_date.id order by log_date.entry_date asc''')
    results = cur.fetchall()
    pr = []
    for i in results:
        single_date = {}
        single_date['date_each'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']
        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
        pr.append(single_date)

    return render_template('home.html',results = pr,)

@app.route('/view/<date>',methods = ['GET','POST'])
def view(date):
    db = get_db()

    curr = db.execute('select id,entry_date from log_date where entry_date = ?',[date])
    date_result = curr.fetchone()

    if request.method == 'POST':
        db.execute('insert into food_data (food_id,log_date_id) values (?,?)',[request.form['food_select'],date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']),'%Y%m%d')
    pr = datetime.strftime(d, '%B %d, %Y')
    food_cur = db.execute('select id,name from food order by id asc')
    food_res = food_cur.fetchall()

    log_cur = db.execute('select food.name,food.protein,food.carbohydrates , food.fat,food.calories from log_date join food_data on food_data.log_date_id = log_date.id join food on food.id = food_data.food_id where log_date.entry_date = ?',[date])
    log_result = log_cur.fetchall()

    total = {}
    total['protein'] = 0
    total['carbohydrates'] = 0
    total['fat'] = 0
    total['calories'] = 0


    for food in log_result:
        total['protein'] += food['protein']
        total['carbohydrates'] += food['carbohydrates']
        total['fat'] += food['fat']
        total['calories'] += food['calories']


    return render_template('day.html',entry_date = date_result['entry_date'],date = pr,food_result = food_res , log_result = log_result,total = total)

@app.route('/food', methods = ['GET','POST'])
def food():
    db=get_db()

    if(request.method == 'POST'):
        name = (request.form['food-name'])
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        calories =(protein * 4 +carbohydrates * 4 + fat * 9)


        db.execute('insert into food (name,protein,carbohydrates,fat,calories) values (?,?,?,?,?)', \
        [name,protein,carbohydrates,fat,calories])
        db.commit()
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()


    return render_template('add_food.html', results = results)


if __name__ == '__main__':
	app.run(debug = True)
