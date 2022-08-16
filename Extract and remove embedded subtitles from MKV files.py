#!/usr/bin/env python3

# -----------------------------------------------------------------------------

# EXTRACT AND REMOVE EMBEDDED SUBTITLES FROM MKV FILES

# Post-process script for SABnzbd
# https://sabnzbd.org/wiki/scripts/post-processing-scripts

# -----------------------------------------------------------------------------

from pathlib import Path
from pprint import pprint
import json
import re
import subprocess
import sys
import os
import zipfile
import glob

codec_map = {
	# MKV valid subtitles: https://www.matroska.org/technical/subtitles.html
	"S_TEXT/UTF8": "srt", # SRT Subtitles
	"S_TEXT/ASS": "ass", # SSA/ASS SubStation Alpha Subtitles
	"S_VOBSUB": "sub", # VobSub image subtitles
	"S_HDMV/PGS": "sup", # HDMV presentation graphics subtitles
	"S_HDMV/TEXTST": "textst", # HDMV presentation text subtitles
	"S_DVBSUB": "dvb", # HDMV presentation text subtitles
}	"S_TEXT/WEBVTT": "vtt", # WebVTT Web Video Text Track subtitles

os.chdir(os.environ['SAB_COMPLETE_DIR']) # Change directory to download path

print(
	"Running script:", os.environ['SAB_SCRIPT'], "for the directory:\r\n",
	os.environ['SAB_COMPLETE_DIR'],	"\r\n")

# --------------------------------------
# Process MKVs in the folder
# --------------------------------------

# For each MKV file found in the folder do...
for i,file in enumerate(os.listdir(os.environ['SAB_COMPLETE_DIR'])):
	if file.endswith(".mkv"):
		file = os.environ['SAB_COMPLETE_DIR'] + "\\" + os.path.basename(file)

		# --------------------------------------
		# Check the MKV for subtitles
		# --------------------------------------

		mkvmerge_result = subprocess.run(
			[
			"mkvmerge",
			"--identify",
			"--identification-format",
			"json", str(file)
			],
			capture_output=True,
			shell=False,
			encoding="utf-8",
		)
		if mkvmerge_result.returncode != 0:
			print(f"Error in mkvmerge while parsing: {file}")
			print(mkvmerge_result.stdout.strip())  # Show error (stdout)
			exit(1)
		d = json.loads(mkvmerge_result.stdout)
		# pprint(d)  # Debug output
		if not "tracks" in d:
			print(f"Invalid JSON output from mkvmerge for file: {file}")
			exit(1) # If the file has no tracks

		# --------------------------------------
		# Check streams and extract subtitles
		# --------------------------------------

		# Check for streams and store variables
		codec_list = [] # Store stream codecs in a list
		for track in d["tracks"]:
			track_id = track["id"]
			p = track["properties"]
			codec = p["codec_id"] if ("codec_id" in p) else None
			language = p["language"] if ("language" in p) else None
			name = p["track_name"] if ("track_name" in p) else None

			# Append every codec to a list
			codec_list.append(track["properties"]["codec_id"])

			# Abort if the stream is not a subtitle type
			if codec is None or codec not in codec_map:
				continue

			# File name for the subtitle extraction
			output_name = [
				Path(os.path.basename(file)).stem,  # Name without ext.
				#str(track_id),  # In case two subs have same language code
				language,  # 3-letter code such as "eng".
				f"({name})" if name is not None else None,  # Track description
				codec_map[codec],  # Proper subtitle extension.
			]
			# Remove all illegal filesystem-characters from the filename.
			# https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
			output_name = ".".join(filter(lambda x: x is not None, output_name))
			output_name = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", output_name)
			print(f"- Track {track_id}: {output_name}")
			output_file = os.environ['SAB_COMPLETE_DIR'] + "\\" + output_name

			# Extract the subtitle with mkvextract
			result = subprocess.run(
				[
				"mkvextract", 
				"tracks", 
				str(file), 
				f"{track_id}:{output_file}"
				],
				capture_output=True,
				shell=False,
				encoding="utf-8",
			)
			if result.returncode != 0:
				print(f"Error while extracting track {track_id} from file: {file}")
				print(result.stdout.strip())  # Show the actual error (it's in stdout).
				exit(1)

		# --------------------------------------
		# Make new video without subtitles...
		# ...and delete the original video
		# --------------------------------------

		# If the video contains subs, make a new video file without subs
		if (any([h in codec_list for h in codec_map])):
			subprocess.run(
			[
			"mkvmerge",
			"--output",
			".tmp",
			"--no-subtitles",
			str(file)
			],
				capture_output=True,
				shell=False,
				encoding="utf-8",
			)
			if result.returncode != 0:
				print("Making a video without subtitles failed...")

			# Delete the original file
			try:
				os.remove(file)
			except OSError as e:
				print("Error: %s - %s." % (e.filename, e.strerror))

			# Rename the temp file to the original name
			os.rename(".tmp", str(file))

			# --------------------------------------
			# Make zip with subtitles (Sonarr hack)
			# --------------------------------------

			# Make a list of file types to be zipped
			zip_files = []
			for i in codec_map: # For each subtitle codec
				k,v = (i, "*." + codec_map[i]) # Add extension to the codec
				zip_files.append(v) # Add the codec to the list

			# Add all subtitle files to a list
			subtitle_files = []
			for a in zip_files:
				subtitle_files.extend(glob.glob(a))

			# Make the zip file
			with zipfile.ZipFile(output_name + ".zip", mode="w", compresslevel=None) as archive:
				for a in subtitle_files:
					archive.write(a)
		else:
			print("Could not make a zip with subs.\r\nThe file probably does not have subs.")
sys.exit(0)
