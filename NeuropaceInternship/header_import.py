from app.py import Collaboration
import csv
import pymongo

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
    {'name': 'Entered by'},
    {'name': 'Date Needed'},
    {'name': 'NP Study Sharing Approval Date'},
    {'name': 'NP Sharing Approval By'},
    {'name': 'Status'},
    {'name': 'NeuroPace Contact'},
    {'name': 'Institution'},
    {'name': 'PI / Institution Contact'},  # split me!!
    {'name': 'Reason for Collaboration'},
    {'name': 'Data Sharing Method'},
    {'name': 'Data Set Description'},
    {'name': 'PHI Present'},
    {'name': 'Data Share Type'},
    {'name': 'Data Sharing Language'},
    {'name': 'Study Type'},
    {'name': 'Study Identifier'},
    {'name': 'Study Risk Level'},
    {'name': 'Description / Study Title'},  # split me!!
    {'name': 'Initial IRB App Date'},
    {'name': 'Latest IRB Exp Date'},
    {'name': 'Research Accessories Needed?'},
    {'name': 'Research Accessories Language'},
    {'name': 'Single or Multi-Ctr'},
    {'name': 'Category'},
    {'name': 'Funding Source'},
    {'name': 'Compensated by NP?'},
    {'name': 'Consultant to NP?'},
    {'name': 'Contract Needed?'},
    {'name': 'Budget Needed?'},
    {'name': 'Contract Status'},
    {'name': 'Contract Approval Date'},
    {'name': 'BOX link'},
    {'name': 'Notes', 'width': 1000}]

# Loop through study_dict and match with Collaboration field names

def import_data():
    # First sheet: data_sharing for studies
    db = pymongo.MongoClient().data_sharing  # assume localhost
    db.drop_collection('clinical_studies')
    c1 = db.clinical_studies
    top_rows = 14  # The first 12 rows have no data??
    with open('DataSharingSpreadsheet.csv', 'rU') as csv_sheet:
        for (row_num, row) in enumerate(csv.reader(csv_sheet, delimiter=',')):#moving down
            if :  # skip the column names


            collab = Collaboration()
            for column_number, study_dict_entry in enumerate(study_dict):
                if study_dict_entry['name'] == '':  # skip certain columns
                    continue
                if '/' in study_dict_entry['name']:  # split this column...
                    # this is pretty horrible
                    # values are separated by commas, column names by slashes
                    # sometimes there are enough values, otherwise use ''
                    split_cell_vals = row[column_number].strip().split(',')
                    for column_header_num, column_value in enumerate(study_dict_entry['name'].split('/')):
                        if len(split_cell_vals) < column_header_num:
                            sheet_dict[column_value] = split_cell_vals[column_header_num]
                        else:  # fill with a blank val
                            sheet_dict[column_value] = ''

                else:  # simple case


                    collab._fields[study_dict_entry['name']] = row[column_number].strip()
            c1.insert_one(sheet_dict)


if __name__ == '__main__':
    import_data()
