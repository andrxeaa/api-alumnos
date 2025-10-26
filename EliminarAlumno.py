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

    if not tenant_id or not alumno_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'tenant_id y alumno_id requeridos'})
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        # ReturnValues='ALL_OLD' devuelve el item borrado si existía
        resp = table.delete_item(
            Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
            ReturnValues='ALL_OLD'
        )
        deleted = resp.get('Attributes')
        if not deleted:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Alumno no encontrado'})
            }
        return {
            'statusCode': 200,
            'body': json.dumps({'deleted': deleted})
        }
    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
