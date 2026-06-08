import pandas as pd
import requests
# Fetch and Parse Data
r = requests.get('https://nfs.faireconomy.media/ff_calendar_thisweek.json')
cal = r.json()
usd = list(filter(lambda x: x['country']=='USD' and x['impact'] in ('Medium', 'High'), cal))
usd_news = pd.json_normalize(usd).drop(['forecast', 'previous','country'], axis=1)
usd_news['date'] = pd.to_datetime(usd_news['date'])
# Handle time zone shifting to Lagos
usd_news = usd_news.set_index('date').tz_convert('Africa/Lagos').reset_index()
# Construct the payload for your Google Apps Script Web App
payload = []
for _, row in usd_news.iterrows():
    # Format dates correctly to ISO string for Google Calendar API
    start_dt = row['date'].isoformat()
    # Assume event lasts 15 minutes
    end_dt = (row['date'] + pd.Timedelta(minutes=15)).isoformat()
    
    payload.append({
        "title": f"[{row['impact']}] {row['title']}",
        "startTime": start_dt,
        "endTime": end_dt,
        "impact": row['impact']
    })
# Deploy to your Google Web App URL
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbw9OAjgMKRXlV_68WvbU8Hw2w0-A_lgJ0VTuxKDIuADLeV6ShUZ-SKyvMc-zNw_v2Sx/exec"
response = requests.post(WEBAPP_URL, json=payload)
print(f"Status: {response.status_code}, Response: {response.text}")
