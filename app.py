import gradio as gr
import smtplib, ssl
import datetime as dt
import os
from scheduler import Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

TZ_INDIA = dt.timezone(dt.timedelta(hours=5.5))


def now():
    return dt.datetime.now(TZ_INDIA)


def get_password():
    try:
        password = open("password.txt", "r").read()
    except:
        password = os.environ.get('password', None)
    if password is None:
        print(os.environ.keys())
        print("Password not found")
    return password


def send_mail(
    receiver_email="aptcyborg@gmail.com", subject="You need to do something!"
):
    print(f"Sending mail to {receiver_email} at {now()}")
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "contactkhelogames@gmail.com"
    password = get_password()
    message = f"""Subject: REMINDER {subject}

This is a reminder scheduled for {now()}."""
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        print(f"Mail sent to {receiver_email}")


schedule = Scheduler()


def run_jobs():
    schedule.exec_jobs()


def set_reminder_offset(
    year_offset,
    month_offset,
    day_offset,
    hour_offset,
    minute_offset,
    receiver_email,
    subject,
):
    print(
        f"Setting reminder for {year_offset} years, {month_offset} months, {day_offset} days, {hour_offset} hours, {minute_offset} minutes from now"
    )
    schedule.once(
        dt.datetime(
            year=now().year + int(year_offset),
            month=now().month + int(month_offset),
            day=now().day + int(day_offset),
            hour=now().hour + int(hour_offset),
            minute=now().minute + int(minute_offset),
        ),
        send_mail,
        args=[receiver_email, subject],
    )
    return 0, 0, 0, 0, 5, "aptcyborg@gmail.com", None

def set_reminder_specific(year, month, day, hour, minute, receiver_email, subject):
    print(
        f"Setting Specific reminder for {year} years, {month} months, {day} days, {hour} hours, {minute} minutes from now"
    )
    schedule.once(
        dt.datetime(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
        ),
        send_mail,
        args=[receiver_email, subject],
    )
    return now().year, now().month, now().day, now().hour, now().minute, "aptcyborg@gmail.com", None 

with gr.Blocks() as offset:
    with gr.Row():
        subject = gr.Textbox(label="Subject")
        mail = gr.Textbox(label="Mail ID", value="aptcyborg@gmail.com")
    with gr.Row():
        minute = gr.Number(label="Minute", value=0)
        hour = gr.Number(label="Hour", value=0)
    with gr.Accordion("Time", open=False):
        year = gr.Radio([0, 1, 2], label="Year", value=0)
        month = gr.Number(label="Month", value=0)
        day = gr.Number(label="day", value=0)
    btn = gr.Button(value="Set reminder")
    btn.click(set_reminder_offset, [year, month, day, hour, minute, mail, subject], [year, month, day, hour, minute, mail, subject])

with gr.Blocks() as specific:
    with gr.Row():
        subject = gr.Textbox(label="Subject")
        mail = gr.Textbox(label="Mail ID", value="aptcyborg@gmail.com")

    with gr.Row():
        minute = gr.Number(label="Minute", value=now().minute)
        hour = gr.Number(label="Hour", value=now().hour)
        day = gr.Number(label="day", value=now().day)
        month = gr.Number(label="Month", value=now().month)
        year = gr.Number(label="Year", value=now().year)
    btn = gr.Button(value="Set reminder")
    btn.click(
        set_reminder_specific, [year, month, day, hour, minute, mail, subject], [year, month, day, hour, minute, mail, subject]
    )


tabbed_interface = gr.TabbedInterface(
    [offset, specific],
    ["Timer", "Calender"],
)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_jobs, trigger="interval", seconds=30)
    scheduler.start()
    tabbed_interface.launch()
