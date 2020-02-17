import json

import boto3

from api import responser

dynamodb_client = boto3.client('dynamodb')

master_table_list = [
    'model_maker',
    'railway_company'
]


def lambda_handler(event, context):
    try:
        return main()
    except Exception as e:
        print("Exception error", e)
        return responser.exception_error()


def main():
    response = responser()

    master_data = {}

    for table_name in master_table_list:
        data_list = fetch_master_data(table_name)
        master_data[table_name] = data_list

    response.body = master_data

    return response.format()


def fetch_master_data(table_name):
    query_res_data = dynamodb_client.scan(
        TableName=table_name
    )
    items = query_res_data['Items']
    dict_key = 'name'
    data = convert_query_response_items_to_dict(items, dict_key)

    return data['KeyList']


def convert_query_response_items_to_dict(query_response_items, dict_key=None):
    converted_data = {
        'Items': [],
        'KeyList': [],
    }

    for train_data in query_response_items:
        item_dict = {}
        for data_key, data_info in train_data.items():
            for data_type, value in data_info.items():
                item_dict[data_key] = convert_type_query_data(data_type, value)

        converted_data['Items'].append(item_dict)

        if dict_key is not None:
            converted_data['KeyList'].append(item_dict[dict_key])

    return converted_data


def convert_type_query_data(data_type, value):
    if data_type == "S":
        converted_value = value
    elif data_type == "N":
        converted_value = int(value)

    return converted_value
