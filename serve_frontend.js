// 静态前端 + /api 反向代理到 AnythingLLM 后端(3001)
const http=require('http'),fs=require('fs'),path=require('path'),url=require('url');
const ROOT=path.join(__dirname,'frontend');
const BACKEND='http://127.0.0.1:3001';
const PORT=Number(process.env.FRONT_PORT||8088);
const MIME={'.html':'text/html;charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.json':'application/json','.ico':'image/x-icon','.woff2':'font/woff2','.ttf':'font/ttf','.map':'application/json'};
http.createServer((req,res)=>{
  if(req.url.startsWith('/api')||req.url.startsWith('/v1')){
    const p=url.parse(req.url);
    const proxy=http.request({host:'127.0.0.1',port:3001,path:req.url,method:req.method,headers:req.headers},pr=>{
      res.writeHead(pr.statusCode,pr.headers);pr.pipe(res);});
    proxy.on('error',e=>{res.writeHead(502);res.end('proxy error '+e.message);});
    req.pipe(proxy);return;
  }
  let f=path.join(ROOT,decodeURIComponent(url.parse(req.url).pathname));
  if(!f.startsWith(ROOT)) {res.writeHead(403);return res.end();}
  if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
  if(!fs.existsSync(f))f=path.join(ROOT,'index.html');
  res.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'});
  fs.createReadStream(f).pipe(res);
}).listen(PORT,'127.0.0.1',()=>console.log('frontend on http://127.0.0.1:'+PORT));
