# Importing flask packages
from flask import Flask, render_template, request, redirect
from flask_assets import Environment
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

class SelectionField(mdb.Document):
    value = mdb.StringField()
    field_name = mdb.StringField()

# Model used to build our collection by passing our documents (document object)
class Collaboration(mdb.Document):
    #Collaboration class will contain all the fields for all WF
    # Initiate Form values
    entry_date = mdb.DateTimeField()
    entered_by = mdb.StringField()
    date_needed = mdb.DateTimeField()
    institution_contact = mdb.StringField()
    pi = mdb.StringField()
    reason = mdb.ReferenceField(SelectionField)#dropdown-menu
    category = mdb.ReferenceField(SelectionField) #dropdown-menu
    init_notes = mdb.StringField()
    # Details workflow (Flow2/Pg1 is Green-light or Red-light)
    neuropace_contact = mdb.ReferenceField(SelectionField) #dropdown-menu
    sharing_method = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_title = mdb.StringField()
    dataset_description = mdb.ReferenceField(SelectionField) #dropdown-menu
    phi_present = mdb.BooleanField()
    share_type = mdb.ReferenceField(SelectionField) #dropdown-menu
    sharing_language = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_type = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_identifier = mdb.StringField()
    risk_level = mdb.ReferenceField(SelectionField) #dropdown-menu
    accessories_needed = mdb.BooleanField()
    accessories_needed_language = mdb.ReferenceField(SelectionField) #dropdown-menu
    single_multi_center = mdb.ReferenceField(SelectionField) #dropdown-menu
    detail_notes = mdb.StringField()
    #Contracts and Financials (Flow2/Pg3)
    funding_source = mdb.ReferenceField(SelectionField) #dropdown-menu
    np_compensation = mdb.BooleanField()
    np_consultant = mdb.BooleanField()
    contract_needed = mdb.StringField()
    budget_needed = mdb.StringField()
    contract_notes = mdb.StringField()
    #Legal
    approval_date = mdb.DateTimeField()
    approval_by = mdb.ReferenceField(SelectionField) # dropdown-menu
    # Legal continued(.pdf values)
    pc_research_acc = mdb.BooleanField()
    pc_data_sharing = mdb.BooleanField()
    icfc_data_sharing = mdb.BooleanField()
    expiration_date = mdb.DateTimeField()
    ds_racc_notes = mdb.StringField()
    legal_notes = mdb.StringField()

    #Closure
    status = mdb.ReferenceField(SelectionField) # dropdown-menu
    closure_notes = mdb.StringField()


def labelize(field_name):
    return field_name.replace('_', ' ').title()

def collab_model_form(model, only, field_args={}, **kwargs):
    for field in only:
        # generate/append field_args for each field; esp label
        if field in field_args:
            field_args[field]['label'] = labelize(field)
        else:
            field_args[field] = {'label': labelize(field)}
        if type(model._fields[field]) == mdb.ReferenceField:
            field_args[field] = {'label_attr' : 'value',
                                 'queryset': SelectionField.objects(field_name=field)}
    # print(field_args)
    return model_form(model, only=only, field_args=field_args, **kwargs)

def generate_id():
    collab = Collaboration()
    return collab.save()

form_dict = {
            'init' : collab_model_form(Collaboration, ['entry_date', 'entered_by', 'institution_contact', 'pi', 'reason', 'category', 'status', 'init_notes']),
            'details' : collab_model_form(Collaboration, ['neuropace_contact', 'sharing_method', 'study_title', 'dataset_description', 'phi_present', 'share_type', 'sharing_language', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_needed_language', 'single_multi_center','status', 'detail_notes']),
            'contract' : collab_model_form(Collaboration, ['funding_source', 'np_consultant', 'np_compensation', 'contract_needed', 'budget_needed', 'status', 'contract_notes']),
            'legal' : collab_model_form(Collaboration, ['approval_date', 'approval_by', 'status', 'legal_notes']),
            'closure' : collab_model_form(Collaboration, ['status', 'closure_notes'])
            }

stage_array = ["init", "details", "contract", "legal", "closure"]
# Controller and routes
@app.route("/")
def main():
    collabs = Collaboration.objects
    return render_template('index.html', collabs=collabs)

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
            return redirect('/')
            # TODO: Insert flash message for collab confirmation

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
