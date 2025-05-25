import requests

def get_stocks_from_api():
    api_key = "g7G2WKYpinzfvmTME20vkg6UYjNxY_Sj"
    url = "https://api.polygon.io/v3/reference/dividends"

    try:
        response = requests.get(f"{url}?apiKey={api_key}")
        if response.status_code == 200:
            data = response.json()

            results = data.get('results', [])
            if not results:
                return {'success': False, 'message': 'No se encontraron resultados'}

            stocks = []
            for stock_data in results:
                stocks.append({
                    'name': stock_data.get('ticker'),
                    'price': stock_data.get('cash_amount'),
                    'currency': stock_data.get('currency', 'USD')
                })

            return {'success': True, 'stocks': stocks}

        else:
            return {'success': False, 'message': f'Error HTTP {response.status_code}'}

    except Exception as e:
        return {'success': False, 'message': f'Excepción: {str(e)}'}