from app import SelectionField
#Create the field_name and value pairs for the dropdows fields in the database
dropdown_dict = {
                'reason' : ['N/A', 'Collaboration', 'Grant Proposal', 'Grant', 'Product Development', 'Publication', 'Research', 'Study'],
                'category' : ['N/A', 'Addiction', 'Epilepsy', 'Memory', 'MRI', 'Spatial Navigation', 'SUDEP', 'Tourette', 'Depression', 'Other'],
                'neuropace_contact' : ['N/A', 'EM', 'FS', 'JHP', 'NH', 'SD', 'TS', 'TT', 'TAC', 'Other'],
                'sharing_method' : ['N/A', 'PDMS', 'Derivative DB', 'USB (encrypted)', 'Email or ftp (encrypted)', 'Cloud (BOX)', 'IEEG.org'],
                'dataset_description' : ['N/A', 'Aggregate ECOG data', 'CRF data', '.dat files', 'Device Historgrams', 'ECOG data', 'ECOG & CRF Data', 'PDMS', 'Other'],
                'share_type' : ['N/A', 'NP Sponsored', 'Investigator Initiated'],
                'sharing_language' : ['N/A', 'NP Protocol/ICF', 'Institution Protocol/ICF'],
                'study_type' : ['N/A', 'IDE', 'IDE/PMA', 'PMA', 'IRB'],
                'risk_level' : ['N/A', 'NSR', 'SR'],
                'accessories_language' : ['N/A', 'NP Protocol', 'Institution Protocol'],
                'single_multi_center' : ['N/A', 'Multiple', 'Single'],
                'funding_source' : ['N/A', 'Grant NP', 'Grant Institution' 'NP', 'Institution', 'TBD'],
                'approval_by' : ['N/A', 'TAC', 'CGS', 'JHP'],
                'status' : ['N/A', 'Complete', 'On Hold', 'Ongoing', 'Cancel', 'Void', 'In Review']
                }
for k, v in dropdown_dict.items():
    for av in v:
        selection = SelectionField(field_name=k, value=av)
        selection.save()
