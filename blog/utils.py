import hashlib
import os.path
from tcd.settings import UPLOAD_DIR, MEDIA_URL


def get_user_path(username):
    m = hashlib.md5()
    m.update(username)
    section = m.hexdigest()[:4]
    return os.path.join(UPLOAD_DIR, section, username)

def get_upload_url(username):
    m = hashlib.md5()
    m.update(username)
    section = m.hexdigest()[:4]
    return "%supload/%s/%s/" % (MEDIA_URL, section, username)
