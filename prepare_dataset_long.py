import csv
import os
import glob
from os import path
from pydub import AudioSegment
from num2words import num2words as n2w
import subprocess

CHANNELS    = 1
SAMPLE_RATE = 22050

err_num = 0

def convert_to_wav(src, dst, sound_file_name):
    global err_num
    for sound in glob.glob(os.path.join(src, '*.mp3')):
        # convert wav to mp3 
        if "crop" not in sound:
            continue
        try:   
            dst_new = dst + sound.split('.mp3')[0].split(sound_file_name)[-1] + ".wav"                                                
            # sound = AudioSegment.from_mp3(sound)
            # sound = sound.set_channels(CHANNELS)
            # sound = sound.set_frame_rate(SAMPLE_RATE)
            # sound.export(dst_new, format="wav")
            subprocess.check_call(args=['ffmpeg', '-i','{}'.format(sound),\
                 '-acodec','pcm_s16le','-ac','1', '-ar', '16000','{}'.format(dst_new), '-y'])

        except Exception:
            # print(e) ## To see the error
            err_num += 1
            print(f"An error occured in {src}, process is continuing.. TOTAL ERRORS:{err_num}")
            continue

    print(f"All mp3 files in {sound_file_name} converted to wav and copied to the wavs directory successfully.")


def prepare_csv_file(dst_path, csv_file_path):
    # Read .wav files from wavs file
    ids = os.listdir(dst_path)
    if ".DS_Store" in ids:
        ids.remove(".DS_Store")

    # open the file in the write mode
    with open(csv_file_path + 'metadata.csv', 'a') as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        for id_ in sorted(ids):
            if "crop" not in id_:
                continue
            ## ReCreate of csv file
            # if sound_file_name.split("/")[0] not in id_:
            #     continue
            id_to_write = id_.split(".wav")[0]
            id_to_txt = id_.replace(".wav", ".txt")
            path = "./1/downloads_convert/" + id_to_write.split("_crop")[0] + "/"
            with open(path + id_to_txt, 'r') as f:
                content = f.readline()   
            content = content.replace("\n", "").replace("'", " ")
            content = content.lower()
            ## convert numbers to text
            content_list = content.split()
            for order, item in enumerate(content_list):
                if item.isdigit():
                    item = (n2w(int(item), lang ='tr'))
                    content_list[order] = item
            content_clean = " ".join(content_list)
            writer.writerow([id_to_write + "|" + content + "|" + content_clean])


    print("metadata.csv file is created successfully.")

# Collect all .wav files in wavs file
src_path = "./1/downloads_convert/"
dst_path = "./LibriSpeech/ArdıcLongDataset/data/wavs/"
csv_file_path = "./LibriSpeech/ArdıcLongDataset/data/"

if not os.path.exists(dst_path):
    os.makedirs(dst_path)
    print("{} directory created.".format(dst_path))

# # convert to wav and export dst path
# for file_path in os.listdir(src_path):
#     if file_path == ".DS_Store":
#         continue
#     src_path_new = src_path + file_path + "/"
#     convert_to_wav(src_path_new, dst_path, file_path + "/")

prepare_csv_file(dst_path, csv_file_path)

