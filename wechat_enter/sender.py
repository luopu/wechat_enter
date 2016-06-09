import requests
from urllib.parse import urljoin, quote
from os.path import split


# Sender Group
class BaseSender(object):
    @staticmethod
    def parse_response(response):
        try:
            dict_of_text = response.json()
        except Exception as e:
            return response
        else:
            if dict_of_text.get("errcode", 0) != 0:
                raise Exception(str(dict_of_text.get("errcode")) + ":" + dict_of_text.get("errmsg"))
            return dict_of_text

    def get(self, url, query_dict):
        response = requests.get(url, params=query_dict)
        return self.parse_response(response)

    def post(self, url, query_dict, body=None, file=None):
        if file:
            # file应该是filename和file的tuple
            response = requests.post(url, params=query_dict, files=file)
        elif body:
            if not isinstance(body, str):
                body = str(body)
            body = body.replace("'", '"')  # weixin要求只能用双引号,不能用单引号
            body = body.encode()
            response = requests.post(url, params=query_dict, data=body)
        return self.parse_response(response)

    def fetch(self, url, query_dict={}, body=None, file=None):
        if body or file:
            value = self.post(url, query_dict, body, file)
        else:
            value = self.get(url, query_dict)
        return value


class WechatObjects(object):
    sender = None
    wechat_conf = None
    access_token = None

    def __init__(self, weixin_conf):
        self.sender = BaseSender()
        self.wechat_conf = weixin_conf

    def attach_access_token(self, query_dict):
        query_dict.setdefault("access_token", self.wechat_conf.default_admin.access_token.value)
        return query_dict

    def cgi_url(self, subpath):
        cgi_url = urljoin(self.wechat_conf.wechat_base_url, "cgi-bin/")
        cgi_url = urljoin(cgi_url, subpath)
        return cgi_url

    def send(self, cmd, query_dict={}, body=None, file=None):
        url = self.cgi_url(subpath=self.common_subpath + cmd)
        query_dict = self.attach_access_token(query_dict)
        return self.sender.fetch(url=url, query_dict=query_dict, body=body, file=file)


class WechatMsgSender(WechatObjects):
    sender = None
    common_subpath = "message/"

    def __init__(self, wechat_conf):
        super().__init__(wechat_conf)

    def send(self, body: dict):
        body.setdefault('agentid', self.wechat_conf.default_agent.agentid)
        text = super().send(cmd="send", body=body)
        return text

    def send_text(self, body: dict):
        """
        body = {
            "touser" : "somebody",
            "toparty": "somedepartment",
            "totag"  : "sometag",
            "msgtype": "text",
            "agentid": "1",
            "text"   : {
                "content": "content"
            },
            "safe"   : 0
        }
        """

        body['msgtype'] = "text"
        self.send(body=body)

    def send_image(self):
        pass

    def send_voice(self):
        pass

    def send_video(self):
        pass

    def send_file(self):
        pass

    def send_news(self):
        pass

    def send_mpnews(self):
        pass


class WechatMedia(WechatObjects):
    common_subpath = ""

    # Media竟然有meida和material两个common_subpath,所以只能在函数中各自定义了

    def upload(self, media_type, filename: str):
        cmd = "media/upload"
        query_dict = {
            "type": media_type
        }

        media = {"media": (
            quote(split(filename)[-1]),
            open(filename, "rb")
        )}

        return self.send(cmd, query_dict, file=media).get('media_id')

    def get_temp(self, media_id):
        cmd = "media/get"
        query_dict = {
            "media_id": media_id
        }
        return self.send(cmd, query_dict)

    def add_material(self, media_type, agentid, filename: str):
        cmd = "material/add_material"
        query_dict = {
            "agentid": agentid,
            "type"   : media_type
        }

        media = {"media": (
            quote(split(filename)[-1]),
            open(filename, "rb")
        )}

        return self.send(cmd, query_dict, file=media).get("media_id")

    def add_mpnews(self, body):
        """
        mpnews_template = {
            "agentid":0,
            "mpnews":{
                   "articles":[
                    {
                       "title": "Title01",
                       "thumb_media_id": "2-G6nrLmr5EC3MMb_-zK1dDdzmd0p7cNliYu9V5w7o8K0",
                       "author": "zs",
                       "content_source_url": "",
                       "content": "Content001",
                       "digest": "airticle01",
                       "show_cover_pic": "0"
                      },
                     {
                       "title": "Title02",
                       "thumb_media_id": "2-G6nrLmr5EC3MMb_-zK1dDdzmd0p7",
                       "author": "Author001",
                       "content_source_url": "",
                       "content": "Content002",
                       "digest": "article02",
                       "show_cover_pic": "0"
                     },
                   //此处有多篇文章
                    ]
            },
        }
        """
        cmd = "material/add_mpnews"
        return self.send(cmd, body=body).get("media_id")

    def get_count(self, agentid):
        cmd = "material/get_count"
        query_dict = {
            "agentid": agentid
        }
        return self.send(cmd, query_dict)

    def batchget(self, body):
        """
        body_template{
           "type": "image",
           "agentid": 1,
           "offset": 0,
           "count": 10
        }"""
        cmd = "material/batchget"
        return self.send(cmd, body=body).get("itemlist")

    def get(self, media_id, agentid):
        cmd = "material/get"
        query_dict = {
            "media_id": media_id,
            "agentid" : agentid
        }
        response = self.send(cmd, query_dict)
        if isinstance(response, requests.Response):
            return response
        else:
            return response.get("mpnews")

    def delete(self, media_id, agentid):
        cmd = "material/del"
        query_dict = {
            "media_id": media_id,
            "agentid" : agentid
        }
        return self.send(cmd, query_dict)

    def update_mpnews(self, body):
        """
        body_template={
           "agentid":0,
           "media_id": "2MKloSBkGMNTs_kXxuBIzjZA_a9GdD66rdelZYAZVYhaMeBMImiDzlv84HOwy5wqsYZTXZcy_HVwJ3iZzPgIYNw",
           "mpnews": {
               "articles": [
                   {
                       "title": "Title01",
                       "thumb_media_id": "2CQQkmXPbHWxZnyLG3Y3ZgSnafR040HI45myZ6dTGvAhchyAEg5dHKYfnLXn5-2ngCrYUggL32vt_tfCUjHlsLA",
                       "author": "zs",
                       "content_source_url": "",
                       "content": "Content001",
                       "digest": "airticle01",
                       "show_cover_pic": "0"
                   },
                   {
                       "title": "Title02",
                       "thumb_media_id": "2CQQkmXPbHWxZnyLG3Y3ZgSnafR040HI45myZ6dTGvAhchyAEg5dHKYfnLXn5-2ngCrYUggL32vt_tfCUjHlsLA",
                       "author": "Author001",
                       "content_source_url": "",
                       "content": "UpdateContent002",
                       "digest": "Updatearticle02",
                       "show_cover_pic": "0"
                   }
               ]
           }
        }"""
        cmd = "material/update_mpnews"
        return self.send(cmd, body=body)

    def uploadimg(self, filename):
        cmd = "media/uploadimg"
        media = {"media": (
            quote(split(filename)[-1]),
            open(filename, "rb")
        )}

        return self.send(cmd, file=media).get('url')


class WechatUsers(WechatObjects):
    common_subpath = "user/"
    sender = None

    def create(self, body):
        """
        body = {
            "userid"        : "zhangsan",
            "name"          : "李四",
            "department"    : [1],
            "position"      : "后台工程师",
            "mobile"        : "15913215421",
            "gender"        : "1",
            "email"         : "zhangsan@gzdev.com",
            "weixinid"      : "lisifordev",
            "enable"        : 1,
            "avatar_mediaid": "2-G6nrLmr5EC3MNb_-zL1dDdzkd0p7cNliYu9V5w7o8K0",
            "extattr"       : {"attrs": [{"name": "爱好", "value": "旅游"}, {"name": "卡号", "value": "1234567234"}]}
        }
        """

        cmd = "create"
        return self.send(cmd, body=body)

    def update(self, body):
        """
        body = {
            "userid"        : "zhangsan",
            "name"          : "李四",
            "department"    : [1],
            "position"      : "后台工程师",
            "mobile"        : "15913215421",
            "gender"        : "1",
            "email"         : "zhangsan@gzdev.com",
            "weixinid"      : "lisifordev",
            "enable"        : 1,
            "avatar_mediaid": "2-G6nrLmr5EC3MNb_-zL1dDdzkd0p7cNliYu9V5w7o8K0",
            "extattr"       : {"attrs": [{"name": "爱好", "value": "旅游"}, {"name": "卡号", "value": "1234567234"}]}
        }
        """

        cmd = "update"
        return self.send(cmd, body=body)

    def delete(self, userid):
        cmd = "delete"
        query_dict = {
            "userid": userid
        }
        return self.send(cmd, query_dict)

    def batch_delete(self, useridlist):
        cmd = "batchdelete"
        body = {
            "useridlist": useridlist
        }
        return self.send(cmd, body=body)

    def get(self, userid):
        cmd = "get"
        query_dict = {
            "userid": userid
        }

        return self.send(cmd, query_dict)

    def simple_list(self, department_id=1, fetch_child=1, status=0):
        cmd = "simplelist"
        query_dict = {
            "department_id": department_id,
            "fetch_child"  : fetch_child,
            "status"       : status
        }

        return self.send(cmd, query_dict).get("userlist")

    def list(self, department_id=1, fetch_child=1, status=0):
        cmd = "list"
        query_dict = {
            "department_id": department_id,
            "fetch_child"  : fetch_child,
            "status"       : status
        }

        return self.send(cmd, query_dict).get("userlist")

    def query_by_code(self, code):
        # OAuth会用到这个功能
        cmd = "getuserinfo"
        query_dict = {
            "code": code
        }
        return self.send(cmd, query_dict)


class WechatDepartments(WechatObjects):
    common_subpath = "department/"
    sender = None
    __list = None

    def create(self, body: dict):
        """
        body = {
            "name"        : "zhangsan",
            "parentid"    : "李四",
            "order"       : [1],
            "id"          : "后台工程师",
        }
        """

        cmd = "create"
        body.setdefault("parentid", 1)
        return self.send(cmd, body=body)

    def update(self, body):
        """
        body = {
            "name"    : "zhangsan",
            "parentid": "李四",
            "order"   : [1],
            "id"      : "后台工程师",
        }
        """

        cmd = "update"
        return self.send(cmd, body=body)

    def delete(self, id):
        cmd = "delete"
        query_dict = {
            "id": id
        }
        return self.send(cmd, query_dict)

    def list(self, id="", refresh=False):
        if self.__list is None or refresh:
            cmd = "list"
            query_dict = {
                "id": id
            }
            self.__list = self.send(cmd, query_dict).get("department")
        return self.__list


class WechatAgents(WechatObjects):
    common_subpath = "agent/"
    sender = None
    __list = None

    def set(self, body):
        """
        body = {
            "agentid"               : "",
            "report_location_flag"  : "0",
            "logo_mediaid"          : "xxx",
            "name"                  : "NAME",
            "description"           : "DESC",
            "redirect_domain"       : "http://xxx",
            "isreportuser"          : "0",
            "isreportenter"         : "0",
            "home_url"              : "http://xxx",
        }
        """

        cmd = "set"
        return self.send(cmd, body=body)

    def get(self, agent_id):
        cmd = "get"
        query_dict = {
            "agentid": agent_id
        }
        return self.send(cmd, query_dict)

    def list(self, refresh=False):
        if self.__list is None or refresh:
            cmd = "list"
            agent_dict = self.send(cmd)
            self.__list = agent_dict.get("agentlist")
        return self.__list
