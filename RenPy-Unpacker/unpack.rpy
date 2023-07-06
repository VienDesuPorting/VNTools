init 4 python:
    import os

    for asset in renpy.list_files():
        if os.path.splitext(asset)[1] != ".rpa":
            output = "unpack/game/" + asset
            if not os.path.exists(os.path.dirname(output)):
                os.makedirs(os.path.dirname(output))

            out_bytes = open(output, "wb")
            out_bytes.write(renpy.file(asset).read())
            out_bytes.close()
