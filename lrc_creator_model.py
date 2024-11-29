import requests
from bs4 import BeautifulSoup
import os
import urllib
import json

def crawling_lrc(available_files, progressBar):
    if len(available_files) == 0: return
    row_index = 0
    
    for row in available_files:
        progressBar.setValue(row_index)
        row_index = row_index + 1
        
        # 태그가 부족하거나 LRC 파일이 이미 있는 경우 제외 처리
        if row['flag'] == 0 or row['lrc_status'] == 1: continue
        
        soup_artist = BeautifulSoup(requests.get('https://music.bugs.co.kr/search/artist?q=%s' % row['artist']).text, 'html.parser')
        soup_album = BeautifulSoup(requests.get('https://music.bugs.co.kr/search/album?q=%s %s' % (row['artist'], row['album'])).text,'html.parser')
        soup_track = BeautifulSoup(requests.get('https://music.bugs.co.kr/search/track?q=%s %s' % (row['artist'], row['title'])).text,'html.parser')
        
        # 검색 결과 없음 처리
        if not (soup_artist.select('#container > section > div > ul > li:nth-of-type(1) > figure > figcaption > a.artistTitle')
                and soup_album.select('#container > section > div > ul > li:nth-of-type(1) > figure')):
            continue
        
        # 아티스트 결과
        for id in soup_artist.select('#container > section > div > ul > li:nth-of-type(1) > figure > figcaption > a.artistTitle'):
            artist_artistid = id['href'][32:-25]
            
        # 앨범검색 결과    
        for id in soup_album.select('#container > section > div > ul > li:nth-of-type(1) > figure'):
            album_artistid = id['artistid']
            #album_albumid = id['albumid']
        
        for id in soup_track.find_all("tr"):
            if id.get('artistid'):
                row['track_artistid'].append(id.get('artistid'))
            if id.get('albumid'):
                row['track_albumid'].append(id.get('albumid'))
            if id.get('trackid'):
                row['track_trackid'].append(id.get('trackid'))
        
        if artist_artistid == album_artistid and artist_artistid in row['track_artistid']:
            n = row['track_artistid'].index(artist_artistid)
            urllib.request.urlretrieve('http://api.bugs.co.kr/3/tracks/%s/lyrics?&api_key=b2de0fbe3380408bace96a5d1a76f800' % row['track_trackid'][n],"%s.lrc" % row['file_name'])
            with open('%s.lrc' % row['file_name'], encoding='UTF8') as json_file:
                data = json.load(json_file)
            fail_flag = True
            if data['result'] is not None:  # 싱크 가사 있을 때,
                if "|" in data['result']['lyrics']:  # time이 있을 때,
                    try:
                        lrc_maker(row['file_name'], data)
                        fail_flag = False
                    except:
                        fail_flag = True
            # time/싱크가사 없거나 파일 생성 오류 처리
            if fail_flag:
                os.remove('%s.lrc' % row['file_name'])

def lrc_maker(file_name, data):
    mm = []
    ss = []
    xx = []
    TIME = []
    LYRICS = []
    TEXT = []
    
    TEXT = data['result']['lyrics']
    TEXT = TEXT.replace("＃", "\n")
    x = TEXT.count("|")
    
    # 크롤링 결과 값을 로컬 파일로 저장
    with open('%s.lrc' % file_name, 'w', encoding='UTF8') as file:  # 덮어씌우기
        file.write(TEXT)
    
    # 재사용 전 초기화
    TEXT = []
    
    with open('%s.lrc' % file_name, 'r', encoding='UTF8') as file:  # 한줄씩 읽어오기
        for j in range(0, x):
            TEXT.append(file.readline().rstrip())
            
    for j in range(0, x):  # 시간과 가사 구분하기
        TIME.append(float(TEXT[j][:TEXT[j].rfind("|")]))
        LYRICS.append(TEXT[j][TEXT[j].rfind("|") + 1:])
        
    for j in range(0, x):
        xx.append(str(round(TIME[j] - int(TIME[j]), 2)))
        if int(TIME[j]) % 60 < 10:
            ss.append("0" + str(int(TIME[j]) % 60))
        else:
            ss.append(str(int(TIME[j]) % 60))
        if int(TIME[j]) // 60 < 10:
            mm.append("0" + str(int(TIME[j]) // 60))
        else:
            mm.append(str(int(TIME[j]) // 60))
    
    # 크롤링 결과를 초기화        
    with open('%s.lrc' % file_name, 'w', encoding='UTF8') as file:  # 초기화
        file.write('')
        
    for j in range(0, x):
        with open('%s.lrc' % file_name, 'a', encoding='UTF8') as file:  # 최종
            if j != x:
                file.write("[" + mm[j] + ":" + ss[j] + xx[j][1:] + "]" + LYRICS[j] + "\n")
            else:
                file.write("[" + mm[j] + ":" + ss[j] + xx[j][1:] + "]" + LYRICS[j])
