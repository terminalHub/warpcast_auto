import uiautomator2 as u2

def connect_u2(port: int):
    return u2.connect(f"127.0.0.1:{port}")

def click_text(d, text):
    d(text=text).click()

def input_text(d, field_text, input_value):
    d(text=field_text).set_text(input_value)
