# Hypercraft
**Challenge scenario**: This email seems to have come from one of our agents, Axel Knight, but Axel has been missing for weeks, and we believe him to be compromised. The email claims to have information that could be vital to our winning this war, but before we use it, we want to make sure it is safe to open. Analyze the given email and see if it's real, or if it's just the Arodorians trying to phish us, and find the flag.

## First stage
An .eml file is provided, which is the extension of Outlook email.
![image](./images/S1UEcb1AZe.png)
A very long Base64 encoded string is given, which is a html document.
![image](./images/rkcMs-1C-x.png)
I saved the output into a sth.html, when I openned it, a website appeared and a zip file is auto downloaded.
![image](./images/H1c82-k0bx.png)
Unzipped it reveals an obfuscated Javascript block.

## Second stage
![image](./images/S1cAa-yAWx.png)
Obfuscationn....
Removed all those nodes reveals the hidden malware.
![image](./images/r1uUCbJRWg.png)
It will remove all s, V in string uwetjyhi. It iterates through the cleaned string in pairs of 2 characters at a time. Converts into hex string and finally calls out phfljyaj. Here I used wscript.echo() to prints out the result.
Executed that malicious script revealed another Javascript block.
![image](./images/HkAMeMJC-e.png)

## Third stage
Continuing with dynamic analysis, where I executed that script on a Virtual Machine, instead of static analysis. 
![image](./images/ryNRZGJR-g.png)
In some last line, the script will pop up a fake notification, bypass antivirus mechanism, while the real malware is still running in victim's machine.
I also notice that variable ynvjonvw also doing some .split("!"), so perhaps there must be something in it. Using wscript.echo() again to see the result.
![image](./images/BJkPmMJAbl.png)
It will decode Base64 and deflate a malicious string to get the next payload.

## Fourth stage
![image](./images/ByERX4yRZx.png)
There is a uycxq() function which executes XOR actions from a hex characters and a XOR key.
![image](./images/rywDN4J0Zx.png)
I also found this block which are some last lines of that malicious obfuscated script. Creating the task action, setting user principal, and configuring task settings.
So I started decoding those hex strings for more details.
![image](./images/H1ZNrEJCZx.png)
![image](./images/SyLKBEkRZl.png)
![image](./images/SJ0vUEJAWe.png)
The attacker has used Powershell to execute harmful commands focusing on persistence establishment.

**FLAG: HTB{l0ts_of_l4Y3rs_iN_th4t_1}**

---

