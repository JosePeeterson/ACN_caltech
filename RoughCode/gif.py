from PIL import Image
import glob

# Create the frames
frames = []
imgs = glob.glob("processed_stations_data/pngs/*.png")
imgs.sort(key=os.path.getmtime)

for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame)

# Save into a GIF file that loops forever
frames[0].save('processed_stations_data/pngs/gif/png_to_gif.gif', format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=200, loop=0)