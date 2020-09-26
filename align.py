from process import inbox , clip , string_to_txt, json_to_csv, outbox, check, cleaning
import os 
import argparse
import requests
import json

parser = argparse.ArgumentParser(description='Align your subtitles in a movie by use of Deep learning library Align. Get a srt file in output using commands listed bellow!')

parser.add_argument('-m', type=str, help='movie file name' , required=True)
parser.add_argument('-s', type=str, help='subtitles file name' , required=True)
parser.add_argument('-o', type=str, help='output srt file',  default = 'new subtitles.srt')


if __name__ == "__main__": 

	args = parser.parse_args()
	srt = args.s
	movie = args.m
	out = args.o

	cut = "cut.mkv"
	audio = "audio.mp3"
	

	text , data = inbox(srt)
	last = data[-1][0]

	clip(last, movie, cut, audio)

	string_to_txt(text)
	print('gentle Docker API -- install by `~$ sudo docker run -P lowerquality/gentle` ')

	params = (
    ('async', 'false'),
	)

	files = {
	    'audio': ('text.mp3', open(audio, 'rb')),
	    'transcript': ('text.txt', open('out.txt', 'rb')),
	}

	r = requests.post('http://localhost:32768/transcriptions', params=params, files=files)
	r = r.json()
	with open('out.json', 'w') as f:
		json.dump(r, f)

	# os.system("curl -X POST -F 'audio=@{}' -F 'transcript=<{}' 'http://gentle-demo.lowerquality.com/transcriptions?async=false' -o {}".format(audio, "out.txt", "out.json"))

	json_to_csv("out.json")

	delay = check(out = "out.csv", data = data)
	print('time delay:', delay)

	outbox(srt, new = out, delay = delay)

	cleaning()	

