import pandas as pd
from pyecharts import Line
from flask import Flask, render_template,session,redirect,url_for,flash,request
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField,StringField
from wtforms.validators import data_required,Regexp
from flask_bootstrap import Bootstrap
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap(app)
REMOTE_HOST = "static/js"


total_birthsqs=pd.read_pickle('file/xingming_qushi_test.pkl')

class NamestrForm(FlaskForm):
    name1 = StringField('请输入名字，不含姓氏',validators=[data_required(),Regexp('^[\u4e00-\u9fa5]{0,4}$',message='请输入1到4个汉字')])
    name2 = StringField('请输入进行比较的名字，不含姓氏',validators=[Regexp('^[\u4e00-\u9fa5]{0,4}$',message='请输入1到4个汉字')])
    submit = SubmitField('确认')

def mingzi_qushi(str,str2=None):
    line3 = Line('命名趋势')
    x = [i for i in total_birthsqs.index]
    if str and str in total_birthsqs.columns:#如果不在字典的列中，会报错
        y = [i for i in total_birthsqs[str]]
        line3.add(str,x,y)
    if str2 and str2 in total_birthsqs.columns:
        y2 = [i for i in total_birthsqs[str2]]
        line3.add(str2,x,y2)
    return line3    

    
@app.route("/", methods=['GET', 'POST'])
def xingming():
    ip = request.remote_addr
    user_agent=request.user_agent
    c_time=datetime.now()
    c_timestr=c_time.strftime('%Y-%m-%d %H:%M')
    with open('simplelog.txt','a') as f:
        if not ip:
            f.write('{'+'ip:\''+'木有ip'+'\','+'browser:\''+user_agent.browser+'\','+'os:\''+user_agent.platform+'\',time:\''+c_timestr+'\'}\n')
        elif not user_agent:
            f.write('{'+'ip:\''+ip+'\','+'browser:\''+'没有UA'+'\','+'os:\''+'没有UA'+'\',time:\''+c_timestr+'\'}\n')
        elif not user_agent.browser:
            f.write('{'+'ip:\''+ip+'\','+'browser:\''+'没有browser'+'\','+'os:\''+user_agent.platform+'\',time:\''+c_timestr+'\'}\n')
        elif not user_agent.platform:
            f.write('{'+'ip:\''+ip+'\','+'browser:\''+user_agent.browser+'\','+'os:\''+'没有os'+'\',time:\''+c_timestr+'\'}\n')
        else:
            f.write('{'+'ip:\''+ip+'\','+'browser:\''+user_agent.browser+'\','+'os:\''+user_agent.platform+'\',time:\''+c_timestr+'\'}\n')
    global total_birthsqs
    form = NamestrForm()
    if form.validate_on_submit():
        session['str'] = form.name1.data
        session['str2'] = form.name2.data
        return redirect(url_for('xingming'))
    if session.get('str'):
        str = session['str']
    else:
        str = None
    if session.get('str2'):
        str2 = session['str2']
    else:
        str2 = None
    if str and str not in total_birthsqs.columns:
        flash('名字是%s的人很少'%str)
    if str2 and str2 not in total_birthsqs.columns:
        flash('名字是%s的人很少'%str2)
    l3 = mingzi_qushi(str,str2)
    if session.get('str'):
        form.name1.data = session['str']
    if session.get('str2'):
        form.name2.data = session['str2']
    return render_template('xingming.html',
                       myechart=l3.render_embed(),
                       host=REMOTE_HOST,
                       script_list=l3.get_js_dependencies(),
                       form = form)

