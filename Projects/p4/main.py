# project: p4
# submitter: chen2328
# partner: none
# hours: 10

# run the main.py 
# then paste url - http://34.70.156.121:5000/

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# fake text and byte files, respectively
from io import StringIO, BytesIO

from flask import Flask, request, jsonify
import re
import time
import flask

matplotlib.use('Agg')

app = Flask(__name__)
df = pd.read_csv("main.csv")    
num_subscribed = 0  # subscribed number for that user
VISIT_COUNT = 0     # count the number of visist when users go to the page
DONATE_COUNT = 0    # count the number of donate when users click donate.html
SOURCE_LINK_DICT = {'A': 0, 'B': 0} # store the number of source when users click
MAX_KEY = "A"    # Set a threshold and then change to version A or B
USER_DICT = {}   # Store the subscribe user and its time when visist the webpage

@app.route('/')
def home():
    global VISIT_COUNT, MAX_KEY, DONATE_COUNT, SOURCE_LINK_DICT

    with open("index.html") as f:
        html = f.read()
#     if MAX_KEY == 'B' and VISIT_COUNT > 10:
#         #html = html.replace("donate.html?from=A", "donate.html?from=B")
#         html = html.replace("donate.html", "donate.html?from=B")
#         html = html.replace("color: blue", "color: red")
#         return html

#     if MAX_KEY != 'B' and VISIT_COUNT > 10:
#         html = html.replace("donate.html", "donate.html?from=A")
#         return html
    
    # A/B testing for the donate page randomly provde the page source
    VISIT_COUNT += 1
    if (VISIT_COUNT % 2 == 0 and VISIT_COUNT <= 10) or (MAX_KEY == 'A' and VISIT_COUNT > 10):
        html = html.replace("donate.html", "donate.html?from=A")

    if VISIT_COUNT % 2 != 0 and VISIT_COUNT <= 10 or (MAX_KEY == 'B' and VISIT_COUNT > 10): 
        html = html.replace("color: blue", "color: red")
        html = html.replace("donate.html", "donate.html?from=B")

    # choose the best version
    if VISIT_COUNT == 10:
        if SOURCE_LINK_DICT['B'] > SOURCE_LINK_DICT['A']:
            MAX_KEY = 'B'  

    return html

@app.route('/browse.html')
def browse():
    global df
    
    html = "<h1>{}<h1>".format("Browse")
    html += "<h3>{}<h3>".format("The dataset shows the movie produced by Walt Disney Animation Studios!")
    html += df.to_html()
    html += "<h3>{}<h3>".format("Data Source: data.world - Walt Disney")
    
    return html


@app.route('/browse.json')
def browse_json():
    global df, USER_DICT

    # get the user
    user = request.remote_addr 
    
    # add user into the dict and assign the time so can do calculation
    if user not in USER_DICT:
        USER_DICT[user] = 0
    
    # calculate the time that stored in the USER_DICT, and see if the difference over 1 min
    if time.time() - USER_DICT[user] > 60:
        USER_DICT[user] = time.time()
        return jsonify(df.to_dict())
    
    html = "too many requests, come back later"
    
    return flask.Response(html, status=429, headers={"Retry-After": 60})


@app.route('/donate.html')
def donate():
    global SOURCE_LINK_DICT, DONATE_COUNT
    
    # header and the link back to homepage
    html = """<html><body><h1>Donate</h1>
    <p><a href='/'>Home Page</a></p>
    </body>
    </html>"""
    # see if has argument
    if dict(request.args):
        args = dict(request.args)
        DONATE_COUNT += 1
     
        if args['from'] == 'A':
            SOURCE_LINK_DICT['A'] += 1
        else:
            SOURCE_LINK_DICT['B'] += 1
   
    return html

@app.route('/email', methods=["POST"])
def email():
    """
    TODO: flask.request.get_data()
    course, def upload() ..
    faster than with open ??
    """
    
    global num_subscribed
    regex = r"[A-Za-z0-9]+@[A-Za-z0-9-]+\.[A-Z|a-z]{2,3}"
    email = str(request.data, "utf-8")
    if re.match(regex, email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + '\n') # 2
            # TODO: if same person keep subscribe ????
            num_subscribed += 1
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("Invalid email address! Please subscribe again :)")

# my first dashboard
@app.route('/dashboard_1.svg')
def gen_svg1():
    # Question why df do not need global variable ???? 
    # --> df in here is a local variable default

    fig, ax = plt.subplots(figsize=(8,6))
    
    new_df = df.copy()
    new_df.total_gross = new_df.total_gross / 1000000
    
    # create the gross table for useage of both chart
    gross = pd.pivot_table(new_df, index=['genre'], values=['total_gross']).sort_values(by=['total_gross'])
    
    args = dict(flask.request.args)
   
    final_dict = {'genre': [], 'gross': [], 'frequency': []} # create dict to plot
    if args:
        gross_dict = gross.total_gross.to_dict() 
        freq_dict = new_df.genre.value_counts().to_dict()

        for k in gross_dict:
            gross_value = gross_dict[k]
            freq_value = freq_dict[k]
            
            final_dict['genre'].append(k)
            final_dict['gross'].append(gross_value)
            final_dict['frequency'].append(freq_value)

        #tb2_dict = dict(lambda tb2[k]: [v] for k, v in tb2_dict.items())
        final_df = pd.DataFrame(final_dict)
        
        final_df.plot.scatter(y='genre', x='gross', ax=ax, c='frequency', cmap='bwr', s=60)
        ax.set_xlabel("Total Gross (Million)")
        ax.set_ylabel("Movie Genre")
        ax.set_title("Top Genre of Total Gross vs Frequency")
        
    else:
        # if no argument, plot the normal one
        gross.plot.barh(ax=ax)
        plt.xlim(0, gross.total_gross.max() + 10)
        ax.set_xlabel("Total Gross (Million)")
        ax.set_ylabel("Movie Genre")
        ax.set_title("Top Genre of Total Gross")
        
    
    f = StringIO() # fake file (has a .write method)
    plt.tight_layout()
    fig.savefig(f, format='svg')
    plt.close()
    
    svg = f.getvalue()
    hdr = {"Content-Type": "image/svg+xml"}
    return flask.Response(svg, headers=hdr)

@app.route('/dashboard_2.svg')
def gen_svg2():
    
    fig, ax = plt.subplots(figsize=(8,6))
    
    top = pd.pivot_table(df, index=['movie_title'], values=['total_gross']).sort_values(by=['total_gross'], ascending=False)
    top[0:10].plot.barh(ax=ax, )
 
    ax.set_xlabel("Total Gross (Million)")
    ax.set_ylabel("Movie")
    ax.set_title("Top 10 movies")
    
    f = StringIO() # fake file (has a .write method)
    plt.tight_layout()
    fig.savefig(f, format='svg')
    plt.close()
    
    svg = f.getvalue()
    hdr = {"Content-Type": "image/svg+xml"}
    return flask.Response(svg, headers=hdr)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.