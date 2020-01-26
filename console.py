import sys

from colorama import Fore, Style

from downloader import Downloader


def long_Str_setter(delim, long):
    a = 1
    b = ""
    while a < long:
        a = a + 1
        b = b + delim
    return b


def disbar(total, now, msg):
    print(long_Str_setter(" ", 50), end="\r")
    print(("-{0}% " + (now + 1).__str__() + "/" + total.__str__() + " " + msg).format(round((now + 1) * 100 / total)),
          end="\r")
    return


def status(s, n, m):
    print(Style.BRIGHT + long_Str_setter(" ", 100) + Style.RESET_ALL, end='\r')
    if s == 'SUCCESS':
        print(Style.BRIGHT + '[' + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Style.BRIGHT + ']', n,
              Fore.YELLOW + m + Style.RESET_ALL)
    if s == 'ERROR':
        print(Style.BRIGHT + '[' + Fore.RED + 'ERROR' + Style.RESET_ALL + Style.BRIGHT + ']', n,
              Fore.MAGENTA + m + Style.RESET_ALL)
    if s == 'CACHED':
        print(
            Style.BRIGHT + '[' + Fore.GREEN + 'SUCCESS' + Fore.WHITE + '][' + Fore.CYAN + 'Cached' + Fore.WHITE + ']'
            + Style.RESET_ALL, Style.DIM + n, Fore.YELLOW + m + Style.RESET_ALL)


def verbose(info):
    if is_verbose:
        print(Style.BRIGHT + info + Style.RESET_ALL)


def detailed(i, f):
    return


def empty():
    return


def download_Start():
    print("Start Download")


def download_end():
    print("End Download")


if __name__ == '__main__':
    cloud_music_api = 'https://163musicapi.star-home.top:4430'
    cloud_music_playlist = ['510113940']
    dir_temp = "cache/"
    dir_end = "music/"
    Enable_ORDER = False
    Clean_Music_Dir = False
    is_verbose = False
    is_cleaned_list = False
    for i in sys.argv[1:]:
        if i[0] == '-':
            if i[1:] == 'v':
                is_verbose = True
                continue
            if i[1] == 'A':
                cloud_music_api = i[2:]
                continue
            if i[1:] == 'c':
                Clean_Music_Dir = True
                continue
            if i[1:] == 'o':
                Enable_ORDER = True
                continue
            if i[1:] == 'T':
                dir_temp = i[2:]
                continue
            if i[1:] == 'M':
                dir_end = i[2:]
                continue
            if i[1:] == 'h':
                print(sys.argv[0] + ' Usage:')
                print("-v => Enable Verbose Log output")
                print("-c => Clear The music dir before downloading")
                print("-o => Order the musics")
                print("-T/cache => Set cache dir to '/cache'")
                print("-M/music => Set music dir to '/music'")
                # noinspection SpellCheckingInspection
                print(
                    "-Ahttps://163musicapi.star-home.top:4430 => Change API to 'https://163musicapi.star-home.top:4430'")
                exit(0)
            print("ERROR: Option", i, 'Unknown')
            exit(1)
        else:
            if not is_cleaned_list:
                cloud_music_playlist.clear()
                is_cleaned_list = True
            cloud_music_playlist.append(i)
    print(Style.BRIGHT + long_Str_setter("-", 50))
    print("    NeteaseCloudMusic Downloader     ")
    print("               Powered by haoxingxing")
    print(Style.BRIGHT + long_Str_setter("-", 50))
    print(Fore.CYAN + "Api:" + cloud_music_api + Fore.WHITE)
    print(Fore.YELLOW + "PlayListId:" + cloud_music_playlist.__str__() + Fore.WHITE)
    print(Style.BRIGHT + long_Str_setter("-", 50) + Style.RESET_ALL)

    for cloud_music_playlist_o in cloud_music_playlist:
        x = Downloader(dir_temp, dir_end + cloud_music_playlist_o + '/', cloud_music_api, Enable_ORDER,
                       cloud_music_playlist_o).setCallBackStatusFunction(
            empty, empty, download_Start, download_end).setCallBackProgressFunction(
            disbar,
            verbose,
            status,
            detailed
        ).run()
