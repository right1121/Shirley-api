import json

import boto3

from api import responser

train_table_name = "depot"
railway_company_table_name = "railway_company"

dynamodb = boto3.resource('dynamodb')
depot_table = dynamodb.Table(train_table_name)
railway_company_table = dynamodb.Table(railway_company_table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        body["owner_id"] = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
        return main(body)
    except ValueError as e:
        print(f"ValueError error: {e}")
        return responser.validation_error()
    except Exception as e:
        print(f"Exception error: {e}")
        return responser.exception_error()


def main(body):
    response = responser()

    verify_body_data(body)

    key = {
        "owner_id": body.pop("owner_id"),
        "train_id": body.pop("train_id")
    }
    param_keys = [key for key in body.keys()]
    expression_assignment = map(lambda key: f"#{key} = :{key}", param_keys)
    update_expression = 'set ' + ','.join(expression_assignment)

    expression_attribute_names = {f"#{v}": v for v in body.keys()}

    expression_attributeValues = {f":{k}": v for k, v in body.items()}

    param = {
        "Key": key,
        'UpdateExpression': update_expression,
        'ExpressionAttributeNames': expression_attribute_names,
        'ExpressionAttributeValues': expression_attributeValues,
    }

    depot_table.update_item(**param)

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

    company_data = railway_company_table.get_item(
        TableName=railway_company_table_name,
        Key={"name": company}
    )
    item = company_data.get('Item', {})

    if len(item) == 0:
        raise ValueError
