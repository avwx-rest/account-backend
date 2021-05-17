"""
App and global resources
"""

from fastapi import FastAPI
from fastapi_mail import FastMail, ConnectionConfig
from mailchimp3 import MailChimp
from motor.motor_asyncio import AsyncIOMotorClient

from account.config import CONFIG

mail_conf = ConnectionConfig(
    MAIL_USERNAME=CONFIG.MAIL_USERNAME,
    MAIL_PASSWORD=CONFIG.MAIL_PASSWORD,
    MAIL_FROM=CONFIG.MAIL_SENDER,
    MAIL_PORT=CONFIG.MAIL_PORT,
    MAIL_SERVER=CONFIG.MAIL_SERVER,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

app = FastAPI()
app.db = AsyncIOMotorClient(CONFIG.MONGO_URI, uuidRepresentation="standard").account
# app.mc = MailChimp(mc_api=CONFIG.MC_KEY, mc_user=CONFIG.MC_USERNAME)
# app.mail = FastMail(mail_conf)
