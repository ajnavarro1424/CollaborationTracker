# Importing flask packages
from flask import Flask, render_template, request, redirect, flash, url_for, \
                  jsonify
from flask_assets import Environment
# Importing mongoengine and forms to our flask framework
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_mongoengine.wtf import model_form
# Packages for the login functionality
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
# Test to see if flask_mongoengine covers below
from mongoengine import signals
import blinker
#Date libaries for parsing strings and datetime objects
from datetime import datetime
import calendar

# TODO: Move global inits into its own __init__.py file.
# global variable representing the entire app (Flask object called 'app')
app = Flask(__name__)
assets = Environment(app)

#Config for remote database
# app.config['MONGO_DBNAME'] = 'collabs_db'
# app.config['MONGO_URI'] = 'mongodb://<ajnavarro1424>:<ajnavarro1424>@ds131511.mlab.com:31511/collabs_db'

#MongoEngine setup
mdb = MongoEngine(app)
# app.session_interface = MongoEngineSessionInterface(mdb)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

    ############################
    #### Model Creation     ####
    ############################

# User model defines the fields necessary for login
class User(mdb.Document, UserMixin):
    username = mdb.StringField(pk = True)
    password = mdb.StringField()
    def get_id(self):
     return self.username

# Necessary for Flask-Login to load the user
@login_manager.user_loader
def load_user(user_id):
 return User.objects(username=user_id).first()

# SelectionField generates dropdown-menus in forms
class SelectionField(mdb.Document):
    value = mdb.StringField()
    field_name = mdb.StringField()

# Collaboration model represents the form fields for all workflows
class Collaboration(mdb.Document):
    # Variables to add functionality to colalboration views
    archive = mdb.BooleanField(default = False)
    date_mod = mdb.DateTimeField(label = "Date Modified")
    favorite_list = mdb.ListField(mdb.ReferenceField(User))

    # Initiation form values
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
    phi_present = mdb.BooleanField(label = "PHI Present", default = False)
    share_type = mdb.ReferenceField(SelectionField, label = "Data Share Type") #dropdown-menu
    sharing_language = mdb.ReferenceField(SelectionField, label = "Data Sharing Language") #dropdown-menu
    study_type = mdb.ReferenceField(SelectionField) #dropdown-menu
    study_identifier = mdb.StringField(max_length = 1000)
    risk_level = mdb.ReferenceField(SelectionField, label = "Study Risk Level") #dropdown-menu
    accessories_needed = mdb.BooleanField(label = "Research Accessories Needed?", default = False)
    accessories_language = mdb.ReferenceField(SelectionField, label = "Research Accessories Language") #dropdown-menu
    single_multi_center = mdb.ReferenceField(SelectionField, label = "Single or Multi-Center") #dropdown-menu
    detail_notes = mdb.StringField()

    #Contracts and Financials (Flow2/Pg3)
    funding_source = mdb.ReferenceField(SelectionField) #dropdown-menu
    np_compensation = mdb.BooleanField(label = "Compensated by NP?", default = False)
    np_consultant = mdb.BooleanField(label = "Consultant to NP?", default = False)
    contract_needed = mdb.ReferenceField(SelectionField, label = "Contract Needed?") # dropdown-menu
    budget_needed = mdb.StringField(label = "Budget Needed?",max_length = 1000)
    inv_sites_approval_req = mdb.StringField(label = "Inv Sites Approval Req'd", max_length = 1000)
    vpn_access = mdb.StringField(label = "VPN access?", max_length = 1000)
    contract_status = mdb.ReferenceField(SelectionField, label = "Contract Status")
    contract_approval_date = mdb.StringField(max_length = 1000)
    contract_notes = mdb.StringField()

    #Legal(Flow4/Pg.4)
    approval_date = mdb.StringField(label='NP Study Sharing Approval Date', max_length = 1000)
    approval_by = mdb.ReferenceField(SelectionField, label='NP Sharing Approval By') # dropdown-menu
    irb_app_date = mdb.StringField(label = 'Initial IRB App Date', max_length = 1000)
    irb_exp_date = mdb.StringField(label = 'Latest IRB Exp Date', max_length = 1000)

    # Legal continued(.pdf exclusive values)
    pc_research_acc = mdb.BooleanField(label = "Protocol Coverage for Research Accessories")
    pc_data_sharing = mdb.BooleanField(label = "Protocol Coverage for Data Sharing")
    icfc_data_sharing = mdb.BooleanField(label = "ICF Coverage for Data Sharing")
    expiration_date = mdb.StringField(max_length = 1000)
    ds_racc_notes = mdb.StringField(label = "Data Sharing / Research Accessories Notes")
    legal_notes = mdb.StringField()

    #Closure
    status = mdb.ReferenceField(SelectionField, label = "Collaboration Status") # dropdown-menu
    box_link = mdb.StringField(label = 'BOX Link', max_length = 1000)
    notes = mdb.StringField()

    #Converts UTC time to local time, necessary for native datetime objects
    def utc_2_local(self, field):
        TIME_FORMAT = '%Y-%m-%d %I:%M:%S'
        timestamp =  calendar.timegm(field.timetuple())
        local = datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)
        return local

#Updates the date_mod field to the current date when collab changes.
def update_modified(sender, document):
    if document._class_name == 'Collaboration':
        document.date_mod = datetime.today()

#Calls to update date_mod before all DB saves.
signals.pre_save.connect(update_modified)

# Part of the Audit model, captures changes made to collaboration fields.
class Change(mdb.EmbeddedDocument):
    stage = mdb.StringField(max_length = 1000)
    field = mdb.StringField(max_length = 1000)
    previous = mdb.StringField(max_length = 1000)
    current = mdb.StringField(max_length = 1000)

# Audit model captures all data regarding field change.
class Audit(mdb.Document):
    date_change = mdb.DateTimeField()
    username = mdb.StringField(max_length = 1000)
    collab_ref = mdb.StringField(max_length = 1000)
    change_list = mdb.ListField(mdb.EmbeddedDocumentField(Change))

    ############################
    #### Helper Methods     ####
    ############################

# Takes MongoDB field object, checks for label attribute
# Returns label or titled variable name.
def labelize(field):
    if hasattr(field, "label"):
        return field.label
    return field.db_field.replace('_', ' ').title()

# Takes in Collaboration model with a field list(only), and builds field_args(labels)
# Returns model_form(WTF forms) for the given stage.
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
                                 'label' : labelize(field),
                                 'allow_blank':True,
                                 'blank_text':u'--Enter Selection--'}
    return model_form(model, only=only, field_args=field_args, **kwargs)

# form_dict generates the appropirate model_form call when a specific stage is passed to the route.
form_dict = {
            'init' : collab_model_form(Collaboration, ['date_mod','entry_date', 'entered_by', 'date_needed', 'institution', 'institution_contact', 'pi', 'reason', 'category', 'status', 'init_notes']),
            'details' : collab_model_form(Collaboration, ['neuropace_contact', 'sharing_method', 'study_title', 'description', 'dataset_description', 'phi_present', 'share_type', 'sharing_language', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_language', 'single_multi_center','status', 'detail_notes']),
            'contract' : collab_model_form(Collaboration, ['funding_source', 'np_consultant', 'np_compensation', 'contract_needed','contract_status', 'budget_needed', 'status', 'contract_notes']),
            'legal' : collab_model_form(Collaboration, ['approval_date', 'approval_by', 'irb_app_date', 'irb_exp_date', 'status', 'legal_notes']),
            'closure' : collab_model_form(Collaboration, ['status', 'box_link', 'notes'])
            }


# Helper methods for Jinja2 templating
# They can be called from the template for processing of fields
@app.context_processor
def utility_processor():
    #Takes in a collaboration value(String or a SelectionField), and returns a boolean
    def not_string(collab_value):
        if type(collab_value) == SelectionField:
            return True
        else:
            return False
    #Labelize definition is on line 152
    return dict(not_string = not_string, labelize=labelize)



# Used exclusively in Report View, ties the stage variable to the associated form fields.
# Looped through, and the field array queries a collab with "collab[field]"
stage_dict = {
            'Initiation' : ['date_mod','entry_date', 'entered_by', 'date_needed', 'institution', 'institution_contact', 'pi', 'reason', 'category', 'status', 'init_notes'],
            'Details' : ['neuropace_contact', 'sharing_method', 'study_title', 'description', 'dataset_description', 'phi_present', 'share_type', 'sharing_language', 'study_type', 'study_identifier', 'risk_level', 'accessories_needed', 'accessories_language', 'single_multi_center','status', 'detail_notes'],
            'Contract' : ['funding_source', 'np_consultant', 'np_compensation', 'contract_needed','contract_status', 'budget_needed', 'status', 'contract_notes'],
            'Legal' : ['approval_date', 'approval_by', 'irb_app_date', 'irb_exp_date', 'status', 'legal_notes'],
            'Closure' : ['status', 'box_link', 'notes']
            }


# TODO: stage_array needs to go into the Collaboration object
stage_array = ["init", "details", "contract", "legal", "closure"]


    ############################
    #Login Functions and Routes#
    ############################

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login/<username>', methods=['GET', 'POST'])
def login(username):
    # Find or create a user with the given username...
    user = User.objects.get(username=username)
    if user is not None:
        login_user(user)
        next = request.args.get('next')
        if not is_safe_url(next):
            flash('URL is not safe')
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


    ############################
    #### Routes             ####
    ############################

@app.route("/")
def main():
    # collabs = Collaboration.objects(archive = False)
    collabs = Collaboration.objects()
    return render_template('index.html', collabs=collabs)

@app.route("/filter/<list>")
def list(list):
    #Returns a specific list of collabs based on passed URL variable
    if list == "all":
        collabs = Collaboration.objects()
    elif list == "favorites":
        collabs = Collaboration.objects(favorite_list = current_user.id)
    elif list == "archived":
        collabs = Collaboration.objects(archive = True)
    # TODO: Thow a 404 if you try to see a list that doesnt exist

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
        # Toggle's the user in the favorite_list.
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
    # TODO: Thow a 404 if you try to pass a collab id that doesnt exist that doesnt exist
    return redirect("/")

# Should be a POST, but as a link a GET is more convienent.
@app.route("/archive", methods=["POST"])
@login_required
def archive():
    ''' Toggle the archived state on a collaboration.
        Meant to be called via AJAX'''
    # Pull collab for archiving
    collab_select = Collaboration.objects.get(id=request.form['collab_id'])
    # Check the archive status and save opposite
    if collab_select.archive ==  False:
        collab_select.archive = True
        # flash('Collaboration %s successfully archived.' % collab_select.id)
    else:
        collab_select.archive = False
        # flash('Collaboration %s successfully restored.' % collab_select.id)
    collab_select.save()
    print("Just above the return")
    # redirect to the index page where the archived collab will have disappeared
    return jsonify(collab_id=str(collab_select.id), success=True,
                   archived=collab_select.archive,
                   new_new_tag=str(collab_select.new_new_tag))

@app.route("/report/<collab_id>", methods=["GET"])
@login_required
def report(collab_id):
    #Go grab selected collaboration from DB
    collab_select = Collaboration.objects(id=collab_id).first()
    report_date = datetime.today().strftime('%Y-%m-%d %I:%M:%S')
    return render_template("report.html", collab_select=collab_select,report_date=report_date, stage_dict=stage_dict)

@app.route("/search")
@login_required
def search():
    # Grab all the collabs from the database to loop through
    collabs = Collaboration.objects()
    return render_template("search.html", collabs=collabs)

# Workflow routes that takke a stage and collab_id. Generates and submits forms.
@app.route("/new/<stage>/<collab_id>", methods=["GET","POST"])
@login_required
def new_stage(stage, collab_id):
    #If new collaboration started, create collaboration document in db
    if collab_id == "none":
        #Create a new collaboraiton object and save to DB
        collab_select = Collaboration()
        collab_select.save()
    else:
        #Select the collab, given the collab_id
        collab_select = Collaboration.objects.get(id=collab_id)
    # Render the appropriate form given the stage
    form_stage = form_dict[stage]
    # If formdata is empty or not provided, this object is checked for attributes matching form field names,
    # which will be used for field values.
    form = form_stage(request.form, obj=collab_select)
    if request.method == 'POST' and form.validate_on_submit():
        del(form.csrf_token)
        form.populate_obj(collab_select)
        form_current = form._fields
        #Create a duplicate object, for comparision for audit log
        collab_previous = Collaboration.objects.get(id=collab_id)
        # Save whats on the form into the selected collab
        collab_select.save()
        #Call audit_save to save changes made to any fields
        audit_save(collab_previous, collab_select, stage)
        # Checks to see if stage is closure to return back to homepage
        if stage == 'closure':
            flash("Collaboration %s saved in DB" %collab_select.id)
            return redirect('/')
        flash(f"Stage {stage.title()} saved for Collaboration {collab_select.id}")
        return redirect('/new/'+ stage_array[stage_array.index(stage)+1] +'/'+ collab_id )
    # Render the view given the stage
    return render_template(stage + '.html', form=form, collab_id=collab_select.id, stage=stage)


def audit_save(collab_previous, collab_select, stage):
    #Look through both dictionaries, if the key/value pairs are different save them audit document
    change_list = []
    # TODO: What happens if the object fields dont match???? Matt slack. ADD AN ELSE Mother fucker.
    for k in collab_previous:
        # Use collab_previous keys(fields) to loop thorugh collab_select to compare values.
        if k in collab_select:
            # Edge case: None cannot have .value() called, needs separate conditional
            if collab_previous[k] is None and type(collab_select[k]) ==  SelectionField:
                change = Change(stage = stage, field = k, previous = str(collab_previous[k]), current = str(collab_select[k].value))
                change_list.append(change)
            # This conditional catches differences in SelectionFields
            elif type(collab_previous[k]) == SelectionField :
                if collab_previous[k].value != collab_select[k].value:
                    change = Change(stage = stage, field = k, previous = str(collab_previous[k].value), current = str(collab_select[k].value))
                    change_list.append(change)
            # This conditional catches differences in StringFields, if they are not date_mod
            elif k != 'date_mod' and collab_previous[k] != collab_select[k]:
                if collab_select[k] != "":
                    change = Change(stage = stage, field = k, previous = str(collab_previous[k]), current = str(collab_select[k]))
                    change_list.append(change)
    # If there are changes, create and save audit and change_list
    if len(change_list) > 0:
        audit = Audit(date_change = datetime.today(), collab_ref = str(collab_select.id), username = current_user.username, change_list = change_list)
        audit.save()


@app.route("/audit")
@login_required
def audit():
    audits = Audit.objects()
    return render_template('audit.html', audits=audits)

#MSB DEBUG ONLY
@app.route("/fav/debug", methods=["GET"])
def fav():
    #Grab collab object from db with collab_id
    u = User.objects.get(username='bauer123')
    collabs = Collaboration.objects(pi = 'Erik Kobylarz').all()
    for collab_select in collabs:
        if len(collab_select.favorite_list) == 0:
            #Add favorited collab to user list of favorites
            collab_select.favorite_list.append(u.id)
            flash("Collaboration %s ADDED to favorites." % collab_select.id)
        else:
            # Toggle's the user in the favorite_list.
            for user in collab_select.favorite_list:
                if u.username == user.username:
                    # Removes user object id from collab's favorite list.
                    collab_select.favorite_list.remove(user)
                    flash("Collaboration %s REMOVED from favorites" %collab_select.id)
                else:
                    #Add favorited collab to user list of favorites
                    collab_select.favorite_list.append(u.id)
                    flash("Collaboration %s ADDED to favorites." % collab_select.id)
        collab_select.save()
    # TODO: Thow a 404 if you try to pass a collab id that doesnt exist that doesnt exist
    return redirect("/")


if __name__ == "__main__":
    app.config.update(DEBUG = True, SECRET_KEY = '')
    app.run()
