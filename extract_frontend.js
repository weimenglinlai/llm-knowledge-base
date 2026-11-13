const fs=require('fs'),path=require('path');
const asarPath='project/学习//Ai前沿技术/项目4/anythingLLM/resources/app.asar';
const outRoot='project/学习//Ai前沿技术/项目4/frontend';
const buf=fs.readFileSync(asarPath);
const headerSize=buf.readUInt32LE(4);
const dataStart=8+headerSize;
const j=JSON.parse(buf.toString('utf8',16,16+buf.readUInt32LE(12)));
let n=0;
function walk(node,rel){
  for(const [k,v] of Object.entries(node.files||{})){
    const p=rel?rel+'/'+k:k;
    if(v.files)walk(v,p);
    else{
      const s=dataStart+parseInt(v.offset), e=s+v.size;
      const dest=path.join(outRoot,p);
      fs.mkdirSync(path.dirname(dest),{recursive:true});
      fs.writeFileSync(dest,buf.slice(s,e));
      n++;
    }
  }
}
walk(j.files['dist'],'');
console.log('extracted',n,'files to',outRoot);
