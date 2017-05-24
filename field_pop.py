from collabtrack import Collaboration, SelectionField, User, Audit, mdb
# Packages for the login functionality - copied from appy.py because login_required wasn't being recognized without explicitly calling it here.
from flask_login import UserMixin, LoginManager, login_required
from urllib.parse import urlparse, urljoin

import csv


#Create the field_name and value pairs for the dropdows fields in the database
dropdown_dict = {
                'reason' : ['N/A', 'Collaboration', 'Grant Proposal', 'Grant', 'Product Development', 'Publication', 'Research', 'Study'],
                'category' : ['Stimulation', 'Analystics'],
                'neuropace_contact' : ['N/A', 'AR', 'AW', 'SD', 'RS' 'Other'],
                'sharing_method' : ['N/A', 'Encrypted Email', 'Derivative DB', 'USB (encrypted)', 'Email or ftp (encrypted)', 'Cloud (BOX)', 'IEEG.org'],
                'dataset_description' : ['N/A', '.CSV', 'Database'],
                'share_type' : ['N/A', 'FD Sponsored', 'Investigator Initiated'],
                'sharing_language' : ['N/A', 'FD RCT', 'Institution WRP'],
                'study_type' : ['N/A', 'Research', 'Academic'],
                'risk_level' : ['N/A', 'Extreme', 'Moderate', "None"],
                'accessories_language' : ['N/A', 'English'],
                'single_multi_center' : ['N/A', 'Multiple', 'Single'],
                'funding_source' : ['N/A'],
                'contract_needed' : ['Yes, new', 'Yes, update', 'Yes, current', 'No'],
                'approval_by' : ['N/A', 'PT', 'TT', 'RN', 'PW', 'AK'],
                'contract_status' : ["N/A", 'Fully Executed', 'In Progress', "Not Complete"],
                #Incomplete is not in the dropdown options in the .csv file
                'status' : ['N/A', 'Complete', 'On Hold', 'Ongoing', 'Cancel', 'Void', 'In Review', 'Incomplete']
                }
def field_pop():
    #Delete existing collecdtions in the test database
    Collaboration.drop_collection()
    SelectionField.drop_collection()
    User.drop_collection()
    Audit.drop_collection()

    for k, v in dropdown_dict.items():
        for av in v:
            selection = SelectionField(field_name=k, value=av)
            selection.save()

    # Create a couple very cool(sorry kaz) users in the db
    alex = User(username="ajnavarro1424", password="cholula")
    luke = User(username="bauer123", password="frisbee")
    alex.save()
    luke.save()



study_dict = [
    {'name': '', 'orig_col': 'Data Sharing Req'},
    {'name': '', 'orig_col': 'Tag #'},
    {'name':'NEW NEW TAG*', 'mdb_name' : 'new_new_tag'},
    {'name': '', 'orig_col': 'New interim Tag'},
    {'name': '', 'orig_col': 'ORIG TAG (CT Log)'},
    {'name': '', 'orig_col': 'ORIG TAG (Inv Init Log)'},
    {'name': 'Entry date', 'mdb_name' : 'entry_date'},
    {'name': 'Entered by', 'mdb_name' : 'entered_by'},
    {"name":'Date Needed', 'mdb_name' : 'date_needed'},
    {"name":'NP Study Sharing Approval Date', 'mdb_name' : 'approval_date'},
    {"name":'NP Sharing Approval By', 'mdb_name' : 'approval_by'},
    {"name":'Status', 'mdb_name' : 'status'},
    {"name":'NeuroPace Contact', 'mdb_name' : 'neuropace_contact'},
    {"name":'Institution', 'mdb_name' : 'institution'},
    {"name":'PI / Institution Contact', 'mdb_name' : ['pi', 'institution_contact']},  # split me!!
    {'name': 'Reason for Collaboration', 'mdb_name' : 'reason'},
    {"name":'Data Sharing Method', 'mdb_name' : 'sharing_method'},
    {"name":'Data Set Description', 'mdb_name' : 'dataset_description'},
    {"name":'PHI Present', 'mdb_name' : 'phi_present'},
    {"name":'Data Share Type', 'mdb_name' : 'share_type'},
    {"name":'Data Sharing Language', 'mdb_name' : 'sharing_language'},
    {"name":'Study Type', 'mdb_name' : 'study_type'},
    {"name":'Study Identifier', 'mdb_name' : 'study_identifier'},
    {"name":'Study Risk Level', 'mdb_name' : 'risk_level'},
    {"name":'Description / Study Title', 'mdb_name' : ['description', 'study_title'] },  # split me!!
    {"name":'Initial IRB App Date', 'mdb_name' : 'irb_app_date'},
    {"name":'Latest IRB Exp Date', 'mdb_name' : 'irb_exp_date'},
    {"name":'Research Accessories Needed?', 'mdb_name' : 'accessories_needed'},
    {"name":'Research Accessories Language', 'mdb_name' : 'accessories_language'},
    {"name":'Single or Multi-Ctr', 'mdb_name' : 'single_multi_center'},
    {"name":"Inv Sites Approval Req'd", 'mdb_name' : "inv_sites_approval_req"},
    {"name":'VPN access?', 'mdb_name' : 'vpn_access'},
    {"name":'Category', 'mdb_name' : 'category'},
    {"name":'Funding Source', 'mdb_name' : 'funding_source'},
    {"name":'Compensated by NP?', 'mdb_name' : 'np_compensation'},
    {"name":'Consultant to NP?', 'mdb_name' : 'np_consultant'},
    {"name":'Contract Needed?', 'mdb_name' : 'contract_needed'},
    {"name":'Budget Needed?', 'mdb_name' : 'budget_needed'},
    {"name":'Contract Status', 'mdb_name' : 'contract_status'},
    {"name":'Contract Approval Date', 'mdb_name' : 'contract_approval_date'},
    {"name":'BOX link', 'mdb_name' : 'box_link'},
    {"name":'Notes', 'width': 1000, 'mdb_name' : 'notes'}]

# Loop through study_dict and match with Collaboration field names

def import_data():
    top_rows = 14  # The first 12 rows have no data??
    end_row = 45
    with open('DataScrubbed_HTML5.csv', 'rU') as csv_sheet:
        for (row_num, row) in enumerate(csv.reader(csv_sheet, delimiter=',')):#moving down
            if row_num < top_rows:  # skip the column names
                continue
            collab = Collaboration()
            if row_num <= end_row:
                for column_number, study_dict_entry in enumerate(study_dict):

                    csv_col = study_dict_entry['name']
                    if csv_col == '':  # skip certain columns
                        continue
                    mdb_col = study_dict_entry['mdb_name']
                    cell_value = row[column_number].strip()

                    if '/' in csv_col: # split this column...
                        # this is pretty horrible
                        # values are separated by commas, column names by slashes
                        # sometimes there are enough values, otherwise use ''
                        split_cell_vals = cell_value.split(',')
                        for column_header_num, column_value in enumerate(mdb_col):
                            if len(split_cell_vals) > column_header_num:
                                collab._data[column_value] = split_cell_vals[column_header_num]
                            else:  # fill with a blank val
                                collab._data[column_value] = ''

                    elif type(collab._fields[mdb_col]) == mdb.ReferenceField:

                        # print(SelectionField.objects(field_name= mdb_col, value__iexact = cell_value).first().value)
                        if SelectionField.objects(field_name= mdb_col, value__iexact = cell_value).first() is not None:
                            collab._data[mdb_col] = SelectionField.objects(field_name= mdb_col, value__iexact = cell_value).first()

                    elif type(collab._fields[mdb_col]) == mdb.BooleanField:

                        if cell_value in ("Yes","YES",'yes'):
                            collab._data[mdb_col] = True
                        else:
                            collab._data[mdb_col] = False

                    else:  # simple case
                        collab._data[mdb_col] = cell_value

                    # print((mdb_col))
                    # print("x%sx" %cell_value)
                collab.save()


if __name__ == '__main__':
    field_pop()
    import_data()
