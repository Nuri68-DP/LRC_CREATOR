import glob
import mutagen
import os
#import json

# mode: 1=flag가 0인 값만, 2=전체
def set_list(search_path, file_types_string, mode = 1):
    
    paths = [search_row for search_row in glob.glob(search_path + "\**", recursive=True) if os.path.isfile(search_row)]
    available_files = []
    
    for array_row in range(0, len(paths)):
        file_datas = os.path.splitext(paths[array_row])
        metadata_details_keys = ('flag', 'file_name', 'file_type', 'album', 'artist', 'title', 'track_artistid', 'track_albumid', 'track_trackid', 'lrc_status')
        metadata_details = dict.fromkeys(metadata_details_keys)
                    
        if file_datas[1].replace(".","") not in file_types_string : continue
        
        try:
            metadata = mutagen.File("%s" % paths[array_row])
            
            if (not check_tags(metadata_details, file_datas[0], file_datas[1], metadata)
            and mode != 2):
                continue
            
            available_files.append(metadata_details)
        except Exception as ex:
            print("error: " + paths[array_row], ex)
        
    return available_files   

def check_tags(metadata_details, file_name, file_type, metadata):
    try:
        metadata_details['flag']            = 0
        metadata_details['file_name']       = file_name
        metadata_details['file_type']       = file_type.replace(".", "")
        metadata_details['track_artistid']  = []
        metadata_details['track_albumid']   = []
        metadata_details['track_trackid']   = []
        metadata_details['lrc_status']      = 0 
        
        if os.path.isfile(os.path.splitext(metadata_details['file_name'])[0] + ".lrc"): 
            metadata_details['lrc_status'] = 1
        
        if file_type == ".flac":
            if 'album' in metadata.keys():  metadata_details['album']   = metadata['album'][0] 
            if 'artist' in metadata.keys(): metadata_details['artist']  = metadata['artist'][0] 
            if 'title' in metadata.keys():  metadata_details['title']   = metadata['title'][0]
            
            if ('album' in metadata.keys() 
            and 'artist' in metadata.keys() 
            and 'title' in metadata.keys()):
                metadata_details['flag']    = 2
                return True
            else: 
                return False
            
        elif file_type == ".mp3" or file_type == ".wav":

            if metadata['TALB'].text[0] is not None: metadata_details['album']   = metadata['TALB'].text[0]
            if metadata['TPE1'].text[0] is not None: metadata_details['artist']  = metadata['TPE1'].text[0]
            if metadata['TIT2'].text[0] is not None: metadata_details['title']   = metadata['TIT2'].text[0]
            
            if (metadata['TALB'].text[0] is not None
            and metadata['TPE1'].text[0] is not None
            and metadata['TIT2'].text[0] is not None):
                metadata_details['flag']    = 2
                return True
            else: 
                return False
            
        elif file_type == ".m4a":
            if metadata['©alb'][0] is not None: metadata_details['album']   = metadata['©alb'][0]
            if metadata['©ART'][0] is not None: metadata_details['artist']  = metadata['©ART'][0]
            if metadata['©nam'][0] is not None: metadata_details['title']   = metadata['©nam'][0]
            
            if (metadata['©alb'][0] is not None
            and metadata['©ART'][0] is not None
            and metadata['©nam'][0] is not None):
                metadata_details['flag']    = 2
                return True
            else: 
                return False
        
        # elif file_type == ".wav":
        #     if metadata['TALB'].text[0] is not None: metadata_details['album']   = metadata['TALB'].text[0]
        #     if metadata['TPE1'].text[0] is not None: metadata_details['artist']  = metadata['TPE1'].text[0]
        #     if metadata['TIT2'].text[0] is not None: metadata_details['title']   = metadata['TIT2'].text[0]
            
        #     if (metadata['TALB'].text[0] is not None
        #     and metadata['TPE1'].text[0] is not None
        #     and metadata['TIT2'].text[0] is not None):
        #         metadata_details['flag']    = 2
        #         return True
        #     else: 
        #         return False
    except:
        return False

