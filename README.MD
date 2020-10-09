# Telegram channel downloader

Desktop backup function is no good due to it being very slow and pretty cumbersome once stopped.
This script ripping telegram channel's files into a local folder.

You need to change the example.ini so it would match to your preference.

[To learn how to get channel's ID](https://stackoverflow.com/a/50984134/3852918)

If you want to upload it to cloud service, use Rclone mounth.

Direct the destination folder into rglone mount
Example command would be as simple as 
> rclone mount config: /your/folder_path/ --allow-other --drive-acknowledge-abuse
[To learn more about Rclone mount](https://rclone.org/commands/rclone_mount/)

I have added example webhook so you can watch the advance on HASSIO/IFTTT without the need to watch the script itself, usefull for huge channels.