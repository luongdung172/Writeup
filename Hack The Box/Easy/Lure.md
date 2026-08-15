### Lure
**Challenge scenario**: The finance team received an important looking email containing an attached Word document. Can you take a look and confirm if it&#039;s malicious?

#### Overview
The challenge brings a Word document. 
![image](./images/ryTvH0Di-g.png)
This raised suspicion about VBA Macros.
**Oleid** confirms it.
![image](./images/BJehBCvsZl.png)

#### VBA Macros
![image](./images/HJk1U0wobx.png)
No AutoOpen() function as usual, but instead Document_Open(). This macro will run whenever clients open this document. A powershell command will be executed, it is encoded Base64.
![image](./images/BJ6SDAPiWl.png)
So this Powershell script downloads something from an URL and execute it. $PshOMe and $PsHoME are two enviroment variables available in Powershell.

#### Decode URL
Rebuild the URL expose the flag of this challenge.
![image](./images/HJa6DADsZe.png)
Partly being URL encoded.
![image](./images/HkGxuAvoWx.png)
**FLAG: HTB{k4REfUl_w1Th_Y0UR_d0CuMeNT5}**

---

