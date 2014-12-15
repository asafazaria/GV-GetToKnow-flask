from flask import Flask, render_template
import json
import feedparser
import globalvoices

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("stories.html",
        country_list_json_text=json.dumps(globalvoices.country_list())
    )

@app.route("/country/<country>")
def country(country):
    stories = globalvoices.recent_stories_from( country )
    print stories
    return render_template("stories.html",
        country_list_json_text=json.dumps(globalvoices.country_list()),
        country_name=country,
        stories=stories
    )
        

if __name__ == "__main__":
    app.debug = True
    app.run()


{'contentSnippet': u"Dennis Keen's beautifully written blogs have exposed English speakers to some inaccessible elements of Central Asian culture. ...", 
'author': u'Chris Rickleton', 
'link': u'http://globalvoicesonline.org/2014/08/20/take-a-lyrical-and-visual-trek-through-the-back-streets-of-almaty-kazakhstan/', 
'title': u'Take a Lyrical and Visual Trek Through the Back Streets of Almaty, Kazakhstan'}