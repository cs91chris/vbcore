from vbcore.net.sendmail import SendMail, SMTPParams

params = SMTPParams(
    host="localhost",
    port=25,
)

if __name__ == "__main__":
    client = SendMail(params)
    response = client.send_message(
        subject="TEST MAIL",
        to="test@localhost",
        sender="sender@localhost",
        html="<h1>TEST</h1>",
        text="TEST MAIL",
    )
    print(response)
