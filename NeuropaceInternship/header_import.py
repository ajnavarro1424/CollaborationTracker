from app.py import Collaboration
import csv


''' Data dictionary:  one row per column in the original spreadsheet
    THE NAME HERE MUST MATCH A NAME IN data_dict.js !!
    name: display name; note that a blank name will be skipped
    orig_col: The column name from the original spreadsheet
    '''

study_dict = [
    {'name': '', 'orig_col': 'Data Sharing Req'},
    {'name': '', 'orig_col': 'Tag #'},
    {'name': 'NEW NEW TAG*'},
    {'name': '', 'orig_col': 'New interim Tag'},
    {'name': '', 'orig_col': 'ORIG TAG (CT Log)'},
    {'name': '', 'orig_col': 'ORIG TAG (Inv Init Log)'},
    {'name': 'Entry date', 'mdb_name' : 'entry_date'},
    {'name': 'Entered by', 'mdb_name' : 'entered_by'},
    {'name': 'Date Needed', 'mdb_name' : 'entry_date'},
    {'name': 'NP Study Sharing Approval Date', 'mdb_name' : 'approval_date'},
    {'name': 'NP Sharing Approval By', 'mdb_name' : 'approval_by'},
    {'name': 'Status', 'mdb_name' : 'status'},
    {'name': 'NeuroPace Contact', 'mdb_name' : 'neuropace_contact'},
    {'name': 'Institution', 'mdb_name' : 'institution'},
    {'name': 'PI / Institution Contact', 'mdb_name' : ['pi', 'institution_contact']},  # split me!!
    {'name': 'Reason for Collaboration', 'mdb_name' : 'reason'},
    {'name': 'Data Sharing Method', 'mdb_name' : 'sharing_method'},
    {'name': 'Data Set Description', 'mdb_name' : 'dataset_description'},
    {'name': 'PHI Present', 'mdb_name' : 'phi_present'},
    {'name': 'Data Share Type', 'mdb_name' : 'share_type'},
    {'name': 'Data Sharing Language', 'mdb_name' : 'sharing_language'},
    {'name': 'Study Type', 'mdb_name' : 'study_type'},
    {'name': 'Study Identifier', 'mdb_name' : 'study_identifier'},
    {'name': 'Study Risk Level', 'mdb_name' : 'risk_level'},
    {'name': 'Description / Study Title', 'mdb_name' : ['description', 'study_title'] },  # split me!!
    {'name': 'Initial IRB App Date', 'mdb_name' : 'irb_app_date'},
    {'name': 'Latest IRB Exp Date', 'mdb_name' : 'irb_exp_date'},
    {'name': 'Research Accessories Needed?', 'mdb_name' : 'accessories_needed'},
    {'name': 'Research Accessories Language', 'mdb_name' : 'accessories_language'},
    {'name': 'Single or Multi-Ctr', 'mdb_name' : 'single_multi_center'},
    {'name': 'Category', 'mdb_name' : 'category'},
    {'name': 'Funding Source', 'mdb_name' : 'funding_source'},
    {'name': 'Compensated by NP?', 'mdb_name' : 'np_compensation'},
    {'name': 'Consultant to NP?', 'mdb_name' : 'np_consultant'},
    {'name': 'Contract Needed?'}, 'mdb_name' : 'contract_needed',
    {'name': 'Budget Needed?', 'mdb_name' : 'budget_needed'},
    {'name': 'Contract Status', 'mdb_name' : 'status'},
    {'name': 'Contract Approval Date', 'mdb_name' : 'approval_date'},
    {'name': 'BOX link', 'mdb_name' : 'box_link'},
    {'name': 'Notes', 'width': 1000, 'mdb_name' : 'closure_notes'}]

# Loop through study_dict and match with Collaboration field names

def import_data():
    # First sheet: data_sharing for studies
    db = pymongo.MongoClient().data_sharing  # assume localhost
    db.drop_collection('clinical_studies')
    c1 = db.clinical_studies
    top_rows = 14  # The first 12 rows have no data??
    with open('DataSharingSpreadsheet.csv', 'rU') as csv_sheet:
        for (row_num, row) in enumerate(csv.reader(csv_sheet, delimiter=',')):#moving down
            if row_num < top_rows:  # skip the column names
                continue
            collab = Collaboration()
            for column_number, study_dict_entry in enumerate(study_dict):
                if study_dict_entry['name'] == '':  # skip certain columns
                    continue
                if '/' in study_dict_entry['name']:  # split this column...
                    # this is pretty horrible
                    # values are separated by commas, column names by slashes
                    # sometimes there are enough values, otherwise use ''
                    split_cell_vals = row[column_number].strip().split(',')
                    for column_header_num, column_value in enumerate(study_dict_entry['mdb_name']):
                        if len(split_cell_vals) < column_header_num:
                            collab._fields[column_value] = split_cell_vals[column_header_num]
                        else:  # fill with a blank val
                            collab._fields[column_value] = ''

                else:  # simple case
                    collab._fields[study_dict_entry['mdb_name']] = row[column_number].strip()
            collab.save()


if __name__ == '__main__':
    import_data()
