import cv2
import numpy as np
import configparser
import requests
from time import sleep
import logging

def processFrame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (19, 19), 0)
    return gray

def detectMovement(delta):
    threshhold = 1000000
    if delta> threshhold:
        return True
    return False

def sendTelegramMessage(token,chat_id):
    message='Movement%20detected!%20See%20http://192.168.178.41:5000/'
    messageUrl='https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&text=' + message
    response = requests.get(messageUrl)

def announce(token, chat_ids):
    for chat_id in chat_ids:
        sendTelegramMessage(token,chat_id)

if __name__ == '__main__':
    # Logging
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, filename='streamDetect.log',)

    # Read Configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    telegramToken = config['Telegram']['Token']
    admins = (config['Telegram']['ChatIds']).split()
    url = config['Website']['VideoFeedUrl']

    # Start Detection
    logging.info('Start Detection ...')
    cap = cv2.VideoCapture(url)
    firstFrame = None
    counter = 0  # counter for subsequent motion detections
    while True:
      ret, frame = cap.read()
      if not ret:
          continue

      currentFrame = processFrame(frame)

      # Initialzie firstFrame if not already set
      if firstFrame is None:
          firstFrame = currentFrame
          continue

      # Calculate Difference between Frames
      frameDelta = np.sum(cv2.absdiff(firstFrame, currentFrame))

      # Detect the movement
      movDetected = detectMovement(frameDelta)
      if movDetected:
          logging.info('Movement detected, Delta: ' + str(frameDelta))
          firstFrame = None
          counter += 1
          if counter >= 3:
              logging.info('Announcing ...')
              announce(telegramToken, admins)
              counter = 0
              logging.info('Going to sleep ...')
              sleep(60)
              logging.info('Woke up')




