from urllib.parse import urlencode, urlunsplit, SplitResult


class WechatOAuth(object):
    sender = None

    def __init__(self, wechat_conf):
        self.wechat_conf = wechat_conf

    def redirect_uri(self, redirect_url):
        query_string = urlencode({
            "appid"        : self.wechat_conf.corp_id,
            "redirect_uri" : redirect_url,
            "response_type": "code",
            "scope"        : "SCOPE",
            "state"        : "STATE"
        })

        url = urlunsplit(SplitResult(
            "https",
            "open.weixin.qq.com",
            "connect/oauth2/authorize",
            query_string,
            "wechat_redirect"
        ))
        return url
