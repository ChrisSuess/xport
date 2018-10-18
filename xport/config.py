import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        ROOT = os.path.dirname(os.path.abspath(root))
    except:
        raise OSError('Error: caannot determine root directory')
    #UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(ROOT, 'webjobs')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/home/ubuntu/shared/webjobs'
    
