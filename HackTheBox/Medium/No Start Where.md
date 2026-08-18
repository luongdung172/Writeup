# No Start Where
**Challenge scenario**: As echoes of the Dark War lingered in UNZ's cyber-warfare HQ, a beacon blinked ominously. An analyst turned a wary eye to the screen. The alarm signal originated from the main system that controls the mining machinery! It was an attack from the Board of Arodor, aimed at crippling the mining infrastructure. Initial investigation of the network traffic revealed that the system has been compromised! Your task is to disinfect the system by uncovering the infiltration method and potential post-exploitation steps!

## Overview
Only the packet capture is provided, but it is enough. 91,8% of packets are transfered through TCP Protocol, including some TLS packets. But it is lucky that I did not have to decrypt TLS traffic in this challenge.
![image](./images/ByzQsClA-e.png)
I followed TCP Stream for more detail.
![image](./images/ryTVnReCbx.png)
![image](./images/ry0O2ClAWe.png)
Victim has installed a zip file which includes a screen saver file. And an executable named WINWORD.EXE, this is the default application that used to open Microsoft doc documents. But what suspicious is that although its name has the extension of .exe, it has a 7z header instead of MZ, showing that this file has been 7z compressed. 
So I extract both these two files for furthur analysis. Renamed WINWORD.EXE to WINWORD.7z to decompress it, but it required a password. 
So I started to examine that baseline.scr file.

## Finding 7z compressed password
Inside the zip file, there is another "Security Baseline Discipline.docx" file, but it is just for decoy, no VBA, no macros. First, I threw that scr file on any.run, and it executed this powershell command.
![image](./images/rJ3MekZCbl.png)
The attacker has downloaded this file from his own IP address, this explain why it is not an executable despite its extension. But there is no command that used to decompress the 7z compressed file.
So I used my virtual machine, combined with Procmon (Process Monitor), filter for Process name is baseline.scr and cmd.exe.
![image](./images/rJmE-JZ0-l.png)
A bat file which is stored in /temp directory is executed. I tried to export this file but it is deleted immediately after execution. So with some help of Gemini, I did a bit configuration modification in /temp directory, so that all files and folders created in this directory will not be deleted.
![image](./images/BJbbzJZAbe.png)
Run that baseline.scr file again and I has successfully had that bat file.
![image](./images/H14LzkZ0-l.png)
![image](./images/Hyx4Qk-RZg.png)
This bat file has been batch obfucated, using enviroment variables to hide real execution commands. For example, %PUBLIC:~x,y% means from C:\Users\Public, from x index, take y characters. So %PUBLIC:~5,1% = e (C:\Us**e**rs\Public).
I did google a bit to find for some batch deobfuscator tools, and I found this repo.
![image](./images/BkjFH1ZCbg.png)
Cloned it to my machine and deobfuscated that batch file successfully.
![image](./images/Hk9EIJZRbx.png)
This commands are seen in any.run earlier, but I have no idea why that unzip command is not shown. Anyway we now have the password, let's decompress it and analyze that bundau.dll (the author from VietNam???)
![image](./images/SkRcPyZCbe.png)
I threw that malicious bundau.dll on VirusTotal and found out that this is used to install some backdoor, and decrypt data using Havoc (a popular C2 framework).
![image](./images/BywfOk-0bx.png)
Since we have known that the traffic is encrypted by Havoc C2, let's start decrypting it.

## Decrypt traffic
I found [this ](https://www.immersivelabs.com/resources/c7-blog/havoc-c2-framework-a-defensive-operators-guide) document, which is so detail of how to decrypt Havoc encrypted traffic, especially this picture.
![image](./images/H17JFJZC-x.png)
So I must view the traffic in Hex Dump, take its AES key and IV which is located in the first packet transfered, then use AES-CTR to decrypt it.
![image](./images/Hy5dY1ZRWe.png)
Then I used Cyberchef to decrypt.
![image](./images/SkDs51-0Zg.png)
But notably, the response from server is encrypted a bit different. Using the same Key and IV, but the ciphertext starts after we remove first 9 bytes.
![image](./images/SyCE2JbAbe.png)
After this machine being pwned, the attacker did some post-exploitation stuffs, as decribed in the scenario. Some basic commands has been executed.
![image](./images/SkYP3y-0-g.png)
![image](./images/SyEn2ybR-l.png)
![image](./images/rJt1py-Abg.png)
![image](./images/r14tTy-AZg.png)
![image](./images/S1UaT1ZAZe.png)
The response of **tasklist** command is posted in three continuos packages, here I just decrypt the last one.
![image](./images/ryzzCJZ0Wx.png)
Next up
![image](./images/SJVU0y-RZx.png)
![image](./images/H1_o0JWCWl.png)
![image](./images/B1XHyl-0Zl.png)
Finally something smells off. The attacker has added a new user named **fileshare** and set its password, then set this user to administrator. So a backdoor has successfully been established.
![image](./images/HktJxxbC-x.png)
![image](./images/rJ0telbCbx.png)
![image](./images/rk8RggZ0Ze.png)

Finally, the attacker downloaded an executable

![image](./images/ryHbfeZRZg.png)

But there are some extra data before the MZ header, so I thought of an idea, convert to hex then remove those bytes manually.
![image](./images/S1_OMeZ0Ze.png)

## Executable analysis
I exported this executable. From DIE, it is compiled in C#, which is great because I can examine it using dotPeek.
![image](./images/SJ9s7xZAbl.png)
The Main() function calls to Checks()
![image](./images/HJ9tVlb0Ze.png)
Then Checks() function will calls to unhide() function with two variables, string and key.
![image](./images/r1J1rxZCbx.png)
The unhide() function will execute XOR between each byte in string with key[index % key.length], where key.length=16.
![image](./images/B1qVBeZC-e.png)
With this information, I used a very simple Python script to execute XOR.
![image](./images/BkyjLxZ0Zg.png)
And the flag is found.

**FLAG: HTB{4_r4ns0mw4r3_4lw4ys_wr34k5_h4v0c}**

---

