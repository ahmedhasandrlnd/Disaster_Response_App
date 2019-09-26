from flask import Flask, render_template, url_for, flash, redirect, request
from datetime import datetime
from forms import MsgForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd
import json
import plotly
from plotly.graph_objs import Bar, Histogram, Scatter, Heatmap
from sklearn.externals import joblib
import string
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import json

#nltk.download(['punkt', 'wordnet','stopwords'])



app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/DisasterResponse.db'
app.config['SQLALCHEMY_BINDS']={'msgs':'sqlite:///site.db'}



db = SQLAlchemy(app)

#engine_dataset = db.get_engine(app, 'dataset')
#sql = text("SHOW TABLES")
#results_dataset = engine_dataset.execute("SHOW TABLES")

def tokenize(text):
    text = "".join([word.lower() for word in text if word not in string.punctuation])
    tokens = re.split('\W+', text)
    text = [nltk.PorterStemmer().stem(word) for word in tokens if word not in stopwords.words('english')]
    lemmed = [WordNetLemmatizer().lemmatize(word, pos='v') for word in text]
    return lemmed


# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('Disaster_Response', engine)

# load model
model = joblib.load("../models/model.pkl")



current_user="Ahmed Hasan"
cats=['related', 'request', 'offer', 'aid_related', 'medical_help',
       'medical_products', 'search_and_rescue', 'security', 'military',
       'child_alone', 'water', 'food', 'shelter', 'clothing', 'money',
       'missing_people', 'refugees', 'death', 'other_aid',
       'infrastructure_related', 'transport', 'buildings', 'electricity',
       'tools', 'hospitals', 'shops', 'aid_centers',
       'other_infrastructure', 'weather_related', 'floods', 'storm',
       'fire', 'earthquake', 'cold', 'other_weather', 'direct_report']


class Msg(db.Model):
    __bind_key__='msgs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default="Ahmed Hasan")
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    related = db.Column(db.Integer,nullable=False, default=0)
    request = db.Column(db.Integer,nullable=False, default=0)
    offer = db.Column(db.Integer,nullable=False, default=0)
    aid_related = db.Column(db.Integer,nullable=False, default=0)
    medical_help = db.Column(db.Integer,nullable=False, default=0)
    medical_products = db.Column(db.Integer,nullable=False, default=0)
    search_and_rescue = db.Column(db.Integer,nullable=False, default=0)
    security = db.Column(db.Integer,nullable=False, default=0)
    military = db.Column(db.Integer,nullable=False, default=0)
    child_alone = db.Column(db.Integer,nullable=False, default=0)
    water = db.Column(db.Integer,nullable=False, default=0)
    food = db.Column(db.Integer,nullable=False, default=0)
    shelter = db.Column(db.Integer,nullable=False, default=0)
    clothing = db.Column(db.Integer,nullable=False, default=0)
    money = db.Column(db.Integer,nullable=False, default=0)
    missing_people = db.Column(db.Integer,nullable=False, default=0)
    refugees = db.Column(db.Integer,nullable=False, default=0)
    death  = db.Column(db.Integer,nullable=False, default=0)
    other_aid  = db.Column(db.Integer,nullable=False, default=0)
    infrastructure_related = db.Column(db.Integer,nullable=False, default=0)
    transport  = db.Column(db.Integer,nullable=False, default=0)
    buildings = db.Column(db.Integer,nullable=False, default=0)
    electricity = db.Column(db.Integer,nullable=False, default=0)
    tools = db.Column(db.Integer,nullable=False, default=0)
    hospitals = db.Column(db.Integer,nullable=False, default=0)
    shops = db.Column(db.Integer,nullable=False, default=0)
    aid_centers = db.Column(db.Integer,nullable=False, default=0)
    other_infrastructure = db.Column(db.Integer,nullable=False, default=0)
    weather_related = db.Column(db.Integer,nullable=False, default=0)
    floods = db.Column(db.Integer,nullable=False, default=0)
    storm = db.Column(db.Integer,nullable=False, default=0)
    fire= db.Column(db.Integer,nullable=False, default=0)
    earthquake = db.Column(db.Integer,nullable=False, default=0)
    cold = db.Column(db.Integer,nullable=False, default=0)
    other_weather = db.Column(db.Integer,nullable=False, default=0)
    direct_report = db.Column(db.Integer,nullable=False, default=0)

    
    def __repr__(self):
        return f"Msg('{self.title}', '{self.date_posted}')"


msgs = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]




@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    msgs = Msg.query.order_by(Msg.date_posted.desc()).paginate(page=page, per_page=1)
    #msgs = Msg.query.all()
    return render_template('home.html', msgs=msgs,cats=cats)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/msg/new", methods=['GET', 'POST'])
#@login_required
def new_msg():
    form = MsgForm()
    if form.validate_on_submit():
        # use model to predict classification for query
        classification_labels = model.predict([form.content.data])[0]
        classification_results = dict(zip(df.columns[4:], classification_labels))
        classification_results['title']=form.title.data
        classification_results['content']=form.content.data
        #print(classification_results)
        msg = Msg(**classification_results)
        db.session.add(msg)
        db.session.commit()
        #flash('Your post has been created!'+json.dumps(classification_results), 'success')
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_msg.html', title='New Message',
                           form=form, legend='New Message')

@app.route("/msg/<int:msg_id>")
def msg(msg_id):
    msg = Msg.query.get_or_404(msg_id)
    return render_template('msg.html', title=msg.title, msg=msg,cats=cats)

@app.route("/msg/<int:msg_id>/update", methods=['GET', 'POST'])
#@login_required
def update_msg(msg_id):
    msg = Msg.query.get_or_404(msg_id)
#    if post.author != current_user:
#        abort(403)
    form = MsgForm()
    if form.validate_on_submit():
        '''        
        classification_labels = model.predict([form.content.data])[0]
        classification_results = dict(zip(df.columns[4:], classification_labels))
        classification_results['title']=form.title.data
        classification_results['content']=form.content.data
        msg = Msg.query.filter(id=msg_id)
        data = msg.data
        data=classification_results
        msg.data = data
        flag_modified(msg, "data")
        db.session.merge(msg)
        db.session.flush()
        '''
        #db.session.commit()
        msg.title = form.title.data
        msg.content = form.content.data
        db.session.commit()
        flash('Your Message has been updated!', 'success')
        return redirect(url_for('msg', msg_id=msg.id))
    elif request.method == 'GET':
        form.title.data = msg.title
        form.content.data = msg.content
    return render_template('create_msg.html', title='Update Message',
                           form=form, legend='Update Message')

@app.route("/msg/<int:msg_id>/delete", methods=['POST'])
#@login_required
def delete_msg(msg_id):
    msg = Msg.query.get_or_404(msg_id)
#    if post.author != current_user:
#        abort(403)
    db.session.delete(msg)
    db.session.commit()
    flash('Your message has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/graph1")
def graph1():
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=genre_names,
                    y=genre_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('graph1.html', ids=ids, graphJSON=graphJSON)


@app.route("/graph2")
def graph2():
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    df_categories = df.drop(['id', 'message','original','genre'], axis=1)
    counts = []
    categories_list = list(df_categories.columns.values)
    for i in categories_list:
        counts.append((i, int(df_categories[i].sum())))
    df_stats = pd.DataFrame(counts, columns=['category', 'number_of_messages']).sort_values('number_of_messages',ascending=False)
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=df_stats['category'],
                    y=df_stats['number_of_messages']
                )
            ],

            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Category",
                    'tickangle':90
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('graph2.html', ids=ids, graphJSON=graphJSON)


@app.route("/graph3")
def graph3():
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    df_categories = df.drop(['id', 'message','original','genre'], axis=1)
    rowsums = df_categories.iloc[:,:].sum(axis=1)
    x=rowsums.value_counts().sort_values()
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Scatter(
                    x=x.index,
                    y=x.values,
                    mode='markers'
                )
            ],

            'layout': {
                'title': 'Multiple categories per messages',
                'yaxis': {
                    'title': "# of Messages"
                },
                'xaxis': {
                    'title': "# of Categories"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('graph3.html', ids=ids, graphJSON=graphJSON)

@app.route("/graph4")
def graph4():
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    lens = df.message.str.len()
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Histogram(
                    x=lens,
                    xbins=dict( # bins used for histogram
                            start=0.0,
                            end=600,
                            size=5
                    ),
                )
            ],

            'layout': {
                'title': 'Histogram',
                'yaxis': {
                    'title': "# of Messages"
                },
                'xaxis': {
                    'title': "Message length"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('graph4.html', ids=ids, graphJSON=graphJSON)


@app.route("/graph5")
def graph5():
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    data = df.iloc[:, 4:].drop('child_alone', axis=1)
    corr_list = []
    correl = data.corr().values
    for row in correl:
        corr_list.append(list(row))
    col_names = [col.replace('_', ' ').title() for col in data.columns]
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Heatmap(
                    z=corr_list, 
                    x=col_names,
                    y=col_names,
                    colorscale='Viridis',
                )
            ],

            'layout': {
                'title': 'What Types of Messages Occur Together?',
                'height': 750,
                'width':750,
                'margin': dict(
                    l = 150,
                    r = 30, 
                    b = 160,
                    t = 60,
                    pad = 4
                ),
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('graph5.html', ids=ids, graphJSON=graphJSON)



if __name__ == '__main__':
    app.run(debug=True)