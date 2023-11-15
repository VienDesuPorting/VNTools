## FFMpeg-Compressor
Python utility uses ffmpeg to compress Visual Novel Resources

### How to use
* Download `ffmpeg-comp.toml` and put in next to binary or in to `/etc` folder
* Change the configuration of the utility in `ffmpeg-comp.toml` for yourself
* `ffmpeg-comp {folder}`
* In result you get `{folder-compressed}` near with original `{folder}`

### Configuration
#### FFMPEG section
* CopyUnprocessed - Copy all files that failed to compress by ffmpeg to destination folder. In can helps to recreate original folder, but with compressed files.
* MimicMode - Rename compressed file to it original name and extension. VN engines determine the file type by its header, so for example PNG file named file.jpg will be loaded as PNG file. (default: `false`)
* HideErrors - Hide some errors about compression. (default: `false`)
* WebpRGBA - Alpha channel in webp. If false switches extension to png. (default: `true`)

#### AUDIO section
* Extension - Required audio file extension. It supports: `.aac`, `.flac`, `.m4a`, `.mp3`, `.ogg`, `.opus`, `.raw`, `.wav`, `.wma`.
* BitRate - (mp3 only, for now) Required audio bitrate. For best quality use `320k` value, but for worse use `1-9` (9 worst) number range.

#### IMAGE section
* Extension - Required image file extension. It supports: `.apng`, `.avif`, `.bmp`, `.tga`, `.tiff`, `.dds`, `.svg`, `.webp`, `.jpg/.jpeg`, `.png`
* Quality - Quality level of images. Values range: `0-100` (100 - best quality, 0 - worst quality)

#### VIDEO section
* Extension - Required image file extension. It supports: `.3gp`, `.amv`, `.avi`, `.gif`, `.m2l`, `.m4v`, `.mkv`, `.mov`, `.mp4`, `.m4v`, `.mpeg`, `.mpv`, `.webm`, `.ogv`
* Codec - (May be optional in future) Required video codec. (See official ffmpeg documentation for supported codecs) 

### TODO (for testing branch)
* [x] Recreate whole game directory with compressed files
* [ ] Cross platform (Easy Windows usage and binaries, MacOS binaries)
* [x] Use ffmpeg python bindings instead of cli commands
* [ ] Reorganize code