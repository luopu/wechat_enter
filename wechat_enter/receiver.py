from .WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.ElementTree as et


# Receiver Group
class MessageBody(object):
    def __getattr__(self, item):
        return None

    def __str__(self):
        text = ""
        for key, value in self.__dict__.items():
            text += "%s:%s\n" % (key, value)
        return text

    def is_event(self):
        if "Event" in self.__dict__:
            return self.Event
        else:
            return False


class WechatURLValidator(object):
    wechat_conf = None
    msg_signature = None
    timestamp = None
    nonce = None

    def __init__(self, wechat_conf):
        self.wechat_conf = wechat_conf

    def validate(self, msg_signature, timestamp, nonce, echostr):
        for agent in self.wechat_conf.agents:
            token = agent["token"]
            encoding_aes_key = agent["encoding_aes_key"]
            wx = WXBizMsgCrypt(token, encoding_aes_key, self.wechat_conf.corp_id)
            ret, text = wx.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if ret == 0:
                return text.decode()

        raise Exception("URL validating require matchs none agent.")


class WechatMessageReceiver(object):
    wechat_conf = None
    msg_signature = None
    timestamp = None
    nonce = None
    msg_body = None
    message = None

    def __init__(self, wechat_conf):
        self.wechat_conf = wechat_conf
        self.message = MessageBody()

    def parse(self, msg_signature, timestamp, nonce, msg_body, agentid=None):
        self.msg_signature = msg_signature
        self.timestamp = timestamp
        self.nonce = nonce
        self.msg_body = msg_body
        agents = self.wechat_conf.agents

        for agent in agents:
            token = agent.token
            encoding_aes_key = agent.encoding_aes_key
            wx = WXBizMsgCrypt(token, encoding_aes_key, self.wechat_conf.corp_id)
            ret, xml_content = wx.DecryptMsg(self.msg_body, self.msg_signature, self.timestamp, self.nonce)
            if ret == 0:
                root = et.fromstring(xml_content.decode())
                for node in root:
                    self.message.__setattr__(node.tag, node.text)
                return self.message

        raise Exception(
            "Weixin message parse Error. None of agents decrypt this message. Signature=%s, timestamp=%s, nonce=%s, body=%s" \
            % (self.msg_signature, self.timestamp, self.nonce, self.msg_body))
