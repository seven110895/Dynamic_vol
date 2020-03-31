from deribit_api import RestClient

deribitAccount = {'id':'IOeexwW4', 'secret': 'RxvnStzNuVLiF4TaffixbV9yo6sSyUBL5YGYmy5tGOo'}
deribitClient = RestClient(deribitAccount["id"], deribitAccount["secret"], url="https://test.deribit.com")

