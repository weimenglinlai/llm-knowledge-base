import requests, json, os, glob, time
B="http://127.0.0.1:3001"
s=requests.Session(); s.trust_env=False
KNOW=r"project/学习//Ai前沿技术/项目4/knowledge"
slug=s.get(B+"/api/workspaces",timeout=30).json()["workspaces"][0]["slug"]
print("slug:",slug)

files=sorted(glob.glob(os.path.join(KNOW,"*.docx")))
for f in files:
    name=os.path.basename(f)
    with open(f,"rb") as fh:
        r=s.post(B+f"/api/workspace/{slug}/upload",
                 files={"file":(name,fh,"application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                 data={"addToWorkspaces":slug}, timeout=300)
    print(name, r.status_code, r.text[:150].replace("\n"," "))
