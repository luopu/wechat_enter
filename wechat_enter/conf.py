# Base Group
from collections import namedtuple
from datetime import datetime, timedelta
from urllib.parse import urljoin
from .sender import BaseSender


class AccessToken(object):
    wechat_conf = None
    pickel_key = "access_token"
    __value = None
    __expires_at = None
    __start_time = None
    pickle = None

    def __init__(self, wechat_conf, secret):
        self.wechat_conf = wechat_conf
        self.secret = secret

    @property
    def value(self):
        try:
            if not self.__value:
                if self.pickle and (not self.expired):
                    self.__value, self.expires_in = self.pickle.read(self.pickel_key)
                else:
                    self.fetch()
        except Exception as e:
            print(e.args)
        finally:
            return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def expired(self):
        return (self.__expires_at is None) or (datetime.now() >= self.__expires_at)

    @property
    def expires_in(self):
        time_delta = self.__expires_at - datetime.now()
        return time_delta.seconds

    @expires_in.setter
    def expires_in(self, expires_in):
        self.__expires_at = datetime.now() + timedelta(seconds=expires_in)

    def query_dict(self):
        query_dict = {
            "corpid"    : self.wechat_conf.corp_id,
            "corpsecret": self.secret
        }
        return query_dict

    def url(self):
        return urljoin(self.wechat_conf.wechat_base_url, "cgi-bin/gettoken")

    def fetch(self):
        sender = BaseSender()
        url = self.url()
        query_dict = self.query_dict()
        dict_of_text = sender.fetch(url=url, query_dict=query_dict)

        self.__start_time = datetime.now()
        self.value = dict_of_text.get("access_token")
        self.expires_in = dict_of_text.get("expires_in")
        try:
            self.pickle.store(name="access_token", context=self.value, expire=self.expires_in)
        finally:
            return self.value


class WeixinAdmin(object):
    secret = None
    __access_token = None

    def __init__(self, wechat_conf, secret):
        self.wechat_conf = wechat_conf
        self.secret = secret

    @property
    def access_token(self):
        if not self.__access_token:
            self.__access_token = AccessToken(self.wechat_conf, self.secret)
        return self.__access_token


Agent = namedtuple('Agent', ['agentid', 'token', "encoding_aes_key"])


class WechatConf(object):
    corp_id = None
    wechat_base_url = None
    admins = []
    agents = []
    default_admin = None
    default_agent = None

    def __init__(self, corp_id, secrets, agent_dicts, wechat_base_url = "https://qyapi.weixin.qq.com/"):
        """
        :param corp_id
        企业号唯一id

        :param secrets
        所有管理员账户的secret的列表
        SECRETS = (sec1, sec2...)


        :param agent_dicts
        所有应用的列表,每个item应当是agentid, token和encoding_aes_key的dict
        agent_dicts = [{"agentid": 1, "token": token, "encoding_aes_key": encoding_aes_key},...]

        """
        for agent in agent_dicts:
            self.agents.append(Agent(**agent))
        self.wechat_base_url = wechat_base_url
        self.corp_id = corp_id
        for secret in secrets:
            self.admins.append(WeixinAdmin(self, secret))
        self.default_admin = self.admins[0]
        self.default_agent = self.agents[0]
