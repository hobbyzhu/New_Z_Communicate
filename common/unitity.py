from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import random, string


class iam(object):
    # 随机字母:
    def rndChar(self):
        return chr(random.randint(65, 90)), chr(random.randint(65, 90)), chr(random.randint(65, 90)), chr(
            random.randint(65, 90))

    # 随机颜色1:
    def rndColor(self):
        return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

    def draw_line(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=2)

    def randon_code(self):
        # 240 x 60:
        width = 60 * 4
        height = 60
        image = Image.new('RGB', (width, height), 'white')
        # 创建Font对象:
        font = ImageFont.truetype('Arial.ttf', 36)
        # 创建Draw对象:
        draw = ImageDraw.Draw(image)
        # 填充每个像素:
        code = self.rndChar()
        # 输出文字:
        for t in range(4):
            draw.text((60 * t + 10, 10), code[t], font=font, fill=self.rndColor())
        # 干扰线
        self.draw_line(draw, 4, width, height)
        # 模糊:
        image = image.filter(ImageFilter.BLUR)
        # image.show()
        return image, ''.join(code)

    def get_code(self):
        image, code = self.randon_code()
        #  创建字节码对象 ，写入字节码
        buf = BytesIO()
        image.save(buf, 'jpeg')
        bstring = buf.getvalue()
        return bstring, code


# 验证码邮件发送
from smtplib import SMTP_SSL, SMTP
from email.mime.text import MIMEText
from email.header import Header


# QQ邮箱验证码，参数为邮件地址和随机生成的6位数
def send_email(address, ecode):
    sender = 'Administrator<451413586@qq.com>'  # 你的邮件账号和发件人签名
    # 定义发送邮件的内容，支持html和css样式
    content = f'<br/>' \
              f'欢迎注册 你的验证码是{ecode}，请注意验证码使用安全' \
              f'<br/>' \
        # 实例化 邮件对象并指定参数
    massage = MIMEText(content, 'html', 'utf-8')
    # 指定邮件的标题，并指定编码
    massage['Subject'] = Header('欢迎注册', 'utf-8')
    massage['From'] = sender  # 发件人信息
    massage['To'] = address  # 收件人信息

    smtpobj = SMTP_SSL('smtp.qq.com', 465)  # 邮箱连接 465是端口
    # 邮箱账号和授权码登录
    smtpobj.login(user='451413586@qq.com', password='tmpzygaqkrvdbjhc')
    # 指定发件人 收件人 邮件内容
    smtpobj.sendmail(sender, address, str(massage))
    smtpobj.quit()


# 邮箱6位密码随机生成
def get_email_code():
    code_str = random.sample(string.digits, 6)
    return ''.join(code_str)


# 数据结构
# 单模型类转换json数据格式
def model_list(result):
    listx = []
    for row in result:
        dictx = {}
        for k, v, in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dictx[k] = v
        listx.append(dictx)
    return listx


# sqlalchemy 连接查询2张表，转换json数据格式[{},{}]
#  Comment, Users ,[(Comment,Users),(Comment,Users),(),()......]
def model_join_list(resilt):
    listx = []
    for obj1, obj2 in resilt:
        dictx = {}
        for k1, v1 in obj1.__dict__.items():  # obj1 是对象
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dictx:  # 字典重构存在的原始就抛弃
                    dictx[k1] = v1
        for k2, v2 in obj2.__dict__.items():  # obj2 是对象
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dictx:
                    dictx[k2] = v2
        listx.append(dictx)
    return listx
