from geetestServer import GeetestValidateServer
from loghelper import log


def game_captcha(gt: str, challenge: str):
     #启动网页服务器，要求用户完成米哈游的验证码
    log.info("遭遇验证码，请在浏览器中打开 http://127.0.0.1:16384 来完成验证码")
    g = GeetestValidateServer()
    return g.solveCaptcha(challenge,gt)  # 失败返回None 成功返回validate


def bbs_captcha(gt: str, challenge: str):
    log.info("遭遇验证码，请在浏览器中打开 http://127.0.0.1:16384 来完成验证码")
    g = GeetestValidateServer()
    return g.solveCaptcha(challenge,gt)
