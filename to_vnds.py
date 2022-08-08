from PIL import Image
import subprocess

import os

from glob import glob

import io
import pathlib

import shutil

screen_size = (640, 480)
back_size = (640, 420)
fg_size = (320, 420) #character images are just half width
screen_offset = (0,16)

debug:int = False

def mk_dirtrees(file_name:str):
    pathlib.Path(os.path.dirname(file_name)).mkdir(parents=True, exist_ok=True)


def VFS_MOUNT(name:str):
    if not os.path.isfile(name):
        print("\n--------------- NO SOURCE FILE -----------------")
        print("Source file " + name + " does not exists.")
        print("------------------------------------------------\n")
        return
    f = open(name, "rb")
    pak = {}
    
    files = {}
    print(name)
    #pak = &paks[paks_count++];

    #strcpy(pak->path, name);
    #pak->rw = f;

    #uint32_t n, pos, len, offset;
	#uint16_t count;

    pos = 0
    length = 0
    offset = 0
    count = 0

    f.seek(8, 0)
	#SDL_RWseek(f, 8, SEEK_SET);
    count = int.from_bytes(f.read(2), "little")
	#SDL_RWread(f, &count , sizeof(count), 1);
    offset = int.from_bytes(f.read(4), "little")
	#SDL_RWread(f, &offset, sizeof(offset), 1);
    f.seek(offset, 0)
	#SDL_RWseek(f, offset, SEEK_SET);
    pos = 0x10
	#for (n = 0; n < count; n++) {
    for n in range(count):
        pass
		#FSLI *slice = &files[files_count++];
        slice_name = f.read(0xC).decode('unicode_escape').split('\x00',1)[0]
        
        #slice_name = tmp_name
        #print(slice_name)
		#SDL_RWread(f, slice->name, 1, 0xC);
        length = int.from_bytes(f.read(4), "little")
		#SDL_RWread(f, &len, sizeof(len), 1);

		#slice->name[0xC] = 0;

		#slice->pak = pak;
		#slice->pos = pos;
		#slice->len = len;
        
        files[slice_name] = [pos, length]
        #print(slice_name)
        pos += length
		#pos += len;
	
    f.close()
    if not os.path.isdir("out"):
        os.mkdir("out")

    
    for file in files.keys():
        print(file)
        b = open(name, "rb")
        b.seek(files[file][0])
        out_file = "out\\" + file.replace(".BMP", ".lz")
        out = open(out_file, "wb")

            
        for i in range(files[file][1]):
            out.write(b.read(1))


        out.close()
    
        
    print("OK " + str(count))
    return True




def uncompress_images():
    for file in glob("out\\**\\*.lz", recursive=True):
        print("Uncompressing " + file.replace(".lz", ".bmp"))
        #c = lzma.open(file, 'rb')
        #c.readlines()
        subprocess.run(["a", file, file.replace(".lz", ".bmp")])
        os.remove(file)
        pass

def export_files():
    VFS_MOUNT("sg.dl1")
    VFS_MOUNT("wv.dl1")
    VFS_MOUNT("ENGLISH.dl1")
    VFS_MOUNT("SPANISH.dl1")
    uncompress_images()

flags = {'flag_0': 1, 'flag_1': 2, 'flag_10': 3, 'flag_11': 4, 'flag_112': 5, 'flag_114': 6, 'flag_115': 7, 'flag_117': 8, 'flag_12': 9, 'flag_13': 10, 'flag_133': 11, 'flag_14': 12, 'flag_15': 13, 'flag_16': 14, 'flag_17': 15, 'flag_18': 16, 'flag_19': 17, 'flag_2': 18, 'flag_20': 19, 'flag_22': 20, 'flag_23': 21, 'flag_24': 22, 'flag_25': 23, 'flag_26': 24, 'flag_27': 25, 'flag_28': 26, 'flag_3': 27, 'flag_31': 28, 'flag_32': 29, 'flag_33': 30, 'flag_34': 31, 'flag_35': 32, 'flag_36': 33, 'flag_4': 34, 'flag_50': 35, 'flag_501': 36, 'flag_502': 37, 'flag_6': 38, 'flag_700': 39, 'flag_701': 40, 'flag_702': 41, 'flag_703': 42, 'flag_704': 43, 'flag_705': 44, 'flag_706': 45, 'flag_707': 46, 'flag_708': 47, 'flag_8': 48, 'flag_800': 49, 'flag_801': 50, 'flag_802': 51, 'flag_803': 52, 'flag_804': 53, 'flag_806': 54, 'flag_807': 55, 'flag_808': 56, 'flag_810': 57, 'flag_9': 58}


script = []
vnds:io.TextIOWrapper
jumps = []
script_pos:int = 0

missing_scripts = ["F11_0", "F34_17", "F34_18", "F34_19", "F34_21", "F34_22", "F34_23"]


def SCRIPT_GET8()->int:
    global script
    global script_pos
    if len(script) < 1: return None
    m = script[0]
    script = script[1:]
    script_pos +=1
    return int.from_bytes(m, "little")

def SCRIPT_GET16()->int:
    global script
    global script_pos
    if len(script) < 2: return None
    m = script[0]    
    m += script[1]

    script = script[2:]
    script_pos +=2
    return int.from_bytes(m, "little")

def SCRIPT_GET32()->int:
    global script
    global script_pos
    if len(script) < 4: return None
    m = script[0]    
    m += script[1]
    m += script[2]
    m += script[3]
    script = script[4:]
    script_pos +=4
    return int.from_bytes(m, "little")

def RANGE_COLLAPSE(v:int, m: int, M: int)->int:
    if (v < m): return m
    if (v > M): return M
    return v

#char  *STRING_GETSZ() { char *r = (char *)scrp; scrp += strlen((char *)scrp) + 1; return r; }
def STRING_GETSZ()->str:
    global script
    global script_pos
    
    ret = ""

    m = script[0]
    script = script[1:]
    script_pos +=1
    while m != b'\x00' and m.isascii():
        ret += m.decode("ascii")
        m = script[0]
        script = script[1:]
        script_pos +=1

    
    return ret.replace("@", "\"")

missing_images = []
wrong_images = {"H_PA": "H_PA0", 'H_PB':'H_PB0', 'H_PC': 'H_PC0', 'H_S4,0J':'H_S4', 'H_T3,0J':'H_T3', 'H_D':'H_D0'}
def collect_bg(s:str):
    global script_file
    global screen_size
    global screen_offset

    file_name = os.path.splitext(s)[0]
    
    if file_name in wrong_images.keys():
        file_name = wrong_images[file_name]
    file_name = "out\\"  + file_name  + ".BMP"
    out_file = file_name.replace("out\\", "vnds\\novel\\background\\").replace(".BMP", ".jpg")
    if os.path.isfile(out_file): return
    if not os.path.isfile(file_name):
        print(script_file)
        print("image file " + file_name + " does not exists\n")
        if not file_name in missing_images:
            missing_images.append(file_name)
    
    m = Image.open(file_name)
    if m.size[0] == 640:
        m = m.crop((32,8, 32 + 576, 8 + 376))
    m = m.resize(back_size, Image.Resampling.HAMMING )
    img = Image.new("RGB", screen_size, (0, 0, 0))
    img.paste(m, screen_offset)
    #img.paste(m, (32,52))
    mk_dirtrees(out_file)
    img.save(out_file)
    pass

def collect_mask(prev_bg_file, s):
    global screen_size
    global screen_offset

    prev_bg_file = "out\\" + os.path.splitext(prev_bg_file)[0] + ".BMP"
    out_file = "vnds\\novel\\background\\" + s.replace(".BMP", ".jpg")
    if os.path.isfile(out_file): return
    s = "out\\" + s
    b = Image.open(prev_bg_file)
    m = Image.open(s)
    mask = Image.open(s)
    base_name = os.path.basename(s).lower()

    datas = mask.getdata()
    newData = []
    if base_name != "i_17a.bmp" and base_name != "i_17b.bmp":
        for item in datas:
            if item[0] == 0 and item[1] == 255 and item[2] == 0:
                newData.append((0, 0, 0))
            else:
                newData.append((255, 255, 255))
    else:
        for item in datas:
            if item[0] == 83 and item[1] == 255 and item[2] == 0:
                newData.append((0, 0, 0))
            else:
                newData.append((255, 255, 255))

    mask.putdata(newData)
    mask = mask.convert("L")
    out_img = Image.composite(m, b, mask)

    out_img = out_img.resize((640, 420))
    
    img = Image.new("RGB", screen_size, (0, 0, 0))
    img.paste(out_img, screen_offset)
    mk_dirtrees(out_file)
    img.save(out_file)



def collect_character(s:str):
    global script_file
    global fg_size

    s = os.path.splitext(s)[0]
    mask_file = "out\\" + s.split("_")[0] + "_0.BMP"
    file_name = "out\\" + s + ".BMP"
    out_file = "vnds\\novel\\foreground\\" + s + ".png"
    if os.path.isfile(out_file): return
    if not os.path.isfile(file_name):
        print(script_file)
        print("image " + file_name + " does not exists.")
        exit()
    if not os.path.isfile(mask_file):
        print(script_file)
        print("Mask " + mask_file + "does not exists.")
        exit()
    
    m1 = Image.open(file_name).convert("RGBA")
    mask = Image.open(mask_file).convert("L")
    m1.putalpha(mask)
    mk_dirtrees(out_file)
    m1.resize(fg_size).save(out_file)

def get_map_option(x1:int, y1:int, x2:int, y2:int)->str:
    #114 42 167 78 Girl's dorm
    #182 117 237 135 Promenade
    #108 147 137 183 W.C.
    #75 187 98 232 Boy's dorm
    #237 136 297 155 Wood Field
    #258 171 297 187 Gym
    #144 227 223 249 Main field
    #275 202 321 221 Main Building
    #334 202 363 220 Cafeteria
    #332 222 350 269 Ishii Hall
    #305 279 343 315 Library
    #503 51 541 71 Cottage

    c = [114, 42, 167, 78, "Girl's dorm"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [182, 117, 237, 135, "Promenade"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [108, 147, 137, 183, "W.C."]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [75, 187, 98, 232, "Boy's dorm"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [237, 136, 297, 155, "Wood Field"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [258, 171, 297, 187, "Gym"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [144, 227, 223, 249, "Main field"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [275, 202, 321, 221, "Main Building"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [334, 202, 363, 220, "Cafeteria"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [332, 222, 350, 269, "Ishii Hall"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [305, 279, 343, 315, "Library"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    c = [503, 51, 541, 71, "Cottage"]
    if x1 == c[0] and y1 == c[1] and x2 == c[2] and y2 == c[3]: return c[4]
    
    print(script_file)
    print("Wrong clip for map.")
    exit()
    return "ERROR"

def convert_script(script_file: str):
    global script
    global vnds
    global jumps
    
    

    jumps = []
    
    read_script(script_file, True)
    read_script(script_file, False)


def read_script(script_file:str, collect_jumps:int):
    global script
    global vnds
    global script_pos
    global wrong_images
    global missing_scripts
    global flags
    global screen_offset
    script_pos = 0
    options = []
    map_options = []
    out_scr_file = script_file.replace("out\\", "vnds\\novel\\script\\").replace(".AB", ".scr")
    mk_dirtrees(out_scr_file)
    script = []
    with open(script_file, "rb") as sc:
        while True:
            m = sc.read(1)
            if not m: break
            script.append(m)
    vnds = open(out_scr_file, "w")
    vnds.write("\n")

    prev_bg_file = "black.jpg"
    while True:
        if not collect_jumps:
            for addr in jumps:
                if addr == script_pos:
                    vnds.write("label addr_" + str(addr) + "\n")
        op:int = SCRIPT_GET16()
        if op is None: break
        
        if debug: vnds.write("#op " + str(op) + "\n")
        if op == 0x02: # JUMP
            #print("jump")
            addr:int = SCRIPT_GET32()
            if not addr in jumps:
                jumps.append(addr)
            jname = "addr_" + str(addr)
            if debug: vnds.write("#jump " + jname + "\n")
            vnds.write("goto " + jname + "\n")

        elif op == 0x10: #{ // JUMP_IF
            #print("jump if")
            flag  = RANGE_COLLAPSE(SCRIPT_GET16(),  0, 999)
            op  = SCRIPT_GET8()
            value = SCRIPT_GET16()
            addr  = SCRIPT_GET32()

            if not addr in jumps:
                jumps.append(addr)

            if debug: vnds.write("#jump_if " + str(flag) + " " + str(op) + " " + str(value) + " -> " + str(addr) + "\n" )
            
            vnds.write("if flag_" + str(flag) + " ")
            
            if op == 123:
                vnds.write(">=") #<
            elif op == 61:
                vnds.write("!=") #==
            elif op == 125:
                vnds.write("<=") #>
            else:
                print(script_file)
                print("WRONG op in if jump " + str(op))
                exit()
            
            vnds.write(" " + str(value) + "\n")
            vnds.write("\tgoto addr_" + str(addr) + "\n")
            vnds.write("fi\n")
            """""
            switch (op) {
                case '=': if (!(save.flags[flag] == value)) GAME_SCRIPT_JUMP(addr); break; // ==
                case '}': if (!(save.flags[flag] >  value)) GAME_SCRIPT_JUMP(addr); break; // >, >= ??
                case '{': if (!(save.flags[flag] <  value)) GAME_SCRIPT_JUMP(addr); break; // <, <= ??
                default:
                    printf("JUMP_IF: unknown operator '%c'\n", op);
                    PROGRAM_EXIT(-1);
                break;
			}
            """
        elif op == 0x03: #{ // FLAG_SET_RANGE
            
            #print("FLAG_SET_RANGE")
            l = RANGE_COLLAPSE(SCRIPT_GET16(), 0, 999)
            h = RANGE_COLLAPSE(SCRIPT_GET16(), 0, 999)
            v = SCRIPT_GET16()
            
            if debug: vnds.write("#FLAG_SET_RANGE " + str(l) + " " + str(h) + " " + str(v) + "\n")
            #if v == 0: v = 1
            #for (; l < h; l++) save.flags[l] = v;
            for i in range(l,h):
                if "flag_" + str(i) in flags.keys():
                    vnds.write("setvar flag_" + str(i) + " = " + str(v) + "\n")
        elif op == 0x4: #{ // FLAG_SET
            #print("FLAG_SET")
            flag  = RANGE_COLLAPSE(SCRIPT_GET16(), 0, 999)
            op  = SCRIPT_GET8()
            value = SCRIPT_GET16()

            vnds.write("setvar flag_" + str(flag) + " ")
            if op == 61:
                vnds.write("=") 
            elif op == 43:
                vnds.write("+") 
            elif op == 45:
                vnds.write("-")
            else:
                print(script_file)
                print("FLAG_SET problem " + str(op))
                exit()

            vnds.write(" " + str(value) + "\n")

            """""
            switch (op) {
                case '=': save.flags[flag]  = value; break; // =
                case '+': save.flags[flag] += value; break; // + ??
                case '-': save.flags[flag] -= value; break; // - ?? (solo una vez -0??)
                default:
                    printf("SET: unknown operator '%c'\n", op);
                    PROGRAM_EXIT(-1);
                break;
            }
            """
            if debug: vnds.write("#FLAG_SET " + str(flag) + " "+ str(value) + "\n")
        elif op == 0x18: #{ // SCRIPT_CHANGE
            #print("SCRIPT_CHANGE")
            s = STRING_GETSZ().strip()
            if s == "":continue
            #if s in missing_scripts: continue
            if "F34" in s: continue
            if "F11_0" in s: continue
            
            vnds.write("jump " + os.path.splitext(s)[0] + ".scr\n")
        elif op == 0x19: #{ // GAME_END
            #print("GAME_END")
            vnds.write("jump main.scr\n")
            pass
            """""
            {
                int n;
                for (n = 0; n < 10; n++) save_s.gallery[n + 140] = 1;
            }
            SYS_SAVE();
            CREDIT_SHOW(0);
            """
        ### INPUT
        elif op == 0x00: #// TEXT
            #print("TEXT")
            #GAME_SAVE_POSITION_2();
            s = STRING_GETSZ()
            if len(s) == 0: continue
            vnds.write("text " + s + "\n")

        elif op == 0x50: #{ // SAVE_TITLE
            #print("SAVE_TITLE")
            s = STRING_GETSZ()
            if debug: vnds.write("#SAVE_TITLE " + s + "\n")
        elif op == 0x06: #{ // OPTION_RESET
            #print("OPTION_RESET")
            if debug: vnds.write("#OPTION_RESET\n")
            options = []
            pass
        elif op == 0x01: #{ // OPTION
            #print("OPTION")
            ptr = SCRIPT_GET32()
            s = STRING_GETSZ()
            if not ptr in jumps:
                jumps.append(ptr)
            options.append([s, ptr])
            if debug: vnds.write("#OPTION " + s + " " + str(ptr) + "\n")
        elif op == 0x07 or op == 0x0A: #{ // OPTION_SHOW | OPTION_RESHOW?
            #print("OPTION_SHOW")
            
            s = ""
            for o in options:
                s += o[0] + "|"
            s = s[:-1]
            vnds.write("choice " + s + "\n")
            for i in range(len(options)):
                vnds.write("if selected == " + str(i + 1) + "\n")
                vnds.write("\tgoto addr_" + str(options[i][1]) + "\n")
                vnds.write("fi\n") 
            if debug: vnds.write("#OPTION_SHOW\n")
            pass
        elif op == 0x37: #{ // MAP_IMAGES
            #print("MAP_IMAGES")
            s1 = STRING_GETSZ()
            s2 = STRING_GETSZ()
            if debug: vnds.write("#MAP_IMAGES " + s1 + " " + s2 + "\n")
            collect_bg(s1)
            collect_bg(s2)
            vnds.write("bgload " + os.path.splitext(s1)[0] + ".jpg 0\n")
            #strcpy(map_images[0], s1);
			#strcpy(map_images[1], s2);
        elif op == 0x38: #{ // MAP_OPTION_RESET
            #print("MAP_OPTION_RESET")
            map_options = []
            if debug: vnds.write("#MAP_OPTION_RESET\n")
            pass
        elif op == 0x40: #{ // MAP_OPTION
            #print('MAP_OPTION')
            ptr = SCRIPT_GET32()
            x1  = SCRIPT_GET16()
            y1  = SCRIPT_GET16()
            x2  = SCRIPT_GET16()
            y2  = SCRIPT_GET16()

            if not ptr in jumps:
                jumps.append(ptr)
            map_options.append([get_map_option(x1, y1, x2, y2), ptr])
            if debug: vnds.write("#MAP_OPTION " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2) + "\n")
            """""
            map_options[map_options_count].ptr = ptr;
            map_options[map_options_count].x1 = x1;
            map_options[map_options_count].y1 = y1;
            map_options[map_options_count].x2 = x2;
            map_options[map_options_count].y2 = y2;
            map_options_count++;
            """
        elif op == 0x41: #{ // MAP_OPTION_SHOW
            #print("MAP_OPTION_SHOW")
            #GAME_INPUT_MAP_OPTIONS();
            s = ""
            for o in map_options:
                s += o[0] + "|"
            s = s[:-1]
            vnds.write("choice " + s + "\n")
            for i in range(len(map_options)):
                vnds.write("if selected == " + str(i + 1) + "\n")
                vnds.write("\tgoto addr_" + str(map_options[i][1]) + "\n")
                vnds.write("fi\n") 
            if debug: vnds.write("#MAP_OPTION_SHOW\n")
            pass
        elif op == 0x11: #{ // WAIT
            #print("WAIT")
            t = SCRIPT_GET16()
            vnds.write("delay " + str(t) + "\n")
            #PROGRAM_DELAY(t * 10);
            if debug: vnds.write("#WAIT\n")
        #SOUND RELATED 
        elif op == 0x26: #{ // MUSIC_PLAY
            #print("MUSIC_PLAY")
            s = STRING_GETSZ()
            vnds.write("music " + s + ".mp3\n")
            if debug: vnds.write("#MUSIC_PLAY " + s + "\n")
        elif op == 0x28: #{ // MUSIC_STOP
            #print("MUSIC_STOP")
            vnds.write("music ~\n")
            if debug: vnds.write("#MUSIC_STOP\n")
            pass
        elif op == 0x2B: #{ // VOICE_PLAY
            #print("VOICE_PLAY")
            s = STRING_GETSZ()
            s = os.path.splitext(s)[0] + ".wav"
            vnds.write("sound " + s + " 1\n")
            out_sound = "vnds\\novel\\sound\\" + s
            if os.path.isfile(out_sound):continue
            mk_dirtrees(s)
            shutil.copy("out\\" + s, out_sound)
            if debug: vnds.write("#VOICE_PLAY " + s + "\n")
        elif op == 0x35: #{ // SOUND
            #print("SOUND")
            s = STRING_GETSZ()
            s = os.path.splitext(s)[0] + ".wav"
            vnds.write("sound " + s + " 1\n")
            if debug: vnds.write("#SOUND " + s + "\n")
            out_sound = "vnds\\novel\\sound\\" + s
            if os.path.isfile(out_sound):continue
            mk_dirtrees(out_sound)
            shutil.copy("out\\" + s, out_sound)
            #out_sound = "vnds\\novel\\wav\\" + s
            #mk_dirtrees(out_sound)
            #shutil.copy("out\\" + s, out_sound)
            
        elif op == 0x36: #{ // SOUND_STOP
            #print("SOUND_STOP")
            vnds.write('sound ~\n')
            if debug: vnds.write("#SOUND_STOP\n")
            pass
        #IMAGE RELATED
        elif op == 0x47 or op == 0x46: #{ // BACKGROUND_INNER
            s = os.path.splitext(STRING_GETSZ().strip())[0]
            #t = SCRIPT_GET8()
            if debug: vnds.write("#BACKGROUND_INNER " + str(s) + "\n")
            
            if s == "H_S4,0J":
                s = "H_S4"
                for _ in range(5): SCRIPT_GET8()
            if s == "H_T3,0J":
                s = "H_T3"
                for _ in range(5): SCRIPT_GET8()
            collect_bg(s)
            if s in wrong_images.keys():
                s = wrong_images[s]
                print(s)
                continue
            prev_bg_file = os.path.splitext(s)[0] + ".jpg"
            vnds.write("bgload " + prev_bg_file + "\n")
            #script = script[1:]
        elif op == 0x16: #{ // IMAGE_MASK
            #print("IMAGE_MASK")
            s = STRING_GETSZ()
            s = os.path.splitext(s)[0] + ".BMP"
            collect_mask(prev_bg_file, s)
            if debug: vnds.write("#mask " + s + "\n")
            vnds.write("bgload " + s.replace(".BMP", ".jpg") + " 0\n")
        elif op == 0x4B: #{ // CHARACTER
            #print("CHARACTER")
            s = STRING_GETSZ()
            collect_character(s)
            s = os.path.splitext(s)[0]
            vnds.write("bgload " + prev_bg_file + " 0\n")
            vnds.write("setimg " + s + ".png 64 6\n")
            if debug: vnds.write("#character " + s + "\n")
        elif op == 0x4C: #{ // TWO CHARACTERS
            #print("TWO CHARACTERS")
            s1 = STRING_GETSZ()
            s2 = STRING_GETSZ()
            collect_character(s1)
            collect_character(s2)
            vnds.write("bgload " + prev_bg_file + " 0\n")
            vnds.write("setimg " + s1 + ".png 0 6\n")
            vnds.write("setimg " + s2 + ".png 128 6\n")
            if debug: vnds.write("#character 1" + s1 + "\n")
            if debug: vnds.write("#character 2" + s2 + "\n")
        #IMAGE/EFFECT RELATED
        elif op == 0x4D: #{ // ANIMATION ABCDEF
            #print("ANIMATION ABCDEF")
            if debug: vnds.write("#ANIMATION ABCDEF" + "\n")
            pass
        elif op == 0x4F:   #// SCROLL_UP (add 'B')
            #print("SCROLL_UP (add 'B')")
            if debug: vnds.write("#SCROLL_UP (add 'B')\n")
            pass
        elif op == 0x4E: #{ // SCROLL_DOWN (add 'A')
            #print("SCROLL_DOWN (add 'A')")
            if debug: vnds.write("#SCROLL_UP (add 'A')\n")
            pass
        #EFFECT RELATED
        elif op == 0x30: #{ // CLIP
            #print("CLIP")
            clip_x = SCRIPT_GET16()
            clip_y = SCRIPT_GET16()
            clip_w = SCRIPT_GET16()
            clip_h = SCRIPT_GET16()
            vnds.write("#CLIP\n")
        elif op == 0x1E: #{ // FADE_OUT
            #print("FADE_OUT")
            vnds.write("bgload black.jpg 60\n")
            if debug: vnds.write("#FADE_OUT\n")
            pass
        elif op == 0x1F: #{ // FADE_OUT_WHITE
            #print("FADE_OUT_WHITE")
            vnds.write("bgload white.jpg 60\n")
            if debug: vnds.write("#FADE_OUT_WHITE\n")
            pass
        elif op == 0x4A: #{ // BUFFER_REPAINT_INNER
            #print("BUFFER_REPAINT_INNER")
            t = SCRIPT_GET16()
            if debug: vnds.write("#BUFFER_REPAINT_INNER " + str(t) + "\n")
            pass
        elif op == 0x14: #{ // BUFFER_REPAINT
            #print("BUFFER_REPAINT")
            t = SCRIPT_GET16()
            if debug: vnds.write("#BUFFER_REPAINT " + str(t) + "\n")
        #ERRORS --- Don't know why but those are errors in the script
        else:
            vnds.write("#-ERROR- " + str(op.to_bytes(2, "little")) + "\n")
            #script = script[2:]
            #vnds.write("jump " + out_scr_file + "\n")
            #jumps = []
            print("---------------------------------------------------------------------")
            print("In script file" + script_file + " op " + str(op) + " does not exists")
            print("---------------------------------------------------------------------")
            #print(script)
            #break
    vnds.close()
    pass




export_files()

not_used_corrupted_script_files = ["F17_34.AB"]

for script_file in glob("out\\**\\*.AB", recursive=True):
    if not os.path.basename(script_file) in not_used_corrupted_script_files:
        convert_script(script_file)


shutil.copy("main.scr", "vnds\\novel\\script\\main.scr")

Image.new("RGB", screen_size, (0, 0, 0)).save("vnds\\novel\\background\\black.jpg")
Image.new("RGB", screen_size, (255, 255, 255)).save("vnds\\novel\\background\\white.jpg")

collect_bg("TITLE")

Image.open("out\\TITLE.BMP").resize((32,32)).save("vnds\\novel\\icon.png")
Image.open("out\\TITLE.BMP").resize((100,75)).save("vnds\\novel\\thumbnail.png")

Image.open("out\\TITLE.BMP").resize((128,128)).save("vnds\\novel\\icon-high.png")
Image.open("out\\TITLE.BMP").resize((512,384)).save("vnds\\novel\\thumbnail-high.png")

info = open("vnds\\novel\\info.txt", "w")
info.write("title=Divi Dead\n")
info.close()

img_ini = open("vnds\\novel\\img.ini", "w")
img_ini.write("width=640\n")
img_ini.write("height=480")
img_ini.close()