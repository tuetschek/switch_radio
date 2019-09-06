import logging
import os
import sqlite3

from flask import Flask, json
from flask_ask import Ask, session, statement, audio, current_stream

app = Flask(__name__)
ask = Ask(app, "/")
logger = logging.getLogger('flask_ask')
logging.getLogger('flask_ask').setLevel(logging.INFO)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'switch_radio.sqlite')

STREAMS = {
    'czech radio one': 'https://api.play.cz/radio/cro1-128.mp3.m3u',
    'NDR culture': 'https://www.ndr.de/resources/metadaten/audio/m3u/ndrkultur.m3u',
    'beat': 'https://api.play.cz/radio/beat128.mp3.m3u',
    'BBC one': 'https://www.listenlive.eu/bbcradio1.m3u',
    'BBC two': 'https://www.listenlive.eu/bbcradio2.m3u',
}
DEFAULT_STATION = list(STREAMS.keys())[0]


@ask.launch
def launch():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute('SELECT * FROM stations WHERE uid = ?', (session.user.userId, ))
    station = c.fetchall()
    if not station:
        station = DEFAULT_STATION
        logger.info('INS uid = %s station = %s' % (session.user.userId, station))
        c.execute('INSERT INTO stations(uid, station) VALUES (?, ?)', (session.user.userId, station))
        db.commit()
    else:
        station = station[0][1]
    db.close()
    return audio().play(STREAMS[station])


@ask.intent('Tune', mapping={'station': 'station'})
def tune(station):
    if station not in STREAMS:
        return statement('I\'m sorry, I don\'t know the station "%s"' % station)

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    logger.info('UPD uid = %s station = %s' % (session.user.userId, station))
    c.execute('UPDATE stations SET station = ? WHERE uid = ?', (station, session.user.userId))
    db.commit()
    db.close()
    return audio().play(STREAMS[station])


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio().stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio().resume()


@ask.intent('AMAZON.StopIntent')
def stop():
    return audio().clear_queue(stop=True)


# optional callbacks
@ask.on_playback_started()
def started(offset, token):
    _infodump('STARTED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('STARTED Audio stream from {}'.format(current_stream.url))


@ask.on_playback_stopped()
def stopped(offset, token):
    _infodump('STOPPED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('Stream stopped playing from {}'.format(current_stream.url))


@ask.on_playback_nearly_finished()
def nearly_finished():
    _infodump('Stream nearly finished from {}'.format(current_stream.url))


@ask.on_playback_finished()
def stream_finished(token):
    _infodump('Playback has finished for stream with token {}'.format(token))


@ask.session_ended
def session_ended():
    return "{}", 200


def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    logger.info(msg)


if __name__ == '__main__':
    # create database
    if not os.path.isfile(DB_FILE):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        c.execute('CREATE TABLE stations (uid varchar(256), station varchar(256))')
        db.commit()
        db.close()
    app.run(debug=True)
