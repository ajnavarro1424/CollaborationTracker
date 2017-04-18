from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

from flask_mongoengine.wtf import model_form



app = Flask(__name__)

# Pymongo setup
# client = MongoClient('localhost', 27017)
# app.mdb = client.test_database
# collaborations = app.mdb.collaborations
#MongoEngine setup
mdb = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(mdb)
# mdb.init_app(app)


class Collaboration(mdb.Document):
    #Collaboration class will contain all the fields for all WF
    entry_date = mdb.DateTimeField(required = False)
    entered_by = mdb.StringField(required = True)
    institution_contact = mdb.StringField(required = True)
    pi = mdb.StringField(required = True)

InitialForm = model_form(
    Collaboration,
    only = ['entry_date', 'entered_by', 'institution_contact', 'pi'],
    field_args = {'entry_date' : {'label': 'Entry Date'},
                'entered_by' : {'label': 'Entered By'},
                'institution_contact' : {'label': 'Institution Contact'},
                'pi' : {'label': 'Principal Investigator'}}
    )



@app.route("/")
def main():


    return render_template('index.html')


@app.route('/init', methods=["GET","POST"])
def initiation():
    form = InitialForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        collab = Collaboration(form.entry_date.data, form.entered_by.data, form.institution_contact.data, form.pi.data)
        collab.save()
        return redirect('/')
    return render_template('init.html', form=form)

@app.route("/details")
def details():pass


@app.route("/contract")
def contract():pass

@app.route("/legal")
def legal():pass

@app.route("/sharing")
def sharing():pass

@app.route("/closure")
def closure():pass


if __name__ == "__main__":
    app.config.update(DEBUG = True, SECRET_KEY = '')

    app.run()
