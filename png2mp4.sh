ffmpeg -r 20 -f image2 -s 640x480 -i plots/plot%04d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p out.mp4
