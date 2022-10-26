# Extract and remove embedded subtitles from MKV files



**A post-process script for SABnzbd**



## What's this?

This is a Python 3 [post-process script](https://sabnzbd.org/wiki/scripts/post-processing-scripts) for for [SABnzbd](https://sabnzbd.org/).

It is specifically meant to work together with [Sonarr](sonarr.tv/) and [Radarr](https://radarr.video/), but it will work regardless.



## What does it do?

1. Extracts all embedded subtitles to external files.
2. Makes a new video file excluding embedded subtitles, and deletes the original video file.
3. Makes a zip file with the extracted subtitles. This is a workaround for Sonarr/Radarr. Read more below.



## Why do you need it?

There are many reasons to prefer external subtitles over embedded, but most importantly:

Plex does not handle image-based subtitles well. 

> ...formats such as VOBSUB, PGS, etc. may work on some Plex apps but not  all. For the majority of apps, both VOBSUB and PGS subtitles will  require the video to be transcoded to “burn in” the subtitles for  streaming. - https://support.plex.tv/articles/200471133-adding-local-subtitles-to-your-media/

Even if Plex did not have this issue I would still prefer to have external subtitles.

- It makes it easier to immediately see which video has which subtitles.

- Editing subtitles is easier since you don't have to extract and rewrite the video file.
- It's easier to remove or keep the subtitles you want without remuxing.
- It's easier to backup the subtitles and to actually see if your backed up videos have subtitles.
- etc... you get the idea.



## Requirements

- [Python](http://python.org/) 3+ installed.
- [SABnzbd](https://sabnzbd.org/) installed.
- [Sonarr](https://sonarr.tv/) or [Radarr](https://radarr.video/) installed.
- [MKVToolNix](https://mkvtoolnix.download/downloads.html#windows) added to PATH(which includes `mkvmerge` and `mkvextract`)



## Installation

**1. Download this Python script**

**2. Add the script to SABnzbd** 

- In SABnzbd go to SABnzbd config ➜ Folders ➜ Set a folder where you want to have your custom scripts.

- Place this script in the SABnzbd scripts folder.
- In SABnzbd go to SABnzbd config ➜ Categories ➜ From the drop-down menu for the movies/tv category select the **.py** script.

![7744753484588243](https://user-images.githubusercontent.com/49068170/197951685-6a8b6520-b253-4339-8082-a74dada1a8b5.png)

- Save (you need to save for each category).

**3. Make Radarr and Sonarr import extra files**

- Open Radarr/Sonarr.
- Go to **Settings** ➜ Media management ➜ "**Import Extra Files**". ➜ **Save**.
- Add these file types to the comma separated list of extra files to import:

```
.srt, .ass, .sub, .sup, .textst, .dvb, .vtt, .zip
```

Importing .zip is optional, but please read why this is recommended in the "workaround" section below.



 ## Usage

If SABnzbd is configured correctly the script should be run during completion.

You don't need to do anything.

That's the beauty of it.



## Limitations

- Only works with MKV files.
- Only tested with Windows. May or may not work with other operating systems.



___



## Why the zip file?

***Workaround for limited language support***

During import of "[extra files](https://wiki.servarr.com/en/sonarr/settings)", such as subtitle files, Sonarr will attempt to rename the subtitle files according to the video file with a language code before the file extension. For example: `VIDEO.4.spa.srt` will become `VIDEO.es.srt`.

However, this does not work for all languages. Unsupported languages will be renamed with a number instead, leaving the original language unknown. This is an irreversible process and the only way to find out the language of the subtitle is to manually check it, but you might not even recognize the language.

To solve this problem, I made the script compress all the subtitles to a zip file. These files won't be renamed by Sonarr/Radarr. So the zip file constitutes a s a backup of the subtitles. 

As long as you set Sonarr to import extra files (more spesifically .zip files) at least you won't lose the subtitle language codes forever, after the script has removed them from the MKV.

It's not pretty, but it is better than nothing I guess.
