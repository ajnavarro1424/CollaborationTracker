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
    # Initiate Form values
    entry_date = mdb.DateTimeField()
    entered_by = mdb.StringField()
    date_needed = mdb.DateTimeField()
    institution_contact = mdb.StringField()
    pi = mdb.StringField()
    reason = mdb.StringField() #dropdown-menu
    category = mdb.StringField() #dropdown-menu
    init_comments = mdb.StringField()
    # Details workflow (Flow2/Pg1 is Green-light or Red-light)
    neuropace_contact = mdb.StringField() #dropdown-menu
    sharing_method = mdb.StringField() #dropdown-menu
    study_title = mdb.StringField()
    dataset_description = mdb.StringField() #dropdown-menu
    phi_present = mdb.BooleanField()
    share_type = mdb.StringField() #dropdown-menu
    study_type = mdb.StringField() #dropdown-menu
    study_identifier = mdb.StringField()
    risk_level = mdb.StringField() #dropdown-menu
    accessories_needed = mdb.BooleanField()
    accessories_needed_language = mdb.StringField() #dropdown-menu
    single_multi_center = mdb.StringField() #dropdown-menu
    detail_comments = mdb.StringField()
    #Contracts and Financials (Flow2/Pg3)
    funding_source = mdb.StringField() #dropdown-menu
    np_compensation = mdb.BooleanField()
    np_consultant = mdb.BooleanField()
    contract_needed = mdb.StringField()
    budget_needed = mdb.StringField()
    contract_notes = mdb.StringField()
    #Legal
    approval_date = mdb.DateTimeField()
    approval_by = mdb.StringField() # dropdown-menu
    # Legal continued(.pdf values)
    pc_research_acc = mdb.BooleanField()
    pc_data_sharing = mdb.BooleanField()
    icfc_data_sharing = mdb.BooleanField()
    expiration_date = mdb.DateTimeField()
    ds_racc_notes = mdb.StringField()
    legal_notes = mdb.StringField()

    #Closure
    status = mdb.StringField() # dropdown-menu
    closure_notes = mdb.StringField()



def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def labelize(field_name):
    return field_name.replace('_', ' ').title()

def collab_model_form(model, only, field_args={}, **kwargs):
     for field in only:
        # generate/append field_args for each field; esp label
        if field in field_args:
            field_args[field]['label'] = labelize(field)
        else:
            field_args[field] = {'label': labelize(field)}

     print (field_args)
     return model_form(model, only=only, field_args=field_args, **kwargs)

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

DetailsForm = collab_model_form(Collaboration, ['neuropace_contact', 'sharing_method', 'study_title', 'dataset_description', 'phi_present', 'share_type', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_needed_language', 'single_multi_center', 'detail_comments'])

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
# We need a way to track a specific collaboration through the flows
@app.route("/details", methods=["GET","POST"])
def details():
    form = DetailsForm(request.form)
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
    return render_template('legal.html', form=form)

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
