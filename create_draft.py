import sys
sys.path.insert(0, r"C:\workspace\google-tools")
from gmail_tool import authenticate, ACCOUNTS
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

def create_draft(account_name, to, subject, body):
    account = next(a for a in ACCOUNTS if a["name"] == account_name)
    creds = authenticate(account["token"])
    service = build("gmail", "v1", credentials=creds)

    msg = MIMEText(body, "html")
    msg["To"] = to
    msg["Subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()
    print(f"Draft created successfully. Draft ID: {draft['id']}")

TH = 'style="background-color:#2c3e50;color:#ffffff;padding:8px 12px;text-align:left;border:1px solid #2c3e50;font-family:Arial,sans-serif;font-size:14px;"'
TD = 'style="padding:8px 12px;border:1px solid #999;font-family:Arial,sans-serif;font-size:14px;"'
TD_ALT = 'style="padding:8px 12px;border:1px solid #999;background-color:#f2f2f2;font-family:Arial,sans-serif;font-size:14px;"'

BODY = f"""<div style="font-family:Arial,sans-serif;font-size:14px;color:#222;line-height:1.6;">

<p>Hello Laila and everyone,</p>

<p>Hope this email finds you well.</p>

<p>Attached to this email is the result of my testing and observations for both AccuRad and RDS from the period of March 30 to April 12, 2026.</p>

<p>That said, please refer to the test parameters as seen below.</p>

<table style="border-collapse:collapse;width:100%;margin:16px 0;">
  <thead>
    <tr>
      <th {TH}>Item</th>
      <th {TH}>AccuRad Android</th>
      <th {TH}>AccuRad iOS</th>
      <th {TH}>RDS Android</th>
    </tr>
  </thead>
  <tbody>
    <tr><td {TD}>App version</td><td {TD}>2.11.0</td><td {TD}>2.11.0(4)</td><td {TD}>2.1.0.7</td></tr>
    <tr><td {TD_ALT}>OS version</td><td {TD_ALT}>Android 16</td><td {TD_ALT}>iOS 26.3.1(a)</td><td {TD_ALT}>Android 16</td></tr>
    <tr><td {TD}>Device model</td><td {TD}>Samsung Galaxy S22</td><td {TD}>iPhone 12 Pro Max</td><td {TD}>Samsung Galaxy S22</td></tr>
    <tr><td {TD_ALT}>Device usage</td><td {TD_ALT}>Secondary device</td><td {TD_ALT}>Daily driver</td><td {TD_ALT}>Secondary device</td></tr>
    <tr><td {TD}>Connection type</td><td {TD}>Opened</td><td {TD}>Opened</td><td {TD}>N/A</td></tr>
  </tbody>
</table>

<h3 style="color:#2c3e50;margin-top:24px;margin-bottom:4px;">AccuRad iOS &ndash; Observations</h3>

<p>Testing for AccuRad iOS version 2.11.0(4) was carried out on the iPhone 12 Pro Max as a daily driver throughout the testing period.</p>

<p>Overall, connectivity with PRD 000003 was relatively stable, though the pattern varied across the two-week period. During the first several days (March 30 through April 4), the 30-MIN graph showed sparse and intermittent data with limited alarm capture, which is consistent with the phone being further from the PRD during that stretch, along with the natural Bluetooth interference from the consistently crowded environment I test in.</p>

<p>From April 5 onward, connectivity improved considerably and alarm capture resumed daily. On April 7 and April 8 in particular, the app showed notably strong performance &mdash; the graph on April 7 was dense and continuous across the afternoon and evening, while April 8 displayed dense data from morning through evening across multiple time windows. The app consistently re-established the Bluetooth connection on its own following any brief disconnections, without requiring manual intervention.</p>

<p>Alarm capture across the second half of the period was consistent, with multiple High Alarms logged across several days and values generally ranging from 5 to 9 microRem/h. The highest reading of the period was 14.3 microRem/h on April 8 (08:00&ndash;08:02 PM, 35 seconds). A Low Alarm was also captured on April 9 (4.1 microRem/h, 07:34&ndash;07:36 PM, 54 seconds). All alarm events were accurately timestamped and categorized throughout the period. No critical bugs or unexpected behaviors were observed.</p>

<h3 style="color:#2c3e50;margin-top:24px;margin-bottom:4px;">AccuRad Android &ndash; Observations</h3>

<p>Testing for AccuRad Android version 2.11.0 was carried out on the Samsung Galaxy S22 as a secondary device, with the connection open throughout the testing period from March 30 through April 10, 2026.</p>

<p>The Android version generally demonstrated stronger and more consistent background Bluetooth performance compared to iOS, particularly during the second week. Dense, continuous data was observed on March 30, April 6, April 7, April 8, and April 9. April 7 was a standout day with data recorded from as early as 4 AM through midnight, reflecting near-continuous PRD connectivity (ACR00002F).</p>

<p>During the earlier part of the period (March 31 through April 2), some daytime windows showed sparse or isolated data points rather than a continuous line, with connectivity improving in the evenings. The daytime gaps likely corresponded to periods when the device was out of PRD range, as alarms were still captured once the connection re-established in the evening. No screenshots were captured for April 4 and April 5. From April 6 onward, the graph was consistently dense throughout each day's active windows.</p>

<p>Alarm capture was steady across all active testing days, with High Alarms logged consistently and readings ranging from 3.3 to 7.3 microRem/h. A notably longer-duration alarm was captured on April 8 (7.1 microRem/h, 08:24&ndash;08:25 PM, 52 seconds).</p>

<h3 style="color:#2c3e50;margin-top:24px;margin-bottom:4px;">RDS Android &ndash; Observations</h3>

<p>Testing for RDS Android version 2.1.0.7 was carried out on the Samsung Galaxy S22 as a secondary device.</p>

<p>The RDS-32 (SN: 2001638) connected successfully on April 12, with the home screen confirming an accumulated dose of 36.8 mrem and a live reading of 4 &micro;Rem/h. Battery was at full charge during the session. The 5-MIN dose rate graph in the Events tab showed a stepped pattern starting from approximately 5:55 PM, accurately reflecting dose accumulation over the session. The map view displayed the current location marker during stationary use. No gradient path was visible, which is consistent with background radiation levels at approximately 4 &micro;Rem/h &mdash; below the visible threshold on the color scale, which starts at 5.0 &micro;Rem/h. No issues were observed with connectivity or dose tracking.</p>

<p>As for the screenshots, please refer to the URL below:<br>
<a href="https://drive.google.com/drive/folders/1uCpnDglGeokc0MIK-3AF77PlTeNMJNIX?usp=sharing" style="color:#2980b9;">https://drive.google.com/drive/folders/1uCpnDglGeokc0MIK-3AF77PlTeNMJNIX?usp=sharing</a></p>

<p>Best regards,<br>Jackie</p>

</div>"""

if __name__ == "__main__":
    create_draft(
        account_name="Freelance",
        to="lmartinez@teamitr.com",
        subject="Re: AccuRad & RDS Testing (Android & iOS)",
        body=BODY
    )
