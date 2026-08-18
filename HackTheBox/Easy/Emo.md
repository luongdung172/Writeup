### Emo
**Challenge scenario**: WearRansom ransomware just got loose in our company. The SOC has traced the initial access to a phishing attack, a Word document with macros. Take a look at the document and see if you can find anything else about the malware and perhaps a flag.

#### Overview
So the challenge gives a .doc file.
Analyzing a bit, this files has been infected by VBA macros.
![image](./images/r16LWh7ibx.png)
Using olevba returns a long obfuscated Powershell script.
![image](./images/ryVa-hQjWg.png)
Hmm... stuck for a while here.

#### Dynamic Analysis
I switch to dynamic analysis, which is running the malicious file to identify its behavior. But ofcourse not on my real machine, I used **any.run**.
![image](./images/Sk3WUh7jWl.png)
Turns out if users open this document, it will somehow open powershell.exe and run that malicious script, using -windowstyle hidden to avoid being seen by users.
After decode Base64, I have a obfuscated Powershell script.
![image](./images/SyicU2XjZx.png)
After some line break, I spotted an array doing some conversion.
![image](./images/r1qHK2QiZe.png)
The array is splited into pieces. The script execute XOR on every element in the array with key 0xdf, then encode Base64 for furthur actions.

#### Decode the flag
So I join parts of the array and XOR with 0xdf, I thought I also need to encode Base64, but the flag appears after XOR action.
![image](./images/SkEqj3Qi-g.png)
**FLAG: HTB{4n0th3R_d4Y_AnoThEr_pH1Sh}**

---

