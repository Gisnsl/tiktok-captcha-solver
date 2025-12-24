# TikTok Slide CAPTCHA Solver 🧩

[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

This project is an advanced **TikTok slide CAPTCHA solver** implemented in Python. It can automatically:

- Retrieve CAPTCHA challenges from TikTok verification servers.
- Decrypt and parse CAPTCHA images.
- Solve the slider puzzle using image processing (OpenCV) and Sobel edge detection.
- Simulate realistic human-like slider movements.
- Verify the CAPTCHA automatically.

> **Note:** This project is for educational purposes only. Do not use it for unauthorized or illegal activities.

---

## Features

- ✅ Fetch CAPTCHA challenges from TikTok
- ✅ Solve slider puzzles with high accuracy
- ✅ Encrypt/decrypt payloads (`edata`)
- ✅ Generate human-like slider movement data
- ✅ Optional support for proxies
- ✅ Fully modular and reusable classes

---

## Installation

Make sure you have **Python 3.10+** installed.

```bash
git clone https://github.com/Gisnsl/tiktok-captcha-solver.git
cd tiktok-captcha-solver
```

**Required Libraries:**

- `requests`
- `opencv-python`
- `numpy`
- `TikSign`

> You may install dependencies via:
>
> ```bash
> pip install requests opencv-python numpy TikSign
> ```

---

## Usage

```python
python solver.py
```

**Classes Explained:**

- `CaptchaSolver`: Main class to fetch and solve CAPTCHAs.
- `PuzzleSolver`: Handles slider image processing and template matching.
- `edata`: Handles encryption/decryption of CAPTCHA payloads.
- `Cha`: Internal class implementing ChaCha-like encryption for `edata`.
- `sign()`: Generates necessary TikTok request signatures (`x-argus`, `x-ladon`, etc.).

---

## Contributing

Feel free to submit issues, pull requests, or improve the solver.  
Make sure you follow the Python best practices and document your code.

---

## Contact

For questions, suggestions, or help, contact me on **Telegram**: [@maho_s9](https://t.me/maho_s9)

---

## License

This project is licensed under the **MIT License**.

