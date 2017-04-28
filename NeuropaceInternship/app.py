# Importing flask packages
from flask import Flask, render_template, request, redirect, flash
from flask_assets import Environment
# Importing mongoengine and forms to our flask framework
from pymongo import MongoClient
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_mongoengine.wtf import model_form

from mongoengine import *
from mongoengine import signals
import blinker

from datetime import datetime
from time import gmtime, strftime

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

class SelectionField(mdb.Document):
    value = mdb.StringField()
    field_name = mdb.StringField()

# Model used to build our collection by passing our documents (document object)
class Collaboration(mdb.Document):
    archive = mdb.BooleanField(default = False)
    date_mod = mdb.DateTimeField()
    #Collaboration class will contain all the fields for all WF
    # Initiate Form values
    new_new_tag = mdb.StringField(label = 'NEW NEW TAG')
    entry_date = mdb.StringField(label = "Entry date")
    entered_by = mdb.StringField(label = "Entered by")
    date_needed = mdb.StringField()
    institution = mdb.StringField()
    institution_contact = mdb.StringField()
    pi = mdb.StringField(label = "PI")
    reason = mdb.ReferenceField(SelectionField, label = "Reason for Collaboration")#dropdown-menu
    category = mdb.ReferenceField(SelectionField) #dropdown-menu
    init_notes = mdb.StringField()
    # Details workflow (Flow2/Pg1 is Green-light or Red-light)
    neuropace_contact = mdb.ReferenceField(SelectionField, label = "NeuroPace Contact") #dropdown-menu
    sharing_method = mdb.ReferenceField(SelectionField, label = "Data Sharing Method") #dropdown-menu
    study_title = mdb.StringField()
    description = mdb.StringField()
    dataset_description = mdb.ReferenceField(SelectionField, label = "Data Set Description") #dropdown-menu
    phi_present = mdb.BooleanField(label = "PHI Present")
    share_type = mdb.ReferenceField(SelectionField, label = "Data Share Type") #dropdown-menu
    sharing_language = mdb.ReferenceField(SelectionField, label = "Data Sharing Language") #dropdown-menu
    study_type = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_identifier = mdb.StringField()
    risk_level = mdb.ReferenceField(SelectionField, label = "Study Risk Level") #dropdown-menu
    accessories_needed = mdb.BooleanField(label = "Research Accessories Needed?")
    accessories_language = mdb.ReferenceField(SelectionField, label = "Research Accessories Language") #dropdown-menu
    single_multi_center = mdb.ReferenceField(SelectionField, label = "Single or Multi-Center") #dropdown-menu
    detail_notes = mdb.StringField()
    #Contracts and Financials (Flow2/Pg3)
    funding_source = mdb.ReferenceField(SelectionField) #dropdown-menu
    np_compensation = mdb.BooleanField(label = "Compensated by NP?")
    np_consultant = mdb.BooleanField(label = "Consultant to NP?")
    contract_needed = mdb.ReferenceField(SelectionField, label = "Contract Needed?") # dropdown-menu
    budget_needed = mdb.StringField(label = "Budget Needed?")
    inv_sites_approval_req = mdb.StringField(label = "Inv Sites Approval Req'd")
    vpn_access = mdb.StringField(label = "VPN access?")
    contract_status = mdb.ReferenceField(SelectionField, label = "Contract Status")
    contract_approval_date = mdb.StringField()
    contract_notes = mdb.StringField()
    #Legal(Flow4/Pg.4)
    # Not Tracked values caused DateTimeField to fail.
    approval_date = mdb.StringField(label='NP Study Sharing Approval Date')
    approval_by = mdb.ReferenceField(SelectionField, label='NP Sharing Approval By') # dropdown-menu
    irb_app_date = mdb.StringField(label = 'Initial IRB App Date')
    irb_exp_date = mdb.StringField(label = 'Latest IRB Exp Date')
    # Legal continued(.pdf values)
    pc_research_acc = mdb.BooleanField()
    pc_data_sharing = mdb.BooleanField()
    icfc_data_sharing = mdb.BooleanField()
    expiration_date = mdb.StringField()
    ds_racc_notes = mdb.StringField()
    legal_notes = mdb.StringField()

    #Closure
    status = mdb.ReferenceField(SelectionField, label = " Colaboration Status") # dropdown-menu
    box_link = mdb.StringField(label = 'BOX link')
    notes = mdb.StringField()


def labelize(field):
    if hasattr(field, "label"):
        return field.label
    return field.db_field.replace('_', ' ').title()

def collab_model_form(model, only, field_args={}, **kwargs):
    for field_name in only:
        field = model._fields[field_name]
        # generate/append field_args for each field; esp label
        if field_name in field_args:
            field_args[field_name]['label'] = labelize(field)
        else:
            field_args[field_name] = {'label': labelize(field)}
        if type(field) == mdb.ReferenceField:
            field_args[field_name] = {'label_attr' : 'value',
                                 'queryset': SelectionField.objects(field_name=field_name),
                                 'label' : labelize(field)}
    return model_form(model, only=only, field_args=field_args, **kwargs)

def generate_id():
    collab = Collaboration()
    return collab.save()

def update_modified(sender, document):
    document.date_mod = datetime.utcnow()

signals.pre_save.connect(update_modified)


form_dict = {
            'init' : collab_model_form(Collaboration, ['date_mod','entry_date', 'entered_by', 'date_needed', 'institution', 'institution_contact', 'pi', 'reason', 'category', 'status', 'init_notes']),
            'details' : collab_model_form(Collaboration, ['neuropace_contact', 'sharing_method', 'study_title', 'description', 'dataset_description', 'phi_present', 'share_type', 'sharing_language', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_language', 'single_multi_center','status', 'detail_notes']),
            'contract' : collab_model_form(Collaboration, ['funding_source', 'np_consultant', 'np_compensation', 'contract_needed','contract_status', 'budget_needed', 'status', 'contract_notes']),
            'legal' : collab_model_form(Collaboration, ['approval_date', 'approval_by', 'irb_app_date', 'irb_exp_date', 'status', 'legal_notes']),
            'closure' : collab_model_form(Collaboration, ['status', 'box_link', 'notes'])
            }

stage_array = ["init", "details", "contract", "legal", "closure"]


# Controller and routes
# Main function will return a different list of collabs based on path variables
@app.route("/")
def main():
    collabs = Collaboration.objects(archive = False)
    collabs_archived = Collaboration.objects(archive = True)
    return render_template('index.html', collabs=collabs, collabs_arch=collabs_archived)

@app.route("/<list>")
def list(list):
    #Returns a specific list of collabs based on passed URL variable
    if list == "all":
        collabs = Collaboration.objects()
        return render_template('index.html', collabs=collabs, list=list)
    else:
        collabs = Collaboration.objects(archive = False)
        flash("The %s list does not exist" % list)
        return render_template('index.html', collabs=collabs)

@app.route("/archive/<collab_id>", methods=["GET"])
def archive(collab_id):
    # Pull collab for archiving
    collab_select = Collaboration.objects(id=collab_id).first()
    # Check the archive status and save opposite
    if collab_select.archive ==  False:
        collab_select.archive = True
        flash('Collaboration %s successfully archived.' % collab_select.id)
    else:
        collab_select.archive = False
        flash('Collaboration %s successfully restored.' % collab_select.id)
    collab_select.save()
    # redirect to the index page where the archived collab will have disappeared
    return redirect('/')
# Abstracted new collaboration workflow that takes in a stage and collab_id
# and generates the appropriate view and form.
@app.route("/new/<stage>/<collab_id>", methods=["GET","POST"])
def new_stage(stage, collab_id):
    #If new collaboration started, create collaboration document in db
    if collab_id == "none":
        #Generate a collab_id with generate_id
        collab_select = generate_id()
    else:
        #Pull empty collaborations from collab_id if not init stage
        collab_select = Collaboration.objects(id=collab_id).first()
    # Render the appropriate form given the stage
    form_stage = form_dict[stage]
    # If formdata is empty or not provided, this object is checked for attributes matching form field names,
    # which will be used for field values.
    form = form_stage(request.form, obj=collab_select)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        # Save whats on the form into the selected collab
        form.populate_obj(collab_select)
        collab_select.save()
        #Checks to see if stage is closure to return back to homepage
        if stage == 'closure':
            flash("Collaboration %s saved in DB" %collab_select.id)
            return redirect('/')
        flash(f"Stage {stage.title()} saved for Collaboration {collab_select.id}")
        return redirect('/new/'+ stage_array[stage_array.index(stage)+1] +'/'+ collab_id )#redirect to the next stage
    # Render the view given the stage
    return render_template(stage + '.html', form=form, collab_id=collab_select.id)


@app.route("/audit")
def audit():pass

@app.route("/reports")
def reports():pass


if __name__ == "__main__":
    app.config.update(DEBUG = True, SECRET_KEY = '')

    app.run()
