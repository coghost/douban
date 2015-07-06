#!/usr/bin/env python3.4
__author__ = 'lfp <lihex.go@gmail.com>'
__date__ = '15-7-3 下午1:49'
__version__ = '0.0.1'

import urllib
import urllib.request
import urllib.parse
import json
import os
import subprocess
import time
import sys
import threading

_uri = {
    'base': 'http://douban.fm',
    'channel': '/j/app/radio/channels',
    'image_pth': '/home/lfp/tmp/douban/images/',
    'playlist': '/j/mine/playlist?type=n&sid=1024291&pt=21.1&pb=128&from=mainsite&r=df3fde8194&channel='
}

player = None
threads = []


def print_usg():
    print('\x1B[1;37;40m')
    print('Usage: aas [OPTION]... [SCRIPT]...')
    print()
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('h/help', '', '', '', 'show all usages. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('c/channel', '', '', '', 'get channel. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('l/playlist', '', '', '', 'get playlist. '))
    print('\t{:<8}{:>16}{:<8}\n{:16}{:>16}'.format('p/play', 'channel_id', '', '', 'running play songs. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('s/stop', '', '', '', 'stop playing. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('q/quit', '', '', '', 'quit . '))
    print('\x1B[0m')


def h_get(url, para):
    succ = False
    buffers = None
    try:
        res = urllib.request.urlopen(url + para)
        buffers = res.read().decode('utf-8')
        if buffers is not None:
            succ = True
        else:
            print('cannot load remote url:' + url + para)
    except urllib.error.URLError as err:
        print(err)
    finally:
        return succ, buffers


def _get_channel():
    __ur = _uri['base'] + _uri['channel']
    # print(__ur)
    # __ur = 'http://192.168.6.112:5000'
    # _suc, buf = h_get(_uri['base'] + _uri['channel'], '')
    _suc, buf = h_get(__ur, '')
    buf = json.loads(buf)
    # print(buf)
    return buf


def _get_playlist(cnl=0):
    __url = _uri['base'] + _uri['playlist'] + str(cnl)
    print(__url)
    _suc, buf = h_get(__url, '')
    buf = json.loads(buf)
    # print(buf)
    return buf


def _get_picture(song):
    _pic = _uri['image_pth'] + song['picture'].split('/')[4]
    print(_pic)

    if not os.path.exists(_pic):
        subprocess.call(['wget', '-P', _uri['image_pth'], song['picture']])

    subprocess.call(
        ['notify-send', '-i', _pic, song['title'], song['artist'] + '\n' + song['albumtitle']])


def play(s):
    # s = _get_playlist(cnl)['song'][0]
    _get_picture(s)
    _to_play(s)
    time.sleep(s['length'])


def th_play(s):
    global threads
    t1 = threading.Thread(target=play, args=(s,))
    threads.append(t1)
    t1.daemon = True
    t1.start()


def stop_all_threads():
    global threads
    for _t in threads:
        _t.stop()
        _t.join()


def _to_play(song):
    global player
    # _p = 'mplayer {} < /dev/null > /dev/null 2>&1 & '.format(song['url'])
    # print(_p)
    # player = subprocess.Popen([_p])
    # player = subprocess.call(_p, shell=True)
    player = subprocess.Popen(['mplayer', song['url']], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    print('歌曲: {:<16}歌手: {:<16}专辑: {:<16}评分: {:<32}'.format(song['title'], song['artist'], song['albumtitle'],
                                                            song['rating_avg']))
    print('url: {}'.format(song['url']))
    # time.sleep(song['length'])
    # player.kill()
    return player


def _to_stop():
    global player
    stop_all_threads()
    if player:
        player.kill()
        player = None


def _get_song(cnl, songs):
    if len(songs) == 0:
        _sl = _get_playlist(cnl)['song']
        songs.extend(_sl)

    song = songs[0]
    songs = songs[1:]
    return song


def _play_next(cnl, songs):
    _to_stop()
    s = _get_song(cnl, songs)
    th_play(s)


if __name__ == '__main__':
    # _get_channel()
    # _get_playlist()
    #
    # if len(sys.argv) < 2:
    #     print_usg()
    # _cnls = _get_channel()
    _cnl = 1
    _song_idx = 0
    _songs = []

    _s = _get_song(_cnl, _songs)

    while True:
        print_usg()
        print()
        try:
            chioses = input('-->: ')
            chiose = chioses.split(' ')
        except EOFError:
            print('\n why EOF')
            sys.exit(100)
        # print(chiose)

        if chiose[0] in ['t']:
            _c = input('-->: ')
            print(_c)
            continue

        if chiose[0] in ['c', 'channel']:
            _cnls = _get_channel()
            # for _ch in _cnls['channels']:
            #     print('{}: {}'.format(_ch['name'], _ch['channel_id']))
            i = 0
            while i < len(_cnls['channels']):
                if i + 1 < len(_cnls['channels']):
                    print('{:<4}: {:<16}{:<4}: {:<16}'.format(_cnls['channels'][i]['channel_id'],
                                                              _cnls['channels'][i]['name'],
                                                              _cnls['channels'][i + 1]['channel_id'],
                                                              _cnls['channels'][i + 1]['name'], ))
                else:
                    print('{:<4}: {:<16}'.format(_cnls['channels'][i]['channel_id'],
                                                 _cnls['channels'][i]['name']))

                i += 2

            continue

        if chiose[0] in ['l', 'playlist'] and len(chiose) == 2:
            _songs = _get_playlist(chiose[1])['song']

            for _s in _songs:
                print('歌曲: {:<16}歌手: {:<16}专辑: {:<32}评分: {:<16}'.format(_s['title'], _s['artist'], _s['albumtitle'],
                                                                        _s['rating_avg']))
                print('url: {}'.format(_s['url']))

            continue

        if chiose[0] in ['p', 'play'] and len(chiose) == 2:
            _cnl = int(chiose[1])
            _s = _get_song(_cnl, _songs)
            th_play(_s)
            continue

        if chiose[0] in ['s', 'stop']:
            _to_stop()
            continue

        if chiose[0] in ['n', 'next']:
            _play_next(_cnl, _songs)
            continue

        if chiose[0] in ['q', 'quit']:
            _to_stop()
            sys.exit(0)
