Intro
=====

**secret-santa** can help you manage a list of secret santa participants by
randomly assigning pairings and sending emails. It can avoid pairing 
couples to their significant other, and allows custom email messages to be 
specified.

Dependencies
------------

pytz
pyyaml

Usage
-----

Copy config.yml.template to config.yml and enter in the connection details 
for your outgoing mail server. Modify the participants and couples lists and 
the email message if you wish.

    cd secret-santa/
    cp config.yml.template config.yml

Here is the example configuration unchanged:

    # Required to connect to your outgoing mail server. Example for using gmail:
    # gmail
    SMTP_SERVER: smtp.gmail.com
    SMTP_PORT: 587
    USERNAME: you@gmail.com
    PASSWORD: "you're-password"

    TIMEZONE: 'Europe/Moscow'

    PARTICIPANTS:
      - Ivan <ivan@somewhere.net>
      - Anton <anton@gmail.net>
      - Anna <Anna@somedomain.net>
      - Tanya <Tanya@hi.org>

    # Warning -- if you mess this up you could get an infinite loop
    DONT-PAIR:
      - Ivan, Anna    # Ivan and Anna are married
      - Anton, Ivan   # Anton and Ivan are best friends
      - Kostya, Rail

    # From address should be the organizer in case participants have any questions
    FROM: Secret Santa <you@gmail.net>

    # Both SUBJECT and MESSAGE can include variable substitution for the 
    # "santa" and "santee"
    SUBJECT: Your secret santa recipient is {santee}
    MESSAGE: 
      <b>Dear {santa}</b>,
      <br><br>
      This year you are <b>{santee}'s</b> Secret Santa!. Ho Ho Ho!
      <br><br>
      Send some gift to wish you a Happy New Year.
      <br><br>
      {secret_santa_image}
      <br><br>
      This message was automagically generated from a computer. 
      <br><br><br><br>
      https://github.com/davydovk/secret-santa

Once configured, call secret-santa:

    python secret_santa.py

Calling secret-santa without arguments will output a test pairing of 
participants.

        Test pairings:

        Anna --> Rail
        Rail --> Ivan
        Anton --> Kostya
        Ivan --> Anna
        Kostya --> Artem
        Artem --> Anton

        To send out emails with new pairings,
        call with the --send argument:

            $ python secret_santa.py --send

To send the emails, call using the `--send` argument

    python secret_santa.py --send