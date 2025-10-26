import boto3
import json

def lambda_handler(event, context):
    print("EVENT:", event)

    # extraer body (soporta body como string JSON o dict)
    body = event.get('body') or {}
    if isinstance(body, str) and body:
        try:
            body = json.loads(body)
        except Exception:
            body = {}

    qs = event.get('queryStringParameters') or {}

    tenant_id = body.get('tenant_id') or event.get('tenant_id') or qs.get('tenant_id')
    alumno_id = body.get('alumno_id') or event.get('alumno_id') or qs.get('alumno_id')
    alumno_datos = body.get('alumno_datos') or event.get('alumno_datos') or qs.get('alumno_datos')

    if not tenant_id or not alumno_id or alumno_datos is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'tenant_id, alumno_id y alumno_datos requeridos'})
        }

    # si alumno_datos llega como string JSON, parsearlo
    if isinstance(alumno_datos, str):
        try:
            alumno_datos = json.loads(alumno_datos)
        except Exception:
            return {'statusCode':400, 'body': json.dumps({'error':'alumno_datos inválido'})}

    if not isinstance(alumno_datos, dict):
        return {'statusCode':400, 'body': json.dumps({'error':'alumno_datos debe ser un objeto (map)'})}

    # eliminar claves con valor None (DynamoDB no acepta None)
    alumno_datos_clean = {k: v for k, v in alumno_datos.items() if v is not None}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        resp = table.update_item(
            Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
            UpdateExpression="SET alumno_datos = :d",
            ExpressionAttributeValues={':d': alumno_datos_clean},
            ReturnValues="ALL_NEW"
        )
        return {'statusCode': 200, 'body': json.dumps({'updated': resp.get('Attributes')})}
    except Exception as e:
        print("ERROR:", str(e))
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
