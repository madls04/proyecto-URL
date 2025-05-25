from app.AWSConnections import AWSConnections
from app.api import get_stocks_from_api
from decimal import Decimal
import sys

aws = AWSConnections()

def saveUserDynamoDB(session, user):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.put_item(Item=user)
    return response

print("Bienvenido")

while True:
    print("\n1. Crear cuenta")
    print("2. Iniciar sesión")
    print("3. Salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        print("\n--- Crear cuenta ---")
        nombre = input("Nombre: ")
        email = input("Email: ")
        password = input("Contraseña: ")
        capital = 1000

        resultado_login = aws.login(email, password)
        if resultado_login["success"]:
            print("El usuario ya existe.")
            input("Presiona ENTER para continuar")
        else:
            aws.crear_usuario(nombre, email, password, Decimal(str(capital)))
            print("Cuenta creada con éxito.")
            input("Presiona ENTER para continuar")

    elif opcion == "2":
        print("\n--- Iniciar sesión ---")
        email = input("Email: ")
        password = input("Contraseña: ")
        result = aws.login(email, password)

        if result["success"]:
            usuario = result["user"]
            print(f"Bienvenido, {usuario['name']}")
            input("Presiona ENTER para continuar")

            while True:
                print("\n--- Menú Principal ---")
                print("1. Comprar stock")
                print("2. Consultar portafolio")
                print("3. Salir")
                opcion2 = input("Elige una opción: ")

                if opcion2 == "1":
                    print("\n--- Comprar Stock ---")
                    stocks_data = get_stocks_from_api()
                    if not stocks_data["success"]:
                        print(stocks_data["message"])
                        input("Presiona ENTER para continuar")
                        continue
                    stocks = stocks_data["stocks"]

                    for i, stock in enumerate(stocks):
                        print(f"{i + 1}. {stock['name']} - ${stock['price']}")

                    eleccion = input("Escribe el número del stock que deseas comprar o 'salir': ")
                    if eleccion.lower() == "salir":
                        continue

                    try:
                        idx = int(eleccion) - 1
                        if idx < 0 or idx >= len(stocks):
                            raise ValueError

                        stock_elegido = stocks[idx]
                        cantidad = int(input(f"¿Cuántas acciones de {stock_elegido['name']} deseas comprar?: "))
                        precio_decimal = Decimal(str(stock_elegido["price"]))
                        total = precio_decimal * cantidad

                        confirmar = input(f"Total a pagar: ${total:.2f}. ¿Deseas continuar? (si/no): ").lower()
                        if confirmar != "si":
                            print("Compra cancelada.")
                            input("Presiona ENTER para continuar")
                            continue

                        stock_para_guardar = {
                            "name": stock_elegido["name"],
                            "price": precio_decimal
                        }

                        for _ in range(cantidad):
                            resultado = aws.agregar_inversion(email, stock_para_guardar)
                            if not resultado["success"]:
                                print(resultado["message"])
                                break
                        else:
                            print("Compra realizada con éxito.")

                        input("Presiona ENTER para continuar")
                    except Exception as e:
                        print("Entrada inválida.")
                        input("Presiona ENTER para continuar")

                elif opcion2 == "2":
                    print("\n--- Portafolio ---")
                    usuario_actualizado = aws.login(email, password)["user"]
                    portfolio = usuario_actualizado.get("portfolio", [])
                    capital = Decimal(str(usuario_actualizado.get("capital", 0)))
                    total_invertido = sum(Decimal(str(stock["price"])) for stock in portfolio)
                    saldo_restante = capital - total_invertido

                    if not portfolio:
                        print("No tienes acciones.")
                    else:
                        resumen = {}
                        for accion in portfolio:
                            ticker = accion["name"]
                            if ticker not in resumen:
                                resumen[ticker] = {"price": Decimal(str(accion["price"])), "cantidad": 0}
                            resumen[ticker]["cantidad"] += 1

                        for nombre, datos in resumen.items():
                            print(f"{nombre} - ${datos['price']} x {datos['cantidad']} acciones")

                    print(f"\nSaldo restante: ${saldo_restante:.2f}")
                    input("Presiona ENTER para continuar")

                elif opcion2 == "3":
                    print("Sesión cerrada.")
                    break
                else:
                    print("Opción inválida.")
                    input("Presiona ENTER para continuar")

        else:
            print(result["message"])
            input("Presiona ENTER para continuar")

    elif opcion == "3":
        print("Saliendo del programa.")
        break
    else:
        print("Opción inválida.")
        input("Presiona ENTER para continuar")