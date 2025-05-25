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
        awss_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('REGION')
        
        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key, aws_secret_access_key = awss_secret_key,region_name='us-east-1')
        self.tabla = self.dynamodb.Table('Users')


    def crear_usuario(self, name, email, plain_password, capital):
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

        item = {
            'email': email,
            'name': name,
            'password': hashed_password.decode('utf-8'),
            'capital': capital,
            'portfolio': []
        }

        response = self.tabla.put_item(Item=item)
        return response


    def login(self, email, password):
        try:
            response = self.tabla.get_item(Key={'email': email})
            usuario = response.get('Item')

            if not usuario:
                return {'success': False, 'message': 'Usuario no encontrado'}

            stored_hash = usuario.get('password')
            if not stored_hash:
                return {'success': False, 'message': 'Contraseña no establecida'}

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Opcional: ocultar contraseña del resultado
                usuario.pop('password', None)
                return {'success': True, 'message': 'Login exitoso', 'user': usuario}
            else:
                return {'success': False, 'message': 'Contraseña incorrecta'}

        except Exception as e:
            return {'success': False, 'message': str(e)}


    def agregar_inversion(self, email, nueva_inversion):
        try:
            response = self.tabla.get_item(Key={'email': email})
            user = response.get('Item')

            if not user:
                return {'success': False, 'message': 'Usuario no encontrado'}

            capital = user.get('capital', 0)
            portfolio = user.get('portfolio', [])

            total_actual = sum(stock.get('price', 0) for stock in portfolio)
            nuevo_total = total_actual + nueva_inversion['price']

            if nuevo_total > capital:
                return {
                    'success': False,
                    'message': f"No hay suficiente capital. Capital: {capital}, Inversión total: {nuevo_total}"
                }

            portfolio.append(nueva_inversion)

            self.tabla.update_item(
                Key={'email': email},
                UpdateExpression='SET portfolio = :nuevo_portfolio',
                ExpressionAttributeValues={':nuevo_portfolio': portfolio}
            )

            return {'success': True, 'message': 'Inversión agregada con éxito', 'portfolio': portfolio}

        except Exception as e:
            return { 'success': False, 'message': str(e)}