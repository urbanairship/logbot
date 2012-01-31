#!/usr/bin/env python
"""
An example IRC log bot - logs a channel's events to a file.

This was compiled from a couple of examples on the internet while
Gavin was watching StarTrek: don't judge.

If someone says the bot's name in the channel followed by a ':',
e.g.

  <foo> logbot: hello!

the bot will reply:

  <logbot> foo: I am a log bot

Run this script with two arguments, the channel name the bot should
connect to, and file to log to, e.g.:

  $ python ircLogBot.py test test.log

will log channel #test to the file 'test.log'.
"""
# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys



class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "logbot"

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        for channel in self.channels:
            self.loghandles[channel] = MessageLogger(open(self.filename[channel], "a"))
            self.loghandles[channel].log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        for channel in self.channels:
            self.loghandles[channel].log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
            self.loghandles[channel].close()

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for channel in self.factor.channels:
            self.join(channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.loghandles[channel].log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.loghandles[channel].log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: view logs at https://logs.urbanairship.com/" % user
            self.msg(channel, msg)
            self.loghandles[channel].log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = LogBot

    def __init__(self, channels):
        """Create a bot that listens on a set of channels.

        channels: list of str, names of channels to join
        """
        self.channels = channels
        self.filenames = {} # Probably redundant.
        self.loghandles = {}
        for channel in channels:
            self.filenames[channel] = "logs/%s.log" % (channel,)

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


def main():
    log.startLogging(sys.stdout)

    channels = sys.argv[1].split()
    # create factory protocol and application
    bot = LogBotFactory(channels)
    # connect factory to this host and port
    reactor.connectTCP("localhost", 6667, bot)

    # run bot
    reactor.run()
