from django.db import IntegrityError, transaction
from django.db.migrations import exceptions

from tableviewer.models import TableColumn, TableSettings

import csv

# Utility Functions
def get_file_data(instance, active_only=False, active_column_header_type="label"):
    file_path = instance.table_file.path
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        try:
            reader = csv.DictReader(csvfile)
            if active_only:
                data = {'columns': instance.get_active_columns(active_column_header_type), 'rows': []}  # the column names are the label column from the TableColumn model
                column_names = instance.get_active_columns('name')  # column names from the TableColumn model to match with the csv file
                for row in reader:
                    new_row = {}
                    for column in column_names:
                        new_row[column] = row[column]
                    data['rows'].append(new_row)
            else:
                columns = [column.strip() for column in reader.fieldnames]
                data = {'columns': columns, 'rows': []}
                for row in reader:
                    data['rows'].append(row)
            return data
        except csv.Error as e:
            return {'error': str(e)}


def search_data(data, keyword, column=None):
    results = []  # empty array to store the results
    # searched_data = [] # for testing
    if column == '':  # if the column is '' then set it to None
        column = None

    for row in data['rows']:  # this data was generated through the get_file_data method
        row_data = {'row': row, 'column_vals': []}
        if column is not None:
            if keyword in row[column]:
                results.append(row)
        else:
            for col in data['columns']:
                row_data['column_vals'].append(row[col])
                if keyword in row[col]:
                    results.append(row)
        # searched_data.append(row_data)  # for testing
    # raise Exception("Manually Stopped") # for testing
    return results


def get_column_name(table_instance, label):
    column = table_instance.columns.filter(label=label)[0]
    return column.name


def save_columns(instance, commit=True):
    """Takes a table instance and a dictionary of data and creates columns for the table."""
    data = get_file_data(instance)
    counter = 0
    column_instances = []

    for column in data["columns"]:
        try:
            column_instance = TableColumn(
                table=instance,
                name=column,
                label=column,
                order=counter,
            )
            column_instances.append(column_instance)
        except IntegrityError as e:
            return None
        counter += 1

    if not commit:
        # committing the changes if commit is false
        for column_instance in column_instances:
            column_instance.save()

    return column_instances


def regenerate_table_columns(columns, instance):
    """Deletes all table columns and regenerates them."""
    # adding all the new columns
    new_columns = save_columns(instance, commit=False)

    if new_columns is not None:
        # deleting all existing columns
        try:
            with transaction.atomic():
                for column in columns:
                    try:
                        column.delete()
                    except IntegrityError as e:
                        raise exceptions.DatabaseError(str(e))
        except IntegrityError as e:
            return e

    for column in new_columns:
        # committing all the new columns
        column.save()

    return True


def _save_table_settings(instance, values):
    """Saves a setting for a table."""
    obj = TableSettings.objects.filter(pk=instance.id).update(**values)
    return obj


# Utility Variables
TOP_BANNER_MESSAGES = {
    "unpublished": {
        "message": "Table not published. To publish it, click the Publish button within the settings tab.",
        "icon": "fa fa-circle-o",
        "type": "warning",
    }
}
