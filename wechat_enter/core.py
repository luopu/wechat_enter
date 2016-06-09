from .oauth import WechatOAuth
from .receiver import WechatMessageReceiver, WechatURLValidator
from .sender import WechatAgents, WechatDepartments, WechatMedia, WechatMsgSender, WechatUsers


class Wechat(object):
    agents = None
    users = None
    departments = None
    oauth = None
    message_sender = None
    media = None
    sender = None

    def __init__(self, wechat_conf):
        self.wechat_conf = wechat_conf

        self.agents = WechatAgents(self.wechat_conf)
        self.users = WechatUsers(self.wechat_conf)
        self.departments = WechatDepartments(self.wechat_conf)
        self.oauth = WechatOAuth(self.wechat_conf)
        self.message_sender = WechatMsgSender(self.wechat_conf)
        self.media = WechatMedia(self.wechat_conf)
        self.message_receiver = WechatMessageReceiver(self.wechat_conf)
        self.url_validator = WechatURLValidator(self.wechat_conf)
