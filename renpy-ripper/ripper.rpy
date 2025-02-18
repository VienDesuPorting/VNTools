init 4 python:
    import os

    for asset in renpy.list_files():
        if os.path.splitext(asset)[1] != ".rpa" and not asset.count("unpack.rpy"): # Ignore .rpa and script itself
            if renpy.macintosh:
                game_path = os.path.expanduser('~') + "/" + config.name # Unpack assets to home folder (on mac you cant get cwd)
                output = game_path + "/game/" + asset
            else:
                output = "unpack/game/" + asset # Unpack assets to game folder

            if not os.path.exists(os.path.dirname(output)):
                os.makedirs(os.path.dirname(output))

            out_bytes = open(output, "wb")
            out_bytes.write(renpy.file(asset).read())
            out_bytes.close()
