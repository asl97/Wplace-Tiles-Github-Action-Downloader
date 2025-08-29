import threading
import queue
import os

jobs = queue.Queue()
workers = []
def start_worker():
    workers.clear()
    o = object()

    def run_worker():
        while (job:=jobs.get()) is not o:
            print(job)
            os.system(job)

    for _ in range(4):
        t = threading.Thread(target=run_worker)
        t.start()
        workers.append(t)
        jobs.put(o)

def wait_for_workers():
    for worker in workers:
        worker.join()

files = [l for l in os.listdir() if l.endswith('.gpg')]
pngs = []

for i, png in enumerate(files):
    pngs.append(png[:-4])
    jobs.put(f'gpg  --quiet --batch --yes --decrypt --passphrase="" --output {png[:-4]} {png}')

start_worker()
wait_for_workers()

groups = set()
times = set()

dpngs = {}
for png in pngs:
    i = png.split("_")[0]
    if i not in dpngs: dpngs[i] = []

    dpngs[i].append(png)

if len(dpngs) > 1:
    png_group = [l for l in zip(*dpngs.values())]
    for group in png_group:
        assert group[0].split("_")[-1] == group[1].split("_")[-1]

    for i, group in enumerate(png_group):
        # combine image side by side, no config/option to easily set layout yet
        os.system(f'convert {" ".join(group)} +append {"%05d.png"%i}')
else:
dpngs = {}
for png in pngs:
    i = png.split("_")[0]
    if i not in dpngs: dpngs[i] = []

    dpngs[i].append(png)

if len(dpngs) > 1:
    png_group = [l for l in zip(*dpngs.values())]
    for group in png_group:
        assert group[0].split("_")[-1] == group[1].split("_")[-1]

    for i, group in enumerate(png_group):
        # combine image side by side, no config/option to easily set layout yet
        jobs.put(f'convert {" ".join(group)} +append -background white -alpha remove -flatten {"%05d.png"%i}')
else:
    for i, png in enumerate(*dpngs.values()):
        jobs.put(f'convert {png} -background white -alpha remove -flatten {"%05d.png"%i}')
        #os.rename(png, '%05d.png'%i)

start_worker()
wait_for_workers()

os.system(r'ffmpeg -r 3 -i "%05d.png" -c:v libx264 -qp 0 '+f'{files[0][2:-8]}_{files[-1][2:-8]}.mp4')
#ffv1 result in giant file
#os.system(r'ffmpeg -r 3 -i "%05d.png" -c:v ffv1 '+f'{files[0][2:-8]}_{files[-1][2:-8]}.mkv')
os.system(r' ffmpeg -r 3 -i "%05d.png" -plays 0 '+f'{files[0][2:-8]}_{files[-1][2:-8]}.apng')
# ffmpeg -r 3 -i "%05d.png" -vf "crop=270:280:0:175" -y -plays 0 out.apng