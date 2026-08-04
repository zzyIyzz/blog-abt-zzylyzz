# -*- coding: utf-8 -*-
"""
Jone Chow's Blog - Local Markdown Editor
Run:  python editor_server.py
Open: http://localhost:8787
"""
import os
import re
import json
import subprocess
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(BASE, "content", "posts")
PORT = 8787

HTML = r"""<!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog Editor</title>
<style>
:root{--black:#000;--white:#fff;--gray:#888;--light:#e5e5e5;--bg:#f5f5f5;
--mono:"SF Mono","Fira Code","Consolas",monospace;
--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:var(--sans);background:var(--white);color:var(--black);font-size:14px;}
header{display:flex;justify-content:space-between;align-items:center;
border-bottom:1px solid var(--light);padding:0 20px;height:50px;}
header h1{font-family:var(--mono);font-size:16px;font-weight:600;}
header .actions{display:flex;gap:8px;}
button{font-family:var(--mono);font-size:12px;padding:7px 14px;cursor:pointer;
background:var(--white);color:var(--black);border:1px solid var(--black);}
button:hover{background:var(--black);color:var(--white);}
button.ghost{border-color:var(--light);color:var(--gray);}
button.ghost:hover{border-color:var(--black);color:var(--black);background:var(--white);}
.layout{display:flex;height:calc(100vh - 50px);}
.sidebar{width:240px;border-right:1px solid var(--light);overflow-y:auto;flex-shrink:0;}
.sidebar .item{padding:12px 16px;border-bottom:1px solid var(--light);cursor:pointer;}
.sidebar .item:hover{background:var(--bg);}
.sidebar .item.active{background:var(--black);color:var(--white);}
.sidebar .item .t{font-size:13px;font-weight:600;}
.sidebar .item .d{font-family:var(--mono);font-size:11px;color:var(--gray);margin-top:2px;}
.sidebar .item.active .d{color:var(--light);}
.editor{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.meta{padding:14px 20px;border-bottom:1px solid var(--light);display:flex;flex-direction:column;gap:8px;}
.meta input{font-family:var(--mono);font-size:13px;padding:8px 10px;
border:1px solid var(--light);background:var(--white);color:var(--black);}
.meta input:focus{outline:none;border-color:var(--black);}
.meta .row{display:flex;gap:8px;}
.meta .row input:first-child{flex:2;}
.meta .row input:last-child{flex:1;}
.panes{flex:1;display:flex;overflow:hidden;}
.pane{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.pane+.pane{border-left:1px solid var(--light);}
.pane .label{font-family:var(--mono);font-size:11px;text-transform:uppercase;
letter-spacing:.05em;color:var(--gray);padding:8px 20px;border-bottom:1px solid var(--light);}
textarea{flex:1;width:100%;border:none;resize:none;padding:20px;
font-family:var(--mono);font-size:13px;line-height:1.7;color:var(--black);background:var(--white);}
textarea:focus{outline:none;}
.preview{flex:1;overflow-y:auto;padding:20px;line-height:1.8;font-size:14px;}
.preview h1,.preview h2,.preview h3{margin:20px 0 10px;font-weight:600;}
.preview h1{font-size:22px;}.preview h2{font-size:18px;}.preview h3{font-size:16px;}
.preview p{margin-bottom:14px;}
.preview code{font-family:var(--mono);font-size:12px;background:var(--bg);padding:2px 5px;}
.preview pre{background:var(--bg);border:1px solid var(--light);padding:14px;overflow-x:auto;margin:14px 0;}
.preview pre code{background:none;padding:0;}
.preview blockquote{border-left:2px solid var(--black);padding:8px 16px;color:var(--gray);margin:14px 0;}
.preview ul,.preview ol{padding-left:22px;margin-bottom:14px;}
.preview a{color:var(--black);}
.preview hr{border:none;border-top:1px solid var(--light);margin:20px 0;}
.status{font-family:var(--mono);font-size:11px;color:var(--gray);padding:6px 20px;
border-top:1px solid var(--light);}
@media(max-width:900px){.panes{flex-direction:column;}.pane+.pane{border-left:none;border-top:1px solid var(--light);}}
</style>
</head>
<body>
<header>
  <h1>Jone Chow's Blog / Editor</h1>
  <div class="actions">
    <button class="ghost" onclick="newPost()">New</button>
    <button class="ghost" onclick="del()">Delete</button>
    <button onclick="save()">Save</button>
    <button onclick="publish()">Publish</button>
  </div>
</header>
<div class="layout">
  <div class="sidebar" id="list"></div>
  <div class="editor">
    <div class="meta">
      <input id="title" placeholder="文章标题 Title">
      <div class="row">
        <input id="tags" placeholder="标签 tags (逗号分隔)">
        <input id="desc" placeholder="描述 description">
      </div>
    </div>
    <div class="panes">
      <div class="pane">
        <div class="label">Markdown</div>
        <textarea id="md" placeholder="在这里写你的 Markdown 内容..." oninput="render()"></textarea>
      </div>
      <div class="pane">
        <div class="label">Preview</div>
        <div class="preview" id="preview"></div>
      </div>
    </div>
    <div class="status" id="status">Ready.</div>
  </div>
</div>
<script>
let currentFile = null;
function $(id){return document.getElementById(id);}
function setStatus(m){$('status').textContent=m;}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function md2html(md){
  let lines=md.split('\n'),out=[],inCode=false,codeBuf=[],para=[];
  function flush(){if(para.length){out.push('<p>'+para.join('<br>')+'</p>');para=[];}}
  for(let raw of lines){
    let line=esc(raw);
    if(/^```/.test(raw.trim())){
      if(inCode){out.push('<pre><code>'+codeBuf.join('\n')+'</code></pre>');codeBuf=[];inCode=false;}
      else{flush();inCode=true;}
      continue;
    }
    if(inCode){codeBuf.push(line);continue;}
    let m;
    if(m=line.match(/^######\s+(.*)/)){flush();out.push('<h6>'+m[1]+'</h6>');}
    else if(m=line.match(/^#####\s+(.*)/)){flush();out.push('<h5>'+m[1]+'</h5>');}
    else if(m=line.match(/^####\s+(.*)/)){flush();out.push('<h4>'+m[1]+'</h4>');}
    else if(m=line.match(/^###\s+(.*)/)){flush();out.push('<h3>'+m[1]+'</h3>');}
    else if(m=line.match(/^##\s+(.*)/)){flush();out.push('<h2>'+m[1]+'</h2>');}
    else if(m=line.match(/^#\s+(.*)/)){flush();out.push('<h1>'+m[1]+'</h1>');}
    else if(/^(-{3,}|\*{3,})$/.test(raw.trim())){flush();out.push('<hr>');}
    else if(m=line.match(/^&gt;\s?(.*)/)){flush();out.push('<blockquote>'+m[1]+'</blockquote>');}
    else if(m=line.match(/^[-*]\s+(.*)/)){flush();out.push('<ul><li>'+m[1]+'</li></ul>');}
    else if(m=line.match(/^\d+\.\s+(.*)/)){flush();out.push('<ol><li>'+m[1]+'</li></ol>');}
    else if(raw.trim()===''){flush();}
    else{para.push(inline(line));}
  }
  flush();
  if(inCode)out.push('<pre><code>'+codeBuf.join('\n')+'</code></pre>');
  return out.join('\n');
}
function inline(s){
  s=s.replace(/`([^`]+)`/g,'<code>$1</code>');
  s=s.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  s=s.replace(/\*([^*]+)\*/g,'<em>$1</em>');
  s=s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');
  return s;
}
function render(){$('preview').innerHTML=md2html($('md').value);}
async function loadList(){
  const r=await fetch('/api/list');const data=await r.json();
  $('list').innerHTML=data.map(p=>
    '<div class="item'+(p.file===currentFile?' active':'')+'" onclick="load(\''+p.file+'\')">'+
    '<div class="t">'+esc(p.title)+'</div><div class="d">'+p.date+'</div></div>').join('')
    ||'<div class="item"><div class="d">No posts yet.</div></div>';
}
async function load(file){
  currentFile=file;
  const r=await fetch('/api/load?file='+encodeURIComponent(file));
  const d=await r.json();
  $('title').value=d.title||'';$('tags').value=(d.tags||[]).join(', ');
  $('desc').value=d.description||'';$('md').value=d.body||'';
  render();loadList();setStatus('Loaded: '+file);
}
function newPost(){
  currentFile=null;
  $('title').value='';$('tags').value='';$('desc').value='';$('md').value='';
  render();loadList();setStatus('New post. Write something.');
}
function collect(){
  return {file:currentFile,title:$('title').value,tags:$('tags').value,
    desc:$('desc').value,body:$('md').value};
}
async function save(){
  const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(collect())});
  const d=await r.json();
  if(d.ok){currentFile=d.file;loadList();setStatus('Saved: '+d.file);}
  else setStatus('Error: '+d.error);
}
async function publish(){
  setStatus('Publishing...');
  const r=await fetch('/api/publish',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(collect())});
  const d=await r.json();
  setStatus(d.ok?('Published! '+d.output):('Error: '+d.error));
  if(d.ok)loadList();
}
async function del(){
  if(!currentFile){setStatus('Nothing selected to delete.');return;}
  if(!confirm('Delete "'+currentFile+'" ?'))return;
  const r=await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({file:currentFile})});
  const d=await r.json();
  if(d.ok){setStatus('Deleted: '+currentFile);newPost();loadList();}
  else setStatus('Error: '+d.error);
}
loadList();
</script>
</body>
</html>"""


def slugify(s):
    s = s.strip().lower()
    s = re.sub(r'[^\w\u4e00-\u9fa5]+', '-', s)
    return s.strip('-') or 'untitled'


def parse_frontmatter(text):
    """Split front matter and body."""
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', text, re.S)
    if not m:
        return {}, text
    fm, body = {}, m.group(2)
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"')
    # tags list
    tm = re.search(r'tags:\s*\[([^\]]*)\]', m.group(1))
    if tm:
        fm['tags'] = [t.strip().strip('"\'') for t in tm.group(1).split(',') if t.strip()]
    return fm, body


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length).decode('utf-8')

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ('/', '/index.html'):
            self._send(200, HTML, 'text/html; charset=utf-8')
        elif u.path == '/api/list':
            posts = []
            if os.path.isdir(POSTS):
                for f in sorted(os.listdir(POSTS), reverse=True):
                    if f.endswith('.md'):
                        try:
                            with open(os.path.join(POSTS, f), encoding='utf-8') as fh:
                                fm, _ = parse_frontmatter(fh.read())
                            posts.append({'file': f, 'title': fm.get('title', f),
                                          'date': fm.get('date', '')[:10]})
                        except Exception:
                            posts.append({'file': f, 'title': f, 'date': ''})
            self._send(200, json.dumps(posts))
        elif u.path == '/api/load':
            q = parse_qs(u.query)
            fname = os.path.basename(q.get('file', [''])[0])
            path = os.path.join(POSTS, fname)
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as fh:
                    fm, body = parse_frontmatter(fh.read())
                self._send(200, json.dumps({'title': fm.get('title', ''),
                                            'tags': fm.get('tags', []),
                                            'description': fm.get('description', ''),
                                            'body': body}))
            else:
                self._send(404, json.dumps({'error': 'not found'}))
        else:
            self._send(404, json.dumps({'error': 'not found'}))

    def do_POST(self):
        u = urlparse(self.path)
        data = json.loads(self._read_body() or '{}')
        if u.path == '/api/save':
            self._save(data)
        elif u.path == '/api/publish':
            self._save(data)
            self._publish()
        elif u.path == '/api/delete':
            self._delete(data)
        else:
            self._send(404, json.dumps({'error': 'not found'}))

    def _delete(self, data):
        try:
            fname = os.path.basename(data.get('file') or '')
            path = os.path.join(POSTS, fname)
            if os.path.isfile(path):
                os.remove(path)
                self._send(200, json.dumps({'ok': True}))
            else:
                self._send(404, json.dumps({'ok': False, 'error': 'not found'}))
        except Exception as e:
            self._send(500, json.dumps({'ok': False, 'error': str(e)}))

    def _save(self, data):
        try:
            title = (data.get('title') or 'Untitled').strip()
            tags = [t.strip() for t in (data.get('tags') or '').split(',') if t.strip()]
            desc = (data.get('desc') or '').strip()
            body = data.get('body') or ''
            date = datetime.datetime.now()
            fname = data.get('file') or (date.strftime('%Y-%m-%d') + '-' + slugify(title) + '.md')
            if not fname.endswith('.md'):
                fname += '.md'
            tags_yaml = '[' + ', '.join('"%s"' % t for t in tags) + ']'
            content = '---\ntitle: "%s"\ndate: %s+08:00\ndraft: false\ntags: %s\ndescription: "%s"\n---\n\n%s' % (
                title, date.strftime('%Y-%m-%dT%H:%M:%S'), tags_yaml, desc, body)
            os.makedirs(POSTS, exist_ok=True)
            with open(os.path.join(POSTS, fname), 'w', encoding='utf-8') as fh:
                fh.write(content)
            self._saved_file = fname
            self._send(200, json.dumps({'ok': True, 'file': fname}))
        except Exception as e:
            self._send(500, json.dumps({'ok': False, 'error': str(e)}))

    def _publish(self):
        try:
            fname = getattr(self, '_saved_file', None)
            cmds = [
                ['git', 'add', '-A'],
                ['git', 'commit', '-m', 'post: %s' % (fname or 'update')],
                ['git', '-c', 'http.sslVerify=false', 'push', 'origin', 'main'],
            ]
            out = []
            for c in cmds:
                r = subprocess.run(c, cwd=BASE, capture_output=True, text=True)
                out.append((r.stdout + r.stderr).strip())
            self._send(200, json.dumps({'ok': True, 'output': 'Pushed to GitHub.'}))
        except Exception as e:
            self._send(500, json.dumps({'ok': False, 'error': str(e)}))


if __name__ == '__main__':
    os.makedirs(POSTS, exist_ok=True)
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print('Blog Editor running at http://localhost:%d' % PORT)
    print('Press Ctrl+C to stop.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
