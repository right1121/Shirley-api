import json

import boto3

from api import responser
from common import generate_uuid

dynamodb_client = boto3.client('dynamodb')

train_table_name = "depot"
railway_company_table_name = "railway_company"


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        body["owner_id"] = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
        return main(body)
    except ValueError as e:
        print("ValueError error", e)
        return responser.validation_error()
    except Exception as e:
        print("Exception error", e)
        return responser.exception_error()


def main(body):
    response = responser()

    verify_body_data(body)

    body["train_id"] = generate_uuid()
    items = generate_param_items(body)

    param = {
        "TableName": train_table_name,
        "Item": items,
        "Expected": {
            "id": {
                "Exists": False
            }
        }
    }

    dynamodb_client.put_item(**param)

    response.body = body

    return response.format()


def verify_body_data(body):
    """bodyのデータが妥当か検証する

    :param body: Request Body
    :type body: dict
    """

    verify_with_company_master_data(body["company"])


def verify_with_company_master_data(company):
    """会社名がマスタデータと一致しているか検証する

    :param company: [description]
    :type company: [type]
    """

    company_data = dynamodb_client.get_item(
        TableName=railway_company_table_name,
        Key={
            "name": {
                'S': company
            }
        }
    )
    item = company_data.get('Item', {})

    if len(item) == 0:
        raise ValueError


def generate_param_items(items):
    param_items = {}
    for k, v in items.items():
        data_type = convert_value_to_data_type(v)
        if data_type is not None:
            param_items[k] = data_type

    return param_items


def convert_value_to_data_type(value):
    value_type = type(value)
    value_str = str(value)

    if value_str == '':
        return None

    if value_type is str:
        return {'S': value_str}
    if value_type in (int, float):
        return {'N': value_str}
    if value_type is None:
        return {'NULL': 'True'}
