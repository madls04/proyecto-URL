import boto3
import botocore
from botocore.config import Config
from botocore.session import Session
import bcrypt
import os
from dotenv import load_dotenv

class AWSConnections:
    # Conexión global a DynamoDB
    def __init__(self):
        load_dotenv()
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('REGION')
        
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        self.table = self.dynamodb.Table('Users')

    def create_user(self, name, email, plain_password, balance):
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

        item = {
            'email': email,
            'name': name,
            'password': hashed_password.decode('utf-8'),
            'balance': balance,
            'investments': []
        }

        response = self.table.put_item(Item=item)
        return response

    def login(self, email, password):
        try:
            response = self.table.get_item(Key={'email': email})
            user = response.get('Item')

            if not user:
                return {'success': False, 'message': 'Usuario no encontrado'}

            stored_hash = user.get('password')
            if not stored_hash:
                return {'success': False, 'message': 'Contraseña no establecida'}

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                user.pop('password', None)  # Ocultar la contraseña
                return {'success': True, 'message': 'Inicio de sesión exitoso', 'user': user}
            else:
                return {'success': False, 'message': 'Contraseña incorrecta'}

        except Exception as e:
            return {'success': False, 'message': f'Error en el inicio de sesión: {str(e)}'}

    def add_investment(self, email, new_investment):
        try:
            response = self.table.get_item(Key={'email': email})
            user = response.get('Item')

            if not user:
                return {'success': False, 'message': 'Usuario no encontrado'}

            balance = user.get('balance', 0)
            investments = user.get('investments', [])

            current_total = sum(stock.get('price', 0) for stock in investments)
            new_total = current_total + new_investment['price']

            if new_total > balance:
                return {
                    'success': False,
                    'message': f"No hay suficiente saldo. Saldo: {balance}, Inversión total: {new_total}"
                }

            investments.append(new_investment)

            self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET investments = :new_investments',
                ExpressionAttributeValues={':new_investments': investments}
            )

            return {
                'success': True,
                'message': 'Inversión agregada con éxito',
                'investments': investments
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al agregar inversión: {str(e)}'}
