import sqlite3
from pydub import AudioSegment
import os
import argparse
from ardicsrtcollector.youtube_srt_mp3 import YoutubeSrtMp3

parser = argparse.ArgumentParser(description="Process to find word in sound.")
parser.add_argument('-f', '--file_dir', type=str, help='path of file.')
parser.add_argument('-d', '--database_dir', type=str, help='path of database.')
parser.add_argument('-ck', '--check_only', default=False, action='store_true', help='check existing files.')
parser.add_argument('-a', '--all', default=False, action='store_true', help='search all words.')
parser.add_argument('--max', type=int, default=0, help='max number of words')
parser.add_argument('-w', '--word', type=str, help='searched word.')
parser.add_argument('-v', '--verbose', default=False, help='If True prints names of matched files.')

## parse args
args = parser.parse_args()

def search_word(parser):
    ## check file path
    if not os.path.exists(parser.file_dir):
        print("Girilen dosya adı mevcut değil.")
        exit(0)
    
    ## check db path
    if not os.path.exists(parser.database_dir):
        print("Girilen dosya adı mevcut değil.")
        exit(0)

    ## create file named with word
    if not parser.all and not parser.check_only:
        try:
            os.mkdir("dataset/" + parser.word)
        except FileExistsError:
            update_or_exit = input("Girilen kelime daha önceden bulunmus. Güncellemek ister misiniz? (E/H) ")
            if update_or_exit == "e" or update_or_exit == "E":
                pass
            elif update_or_exit == "h" or update_or_exit == "H":
                print("Program sonlandırılyor.")
                exit(0)
            else:
                print("Hatalı giriş.")
                exit(0)

    elif parser.all and parser.max == 0:
        dst_path = "dataset/all_words/"
        os.mkdir(dst_path)

    elif parser.all and parser.max != 0:
        dst_path = f"dataset/all_words_limited_{parser.max}/"
        os.mkdir(dst_path)


    dir_path   = parser.file_dir
    db_name    = parser.database_dir
    query_word = parser.word

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    query = "SELECT * FROM google_responses_raw" 
    cursor.execute(query)
    datas_from_db = cursor.fetchall()

    limit_ = parser.max
    if parser.max == 0:
        limit_ = len(datas_from_db)

    print("Eslesmeler araniyor...")
    matches = 0
    
    with open("words.txt", "w") as file_: ## !!!! 
        for data in datas_from_db[0:limit_]: 
            file_path = data[0]
            vid_id = data[1]  

            try:
                soundFile = AudioSegment.from_mp3(dir_path + file_path.replace("~", ""))
            except:
                check_server(vid_id)

            if parser.check_only:
                continue
            else:
                soundFile = AudioSegment.from_mp3(dir_path + file_path.replace("~", ""))

            name = file_path.split("/")[-1].split("/")[-1].split(".mp3")[0]
            response = data[2].encode().decode('unicode-escape').encode('latin1').decode('utf-8')
            
            file_.write(f"\tFILENAME -> {file_path}\n")
            response_ = str(response).split("words ")
            for word in response_[1::]:
                ## Getting time format and Word
                start_time = word.split("start_time")[-1]\
                    .split("}")[0].replace('\n', ' ')\
                        .replace('{', ' ').strip()
                word_ = word.split("word:")[-1]\
                    .split("}")[0].replace('\n', ' ')\
                        .replace('{', ' ').strip().replace('"', " ")
                end_time = word.split("end_time")[-1]\
                    .split("}")[0].replace('\n', ' ')\
                        .replace('{', ' ').strip()
                start_time = "nanos: 0" if start_time == ""\
                    else start_time

                init_secs  = ['seconds:', '0']
                init_nanos = ['nanos:'  , '0']

                s_time = start_time.split()   
                if "seconds" not in start_time:
                    s_time = init_secs + s_time
                elif "nanos" not in start_time:
                    s_time = s_time + init_nanos
                start_seconds = float(s_time[1] + '.' + s_time[3])

                e_time = end_time.split()   
                if "seconds" not in end_time:
                    e_time = init_secs + e_time
                elif "nanos" not in end_time:
                    e_time = e_time + init_nanos
                end_seconds = float(e_time[1] + '.' + e_time[3])

                ## Report Parsed Words
                file_.write("WORD       -> {}\n".format(word_))
                file_.write("START TIME -> {}\n".format(start_time))
                file_.write("END TIME   -> {}\n".format(end_time))
                file_.write("Start Seconds: {} - End Seconds: {}\n".format(start_seconds, end_seconds))
                file_.write("\n\n")

                ## crop sounds if matching found (case 1)
                if not parser.all:
                    if word_.casefold().strip() == query_word:
                        matches += 1
                        startTime = int(start_seconds * 1000 - 100) 
                        if startTime < 0: startTime = 0
                        endTime   = int(end_seconds   * 1000 - 80)
                        
                        if parser.verbose:
                            print(f"{query_word} found in {name}.mp3")

                        cropped = soundFile[startTime:endTime]
                        # Saving
                        cropped = cropped.set_frame_rate(22050)
                        cropped = cropped.set_channels(1)
                        cropped.export("dataset/" + parser.word + '/' + name +\
                            f"-{query_word}.wav", format="wav")
                ## crop sounds for all words (case 2)
                else:
                    word_to_crop = word_.casefold().strip()
                    if not os.path.exists(dst_path + word_to_crop):
                        os.makedirs(dst_path + word_to_crop)
                        matches += 1
                    startTime = int(start_seconds * 1000 - 100) 
                    if startTime < 0: startTime = 0
                    endTime   = int(end_seconds   * 1000 - 80)
                    
                    if parser.verbose:
                        print(f"{query_word} found in {name}.mp3")

                    cropped = soundFile[startTime:endTime]
                    # adjusting
                    cropped = cropped.set_frame_rate(22050)
                    cropped = cropped.set_channels(1)
                    # Saving
                    try:
                        cropped.export(dst_path + word_to_crop +\
                             '/' + name + f"-{word_to_crop}.wav", format="wav")
                    except:
                        print(f" Belirtile dosya yazılamadı: {dst_path}{word_to_crop}/ \
                            {name}{word_to_crop}.wav")

    if not parser.all:
        print("{} eslesme bulundu.".format(matches))
        if matches == 0:
            os.rmdir("dataset/" + parser.word)
    elif parser.all and parser.max == 0:
        print("Tüm kelimeler ayrıldı toplamda {} kelime bulundu.".format(matches))
    elif parser.all and parser.max != 0:
        print(f"   Kısıtlı {parser.max} veri içinden;")
        print("Tüm kelimeler ayrıldı toplamda {} kelime bulundu.".format(matches))

    cursor.close()
    conn.close()

def check_server(vid_id):
    print("Videoya ait dosya bulunamadı. Dosya indiriliyor...")
    youtube_url = "https://www.youtube.com/watch?v="
    with open("failed_url.txt", "w") as url_file:
        url_file.write(youtube_url + vid_id)
    YoutubeSrtMp3(urls_file_path="failed_url.txt", save_dir=args.file_dir).convert()

        


if __name__ == "__main__":
    search_word(args)

## list of tables
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# list_of_db_tables = cursor.fetchall()


            
