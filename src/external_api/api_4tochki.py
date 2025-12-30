from zeep import Client, helpers

wsdl_url = "http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl"
API_LOGIN = 'autosnab54'
API_PASSWORD = '33754beN'
client = Client(wsdl=wsdl_url)
codes = ['AB6011U']


r = client.service.GetGoodsInfo(login=API_LOGIN, password=API_PASSWORD, code_list=codes)
result = helpers.serialize_object(r)
titles = {tire.get("code"): tire.get("name") for tire in result.get("tyreList").get("TyreContainer")}
print(titles)
