import base64
import hashlib
import json
import random
import secrets
import string
import time
from hashlib import md5
from urllib.parse import urlencode
import cv2
import numpy as np
import requests
from TikSign import Argus, Ladon, Gorgon, Newparams, UserAgentTik


class Cha:
    def __init__(self, key: bytes, nonce: bytes, counter: int = 0):
        if len(key) != 32 or len(nonce) != 12:
            raise ValueError("Invalid key or nonce length")
        self.k = key
        self.n = nonce
        self.c = counter

    @staticmethod
    def _r(v, n):
        return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))

    @staticmethod
    def _qr(s, a, b, c, d):
        s[a] = (s[a] + s[b]) & 0xFFFFFFFF
        s[d] ^= s[a]
        s[d] = Cha._r(s[d], 16)
        s[c] = (s[c] + s[d]) & 0xFFFFFFFF
        s[b] ^= s[c]
        s[b] = Cha._r(s[b], 12)
        s[a] = (s[a] + s[b]) & 0xFFFFFFFF
        s[d] ^= s[a]
        s[d] = Cha._r(s[d], 8)
        s[c] = (s[c] + s[d]) & 0xFFFFFFFF
        s[b] ^= s[c]
        s[b] = Cha._r(s[b], 7)

    def _block(self, ctr: int):
        s = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
        s += [int.from_bytes(self.k[i * 4:(i + 1) * 4], "little") for i in range(8)]
        s.append(ctr & 0xFFFFFFFF)
        s += [int.from_bytes(self.n[i * 4:(i + 1) * 4], "little") for i in range(3)]
        w = s[:]
        for _ in range(10):
            self._qr(w, 0, 4, 8, 12)
            self._qr(w, 1, 5, 9, 13)
            self._qr(w, 2, 6, 10, 14)
            self._qr(w, 3, 7, 11, 15)
            self._qr(w, 0, 5, 10, 15)
            self._qr(w, 1, 6, 11, 12)
            self._qr(w, 2, 7, 8, 13)
            self._qr(w, 3, 4, 9, 14)
        return b''.join(((w[i] + s[i]) & 0xFFFFFFFF).to_bytes(4, 'little') for i in range(16))

    def _ks(self):
        ctr = self.c
        while True:
            block = self._block(ctr)
            ctr = (ctr + 1) & 0xFFFFFFFF
            for b in block:
                yield b

    def _p(self, data: bytes) -> bytes:
        ks = self._ks()
        return bytes([b ^ next(ks) for b in data])


class edata:
    FLAG = b'\x01'

    @staticmethod
    def encrypt(txt: str) -> str:
        d = txt.encode('utf-8')
        k = secrets.token_bytes(32)
        n = secrets.token_bytes(12)
        c = Cha(k, n, 0)
        ct = c._p(d)
        raw = edata.FLAG + k + n + ct
        return base64.b64encode(raw).decode()

    @staticmethod
    def decrypt(txt: str) -> str:
        raw = base64.b64decode(txt)
        if len(raw) < 1 + 32 + 12:
            raise ValueError("Invalid edata")
        k = raw[1:33]
        n = raw[33:45]
        ct = raw[45:]
        c = Cha(k, n, 0)
        plain = c._p(ct)
        return plain.decode('utf-8', errors='replace')


def sign(
    params: str,
    payload: str = None,
    sec_device_id: str = '',
    cookie: str = None,
    aid: int = 1233,
    license_id: int = 1611921764,
    sdk_version_str: str = 'v05.00.06-ov-android',
    sdk_version: int = 167775296,
    platform: int = 0,
    unix: float = None
):    
    aid = 1233   
    if payload is None or payload == "":
        x_ss_stub = None
    else:
        x_ss_stub = md5(payload.encode('utf-8')).hexdigest()
    if not unix:
        unix = time.time()
    
    result = Gorgon(aid).Encoder(
        params=params,
        data=payload if payload is not None else "",
        cookies=cookie,
        unix=unix
    )    
    sign_dict = {
        'content-length': str(len(payload)) if payload else '0',
    }    
    if x_ss_stub:
        sign_dict['x-ss-stub'] = x_ss_stub.upper()
    
    sign_dict.update({
        'x-ladon': Ladon.encrypt(int(unix), license_id, aid),
        'x-argus': Argus.get_sign(
            params,
            x_ss_stub,
            int(unix),
            platform=platform,
            aid=aid,
            license_id=license_id,
            sec_device_id=sec_device_id,
            sdk_version=sdk_version_str,
            sdk_version_int=sdk_version
        )
    })
    
    result.update(sign_dict)
    return result


def getparams(iid, dev, brn, typ):
    params = {
        "lang": "en",
        "app_name": "musical_ly",
        "h5_sdk_version": "2.33.17",
        "h5_sdk_use_type": "goofy",
        "sdk_version": "2.3.8.i18n",
        "iid": iid,
        "did": dev,
        "device_id": dev,
        "ch": "googleplay",
        "aid": "1233",
        "os_type": "0",
        "mode": "slide",
        "tmp": str(int(time.time() * 1000)),
        "platform": "app",
        "webdriver": "false",
        "enable_image": "1",
        "verify_host": "https://rc-verification-sg.tiktokv.com/",
        "locale": "ar",
        "channel": "googleplay",
        "app_key": "",
        "vc": "37.0.4",
        "app_version": "37.0.4",
        "session_id": "",
        "region": "sg",
        "userMode": "257",
        "use_native_report": "1",
        "use_jsb_request": "1",
        "orientation": "2",
        "resolution": "1080*2220",
        "os_version": "30",
        "device_brand": brn,
        "device_model": typ,
        "os_name": "Android",
        "version_code": "3704",
        "device_type": typ,
        "device_platform": "Android",
        "type": "verify",
        "detail": "",
        "server_sdk_env": '{"idc":"my","region":"ALISG","server_type":"business"}',
        "imagex_domain": "",
        "subtype": "slide",
        "challenge_code": "99999",
        "triggered_region": "sg",
        "cookie_enabled": "true",
        "screen_width": "393",
        "screen_height": "851",
        "browser_language": "en",
        "browser_platform": "Linux aarch64",
        "browser_name": "Mozilla",
        "browser_version": "5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 BytedanceWebview/d8a21c6"
    }
    return params


def get_captcha(iid, dev, brn, typ, session: requests.Session = None):
    if session is None:
        session = requests.Session()
    params = getparams(iid, dev, brn, typ)
    try:
        signs = sign(params=urlencode(params), payload="")  
        headers = {
            "content-type": "application/json; charset=utf-8",
            "user-agent": ua["User-Agent"],
        }
        headers.update(signs)
        res = session.get("https://rc-verification-sg.tiktokv.com/captcha/get", headers=headers, params=params, timeout=15)
        if res.status_code != 200:
            print(f"get_captcha: unexpected status code {res.status_code}")
            print("Response text:", res.text)
            return None
        try:
            j = res.json()
        except Exception:
            print("get_captcha: failed to parse JSON. Raw response:")
            print(res.text)
            return None


        if "edata" in j:
            cap = j["edata"]
        elif "data" in j and isinstance(j["data"], dict) and "edata" in j["data"]:
            cap = j["data"]["edata"]
        else:
            print(json.dumps(j, indent=2))
            return None

        dec = edata.decrypt(cap)
        return dec
    except Exception as e:
        print(f"Error in get_captcha: {e}")
        return None


def verify_captcha(payload_dict, params, session: requests.Session = None):
    if session is None:
        session = requests.Session()
    try:
        headers = {
            "content-type": "application/json; charset=utf-8",
            "user-agent": ua["User-Agent"],
        }
        
        data = payload_dict
        json_data = json.dumps({"edata": edata.encrypt(json.dumps(data))})  
        signs = sign(params=urlencode(params), payload=json_data)
        headers.update(signs)        
        res = session.post("https://rc-verification-sg.tiktokv.com/captcha/verify", headers=headers, params=params, data=json_data, timeout=15)
        if res.status_code != 200:            
            return None
        j = res.json()
        if "edata" in j:
            return edata.decrypt(j["edata"])
        elif "data" in j and isinstance(j["data"], dict) and "edata" in j["data"]:
            return edata.decrypt(j["data"]["edata"])
        else:
            print("verify_captcha: 'edata' not in response JSON. Full JSON:")
            print(json.dumps(j, indent=2))
            return None
    except Exception as e:
        print(f"Error in verify_captcha: {e}")
        return None


class PuzzleSolver:
    def __init__(self, base64puzzle, base64piece):
        self.puzzle = base64puzzle
        self.piece = base64piece
        self.methods = (cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED)

    def get_position(self):
        try:
            p = self._sobel(self._img(self.piece))
            t = self._sobel(self._img(self.puzzle))
            results = self._match_all(p, t)
            results += self._match_all(self._enhance(p), self._enhance(t))
            results.append(self._match_single(self._edges(p), self._edges(t)))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[0][0]
        except Exception:
            p = self._sobel(self._img(self.piece))
            t = self._sobel(self._img(self.puzzle))
            return self._match_single(p, t)[0]

    def _match_all(self, a, b):
        out = []
        for m in self.methods:
            matched = cv2.matchTemplate(a, b, m)
            mn, mx, mn_loc, mx_loc = cv2.minMaxLoc(matched)
            if m == cv2.TM_SQDIFF_NORMED:
                out.append((mn_loc[0], 1 - mn))
            else:
                out.append((mx_loc[0], mx))
        return out

    def _match_single(self, a, b):
        matched = cv2.matchTemplate(a, b, cv2.TM_CCOEFF_NORMED)
        mn, mx, mn_loc, mx_loc = cv2.minMaxLoc(matched)
        return (mx_loc[0], mx)

    def _img(self, b64):
        data = base64.b64decode(b64)
        arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("Failed to decode image")
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        return img

    def _enhance(self, img):
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)

    def _edges(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        return cv2.Canny(blurred, 50, 150)

    def _sobel(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gx = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
        ax = cv2.convertScaleAbs(gx)
        ay = cv2.convertScaleAbs(gy)
        grad = cv2.addWeighted(ax, 0.5, ay, 0.5, 0)
        return cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX)


class CaptchaSolver:
    def __init__(self, iid, dev, brn, typ, proxy=None):
        self.iid = iid
        self.dev = dev
        self.brn = brn
        self.typ = typ
        self.proxy = proxy
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.params = getparams(iid, dev, brn, typ)

    def get_captcha(self):
        return get_captcha(self.iid, self.dev, self.brn, self.typ, session=self.session)

    def verify_captcha(self, payload):
        return verify_captcha(payload, self.params, session=self.session)

    def start(self):
        try:
            _captcha = self.get_captcha()
            if not _captcha:
                print("start: no captcha obtained")
                return None
                
            captcha_data = json.loads(_captcha)
            
            cd = captcha_data["data"]["challenges"][0]
            
            q = cd["question"]
            url1 = q.get("url1")
            url2 = q.get("url2")
            if not url1 or not url2:
                print("start: missing image URLs in challenge data")
                return None

            r1 = self.session.get(url1, timeout=10)
            r2 = self.session.get(url2, timeout=10)
            if r1.status_code != 200 or r2.status_code != 200:
                print("start: failed to download puzzle images")
                print("url1 status:", r1.status_code, "url2 status:", r2.status_code)
                return None

            puzzle_b64 = base64.b64encode(r1.content).decode()
            piece_b64 = base64.b64encode(r2.content).decode()

            max_loc = PuzzleSolver(puzzle_b64, piece_b64).get_position()
            
            rand_len = random.randint(40, 100)

            movements = []
            total_time = 0
            for i in range(rand_len):
                progress = (i + 1) / rand_len
                x_pos = round(max_loc * progress)
                y_offset = random.randint(-2, 2) if 0 < i < rand_len - 1 else 0
                y_pos = cd["question"].get("tip_y", 0) + y_offset
                
                step = random.randint(8, 40)
                total_time += step
                movements.append({"relative_time": total_time, "x": x_pos, "y": y_pos})

            payload = {
                "modified_img_width": 552,
                "id": cd["id"],
                "mode": "slide",
                "reply": movements,
                "verify_id": captcha_data["data"]["verify_id"]
            }
            
            return self.verify_captcha(payload)
        except Exception as e:
            print(f"Error in start: {e}")
            return None


def send(device, proxy=None):
    solver = CaptchaSolver(device[0], device[1], device[2], device[3], proxy)
    return solver.start()


# usage
p = Newparams()
ua = UserAgentTik()

device = [
    p.get("iid", ""),  # iid
    p.get("device_id", ""),  # did
    ua.get("type", ""),  # device_type
    ua.get("brand", ""),  # device_brand
]

if __name__ == "__main__":
    print(send(device, proxy=None))
