## vnrecode
Python utility uses Pillow and ffmpeg to compress Visual Novel Resources

### Configuration file
#### FFMPEG section
* CopyUnprocessed - Copy all files that failed to compress by ffmpeg to destination folder. In can help to recreate original folder, but with compressed files. (default: `true`)
* ForceCompress - Force try to compress all files in directory via ffmpeg. (default: `false`)
* MimicMode - Rename compressed file to it original name and extension. VN engines determine the file type by its header, so for example PNG file named file.jpg will be loaded as PNG file. (default: `true`)
* HideErrors - Hide some errors about compression. (default: `true`)
* WebpRGBA - Alpha channel in webp. If false switches extension to png. (default: `true`)

#### AUDIO section
* Extension - Required audio file extension. It supports: `.aac`, `.flac`, `.m4a`, `.mp3`, `.ogg`, `.opus`, `.raw`, `.wav`, `.wma`.
* BitRate - Required audio bitrate. For best quality use `320k` value.

#### IMAGE section
* ResDownScale - Downscale image resolution count. (default: `1`)
* Extension - Required image file extension. It supports: `.apng`, `.avif`, `.bmp`, `.tga`, `.tiff`, `.dds`, `.svg`, `.webp`, `.jpg/.jpeg`, `.png`
* FallBackExtension - Extension if current format does not support RGBA.
* Lossless - Enables lossless compression for supported formats. With this quality parameter means quality of compression. (default: `false`)
* Quality - Quality level of images. Values range: `0-100` (100 - best quality, 0 - worst quality)

#### VIDEO section
* CRF ("Constant Quality") - Video quality parameter for ffmpeg. The CRF value can be from 0 to 63. Lower values mean better quality. Recommended values range from 15 to 35, with 31 being recommended for 1080p HD video. (default: `27`)
* SkipVideo - Skip processing all video files. (default: `false`)
* Extension - Required image file extension. It supports: `.3gp`, `.amv`, `.avi`, `.gif`, `.m2l`, `.m4v`, `.mkv`, `.mov`, `.mp4`, `.m4v`, `.mpeg`, `.mpv`, `.webm`, `.ogv`
* Codec - (Maybe optional in future) Required video codec. (See official ffmpeg documentation for supported codecs) 

### CLI Parameters
##### positional arguments:
*  source                - Directory with game files to recode

##### options:
* ` -h, --help `           - show this help message and exit
* ` -c CONFIG `            - Utility config file
* ` -nu `                  - Don't copy unprocessed
* ` -f, --force `          - Try to recode unknown files
* ` -nm, --no-mimic `      - Disable mimic mode
* ` -v, --show_errors `    - Show recode errors
* ` --webp-rgb `           - Recode .webp without alpha channel
* ` -j JOBS, --jobs JOBS ` - Number of threads
* ` -ae A_EXT `            - Audio extension
* ` -ab A_BIT `            - Audio bit rate
* ` -id I_DOWN `           - Image resolution downscale multiplier
* ` -ie I_EXT `            - Image extension
* ` -ife I_FALLEXT `       - Image fallback extension
* ` -il `                  - Image losing compression mode
* ` -iq I_QUALITY `        - Image quality
* ` --v_crf V_CRF `        - Video CRF number
* ` -vs `                  - Skip video recoding
* ` -ve V_EXT `            - Video extension
* ` -vc V_CODEC `          - Video codec name

### TODO (for testing branch)
* [x] Recreate whole game directory with compressed files
* [x] Cross-platform (Easy Windows usage and binaries, macOS binaries)
* [x] Use ffmpeg python bindings instead of os.system
* [x] Multithread
* [ ] Reorganize code