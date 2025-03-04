import os
import json
import time
import base64
import asyncio
import string
#import pysilk
import qrcode
import aiohttp
import threading
import subprocess
from random import choice
from io import BytesIO
from pathlib import Path
from typing import Union
from loguru import logger
from pydub import AudioSegment
from pymediainfo import MediaInfo
from aiohttp.helpers import sentinel

class MarshallingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UnmarshallingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MMTLSError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PacketError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ParsePacketError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DatabaseError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class LoginError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UserLoggedOut(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class BanProtection(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Client:
    def __init__(self,opt:str=None,handler=None):
        self.config = {"id": "wxid_xxxxxx", "devicename": "", "deviceid": "","host":"192.168.1.2","port":"9000","time":100}
        self.optfile = "./config.json"
        self.host = "192.168.1.2"
        self.port = "9000"
        self.id = None
        self.name = None
        self.nickname = None
        self.alias = None
        self.phone = None
        self.deviceid = None
        self.devicename = None
        self.time = 0
        self.delay = 0.5
        self.executable_path = "./XYWechatPad"
        self.handler=handler
        self.starttime=time.time()
        self.target=None
        self.thread=None
        self.core = None
        self.logthread = None
        self.errthread = None
        self.run = False
        self.state=0

        self.loadopt(opt)
    
    async def cls(self):
        self.logout()
        self.id = None
        self.name = None
        self.nickname = None
        self.alias = None
        self.phone = None
        self.deviceid = None
        self.devicename = None
        self.time = 0
        self.saveopt(self.optfile)
    
    def saveopt(self,optfile):
        self.optfile = optfile
        self.config["time"] = self.time
        self.config["id"] = self.id 
        self.config["name"] = self.name
        self.config["nickname"] = self.nickname
        self.config["alias"] = self.alias
        self.config["phone"] = self.phone
        self.config["deviceid"] = self.deviceid
        self.config["devicename"] = self.devicename
        with open(optfile, "w") as file:
            self.config = json.dump(self.config,file)
        
    def loadopt(self,optfile:str = None):
        if optfile!=None:
            self.optfile = optfile
            with open(optfile, "r") as file:
                self.config = json.load(file)

        self.host = self.config.get("host","127.0.0.1")
        self.port = self.config.get("port","9000")
        self.id = self.config.get("id",None)
        self.name = self.config.get("name",None)
        self.nickname = self.config.get("nickname",None)
        self.alias = self.config.get("alias",None)
        self.phone = self.config.get("bindmobile",None)
        self.time = self.config.get("time",0)
        self.delay = self.config.get("delay",0.5)
        self.executable_path = self.config.get("core","./XYWechatPad")
        self.deviceid = self.config.get("deviceid",Client.createid())
        self.devicename = self.config.get("devicename",Client.createname())

    @staticmethod
    def createid(text=""):
        if text == "" or text == "string":
            text = ''.join(choice(string.ascii_letters) for _ in range(15))
        return text

    @staticmethod
    def createname():
        first_names = [
            "Oliver", "Emma", "Liam", "Ava", "Noah", "Sophia", "Elijah", "Isabella",
            "James", "Mia", "William", "Amelia", "Benjamin", "Harper", "Lucas", "Evelyn",
            "Henry", "Abigail", "Alexander", "Ella", "Jackson", "Scarlett", "Sebastian",
            "Grace", "Aiden", "Chloe", "Matthew", "Zoey", "Samuel", "Lily", "David",
            "Aria", "Joseph", "Riley", "Carter", "Nora", "Owen", "Luna", "Daniel",
            "Sofia", "Gabriel", "Ellie", "Matthew", "Avery", "Isaac", "Mila", "Leo",
            "Julian", "Layla"
        ]

        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
            "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
            "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans"
        ]
        return choice(first_names) + " " + choice(last_names) + "'s Pad"

    def valide(self):
        return self.state==3
    
    def output(self,text:str):
        print(text)

    def e_handler(self,msg):
        code = msg.get("Code")
        if code == -1:  # 参数错误
            raise ValueError(msg.get("Message"))
        elif code == -2:  # 其他错误
            raise Exception(msg.get("Message"))
        elif code == -3:  # 序列化错误
            raise MarshallingError(msg.get("Message"))
        elif code == -4:  # 反序列化错误
            raise UnmarshallingError(msg.get("Message"))
        elif code == -5:  # MMTLS初始化错误
            raise MMTLSError(msg.get("Message"))
        elif code == -6:  # 收到的数据包长度错误
            raise PacketError(msg.get("Message"))
        elif code == -7:  # 已退出登录
            raise UserLoggedOut("Already logged out")
        elif code == -8:  # 链接过期
            raise Exception(msg.get("Message"))
        elif code == -9:  # 解析数据包错误
            raise ParsePacketError(msg.get("Message"))
        elif code == -10:  # 数据库错误
            raise DatabaseError(msg.get("Message"))
        elif code == -11:  # 登陆异常
            raise UserLoggedOut(msg.get("Message"))
        elif code == -12:  # 操作过于频繁
            raise Exception(msg.get("Message"))
        elif code == -13:  # 上传失败
            raise Exception(msg.get("Message"))

    def s_handler(self,msg):
        
        if self.handler!=None:
            return self.handler.handler(msg)
        
        msg_type = msg.get("MsgType")

        # 预处理消息
        msg["FromWxid"] = msg.get("FromUserName").get("string")
        msg.pop("FromUserName")
        msg["ToWxid"] = msg.get("ToWxid").get("string")

        # 处理一下自己发的消息
        if msg["FromWxid"] == self.id and msg["ToWxid"].endswith("@chatroom"):  # 自己发发到群聊
            # 由于是自己发送的消息，所以对于自己来说，From和To是反的
            msg["FromWxid"], msg["ToWxid"] = msg["ToWxid"], msg["FromWxid"]

        # 根据消息类型触发不同的事件
        if msg_type == 1:  # 文本消息
            self.on_text(msg)

        elif msg_type == 3:  # 图片消息
            self.on_image(msg)

        elif msg_type == 34:  # 语音消息
            self.on_voice(msg)

        elif msg_type == 43:  # 视频消息
            self.on_video(msg)
        
        elif msg_type in [48,49]:  # xml消息
            self.on_xml(msg)

        elif msg_type == 10002:  # 系统消息
            self.on_system(msg)

        elif msg_type == 37:  # 好友请求
            if self.time > 14400:
                self.on_verify(msg)
            else:
                self.output("风控保护: 新设备登录后4小时内请挂机")

        elif msg_type == 51:
            self.on_other(msg)
        else:
            self.on_other(msg)
        return
    
    def on_text(self,msg):
        self.on_other(msg)

    def on_image(self,msg):
        self.on_other(msg)

    def on_voice(self,msg):
        self.on_other(msg)

    def on_video(self,msg):
        self.on_other(msg)

    def on_xml(self,msg):
        self.on_other(msg)

    def on_system(self,msg):
        self.on_other(msg)

    def on_verify(self,msg):
        self.on_other(msg)
    
    def on_other(self,msg):
        mt = msg.get("MsgType")
        self.output(f"未知的消息类型: {mt}\r\n{msg}")

    async def session_post(self,method,args,timeout:int=0):
        try:
            async with aiohttp.ClientSession(timeout=sentinel if timeout==0 else aiohttp.ClientTimeout(total=timeout)) as session:
                response = await session.post(f'http://{self.host}:{self.port}/{method}', json=args)
                jrs = await response.json()
                if jrs.get("Success"):
                    data = jrs.get("Data",None)
                    if data!=None:
                        return data
                    return jrs
                else:
                    self.e_handler(jrs)
                    return None
        except:
            return None

    async def session_get(self,method:str,timeout:int=0):
        try:
            async with aiohttp.ClientSession(timeout=sentinel if timeout==0 else aiohttp.ClientTimeout(total=timeout)) as session:
                response = await session.get(f'http://{self.host}:{self.port}/{method}')
                return response
        except:
            return {}
    
    async def start(self,block=False,count=5):
        if not await self.alive():
            self.output("核心进程未启动")
            if not self.setup():
                self.output("核心进程启动失败")
                return False
            else:
                while not await self.alive():
                    time.sleep(0.1)
                    count-=1

                    if count == 0:
                        break
        
        if await self.alive():
            self.run=True
        else:
            self.output("启动失败")
            return False
        
        self.state = 1

        await self.logon()
        
        self.state = 2

        try:
            success = await self.auto_beat()
        except:
            self.output("启动自动心跳失败")
        
        self.state = 3

        if block:
            self.call_stub(self.worker)
            return True
        else:
            self.thread = threading.Thread(target = self.call_stub,args=(self.worker,),  daemon=True)
            self.thread.start()
            return True

    def setup(self):
        arguments = ["--port", self.port, "--mode", "release", "--redis-host", "127.0.0.1", "--redis-port", "6379",
                          "--redis-password", "", "--redis-db", "0"]

        command = [self.executable_path] + arguments
        
        self.core = subprocess.Popen(command, cwd=os.path.dirname(os.path.abspath(self.executable_path)), stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if None == self.core:
            return False

        self.logthread = threading.Thread(target=self.core_log, daemon=True)
        self.errthread = threading.Thread(target=self.core_err, daemon=True)
        if None != self.logthread:
            self.logthread.start()
        if None != self.errthread:
            self.errthread.start()
        return True

    def shutdown(self,core=False):
        self.run=False
        if core and self.core!=None:
            self.core.terminate()
        if self.logthread!=None:
            self.logthread.join()
        if self.errthread!=None:
            self.errthread.join()
        self.core = None
        self.logthread=None
        self.errthread=None
    
    def core_log(self):
        while self.run:
            line = self.core.stdout.readline()
            if not line:
                break
        self.logthread=None
        

    def core_err(self):
        while self.run:
            line = self.core.stderr.readline()
            if not line:
                break
        self.errthread=None

    def show_qr(self,url):
        qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii()

    async def worker(self):
        last = now = time.time()
        while self.run:
            try:
                now = time.time()
                delay = now - last
                self.time += delay
                last = now
                if self.time > 120:
                    await self.logout()
                    await asyncio.sleep(10)
                    await self.logon()
                    await asyncio.sleep(5)
                    self.time = 0

                rs = await self.send_sync()
                if None == rs:
                    await asyncio.sleep(self.delay)
                    continue

                msgs = rs.get("AddMsgs")
                if None == msgs:
                    await asyncio.sleep(self.delay)
                    continue

                for msg in msgs:
                    self.s_handler(msg)
            except SystemExit:
                raise  # 不捕获系统退出
            except KeyboardInterrupt:
                raise  # 不捕获键盘中断
            except Exception as e:
                self.output(f"Client.worker 异常\n{e}")
            except BaseException as e:
                self.output(f"Client.worker 异常\n{e}")
        self.thread=None

    @staticmethod
    def call_stub(func):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            loop.create_task(func())
        else:
            loop.run_until_complete(func())

    async def logon(self):
        uuid = None
        if not await self.check_logoned(self.id):
            while not await self.check_logoned(self.id):
                try:
                    if await self.get_cached(self.id):
                        uuid = await self.awaken(self.id)
                    else:
                        if not self.deviceid:
                            self.deviceid = self.createid()
                        if not self.devicename:
                            self.devicename = self.createname()
                        uuid,url = await self.get_qrcode(self.devicename,self.deviceid)
                        self.show_qr(f'http://weixin.qq.com/x/{uuid}')
                except:
                    if not self.devicename:
                        self.devicename = self.createname()
                    if not self.deviceid:
                        self.deviceid = self.createid()
                    uuid , url = await self.get_qrcode(self.devicename,self.deviceid)
                    self.show_qr(f'http://weixin.qq.com/x/{uuid}')

                while self.run:
                    stat,data = await self.check_uuid(uuid)
                    if stat:
                        break
                    await asyncio.sleep(5)

            self.config["id"] = self.id
            self.config["name"] = self.name
            self.config["nickname"] = self.nickname
            self.config["alias"] = self.alias
            self.config["phone"] = self.phone
            self.config["deviceid"] = self.deviceid
            self.config["devicename"] = self.devicename
        else:
            profile = await self.get_profile(self.id)
            self.nickname = profile.get("NickName").get("string")
            self.alias = profile.get("Alias")
            self.phone = profile.get("BindMobile").get("string")
            
            self.config["nickname"] = self.nickname
            self.config["alias"] = self.alias
            self.config["phone"] = self.phone
        
        self.output("登录成功!!!")
        return True

    async def logout(self):
        
        if not self.valide():
            return True

        args={"Wxid": self.id}
        rs = await self.session_post("Logout",args)
        if None != rs:
            return True
        
        return False

    async def set_step(self,count:int):
        if not self.valide():
            return False
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        
        args = {"Wxid": self.id, "StepCount": count}
        rs = await self.session_post("SetStep",args)
        return rs!=None
    
    async def set_revoke(self,target:str,client_msg_id:int,create_time,msgid:int):
        if not self.valide():
            return False
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "ClientMsgId": client_msg_id, "CreateTime": create_time,"NewMsgId": msgid}
        rs = await self.session_post("RevokeMsg",args)
        return rs != None
        
    async def set_proxy(self,url:str,user:str="",pwd:str=""):
        if not self.valide():
            return False
        
        args = {"Wxid": self.id,
                "Proxy": {
                    "ProxyIp": url,
                    "ProxyUser": user,
                    "ProxyPassword": pwd
                    }
                }
        rs = await self.session_post("SetProxy",args)
        return rs != None
    
    async def check_db(self):
        response = await self.session_get("CheckDatabaseOK")
        resp = await response.json()
        if resp.get("Running"):
            return True
        else:
            return False
            
    async def check_logoned(self,id):
        if id==None:
           id = self.id
        try:
            prof = await self.get_profile(id)
            if None == prof:
                return False
            return True
        except:
            return False 

    async def alive(self):
        try:
            response = await self.session_get("IsRunning",10)
            return await response.text() == 'OK'
        except:
            return False

    async def awaken(self,id):
        if id == None:
            id = self.id
        args = {"Wxid":id}
        rs = await self.session_post("AwakenLogin",args)
        if None == rs:
            return None
        return rs.get("QrCodeResponse").get("Uuid")
    
    async def check_uuid(self,uuid):
        args = {"Uuid": uuid}
        rs = await self.session_post("CheckUuid",args)
        if None == rs:
            return None
        rsp = rs.get("acctSectResp", "")
        if rsp:
            self.id = rsp.get("userName")
            self.name = rsp.get("nickName")
            self.alias = rsp.get("alias")
            self.phone = rsp.get("bindMobile")
            return  True, rs
        else:
            return False, rs.get("expiredTime")


    async def get_cached(self,id):
        if not self.valide():
            id = self.id
        args = {"Wxid":id}
        rs = await self.session_post("GetCachedInfo",args)
        if None == rs:
            return {}
        return rs

    async def get_profile(self,id):
        args = {"Wxid": id}
        rs= await self.session_post("GetProfile",args)
        if None!=rs:
            return rs.get("userInfo")
        return None

    async def get_myqrcode(self,style:int=0):

        args =  {"Wxid": self.id, "Style": style}
        rs = await self.session_post("GetMyQRCode",args)
        if None!=rs:
            return rs.get("qrcode").get("buffer")
        return None

    async def get_qrcode(self,device_name,device_id):
        args = {'DeviceName': device_name, 'DeviceID': device_id}
        rs = await self.session_post("GetQRCode",args)
        if None == rs:
            return None
        return rs.get("Uuid"),rs.get("QRCodeURL")

    async def heart_beat(self):
        if not self.valide():
            return False
        args = {"Wxid": self.id}
        rs = await self.session_post("Heartbeat",args)
        if None != rs:
            return True
        return False

    async def auto_beat(self,start=True):
        if not self.valide():
            return False
        args = {"Wxid": self.id}
        rs = await self.session_post("AutoHeartbeatStart" if start else "AutoHeartbeatStop" ,args)
        if None != rs:
            return True
        return False

    async def heart_status(self):
        if not self.valide():
            return None
        args = {"Wxid": self.id}
        rs = await self.session_post("AutoHeartbeatStatus",args)
        if None == rs:
            return None
        return rs.get("Running")
    
    async def accept_friend(self,scene,v1,v2):
        if not self.valide():
            return False
        args = {"Wxid": self.id, "Scene": scene, "V1": v1, "V2": v2}
        rs = await self.session_post("AcceptFriend",args)
        if None != rs:
            return True
        return False
    
    async def get_contact(self,id:Union[str, list[str]]):
        if not self.valide():
            return None
        if isinstance(id,list):
            id = ",".join(id)
        args = {"Wxid": self.id, "RequestWxids": id}
        rs = await self.session_post("GetContact",args)
        if None == rs:
            return None
        contact = rs.get("ContactList")
        if len(contact) == 1:
            return contact[0]
        else:
            return contact
        
    async def get_contact_detail(self,id:Union[str, list[str]],chatroom:str=""):
        if not self.valide():
            return None
        if isinstance(id,list):
            if len(id) > 20:
                raise ValueError("一次最多查询20个联系人")
            id = ",".join(id)
        args = {"Wxid": self.id, "RequestWxids": id, "Chatroom": chatroom}
        rs = await self.session_post("GetContractDetail",args)
        if None == rs:
            return None
        return rs.get("ContactList")

    async def get_contact_list(self,wx_seq:int=0,chatroom_seq:int=0):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "CurrentWxcontactSeq": wx_seq, "CurrentChatroomContactSeq": chatroom_seq}
        return await self.session_post("GetContractList",args)
    
    async def get_nickname(self,id: Union[str, list[str]]):
        data = await self.get_contact_detail(id)
        if None == data:
            return ""
        if isinstance(id,str):
            try:
                return data[0].get("NickName").get("string")
            except:
                return ""
        else:
            result = []
            for contact in data:
                try:
                    result.append(contact.get("NickName").get("string"))
                except:
                    result.append("")
            return result
        
    async def get_redpack(self,xml:str,key:str,user:str):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "Xml": xml, "EncryptKey": key, "EncryptUserinfo": user}
        return await self.session_post("GetHongBaoDetail",args)
    
    async def chatroom_add(self,chatroom,id):
        if not self.valide():
            return False
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.wxid, "Chatroom": chatroom, "InviteWxids": id}
        rs = await self.session_post("AddChatroomMember",args)
        return rs != None
    
    async def chatroom_notice(self,chatroom):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "Chatroom": chatroom}
        rs = await self.session_post("GetChatroomInfo",args)
        if None == rs:
            return None
        data = dict(rs)
        data.pop("BaseResponse")
        return data
    
    async def chatroom_info(self,chatroom):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "Chatroom": chatroom}
        rs = await self.session_post("GetChatroomInfoNoAnnounce",args)
        if None == rs:
            return None
        return rs.get("ContactList")[0]
        
    async def chatroom_member(self,chatroom):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "Chatroom": chatroom}
        rs = await self.session_post("GetChatroomMemberDetail",args)
        if None == rs:
            return None
        return rs.get("NewChatroomData").get("ChatRoomMember")
    
    async def chatroom_qrcode(self,chatroom):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "Chatroom": chatroom}
        rs = await self.session_post("GetChatroomQRCode",args)
        if None == rs:
            return None
        return {"base64": rs.get("qrcode").get("buffer"), "description": rs.get("revokeQrcodeWording")}
    
    async def chatroom_invite(self,id: Union[str, list], chatroom: str):
        if not self.valide():
            return False
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "Chatroom": chatroom, "InviteWxids": id}
        rs = await self.session_post("InviteChatroomMember", args)
        return rs!=None
    

    async def send_sync(self):
        args = {"Wxid": self.id, "Scene": 0, "Synckey": ""}
        rs = await self.session_post("Sync",args,timeout=10)
        return rs
    
    
    async def send_text(self,target=None,content="",atlst=""):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        if target!=None:
            self.target = target
        else:
            target = self.target

        args = {"Wxid":self.id,"ToWxid":target,"Content":content,"Type":1,"At":atlst}
        rs = await self.session_post("SendTextMsg",args=args)
        if None == rs:
            return None
        return rs.get("ClientImgId").get("string"), rs.get("CreateTime"), rs.get("Newmsgid")

    async def send_image(self,target:str,image:Union[str,bytes,os.PathLike]):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        
        if isinstance(image,str):
            pass
        elif isinstance(image,bytes):
            image = base64.b64encode(image).decode()
        elif isinstance(image,os.PathLike):
            with open(image,'rb') as file:
                image = base64.b64encode(file.read()).decode()
        else:
            raise ValueError("Argument 'image' can only be str, bytes, or os.PathLike")

        args = {"Wxid": self.id, "ToWxid": target, "Base64": image}
        rs = await self.session_post("SendImageMsg",args)
        if None == rs:
            return None
        return rs.get("ClientImgId").get("string"), rs.get("CreateTime"), rs.get("Newmsgid")

    async def send_link(self,target,title,desc,thumb,url):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Url": url, "Title": title, "Desc": desc,
                          "ThumbUrl": thumb}
        rs = await self.session_post("SendShareLink",args)
        if None == rs:
            return None
        return rs.get("clientMsgId"), rs.get("createTime"), rs.get("newMsgId")

    async def send_emoj(self,target,em,len):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Md5": em, "TotalLen": len}
        rs = await self.session_post("SendEmojiMsg",args)
        if None == rs:
            return None
        return rs.get("emojiItem")
    
    async def send_video(self,target: str, video: Union[str, bytes, os.PathLike],image: [str, bytes, os.PathLike] = None):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        
        if not image:
            image = Path(os.path.join(Path(__file__).resolve().parent, "fallback.png"))
        # get video base64 and duration
        if isinstance(video, str):
            vid_base64 = video
            video = base64.b64decode(video)
            file_len = len(video)
            media_info = MediaInfo.parse(BytesIO(video))
        elif isinstance(video, bytes):
            vid_base64 = base64.b64encode(video).decode()
            file_len = len(video)
            media_info = MediaInfo.parse(BytesIO(video))
        elif isinstance(video, os.PathLike):
            with open(video, "rb") as f:
                file_len = len(f.read())
                vid_base64 = base64.b64encode(f.read()).decode()
            media_info = MediaInfo.parse(video)
        else:
            raise ValueError("video should be str, bytes, or path")
        duration = media_info.tracks[0].duration

        # get image base64
        if isinstance(image, str):
            image_base64 = image
        elif isinstance(image, bytes):
            image_base64 = base64.b64encode(image).decode()
        elif isinstance(image, os.PathLike):
            with open(image, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
        else:
            raise ValueError("image should be str, bytes, or path")

        args = {"Wxid": self.id, "ToWxid": target, "Base64": vid_base64, "ImageBase64": image_base64,
                          "PlayLength": duration}
        rs = await self.session_post("SendVideoMsg",args)
        if rs == None:
            return None
        return rs.get("clientMsgId"), rs.get("newMsgId")

    async def send_voice(self,target:str,voice: Union[str, bytes, os.PathLike], format: str = "amr"):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        if format not in ["amr", "wav", "mp3"]:
            raise ValueError("format must be one of amr, wav, mp3")
        # read voice to byte
        if isinstance(voice, str):
            voice_byte = base64.b64decode(voice)
        elif isinstance(voice, bytes):
            voice_byte = voice
        elif isinstance(voice, os.PathLike):
            with open(voice, "rb") as f:
                voice_byte = f.read()
        else:
            raise ValueError("voice should be str, bytes, or path")

        # get voice duration and b64
        if format.lower() == "amr":
            audio = AudioSegment.from_file(BytesIO(voice_byte), format="amr")
            voice_base64 = base64.b64encode(voice_byte).decode()
        elif format.lower() == "wav":
            audio = AudioSegment.from_file(BytesIO(voice_byte), format="wav").set_channels(1)
            audio = audio.set_frame_rate(self._get_closest_frame_rate(audio.frame_rate))
            voice_base64 = base64.b64encode(
                await pysilk.async_encode(audio.raw_data, sample_rate=audio.frame_rate)).decode()
        elif format.lower() == "mp3":
            audio = AudioSegment.from_file(BytesIO(voice_byte), format="mp3").set_channels(1)
            audio = audio.set_frame_rate(self._get_closest_frame_rate(audio.frame_rate))
            voice_base64 = base64.b64encode(
                await pysilk.async_encode(audio.raw_data, sample_rate=audio.frame_rate)).decode()
        else:
            raise ValueError("format must be one of amr, wav, mp3")

        duration = len(audio)

        format_dict = {"amr": 0, "wav": 4, "mp3": 4}

        args = {"Wxid": self.id, "ToWxid": target, "Base64": voice_base64, "VoiceTime": duration,
                          "Type": format_dict[format]}
        rs = await self.session_post("SendVideoMsg",args)
        if rs == None:
            return None
        return int(rs.get("ClientMsgId")), rs.get("CreateTime"), rs.get("NewMsgId")

    async def send_card(self,target, card_id: str, card_nickname: str, card_alias: str = ""):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": id, "CardWxid": card_id, "CardAlias": card_alias,"CardNickname": card_nickname}
        rs = await self.session_post("SendCardMsg",args)
        if rs == None:
            return None
        return rs.get("List")[0].get("ClientMsgid"), rs.get("List")[0].get("Createtime"), rs.get("List")[0].get("NewMsgId")
    
    async def send_app(self,target,xml,type: int):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Xml": xml, "Type": type}
        rs = await self.session_post("SendAppMsg",args)
        if None == rs:
            return rs
        return rs.get("clientMsgId"), rs.get("createTime"), rs.get("newMsgId")
    
    async def send_loc(self,target,xml):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Xml": xml, "Type": 48}
        rs = await self.session_post("SendShareLocation",args)
        if rs == None:
            return None
        return rs
    
    async def send_cdnimg(self,target,xml):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Content": xml}
        rs = await self.session_post("SendCDNImgMsg",args)
        if None == rs:
            return None
        return rs.get("ClientImgId").get("string"), rs.get("CreateTime"), rs.get("Newmsgid")
    
    async def send_cdnfile(self,target,xml):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Content": xml}
        rs = await self.session_post("SendCDNFileMsg",args)
        if None == rs:
            return None
        return rs.get("clientMsgId"), rs.get("createTime"), rs.get("newMsgId")
    
    async def send_cdnvideo(self,target,xml):
        if not self.valide():
            return None
        if self.time < 14400:
            raise ValueError("风控保护: 新设备登录后4小时内请挂机")
        args = {"Wxid": self.id, "ToWxid": target, "Content": xml}
        rs = await self.session_post("SendCDNVideoMsg",args)
        if None == rs:
            return None
        return rs.get("clientMsgId"), rs.get("newMsgId")
    
    async def download_image(self,aeskey:str,url:str):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "AesKey": aeskey, "Cdnmidimgurl": url}
        return await self.session_post("CdnDownloadImg",args)
        
    async def download_voice(self,msgid:str,url:str,length:int):
        if not self.valide():
            return None
        args ={"Wxid": self.id, "MsgId": msgid, "Voiceurl": url, "Length": length}
        rs = await self.session_post("DownloadVoice",args)
        if None == rs:
            return None
        return rs.get("data").get("buffer")
    
    async def download_attach(self,attid:str):
        if not self.valide():
            return None
        args = {"Wxid": self.id, "AttachId": attid}
        rs = await self.session_post("DownloadAttach",args)
        if None == rs:
            return None
        return rs.get("data").get("buffer")
    
    async def download_video(self,msgid:str):
        if not self.valide():
            return None
        args ={"Wxid": self.id, "MsgId": msgid}
        rs = await self.session_post("DownloadVideo",args)
        if None == rs:
            return None
        return rs.get("data").get("buffer")
    
    @staticmethod
    def _get_closest_frame_rate(frame_rate: int) -> int:
        supported = [8000, 12000, 16000, 24000]
        closest_rate = None
        smallest_diff = float('inf')
        for num in supported:
            diff = abs(frame_rate - num)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_rate = num

        return closest_rate
#测试
class ClientManager:
    def __init__(self):
        self.client=Client("./wechat.json",None)

    async def start(self):
        await self.client.start(count=20)

    def handler(self,msg):
        pass

async def main():
    c = Client()
    if not await c.alive():
        print("XYWechatPad -p 9000 -m debug -rh 127.0.0.1 -rp 6379 -rdb 0 -rpwd  ")
        return
    await c.start(block=True)

if __name__ == "__main__":
    asyncio.run(main())
    #main()
