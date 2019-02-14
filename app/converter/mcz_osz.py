import zipfile
import os
import traceback
from app.converter import mc_osu


def mcz_osz_v14(mcz_path, osz_path, od=8, hp=7, vol=70, keep_sv=True):
    global success_c
    try:
        d = mcz_path.rsplit(".", 1)[0]
        os.makedirs(d, exist_ok=True)
        zipfile.ZipFile(mcz_path).extractall(d)

        success_c = 0
        convert(d, od, hp, vol, keep_sv)
        if success_c == 0:
            raise Exception()

        zip_dir(d, osz_path)

    except Exception:
        msg = traceback.format_exc()
        print(msg)
        raise ValueError("该谱面文件格式有误")


# noinspection PyBroadException,PyTypeChecker
def convert(d, od=8, hp=7, vol=70, keep_sv=True):
    global success_c
    for file in os.listdir(d):
        file = os.path.join(d, file)
        if os.path.isdir(file):
            convert(file, od, hp, vol, keep_sv)
        else:
            suffix = file.rsplit(".", 1)[-1]
            name = file.rsplit(".", 1)[0]
            if suffix == 'mc':
                try:
                    mc_osu.fmc_osu_v14(file, name + ".osu", od, hp, vol, keep_sv)
                    success_c += 1
                except Exception:
                    pass
                finally:
                    os.remove(file)


def zip_dir(dirpath, outname):
    with zipfile.ZipFile(outname, "w", zipfile.ZIP_DEFLATED) as z:
        for path, dirnames, filenames in os.walk(dirpath):
            fpath = path.replace(dirpath, '')
            for filename in filenames:
                z.write(os.path.join(path, filename), os.path.join(fpath, filename))
