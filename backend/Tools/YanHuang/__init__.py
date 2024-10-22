from Tools.YanHuang import auth, search

apiRootUrl = "http://10.148.33.50:30080/api"
adminUsername = "admin"
adminPassword = "**************"

class Auth:
    def __init__(self):
        self._apiRootUrl = apiRootUrl
        self._adminUsername = adminUsername
        self._adminPassword = adminPassword
        self._accessToken, self._refreshToken = self.login(self._apiRootUrl, self._adminUsername, self._adminPassword)
        print(self._accessToken)

    def login(self, apiRootUrl, adminUsername, adminPassword):
        getDate = auth.login(apiRootUrl, adminUsername, adminPassword)
        if getDate is not None:
            self._accessToken = getDate['accessToken']
            self._refreshToken = getDate['refreshToken']
            return self._accessToken, self._refreshToken
        else:
            self._accessToken = "accessToken获取失败"
            self._refreshToken = "refreshToken获取失败"
            return self._accessToken, self._refreshToken


class Search:
    def __init__(self):
        self._accessToken, self._refreshToken = Auth.login(self=Auth(), apiRootUrl=apiRootUrl, adminUsername=adminUsername, adminPassword=adminPassword)
        # print(self._accessToken)

    def commands(self, searchCommands):
        searchDate = search.commands(apiRootUrl, self._accessToken, searchCommands)
        if searchDate is not None:
            self._searchDate = searchDate
            return self._searchDate
        else:
            self._searchDate = "搜索失败"
            return self._searchDate



