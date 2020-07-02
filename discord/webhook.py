import urllib.request
import logging
import json


class Discord():
    def __init__(self, webhook):
        self.webhook_url = webhook

    def send(self, msg):
        payload = {
            "content": msg
        }
        j = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PSEGBot"
        }
        req = urllib.request.Request(url=self.webhook_url,
                                     method="POST", headers=headers)
        try:
            resp = urllib.request.urlopen(req, data=j)
            if resp.status != 204:
                e = "Webhook invocation failed. {} - {}".format(
                    resp.status, resp.msg)
                logging.error(e)
        except:
            e = "Webhook invocation failed. {} - {}".format(
                resp.status, resp.msg)
            logging.error(e)

    def error(self, msg):
        msg_txt = "Failed to get next PSE&G meter reading date. ```{}```".format(
            msg)
        self.send(msg_txt)
