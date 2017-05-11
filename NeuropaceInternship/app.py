# Importing flask packages
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_assets import Environment
# Importing mongoengine and forms to our flask framework
from pymongo import MongoClient
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_mongoengine.wtf import model_form
#This library will help convert the textarea's into inputs for styling
# from wtforms import widgets, StringField
# Packages for the login functionality
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin

from mongoengine import *
from mongoengine import signals
import blinker

from datetime import datetime
import calendar
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

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

class User(mdb.Document, UserMixin):
    username = mdb.StringField(pk = True)
    password = mdb.StringField()
    def get_id(self):
     return self.username

class SelectionField(mdb.Document):
    value = mdb.StringField()
    field_name = mdb.StringField()
# Model used to build our collection by passing our documents (document object)
class Collaboration(mdb.Document):
    archive = mdb.BooleanField(default = False)
    date_mod = mdb.DateTimeField()
    favorite_list = mdb.ListField(mdb.ReferenceField(User))
    #Collaboration class will contain all the fields for all WF
    # Initiate Form values
    new_new_tag = mdb.StringField(label = 'NEW NEW TAG')
    entry_date = mdb.StringField(label = "Entry date", max_length = 1000)
    entered_by = mdb.StringField(label = "Entered by", max_length = 1000)
    date_needed = mdb.StringField(max_length = 1000)
    institution = mdb.StringField(max_length = 1000)
    institution_contact = mdb.StringField(max_length = 1000)
    pi = mdb.StringField(label = "Primary Investigator", max_length = 1000)
    reason = mdb.ReferenceField(SelectionField, label = "Reason for Collaboration")#dropdown-menu
    category = mdb.ReferenceField(SelectionField) #dropdown-menu
    init_notes = mdb.StringField(label = "Initiation Notes")
    # Details workflow (Flow2/Pg1 is Green-light or Red-light)
    neuropace_contact = mdb.ReferenceField(SelectionField, label = "NeuroPace Contact") #dropdown-menu
    sharing_method = mdb.ReferenceField(SelectionField, label = "Data Sharing Method") #dropdown-menu
    study_title = mdb.StringField(max_length = 1000)
    description = mdb.StringField(max_length = 1000)
    dataset_description = mdb.ReferenceField(SelectionField, label = "Data Set Description") #dropdown-menu
    phi_present = mdb.BooleanField(label = "PHI Present")
    share_type = mdb.ReferenceField(SelectionField, label = "Data Share Type") #dropdown-menu
    sharing_language = mdb.ReferenceField(SelectionField, label = "Data Sharing Language") #dropdown-menu
    study_type = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_identifier = mdb.StringField(max_length = 1000)
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
    budget_needed = mdb.StringField(label = "Budget Needed?",max_length = 1000)
    inv_sites_approval_req = mdb.StringField(label = "Inv Sites Approval Req'd", max_length = 1000)
    vpn_access = mdb.StringField(label = "VPN access?", max_length = 1000)
    contract_status = mdb.ReferenceField(SelectionField, label = "Contract Status")
    contract_approval_date = mdb.StringField(max_length = 1000)
    contract_notes = mdb.StringField()
    #Legal(Flow4/Pg.4)
    # Not Tracked values caused DateTimeField to fail.
    approval_date = mdb.StringField(label='NP Study Sharing Approval Date', max_length = 1000)
    approval_by = mdb.ReferenceField(SelectionField, label='NP Sharing Approval By') # dropdown-menu
    irb_app_date = mdb.StringField(label = 'Initial IRB App Date', max_length = 1000)
    irb_exp_date = mdb.StringField(label = 'Latest IRB Exp Date', max_length = 1000)
    # Legal continued(.pdf values)
    pc_research_acc = mdb.BooleanField()
    pc_data_sharing = mdb.BooleanField()
    icfc_data_sharing = mdb.BooleanField()
    expiration_date = mdb.StringField(max_length = 1000)
    ds_racc_notes = mdb.StringField()
    legal_notes = mdb.StringField()

    #Closure
    status = mdb.ReferenceField(SelectionField, label = "Collaboration Status") # dropdown-menu
    box_link = mdb.StringField(label = 'BOX link', max_length = 1000)
    notes = mdb.StringField()

    #Converts UTC time to local time
    def utc_2_local(self, field):
        TIME_FORMAT = '%Y-%m-%d %I:%M:%S'
        timestamp =  calendar.timegm(field.timetuple())
        local = datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)
        return local

class Change(mdb.EmbeddedDocument):
    stage = mdb.StringField()
    field = mdb.StringField()
    previous = mdb.StringField()
    current = mdb.StringField()

class Audit(mdb.Document):
    date_change = mdb.DateTimeField()
    username = mdb.StringField()
    collab_ref = mdb.StringField()
    change_list = mdb.ListField(mdb.EmbeddedDocumentField(Change))



@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


def update_modified(sender, document):
    if document._class_name == 'Collaboration':
        document.date_mod = datetime.today()

signals.pre_save.connect(update_modified)

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
            field_args[field_name] = {'label': labelize(field)

                                    }
        if type(field) == mdb.ReferenceField:
            field_args[field_name] = {'label_attr' : 'value',
                                 'queryset': SelectionField.objects(field_name=field_name),
                                 'label' : labelize(field),
                                 'allow_blank':True,
                                 'blank_text':u'--please please choose--'}
    return model_form(model, only=only, field_args=field_args, **kwargs)

def generate_id():
    collab = Collaboration()
    return collab.save()



form_dict = {
            'init' : collab_model_form(Collaboration, ['date_mod','entry_date', 'entered_by', 'date_needed', 'institution', 'institution_contact', 'pi', 'reason', 'category', 'status', 'init_notes']),
            'details' : collab_model_form(Collaboration, ['neuropace_contact', 'sharing_method', 'study_title', 'description', 'dataset_description', 'phi_present', 'share_type', 'sharing_language', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_language', 'single_multi_center','status', 'detail_notes']),
            'contract' : collab_model_form(Collaboration, ['funding_source', 'np_consultant', 'np_compensation', 'contract_needed','contract_status', 'budget_needed', 'status', 'contract_notes']),
            'legal' : collab_model_form(Collaboration, ['approval_date', 'approval_by', 'irb_app_date', 'irb_exp_date', 'status', 'legal_notes']),
            'closure' : collab_model_form(Collaboration, ['status', 'box_link', 'notes'])
            }

stage_array = ["init", "details", "contract", "legal", "closure"]

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login/<username>', methods=['GET', 'POST'])
def login(username):
    # Find or create a user with the given username...
    user = User.objects(username = username).first()
    if user is not None:
        login_user(user)
        next = request.args.get('next')
        if not is_safe_url(next):
            flash('URL is not safe, hide your kids, hide your wife.')
            return flask.abort(400)
        flash('Logged in successfully.')
        return redirect(next or url_for('main'))
    else:
        flash('Login failed. Try again.')
        return redirect("/")

@app.route("/logout")
# @login_required
def logout():
    logout_user()
    flash('You are successfully logged out.')
    return redirect("/")


#### MAIN
@app.route("/")
def main():
    collabs = Collaboration.objects(archive = False)

    return render_template('index.html', collabs=collabs)
####
@app.route("/filter/<list>")
def list(list):
    #Returns a specific list of collabs based on passed URL variable
    if list == "all":
        collabs = Collaboration.objects()
    elif list == "favorites":
        collabs = Collaboration.objects(favorite_list = current_user.id)
    elif list == "archived":
        collabs = Collaboration.objects(archive = True)

    return render_template('index.html', collabs=collabs)

# Favorite function, takes in collab_id and adds it to list of favorited collabs
@app.route("/favorite/<collab_id>", methods=["GET"])
@login_required
def favorite(collab_id):
    #Grab collab object from db with collab_id
    collab_select = Collaboration.objects(id = collab_id).first()
    if len(collab_select.favorite_list) == 0:
        #Add favorited collab to user list of favorites
        collab_select.favorite_list.append(current_user.id)
        flash("Collaboration %s ADDED to favorites." % collab_select.id)
    else:
        for user in collab_select.favorite_list:
            if current_user.username == user.username:
                # Removes user object id from collab's favorite list.
                collab_select.favorite_list.remove(user)
                flash("Collaboration %s REMOVED from favorites" %collab_select.id)
            else:
                #Add favorited collab to user list of favorites
                collab_select.favorite_list.append(current_user.id)
                flash("Collaboration %s ADDED to favorites." % collab_select.id)
    collab_select.save()
    return redirect("/")

# Should be a POST, but as a link a GET is more convienent.
@app.route("/archive/<collab_id>", methods=["GET"])
@login_required
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


@app.route("/search")
@login_required
def search():
    collabs = Collaboration.objects()
    return render_template("search.html", collabs=collabs, type=type)







# Abstracted new/edit collaboration workflow that takes in a stage and collab_id
# and generates the appropriate view and form.
@app.route("/new/<stage>/<collab_id>", methods=["GET","POST"])
@login_required
def new_stage(stage, collab_id):
    #If new collaboration started, create collaboration document in db
    if collab_id == "none":
        #Generate a collab_id with generate_id
        collab_select = generate_id()
    else:
        #Select the collab, given the collab_id(could be blank, or populated)
        collab_select = Collaboration.objects(id=collab_id).first()
        #Create a duplicate object, for comparision for audit log
        collab_previous = Collaboration.objects(id=collab_id).first()
    # Render the appropriate form given the stage
    form_stage = form_dict[stage]
    # If formdata is empty or not provided, this object is checked for attributes matching form field names,
    # which will be used for field values.
    form = form_stage(request.form, obj=collab_select)

    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        # Save whats on the form into the selected collab
        # Check to see if there were changes to any fields, if so, save them in an audit doc
        form.populate_obj(collab_select)
        form_current = form._fields
        collab_select.save()
        # raise("gimme console")
        #Look through both dictionaries, if the key/value pairs are different save them audit document
        # Checks to see if stage is closure to return back to homepage
        change_list = []
        for k in collab_previous:
            #Search the previous key in select, it should be there...
            if k in collab_select:
                # Catch special cases where collab_previous = None -> "", SelectionField, "String"
                # if collab_previous[k] is not None:
                # Compares SelectionField values between previous&selection
                # print(k)
                # print(type(collab_previous[k]))
                # print(collab_previous[k])
                # print(collab_select[k])

                if collab_previous[k] is None and type(collab_select[k]) ==  SelectionField:
                    # print("none to SelectionField object")
                    change = Change(stage = stage, field = k, previous = str(collab_previous[k]), current = str(collab_select[k].value))
                    change_list.append(change)

                elif type(collab_previous[k]) == SelectionField :
                    if collab_previous[k].value != collab_select[k].value:
                        # print("inside sleection field and different")
                        change = Change(stage = stage, field = k, previous = str(collab_previous[k].value), current = str(collab_select[k].value))
                        change_list.append(change)
                # Compares non-SelectionField values between previous&selection, if they are not date_mod
                elif k != 'date_mod' and collab_previous[k] != collab_select[k]:
                    if collab_previous[k] is None and collab_select[k] != "":
                        change = Change(stage = stage, field = k, previous = str(collab_previous[k]), current = str(collab_select[k]))
                        change_list.append(change)
                    elif collab_previous[k] is not None and collab_select[k] != "":
                        change = Change(stage = stage, field = k, previous = str(collab_previous[k]), current = str(collab_select[k]))
                        change_list.append(change)

        # If there are changes, create an audit object and save both
        if len(change_list) > 0:
            audit = Audit(date_change = datetime.today(), collab_ref = str(collab_select.id), username = current_user.username, change_list = change_list)
            # print("about to save audit wooh")
            audit.save()
            # raise "wtf selection field object??"

        if stage == 'closure':
            flash("Collaboration %s saved in DB" %collab_select.id)
            return redirect('/')
        flash(f"Stage {stage.title()} saved for Collaboration {collab_select.id}")
        return redirect('/new/'+ stage_array[stage_array.index(stage)+1] +'/'+ collab_id )#redirect to the next stage
    # Render the view given the stage

    return render_template(stage + '.html', form=form, collab_id=collab_select.id, stage=stage)


@app.route("/audit")
@login_required
def audit():
    audits = Audit.objects()
    return render_template('audit.html', audits=audits)


@app.route("/reports")
def reports():pass


if __name__ == "__main__":
    app.config.update(DEBUG = True, SECRET_KEY = '')

    app.run()
