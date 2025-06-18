from urllib.parse import urlencode

class RequestParams:
    def __init__(self, username="${username}", password="${password}"):
        self.username = username
        self.password = password
        self.base_params = {
            "loginType": "",
            "auth_type": "0",
            "loginType": "",
            "auth_type": "0",
            "isBindMac1": "0",
            "listbindmac": "0",
            "recordmac": "0",
            "isRemind": "",
            "loginTimes": "",
            "groupId": "",
            "distoken": "",
            "echostr": "",
            "url": "",
            "isautoauth": "",
            "userId": self.username,
            "passwd": self.password
        }
    
    def get_pc(self):
        params = {
            **self.base_params,
            "hostIp": "http://127.0.0.1:8083",
            "pageid": "1",
            "templatetype": "1",
            "isRemind": "1",
            "notice_pic_loop1": "/portal/uploads/pc/demo3/images/logo.jpg",
            "notice_pic_loop2": "/portal/uploads/pc/demo3/images/rrs_bg.jpg"
        }
        return urlencode(params, doseq=True)
    
    def get_mobile(self):
        params = {
            **self.base_params,
            "hostIp": "http://127.0.0.1:8080",
            "pageid": "2",
            "templatetype": "2",
            "isRemind": "0",
            "notice_pic_loop1": "/portal/uploads/mobile/demo3/images/logo.jpg"
        }
        return urlencode(params, doseq=True)