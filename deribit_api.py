import openapi_client
from openapi_client import configuration
from openapi_client import api_client

class Deribit_Trade:
    def __init__(self, cliend_id, cliend_secret, host = "https://test.deribit.com/api/v2"):
        self.host = host
        self.id = cliend_id
        self.secret = cliend_secret

    def athentication_account(self):
        # account authentication in testnet
        conf = configuration.Configuration( host=self.host)
        client = api_client.ApiClient(conf)
        publicApi = openapi_client.api.public_api.PublicApi(client)
        # Authenticate with API credentials
        response = publicApi.public_auth_get('client_credentials', '', '', self.id, self.secret, '', '', '')
        access_token = response['result']['access_token']
        conf_authed = configuration.Configuration( host=self.host)
        conf_authed.access_token = access_token
        # Use retrieved authentication token to setup private endpoint client
        client_authed = api_client.ApiClient(conf_authed)
        return client_authed



cliend = Deribit_Trade("IOeexwW4", "RxvnStzNuVLiF4TaffixbV9yo6sSyUBL5YGYmy5tGOo")
client_authed = cliend.athentication_account()

# buy order
api_instance = openapi_client.PrivateApi(client_authed)
instrument_name = 'BTC-24APR20-6500-C' # str | Instrument name
amount = 1
type = 'limit'
price = 0.064

#max_show = 0
post_only = False
reduce_only = False # bool | If `true`, the order is considered reduce-only which is intended to only reduce a current position (optional) (default to False)
try:
    # Places a buy order for an instrument.
    api_response = api_instance.private_sell_get(instrument_name, amount, type=type, price= price)
    print(api_response)
except openapi_client.ApiException as e:
    print("Exception when calling PrivateApi->private_buy_get: %s\n" % e)

# close position
api_instance = openapi_client.PrivateApi(client_authed)
instrument_name = 'BTC-25SEP20-11000-C'
type = 'market'
try:
    # Makes closing position reduce only order .
    api_response = api_instance.private_close_position_get(instrument_name, type)
    print(api_response)
except openapi_client.ApiException as e:
    print("Exception when calling PrivateApi->private_close_position_get: %s\n" % e)