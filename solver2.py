import requests, cv2, time, base64, secrets, string, random, hashlib, numpy as np, os
try:
    from TikSign import Newparams, UserAgentTik, sign, xor, Argus
except:
    os.system("pip install TikSign==0.2.9999999")
    from TikSign import Newparams, UserAgentTik, sign, xor, Argus
    
p = Newparams()
ua = UserAgentTik()

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
            out.append((mn_loc[0], 1 - mn) if m == cv2.TM_SQDIFF_NORMED else (mx_loc[0], mx))
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
        ax = cv2.convertScaleAbs(gx); ay = cv2.convertScaleAbs(gy)
        grad = cv2.addWeighted(ax, 0.5, ay, 0.5, 0)
        return cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX)

class CaptchaSolver:
    def __init__(self, iid: str, did: str, device_type: str, device_brand: str, country: str, proxy: str = None):
        self.iid = iid; self.did = did
        self.device_type = device_type; self.device_brand = device_brand
        self.host = 'rc-verification-sg.tiktokv.com'
        self.host_region = self.host.split('-')[2].split('.')[0]
        self.country = country
        self.session = requests.Session()
        if proxy:
            self.session.proxies.update({"http": f"http://{proxy}", "https": f"http://{proxy}"})

    def _base_params(self):
        tmp = f"{int(time.time())}{random.randint(111,999)}"
        return (f'lang=en&app_name=musical_ly&h5_sdk_version=2.33.7&h5_sdk_use_type=cdn&sdk_version=2.3.4.i18n'
                f'&iid={self.iid}&did={self.did}&device_id={self.did}&ch=googleplay&aid=1233&os_type=0&mode=slide'
                f'&tmp={tmp}&platform=app&webdriver=undefined&verify_host=https%3A%2F%2F{self.host_region}%2F'
                f'&locale=en&channel=googleplay&app_key&vc=32.9.5&app_version=32.9.5&session_id&region={self.host_region}'
                f'&use_native_report=1&use_jsb_request=1&orientation=2&resolution=720*1280&os_version=25'
                f'&device_brand={self.device_brand}&device_model={self.device_type}&os_name=Android'
                f'&version_code=3275&device_type={self.device_type}&device_platform=Android&type=verify'
                f'&detail=&server_sdk_env=&imagex_domain&subtype=slide&challenge_code=99996&triggered_region={self.host_region}'
                f'&cookie_enabled=true&screen_width=360&screen_height=640&browser_language=en'
                f'&browser_platform=Linux%20i686&browser_name=Mozilla&browser_version=5.0%20%28Linux%3B%20Android%207.1.2%3B%20{self.device_type}%20Build%2FN2G48C%3B%20wv%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Version%2F4.0%20Chrome%2F86.0.4240.198%20Mobile%20Safari%2F537.36%20BytedanceWebview%2Fd8a21c6')

    def _signed_headers(self, params):
        sig = sign(params=params)
        headers = {
            'X-Tt-Request-Tag': 'n=1;t=0',
            'X-Vc-Bdturing-Sdk-Version': '2.3.4.i18n',
            'X-Tt-Bypass-Dp': '1',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Tt-Dm-Status': 'login=0;ct=0;rt=7',
            'X-Tt-Store-Region': self.country,
            'X-Tt-Store-Region-Src': 'did',
            'User-Agent': ua["User-Agent"],
        }
        headers.update(sig)
        return headers

    def get_captcha(self):
        params = self._base_params()
        return self.session.get(f'https://{self.host}/captcha/get?{params}', headers=self._signed_headers(params)).json()

    def verify_captcha(self, data):
        params = self._base_params()
        return self.session.post(f'https://{self.host}/captcha/verify?{params}', headers=self._signed_headers(params), json=data).json()

    def start(self):
        try:
            _captcha = self.get_captcha()
            print(_captcha)
            cd = _captcha["data"]["challenges"][0]
            puzzle_b64 = base64.b64encode(self.session.get(cd["question"]["url1"]).content)
            piece_b64 = base64.b64encode(self.session.get(cd["question"]["url2"]).content)

            max_loc = PuzzleSolver(puzzle_b64, piece_b64).get_position()
            rand_len = random.randint(50, 100)

            movements = []
            for i in range(rand_len):
                progress = (i + 1) / rand_len
                x_pos = round(max_loc * progress)
                y_offset = random.randint(-2, 2) if 0 < i < rand_len - 1 else 0
                y_pos = cd["question"]["tip_y"] + y_offset
                movements.append({"relative_time": i * rand_len + random.randint(-5, 5), "x": x_pos, "y": y_pos})

            payload = {"modified_img_width": 552, "id": cd["id"], "mode": "slide", "reply": movements, "verify_id": _captcha["data"]["verify_id"]}
            return self.verify_captcha(payload)
        except Exception:
            return None

def send(device, proxy=None):
    solver = CaptchaSolver(device[0], device[1], device[2], device[3], device[4], proxy)
    return solver.start()




country = "ye"   
device = [
    p["iid"],           # iid
    p["device_id"],           # did
    ua["type"],   # device_type
    ua["brand"],  # device_brand
    country        # country
]
print(send(device, proxy=None))
