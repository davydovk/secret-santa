import datetime
import getopt
import os
import random
import re
import smtplib
import socket
import sys
import time
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import pytz
import yaml

help_message = '''
To use, fill out config.yml with your own participants. You can also specify 
DONT-PAIR so that people don't get assigned their significant other.

You'll also need to specify your mail server settings. An example is provided
for routing mail through gmail.

For more information, see README.
'''

REQUIRED = (
    'SMTP_SERVER',
    'SMTP_PORT',
    'USERNAME',
    'PASSWORD',
    'TIMEZONE',
    'PARTICIPANTS',
    'DONT-PAIR',
    'FROM',
    'SUBJECT',
    'MESSAGE',
)

HEADER = '''
Date: {date}
Content-Type: text/plain; charset="utf-8"
Message-Id: {message_id}
From: {frm}
To: {to}
Subject: {subject}
        
'''

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')


class Person:
    def __init__(self, name, email, invalid_matches):
        self.name = name
        self.email = email
        self.invalid_matches = invalid_matches

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Pair:
    def __init__(self, giver, receiver):
        self.giver = giver
        self.receiver = receiver

    def __str__(self):
        return f'{self.giver.name} --> {self.receiver.name}'


def parse_yaml(yaml_path=CONFIG_PATH):
    return yaml.full_load(open(yaml_path))


def choose_receiver(giver, receivers):
    choice = random.choice(receivers)
    if choice.name in giver.invalid_matches or giver.name == choice.name:
        if len(receivers) == 1:
            raise Exception('Only one receiver left, try again')
        return choose_receiver(giver, receivers)
    else:
        return choice


def create_pairs(giver, receiver_):
    givers = giver[:]
    receivers = receiver_[:]
    pairs = []

    for giver in givers:
        try:
            receiver = choose_receiver(giver, receivers)
            receivers.remove(receiver)
            pairs.append(Pair(giver, receiver))

        except Exception:
            return create_pairs(giver, receiver_)

    return pairs


class Usage(Exception):
    def __init__(self, message):
        self.msg = message


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'shc', ['send', 'help'])

        except getopt.error as msg:
            raise Usage(msg)

        send = False

        for option, value in opts:
            if option in ('-S', '--send'):
                send = True
            elif option in ('-H', '--help'):
                raise Usage(help_message)

        config = parse_yaml()

        for key in REQUIRED:
            if key not in config.keys():
                raise Exception(f'Required parameter {(key,)} not in yaml config file!')

        participants = config['PARTICIPANTS']
        dont_pair = config['DONT-PAIR']

        if len(participants) < 2:
            raise Exception('Not enough participants specified.')

        givers = []

        for person in participants:
            name, email = re.match(r'([^<]*)<([^>]*)>', person).groups()
            name = name.strip()
            invalid_matches = []
            for pair in dont_pair:
                names = [n.strip() for n in pair.split(',')]
                if name in names:
                    for member in names:
                        if name != member:
                            invalid_matches.append(member)
            person = Person(name, email, invalid_matches)
            givers.append(person)

        receivers = givers[:]
        pairs = create_pairs(giver=givers, receiver_=receivers)

        test_pairs = ('\n'.join([str(p) for p in pairs]))
        text_not_send = f'Test pairs:\n\n' \
                        f'{test_pairs}\n\n' \
                        f'To send out emails with new pairings,\n' \
                        f'call with the --send argument:\n\n' \
                        f'$ python secret_santa.py --send'
        if not send:
            print(text_not_send)

        if send:
            server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
            server.starttls()
            server.login(config['USERNAME'], config['PASSWORD'])
        for pair in pairs:
            zone = pytz.timezone(config['TIMEZONE'])
            now = zone.localize(datetime.datetime.now())
            date = now.strftime('%a, %d %b %Y %T %Z')
            message_id = f'<{str(time.time()) + str(random.random())}@{socket.gethostname()}>'

            msg = MIMEMultipart()
            msg['Subject'] = config['SUBJECT'].format(santee=pair.receiver.name)
            msg['From'] = config['FROM']
            msg['To'] = pair.giver.email

            text = MIMEText(config['MESSAGE'].format(santa=pair.giver.name, santee=pair.receiver.name,
                                                     secret_santa_image='<img src="cid:my_image">'), 'html')
            msg.attach(text)

            image = MIMEImage(open('secret-santa.jpg', 'rb').read())
            image.add_header('Content-ID', '<my_image>')
            msg.attach(image)

            html_part = MIMEMultipart(_subtype='related')
            body = MIMEText('<p>Hello <img src="cid:myimage" /></p>', _subtype='html')
            html_part.attach(body)

            frm = config['FROM']
            to = pair.giver.email
            if send:
                server.sendmail(frm, [to], msg.as_string())
                print(f'Emailed {pair.giver.name} <{to}>')

            # frm = config['FROM']
            # to = pair.giver.email
            # subject = config['SUBJECT'].format(santa=pair.giver.name, santee=pair.receiver.name)

            # body = (HEADER + config['MESSAGE']).format(
            #     date=date,
            #     message_id=message_id,
            #     frm=frm,
            #     to=to,
            #     subject=subject,
            #     santa=pair.giver.name,
            #     santee=pair.receiver.name,
            # )
            # if send:
            #     server.sendmail(frm, [to], body)
            #     print(f'Emailed {pair.giver.name} <{to}>')

        if send:
            server.quit()

    except Usage as err:
        print(sys.stderr, sys.argv[0].split("/")[-1] + ': ' + str(err.msg))
        print(sys.stderr, '\t for help use --help')
        return 2


if __name__ == '__main__':
    sys.exit(main())
