f = open('ioctl_list') # found by find_ioctls.py
m = open('manually_found') # found by the Mach V Eyeball
i = open('ignore_list') # removed from the output of find_ioctls.py

ioctls = [] # ones we want to actually process

for ioctl in f:
    ioctls.append(eval(ioctl))
for ioctl in m:
    ioctls.append(eval(ioctl))

mp = { "_IO": "none", "_IOR": "read", "_IOW": "write", "_IOWR": "readwrite",
        "DRM_IO": "none", "DRM_IOR": "read", "DRM_IOW": "write", "DRM_IOWR": "readwrite"}

tys = {
        "__uint8_t": "u8",
        "__uint16": "u16",
        "__uint32_t": "u32",
        "__uint64_t": "u64",
        "__int8_t": "i8",
        "__int16": "i16",
        "__int32_t": "i32",
        "__int64_t": "i64",
        "__u8": "u8",
        "__u16": "u16",
        "__u32": "u32",
        "__u64": "u64",
        "__s8": "i8",
        "__s16": "i16",
        "__s32": "i32",
        "__s64": "i64",
        "int": "c_int",
        "long": "c_long",
}

utys = {
        "int": "c_uint",
        "long": "c_ulong",
        "char": "c_uchar",
}

def translate(ty):
    if len(ty) == 1:
        return tys.get(ty[0], "FIXME1<%s>" % ty)
    elif len(ty) == 2:
        if ty[0] == "struct":
            return "Struct_%s" % ty[1]
        elif ty[0] == "unsigned":
            return utys[ty[1]]
        else:
            return "FIXME2<%s>" % ty
    elif ty[-1] == '*':
        return "*mut " + translate(ty[:-1])
    elif ty[-1] == ']':
        count = ty[-2]
        return "[%s; %s]" % (translate(ty[:-3]), count)
    else:
        return "FIXME3<%s>" % ty

def translate_type_code(ty):
    if ty[0] == "'":
        return "b" + ty
    else:
        return ty

def process(ioctl):
    name = ioctl[0]
    rhs = ioctl[1:-1] # remove '#' or trailing comment
    cmd = rhs[0]
    body = rhs[2:-1]

    if cmd == "_IO":
        print("ioctl!(none %s with %s, %s);" % (name.lower(), translate_type_code(body[0]),
            body[2]))
    elif cmd == '_IOR' or cmd == '_IOW' or cmd == '_IOWR':
        if body[3] == ',':
            # this looks like _IOR(X, B, type...)
            first = body[0]
            second = body[2]
            ty = body[4:]
            print("ioctl!(%s %s with %s, %s; %s);" % (mp[cmd], name.lower(),
                translate_type_code(first), second, translate(ty)))
        elif body[3] == '+':
            first = body[0]
            second = " ".join(body[2:5])
            ty = body[6:]
            print("ioctl!(%s %s with %s, %s; %s);" % (mp[cmd], name.lower(),
                translate_type_code(first), second, translate(ty)))
            # We probably have _IOR(X, B + C, type...)
        else:
            print("This really shouldn't happen!")
            exit()
    elif cmd == "_IOC":
        print("_IOC_CRAP %s" % ioctl)
    elif cmd == "DRM_IO" or cmd == "DRM_IOR" or cmd == "DRM_IOW" or cmd == "DRM_IOWR":
        # rewrite into "canonical" version.
        process([name, cmd[3:], "(", "DRM_IOCTL_BASE", ","] + rhs[2:] + ["#"])
    elif len(rhs) == 1: # single constant :(
        print("ioctl!(bad %s with %s);" % (name.lower(), rhs[0]))
    elif len(rhs) == 3 and rhs[0] == "(": # single constant in parens
        print("ioctl!(bad %s with %s);" % (name.lower(), rhs[1]))
    elif rhs[2] == "+": # we have the sum of two constants
        print("ioctl!(bad %s with %s);" % (name.lower(), " ".join(rhs[1:-1])))
    elif rhs[2] == "|": # we have an or of two constants (eugh)
        print("ioctl!(bad %s with %s);" % (name.lower(), " ".join(rhs[1:-1])))
    else:
        print("// TODO #define %s %s" % (name, " ".join(rhs)))

for ioctl in ioctls:
    process(ioctl)