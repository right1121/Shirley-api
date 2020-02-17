import boto3

from api import responser

dynamodb_client = boto3.client('dynamodb')

depot_table_name = 'depot'


def lambda_handler(event, context):
    try:
        print(event)
        user_id = find_username_from_event(event)
        return main(user_id)
    except ValueError as e:
        print('ValueError error', e)
        return responser.validation_error()
    except Exception as e:
        print('Exception error', e)
        return responser.exception_error()


def find_username_from_event(handler_event):
    """lambda handlerのイベントからユーザー名を取得する

    :param handler_event: lambda handlerのイベント
    :type handler_event: dict
    """
    username = handler_event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    return username


def main(user_id):
    response = responser()

    res = query_ownership_train_cars(depot_table_name, user_id)

    response.body = res

    return response.format()


def query_ownership_train_cars(table_name, owner_id):
    res = dynamodb_client.query(
        TableName=depot_table_name,
        KeyConditions={
            'owner_id': {
                'ComparisonOperator': 'EQ',
                'AttributeValueList': [
                    {'S': owner_id}
                ]
            }
        }
    )

    train_car_items = res['Items']

    dict_key = "train_id"

    cars_info_dict = convert_query_response_items_to_dict(
        train_car_items, dict_key)

    return cars_info_dict


def convert_query_response_items_to_dict(query_response_items, dict_key):
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
        converted_data['KeyList'].append(item_dict[dict_key])

    return converted_data


def convert_type_query_data(data_type, value):
    if data_type == "S":
        converted_value = value
    elif data_type == "N":
        converted_value = int(value)

    return converted_value
