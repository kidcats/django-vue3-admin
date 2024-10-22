from Tools.Forescout import get_access_token

apiRootUrl = "https://10.148.1.29"
adminUsername = "apiread"
adminPassword = "*****************"

class Forescout:

    def __init__(self):
        self._apiRootUrl = apiRootUrl
        self._adminUsername = adminUsername
        self._adminPassword = adminPassword
        self._accessToken = self.getAccessToken(self._apiRootUrl, self._adminUsername, self._adminPassword)
        print(self._accessToken)

    def getAccessToken(self, apiRootUrl, adminUsername, adminPassword):
        getDate = get_access_token.getToken(apiRootUrl, adminUsername, adminPassword)
        if getDate is not None:
            self._accessToken = getDate['access_token']
            return self._accessToken
        else:
            self._accessToken = "accessToken获取失败"
            return self._accessToken

