import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import time
LOGIN_URL = "https://infomentor.se/swedish/production/mentor/"
TIMETABLE_URL = "https://hub.infomentor.se/timetable/timetable/gettimetablelist"
TIME_REGISTRATION_URL = "https://hub.infomentor.se/TimeRegistration/TimeRegistration/GetTimeRegistrations"

def get_next_month_range():
    today = datetime.now()
    start = today.date()
    # Add 1 month (approximate as 30 days for simplicity, or use dateutil.relativedelta for exact)
    try:
        from dateutil.relativedelta import relativedelta
        end = (today + relativedelta(months=1)).date()
    except ImportError:
        end = (today + timedelta(days=30)).date()
    return start.isoformat(), end.isoformat()

def get_utc_offset_minutes():
    # time.altzone is negative of offset in seconds
    if time.localtime().tm_isdst and time.daylight:
        offset = -time.altzone
    else:
        offset = -time.timezone
    return int(offset / 60)

class InfomentorApi:
    def __init__(self, username, password):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })
        self._username = username
        self._password = password
        self._logged_in = False

    def login(self):
        resp = self._session.get(LOGIN_URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        post_url = form["action"] if form and form.has_attr("action") else LOGIN_URL
        post_url = urljoin(LOGIN_URL, post_url)
        data = {}
        for tag in soup.find_all("input", {"type": "hidden"}):
            if tag.has_attr("name"):
                data[tag["name"]] = tag.get("value", "")
        data["login_ascx$txtNotandanafn"] = self._username
        data["login_ascx$txtLykilord"] = self._password
        data["login_ascx$btnLogin"] = "Logga in"
        resp = self._session.post(post_url, data=data, allow_redirects=True)
        # Handle OpenID/OAuth callback forms if present
        while True:
            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form", {"id": "openid_message"})
            if not form:
                break
            action = form["action"]
            action = urljoin(post_url, action)
            oauth_token = form.find("input", {"name": "oauth_token"})["value"]
            resp = self._session.post(action, data={"oauth_token": oauth_token}, allow_redirects=True)
        # Save debug HTML if needed
        # with open("/config/infomentor_login_debug_final.html", "w", encoding="utf-8") as f:
        #     f.write(resp.text)
        if "Logga ut" not in resp.text and "logout" not in resp.text.lower():
            raise Exception("Infomentor login failed")
        self._logged_in = True
        # Try to select pupil if needed
        self._select_pupil(resp.text)

    def _select_pupil(self, html):
        # Try to find a switchPupilUrl in the HTML and GET it if present
        import re
        match = re.search(r'"switchPupilUrl":"(https://hub\.infomentor\.se/Account/PupilSwitcher/SwitchPupil/\d+)"', html)
        if match:
            url = match.group(1).replace('\\/', '/')
            self._session.get(url)

    def get_timetable(self):
        if not self._logged_in:
            self.login()
        start, end = get_next_month_range()
        utc_offset = get_utc_offset_minutes()
        payload = {
            "UTCOffset": str(utc_offset),
            "start": start,
            "end": end,
        }
        resp = self._session.post(TIMETABLE_URL, data=payload)
        resp.raise_for_status()
        return resp.json()

    def get_time_registrations(self, date=None):
        if not self._logged_in:
            self.login()
        import json
        from datetime import datetime
        if date is None:
            date = datetime.now().strftime("%Y-%m-%dT00:00:00.000Z")
        payload = {
            "date": date,
            "showNextWeekIfNoMoreSchoolDays": True
        }
        resp = self._session.post(TIME_REGISTRATION_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()