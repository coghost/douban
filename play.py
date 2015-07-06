#!/usr/bin/env python3.4
__author__ = 'lfp <lihex.go@gmail.com>'
__date__ = '15-7-3 下午1:49'
__version__ = '0.0.1'

import urllib
import urllib.request
import urllib.parse
import urllib.error
import json
import os
import subprocess
import time
import sys
import threading

_uri = {
    'base': 'http://douban.fm',
    'channel': '/j/app/radio/channels',
    'image_pth': '/tmp/douban/images/',
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
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('cl/clean', '', '', '', 'clean mplayer process. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('sc/setchannel', '', '', '', 'set channel. '))
    print('\t{:<8}{:<8}{:<8}\n{:16}{:>16}'.format('l/playlist', '', '', '', 'show current channel and playlist. '))
    print('\t{:<8}{:>16}{:<8}\n{:16}{:>16}'.format('p/n/play/next', 'channel_id(optional)', '', '',
                                                   'running play songs. '))
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


def play(cnl_id, songs_in, curr):
    # s = _get_playlist(cnl)['song'][0]

    while True:
        s, songs_in = _get_song(cnl_id, songs_in)
        curr['song'] = s
        _get_picture(s)
        _to_play(s)
        time.sleep(s['length'])


def th_play(cnl_id, songs_in, curr):
    global threads
    t1 = threading.Thread(target=play, args=(cnl_id, songs_in, curr,))
    threads.append(t1)
    t1.daemon = True
    t1.start()


def clean_mplay_proc():
    subprocess.call('killall mplayer', shell=True)
    # print('clean all alived mplayer process. if you use mplayer other place, i can only say sorry...')


def _to_play(song):
    global player
    # _p = 'mplayer {} < /dev/null > /dev/null 2>&1 & '.format(song['url'])
    # print(_p)
    # player = subprocess.Popen([_p])
    # player = subprocess.call(_p, shell=True)
    player = subprocess.Popen(['mplayer', song['url']], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    print(
        '歌曲: {:<16}歌手: {:<16}专辑: {:<16}评分: {:<16} 长度: {:>8}s'.format(song['title'], song['artist'], song['albumtitle'],
                                                                     song['rating_avg'], song['length']))
    print('url: {}'.format(song['url']))
    # time.sleep(song['length'])
    # player.kill()
    return player


def _to_pause():
    global player
    if player:
        player.wait()


def _to_resume():
    global player
    if player:
        player.wait()


def _to_stop():
    global player
    # stop_all_threads()
    if player:
        player.kill()
        player = None


def _get_song(cnl, songs_in):
    if len(songs_in) == 0:
        _sl = _get_playlist(cnl)['song']
        songs_in.extend(_sl)

    song = songs_in[0]
    del songs_in[0]
    return song, songs_in


def _play_next(cnl_id, songs_in, curr):
    _to_stop()
    clean_mplay_proc()
    th_play(cnl_id, songs_in, curr)


def get_cnl(cnls, idx):
    for _cn in cnls['channels']:
        if int(_cn['channel_id']) == idx:
            return _cn

    return None


def show_cnl(cnl):
    print(cnl)
    if cnl is not None:
        print('当前channel: {}: {}'.format(cnl['channel_id'],
                                         cnl['name']))


def show_song(songs_lst, current_song):
    song_lst = []
    if len(songs_lst) > 0:
        song_lst = songs_lst
    elif current_song is not None:
        song_lst.append(current_song)
    else:
        print('当前没有播放歌曲!')

    if len(song_lst) > 0:
        for sg in song_lst:
            print(
                '歌曲: {:<16}歌手: {:<16}专辑: {:<32}评分: {:<16}长度: {:>8}s'.format(sg['title'], sg['artist'], sg['albumtitle'],
                                                                            sg['rating_avg'], sg['length']))
            print('url: {}'.format(sg['url']))


def t_alist(alist):
    del alist[0]


def __test():
    a_lst = ['a', 'b', 'c']
    print(a_lst)
    t_alist(a_lst)
    print(a_lst)


if __name__ == '__main__':
    _cnls = _get_channel()
    _song_idx = 0
    _songs = []
    _curr = {
        'channel_id': 0,
        'cnl': None,
        'song': None
    }

    while True:
        try:
            chioses = input('-->: ')
            chiose = chioses.rstrip().split(' ')
        except EOFError:
            print('\n why EOF')
            sys.exit(100)

        if chiose[0] in ['c', 'channel']:
            if len(_cnls) == 0:
                _cnls = _get_channel()

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

        if chiose[0] in ['sc', 'setchannel'] and len(chiose) == 2:
            _curr['cnl'] = get_cnl(_cnls, int(chiose[1]))
            show_cnl(_curr['cnl'])
            continue

        if chiose[0] in ['l', 'playlist']:
            show_cnl(_curr['cnl'])
            show_song(_songs, _curr['song'])
            continue

        if chiose[0] in ['h', 'help']:
            print_usg()
            continue

        if chiose[0] in ['p', 'play', 'n', 'next']:
            if len(chiose) == 2:
                _curr['channel_id'] = int(chiose[1])

            _play_next(_curr['channel_id'], _songs, _curr)
            continue

        if chiose[0] in ['s', 'stop']:
            _to_stop()
            continue

        if chiose[0] in ['cl', 'clean']:
            clean_mplay_proc()
            continue

        if chiose[0] in ['q', 'quit']:
            _to_stop()
            clean_mplay_proc()
            sys.exit(0)
