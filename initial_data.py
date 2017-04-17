import csv
from data_sharing import app, data_dict
# from . import app


def import_data():
    # First sheet: data_sharing for studies
    app.mdb.drop_collection('clinical_studies')
    c1 = app.mdb.clinical_studies
    top_rows = 12  # The first 12 rows have no data??

    with open('DataSharingSpreadsheet.csv', 'rU') as csv_sheet:
        for (row_num, row) in enumerate(csv.reader(csv_sheet, delimiter=',')):
            if row_num < top_rows:  # skip the column names
                continue
            idx = 0
            sheet_dict = {}
            for key in data_dict.study_dict:
                if key['name']:  # skip certain columns
                    sheet_dict[key['name']] = row[idx].strip()
                idx += 1
            c1.insert_one(sheet_dict)


if __name__ == '__main__':
    import_data()
