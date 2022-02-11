from vbcore.sendmail import SendMail, SMTPParams

if __name__ == "__main__":
    client = SendMail(SMTPParams(host="localhost", port=25))
    response = client.send_message(
        subject="TEST MAIL",
        to="test@localhost",
        sender="sender@localhost",
        html="<h1>TEST</h1>",
        text="TEST MAIL",
    )
    print(response)
