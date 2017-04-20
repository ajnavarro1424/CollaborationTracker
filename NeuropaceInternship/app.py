# Importing flask packages
from flask_assets import Environment
from flask import Flask, render_template, request, redirect
# Importing mongoengine and forms to our flask framework
from pymongo import MongoClient
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

from flask_mongoengine.wtf import model_form


# global variable representing the entire app (Flask object called 'app')
app = Flask(__name__)
assets = Environment(app)
# Pymongo setup
# client = MongoClient('localhost', 27017)
# app.mdb = client.test_database
# collaborations = app.mdb.collaborations
#MongoEngine setup
mdb = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(mdb)
# mdb.init_app(app)

# Model used to build our collection by passing our documents (document object)
class Collaboration(mdb.Document):
    #Collaboration class will contain all the fields for all WF
    entry_date = mdb.DateTimeField()
    entered_by = mdb.StringField()
    institution_contact = mdb.StringField()
    pi = mdb.StringField()

# Form representing the initiation view/stage
InitiationForm = model_form(
    Collaboration,
    # fields that InitiationForm takes in
    only = ['entry_date', 'entered_by', 'institution_contact', 'pi'],
    # labels of fields in InitiationForm
    field_args = {'entry_date' : {'label': 'Entry Date'},
                'entered_by' : {'label': 'Entered By'},
                'institution_contact' : {'label': 'Institution Contact'},
                'pi' : {'label': 'Principal Investigator'}}
    )


# Controller and routes
@app.route("/")
def main():
    collabs = Collaboration.objects

    return render_template('index.html', collabs=collabs)


@app.route("/edit/<collab_id>", methods=["GET","POST"])
def edit(collab_id):
    # Pre-created form
    if request.method == 'GET':
        # Get a user chosen collab from the db
        collab_select = Collaboration.objects(id=collab_id).first()
        # Use selected collab to generate populated init form
        form = InitiationForm(instance=collab_select)

    elif request.method == 'POST':
        form = InitiationForm(request.form)
        if form.validate_on_submit():
            del(form.csrf_token)
            form.save()
            return redirect('/')
    # Pass form to template to render on view
    return render_template('edit.html', form=form)

@app.route('/init', methods=["GET","POST"])
def initiation():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('init.html', form=form)

@app.route("/details")
def details():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('details.html', form=form)

@app.route("/contract")
def contract():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('contract.html', form=form)

@app.route("/legal")
def legal():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('contract.html', form=form)

@app.route("/sharing")
def sharing():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('sharing.html', form=form)

@app.route("/closure")
def closure():
    form = InitiationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.save()
        return redirect('/')
    return render_template('closure.html', form=form)

@app.route("/audit")
def audit():pass

@app.route("/reports")
def reports():pass


if __name__ == "__main__":
    app.config.update(DEBUG = True, SECRET_KEY = '')

    app.run()
