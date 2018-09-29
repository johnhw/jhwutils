import matplotlib.pyplot as plt
import numpy as np

import skimage.io, skimage.color

import PIL.Image
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
import IPython.display
import numpy as np


def show_gif(a, width="100%", duration=10):
    a = np.uint8(np.clip(a,0,1)*255.0)
    f = StringIO()    
    frames = []
    for frame in range(a.shape[0]):
        img = PIL.Image.fromarray(a[frame,...])
        frames.append(img)
    img.save(f, format='gif', save_all=True, append_images=frames, loop=0, duration=duration)
    IPython.display.display(IPython.display.Image(data=f.getvalue(), width=width))

def show_image(a, fmt='png', width="100%"):
    a = np.uint8(np.clip(a,0,1)*255.0)
    f = StringIO()
    PIL.Image.fromarray(a).save(f, fmt)
    IPython.display.display(IPython.display.Image(data=f.getvalue(), width=width))

def load_image_colour(fname):
    img = skimage.io.imread(fname)
    return img.astype(np.float64)/255.0

def load_image_gray(fname):
    img = skimage.color.rgb2gray(skimage.io.imread(fname))
    return img.astype(np.float64)

def show_frames(img_seq, n=10):
    plt.figure(figsize=(16,4))
    for i in range(n):        
        plt.subplot(1,n, i+1)
        ix = int((i*img_seq.shape[0]) / float(n))
        show_image(img_seq[ix])
    
def show_image_mpl(array):    
    if len(array.shape)==2 or array.shape[2]==1:
        array = array.reshape(array.shape[0], array.shape[1])
        array = np.clip(array,0,1)        
        plt.imshow(array, interpolation="nearest", cmap="gray",vmin=0,vmax=1)
    
    if len(array.shape)==3 and array.shape[2]==3:        
        array = np.clip(array,0,1)
        plt.imshow(array, interpolation="nearest")        
    plt.axis("off")
    
    
import scipy.io.wavfile
import IPython
def load_sound(wav_file):    
    sr, sound = scipy.io.wavfile.read(wav_file)
    sound = sound.astype(np.float64)/32767.0

    if len(sound.shape)>1:
        sound = (sound[:,0]/2 + sound[:,1]/2)
    return sound

def play_sound(audio,sr=44100):
    audio = (np.clip(audio,-1,1)*32767.0).astype(np.int16)
    audio[-1] = -32767
    audio[-2] = 32767    
    IPython.display.display(IPython.display.Audio(audio, rate=sr))
    

def plot_sound(audio):
    ts = np.arange(len(audio))/44100.0
    plt.plot(ts, audio, 'c', alpha=0.5)
    plt.xlabel("Time (s)")    
    
    
        
def load_obj(filename, swapyz=False):
    """Loads a Wavefront OBJ file. """
    vertices = []
    normals = []
    texcoords = []
    faces = []

    material = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            vertices.append(v)
        elif values[0] == 'vn':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            normals.append(v)
        elif values[0] == 'vt':
            texcoords.append(map(float, values[1:3]))           
        elif values[0] == 'f':
            face = []
            texcoords = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    texcoords.append(int(w[1]))
                else:
                    texcoords.append(0)
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            faces.append((face, norms, texcoords, material))

    return np.array(vertices), faces