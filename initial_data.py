import csv
import pymongo
import data_dict


def import_data():
    # First sheet: data_sharing for studies
    db = pymongo.MongoClient().data_sharing  # assume localhost
    db.drop_collection('clinical_studies')
    c1 = db.clinical_studies
    top_rows = 14  # The first 12 rows have no data??

    with open('DataSharingSpreadsheet.csv', 'rU') as csv_sheet:
        for (row_num, row) in enumerate(csv.reader(csv_sheet, delimiter=',')):
            if row_num < top_rows:  # skip the column names
                continue
            sheet_dict = {}
            for idx, key in enumerate(data_dict.study_dict):
                if key['name'] == '':  # skip certain columns
                    continue
                if '/' in key['name']:  # split this column...
                    # this is pretty horrible
                    # values are separated by commas, column names by slashes
                    # sometimes there are enough values, otherwise use ''
                    vals = row[idx].strip().split(',')
                    for kidx, k in enumerate(key['name'].split('/')):
                        if len(vals) < kidx:
                            sheet_dict[k] = vals[kidx]
                        else:  # fill with a blank val
                            sheet_dict[k] = ''

                else:  # simple case
                    sheet_dict[key['name']] = row[idx].strip()
            c1.insert_one(sheet_dict)


if __name__ == '__main__':
    import_data()
