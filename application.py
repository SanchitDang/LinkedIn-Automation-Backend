from flask import Flask,render_template,request
from flask_socketio import SocketIO, emit
import subprocess
from threading import Thread
import sys
# import eventlet
# import eventlet.wsgi
from flask_cors import CORS 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# eventlet.monkey_patch()
app = Flask(__name__)
CORS(app)
# eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
socketio = SocketIO(app,cors_allowed_origins='*')

def run_linkedin_bot(socketio, targetSearch):
    def emit_log(message):
        socketio.emit('bot_log', {'data': message})
    
    webdriver_path = 'chromedriver.exe'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--webdriver-path={webdriver_path}')
    driver = webdriver.Chrome(options=chrome_options)

    email_or_phone = 'your@email.com' 
    password = 'your password'

    driver.get('https://www.linkedin.com/')
    time.sleep(random.uniform(2, 4))  

    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'session_key'))
    )

    username_field.clear()

    for word in email_or_phone.split():
        username_field.send_keys(word)
        time.sleep(random.uniform(1, 2))  

    time.sleep(1)

    password_field = driver.find_element(By.ID, 'session_password')
    password_field.clear()

    for word in password.split():
        password_field.send_keys(word)
        time.sleep(random.uniform(1, 2))  

    time.sleep(1)

    password_field.send_keys(Keys.RETURN)

    emit_log("Successfully Logged In")

    WebDriverWait(driver, 10).until(
        EC.url_contains('https://www.linkedin.com/feed/')
    )

    time.sleep(random.uniform(2, 5))

    search_query = targetSearch

    search_field = driver.find_element(By.CSS_SELECTOR, '.search-global-typeahead__input')
    search_field.clear()

    for word in search_query.split("-"):
        search_field.send_keys(word)
        time.sleep(random.uniform(0.5, 1.5)) 
    time.sleep(1)
    search_field.send_keys(Keys.RETURN)

    emit_log("Seached For Abhay Bhan")

    time.sleep(2)
    button_text = "People"
    button_xpath = f"//button[text()='{button_text}']"
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, button_xpath))
    )
    button.click()

    emit_log("Put People Filter")

    span_text = "Message"
    button_xpath = f"//button[.//span[text()='{span_text}']]"
    # Wait for the button with the specified text in the span to be present on the page
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, button_xpath))
    )
    button.click()
    
    emit_log("Clicked on Message Abhay Bhan")
    time.sleep(random.uniform(2, 5))



    contenteditable_div = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.msg-form__contenteditable[contenteditable="true"]'))
    )
    contenteditable_div.click()
    message_text = "Hi! How Are You Doing?"
    contenteditable_div.send_keys(message_text)

    emit_log("Wrote Message to Abhay")


    time.sleep(3)
    button_text = "Send"
    button_xpath = f"//button[text()='{button_text}']"
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, button_xpath))
    )
    button.click()
    emit_log("Sent a Message to Abhay")
    time.sleep(10)


@app.route('/home')
def main():
        return render_template('base.html')

@app.route('/hello')
def hello():
        return 'hello'

@socketio.on("bot_init")
def linkedinBot(data):
    target_search = data.get('target_search')
    Thread(target=run_linkedin_bot, args=(socketio,target_search), daemon=True).start()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
