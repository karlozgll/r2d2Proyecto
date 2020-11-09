
import ipinfo 

class Ipinfo:
    def __init__(self):
        self.access_token = '06d7e4f581ad6c'
        self.handler=ipinfo.getHandler(self.access_token)

    def ip_scraping(self,ip_address=""):
        print("iniciando con:"+ ip_address)
        details = self.handler.getDetails(ip_address)
        print("detalles:")
        print(details)
        return (details.all)



