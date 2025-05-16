import os

# more extension can be added
def isImage(filename: str, 
            extension: str | tuple[str, ...] =('.png', '.jpg', '.jpeg', '.bmp', '.dib', 
                                 '.pbm', '.pgm', '.ppm' '.pxm', '.pnm', 'webp')):
    return filename.endswith(extension)

def isHeic(filename:str, 
           extension: str | tuple[str, ...] ='.heic'):
    return filename.endswith(extension)

def isDirectory(path:str):
    return os.path.isdir(path)


