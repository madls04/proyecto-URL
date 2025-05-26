from app.AWSConnections import AWSConnections
from app.api import get_stocks_from_api
from decimal import Decimal
import sys

aws = AWSConnections()

def save_user_dynamodb(session, user):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.put_item(Item=user)
    return response

print("Bienvenido")

while True:
    print("\n1. Crear cuenta")
    print("2. Iniciar sesión")
    print("3. Salir")
    option = input("Elige una opción: ")

    if option == "1":
        print("\n--- Crear cuenta ---")
        name = input("Nombre: ")
        email = input("Email: ")
        password = input("Contraseña: ")
        balance = 1000

        login_result = aws.login(email, password)
        if login_result["success"]:
            print("El usuario ya existe.")
            input("Presiona ENTER para continuar")
        else:
            aws.create_user(name, email, password, Decimal(str(balance)))
            print("Cuenta creada con éxito.")
            input("Presiona ENTER para continuar")

    elif option == "2":
        print("\n--- Iniciar sesión ---")
        email = input("Email: ")
        password = input("Contraseña: ")
        result = aws.login(email, password)

        if result["success"]:
            user = result["user"]
            print(f"Bienvenido, {user['name']}")
            input("Presiona ENTER para continuar")

            while True:
                print("\n--- Menú Principal ---")
                print("1. Comprar stock")
                print("2. Consultar portafolio")
                print("3. Salir")
                option2 = input("Elige una opción: ")

                if option2 == "1":
                    print("\n--- Comprar Stock ---")
                    stocks_data = get_stocks_from_api()
                    if not stocks_data["success"]:
                        print(stocks_data["message"])
                        input("Presiona ENTER para continuar")
                        continue
                    stocks = stocks_data["stocks"]

                    for i, stock in enumerate(stocks):
                        print(f"{i + 1}. {stock['name']} - ${stock['price']}")

                    choice = input("Escribe el número del stock que deseas comprar o 'salir': ")
                    if choice.lower() == "salir":
                        continue

                    try:
                        idx = int(choice) - 1
                        if idx < 0 or idx >= len(stocks):
                            raise ValueError

                        selected_stock = stocks[idx]
                        quantity = int(input(f"¿Cuántas acciones de {selected_stock['name']} deseas comprar?: "))
                        price_decimal = Decimal(str(selected_stock["price"]))
                        total = price_decimal * quantity

                        confirm = input(f"Total a pagar: ${total:.2f}. ¿Deseas continuar? (si/no): ").lower()
                        if confirm != "si":
                            print("Compra cancelada.")
                            input("Presiona ENTER para continuar")
                            continue

                        stock_to_save = {
                            "name": selected_stock["name"],
                            "price": price_decimal
                        }

                        for _ in range(quantity):
                            result = aws.add_investment(email, stock_to_save)
                            if not result["success"]:
                                print(result["message"])
                                break
                        else:
                            print("Compra realizada con éxito.")

                        input("Presiona ENTER para continuar")
                    except Exception as e:
                        print("Entrada inválida.")
                        input("Presiona ENTER para continuar")

                elif option2 == "2":
                    print("\n--- Portafolio ---")
                    updated_user = aws.login(email, password)["user"]
                    investments = updated_user.get("investments", [])
                    balance = Decimal(str(updated_user.get("balance", 0)))
                    total_invested = sum(Decimal(str(stock["price"])) for stock in investments)
                    remaining_balance = balance - total_invested

                    if not investments:
                        print("No tienes acciones.")
                    else:
                        summary = {}
                        for stock in investments:
                            ticker = stock["name"]
                            if ticker not in summary:
                                summary[ticker] = {"price": Decimal(str(stock["price"])), "quantity": 0}
                            summary[ticker]["quantity"] += 1

                        for name, data in summary.items():
                            print(f"{name} - ${data['price']} x {data['quantity']} acciones")

                    print(f"\nSaldo restante: ${remaining_balance:.2f}")
                    input("Presiona ENTER para continuar")

                elif option2 == "3":
                    print("Sesión cerrada.")
                    break
                else:
                    print("Opción inválida.")
                    input("Presiona ENTER para continuar")

        else:
            print(result["message"])
            input("Presiona ENTER para continuar")

    elif option == "3":
        print("Saliendo del programa.")
        break
    else:
        print("Opción inválida.")
        input("Presiona ENTER para continuar")
