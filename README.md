# Wechat-Enter 微信企业号Python-SDK
wechat-enter是一个微信企业号开发的Python SDK，可以大幅简化微信企业号后台开发，适用于Python3。
## 目前已经实现的功能：
<table>
<tbody>
<tr>
<td><p>分类</p></td>
<td><p>功能名称</p></td>
<td><p>是否实现</p></td>
</tr>
<tr>
<td rowspan=2><p>基础</p></td>
<td><p>主动调用</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td><p>回调模式</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td rowspan=3><p>认证接口</p></td>
<td><p>身份验证</p></td>
<td><p>Oauth验证</p></td>
</tr>
<tr>
<td><p>成员登录授权</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>单点登录授权</p></td>
<td><p></p></td>
</tr>
<tr>
<td rowspan=4><p>资源接口</p></td>
<td><p>管理企业号应用</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td><p>自定义菜单</p></td>
<td><p><br></p></td>
</tr>
<tr>
<td><p>管理通讯录</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td><p>管理素材文件</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td rowspan=7><p>能力接口</p></td>
<td><p>发消息</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td><p>接收消息与事件</p></td>
<td><p>是</p></td>
</tr>
<tr>
<td><p>微信JS-SDK接口</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>会话服务</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>客服服务</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>企业号微信支付</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>摇一摇周边</p></td>
<td><p></p></td>
</tr>
<tr>
<td rowspan=3><p>SAAS套件接口</p></td>
<td><p>第三方应用授权</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>通讯录权限体系</p></td>
<td><p></p></td>
</tr>
<tr>
<td><p>管理后台单点登录</p></td>
<td><p></p></td>
</tr>
</tbody>
</table>


## 使用前配置
	from wechat_enter import WechatConf
	corp_id = "wx1234567890”
	secrets = (“xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx”,)
	agent_dicts = [
	”agentid": 1, "token": “ttttttttt”, "encoding_aes_key": “eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee”},
	{“agentid": 2, "token": "ttttttttt", "encoding_aes_key": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee”},
	]
	
	wechat_conf = WechatConf(corp_id=corp_id, secrets= secrets, agent_dicts=agent_dicts)
	
其中：
`corp_id`是企业号全局性的标示符，在企业号设置-基本信息-账号信息中可以找到。  
`secrets`是企业号管理员账号的secrets，在设置-功能设置-权限管理中可以找到。使用前注意查看不同管理员的权限设置，不同管理员对通讯录和企业号应用的权限是不一样的。需要调用的管理员的secrets统一放到这个tuple中去。  
`agent_dicts`是企业号应用的信息，在应用中心-回调模式中可以找到。每个应用的信息包括`agentid`、`token`、`encoding_aes_key`三个参数，需要用到的应用信息组成一个tuple。  

## 调用
假设已经配置好了wechat_conf
### 
	from wechat_enter import Wechat  
	wechat = Wechat(wechat_conf)
### 回调URL验证
	text = wechat.url_validator.validate(msg_signature, timestamp, nonce, echostr)
	#再用最简单的HttpResponse返回这个text即可完成验证
### 获取通讯录用户列表
	user_list = wechat.users.list()
### 获取通讯录部门列表
	depart_list = wechat.departments.list()
### 发送文本消息
	body = {
	    "touser" : userid,
	    "text"   : {
  	        "content": content
	    },
	}
	wechat.message_sender.send_text(body)
### 接受消息和事件
	message=wechat.message_receiver.parse(msg_signature, timestamp, nonce, msg_body)
	if message.type == “text”:
		print(message.content)
	elif message.type == “Event” and message.EVENT == “Location”:
		print(message.Latitude, message.Longitude)

## Contribute
如果要新增功能，原则上需要引入WechatObejcts(这是一个发消息的基类)。  
继承这个基类之后，调用send函数即可。  
以获取自定义菜单列表为例，微信标准API是：  
https://qyapi.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN&agentid=AGENTID  
菜单类应该写为： 
### 
	class WechatMenu(WechatObjects):
	    def get(self, agentid):
		query_dict = {
		    "agentid":agentid
		}
	    return self.send("menu/get", query_dict = query_dict)

## To Do List
AccessToken持久化

		
