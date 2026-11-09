from pathlib import Path
import json, csv
root=Path(__file__).resolve().parents[2]
with (root/'localization/en_ru.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
template=r'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>LeafGreen · Студия перевода EN / RU</title>
<style>
:root{font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif;color:#263747;background:#f5f8f6;font-synthesis:none}
*{box-sizing:border-box}body{margin:0}button,input,textarea,select{font:inherit}button{cursor:pointer}button:disabled{cursor:not-allowed;opacity:.44}
.top{background:#fff;border-bottom:1px solid #dce6e1;padding:18px clamp(14px,3vw,42px);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:17px}
.brand{display:flex;gap:13px;align-items:center}.logo{height:44px;width:44px;display:grid;place-items:center;border-radius:14px;background:#176d54;color:#fff;font-weight:800;font-size:24px;box-shadow:0 4px 10px #0d69452a}
h1{margin:0;font-size:20px;letter-spacing:-.5px;font-weight:760}.sub{color:#667b74;font-size:12px;margin-top:3px}.topActions{display:flex;gap:9px;align-items:center;flex-wrap:wrap}
button{padding:10px 14px;border:1px solid #d4e0da;border-radius:9px;color:#2c5547;background:#fff;font-weight:600;font-size:13px}
button:hover:not(:disabled){background:#edf6f1;border-color:#94b6a5}button.primary{background:#176d54;color:#fff;border-color:#176d54}button.primary:hover:not(:disabled){background:#105640}.mutedButton{font-weight:500}.fileInput{display:none}
.metrics{background:#fff;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:12px clamp(14px,3vw,42px) 16px;border-bottom:1px solid #dce6e1}.metric{padding:0 15px;border-left:3px solid #dce9e3}.metric:first-child{border-left-color:#176d54}.metric strong{display:block;font-size:19px;letter-spacing:-.5px}.metric small{font-size:12px;color:#71867e}.progress{grid-column:1/-1;height:6px;border-radius:20px;background:#e5efe9;overflow:hidden;margin-top:1px}.progressFill{height:100%;width:0%;background:#1b8865;transition:width .2s}
.shell{display:grid;grid-template-columns:335px minmax(0,1fr);min-height:calc(100vh - 160px)}
aside{border-right:1px solid #dce6e1;background:#fff;padding:20px 16px;min-width:0}.sidetitle{font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:1px;color:#71857c;margin:0 0 12px}.search{width:100%;padding:12px;border-radius:10px;border:1px solid #cdded5;background:#fafcfb;outline-color:#439778;font-size:13px}.filterrow{display:flex;gap:8px;margin:9px 0 14px}select{border:1px solid #d1dfd8;background:#fff;color:#354b43;border-radius:9px;padding:10px;width:100%;min-width:0;font-size:12px}
.listmeta{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#84938b;margin:12px 0}.list{display:grid;gap:6px;max-height:calc(100vh - 315px);overflow:auto;padding-right:4px;scrollbar-color:#c4d8cc transparent}.item{display:block;text-align:left;width:100%;padding:11px 12px;border-radius:10px;border:1px solid #e1eae5;background:#fff;min-width:0}.item.active{border-color:#4eaa87;background:#eff8f2;box-shadow:0 0 0 1px #9cd6b5}.item:hover{background:#f7fbf8}.itemHead{display:flex;justify-content:space-between;gap:8px}.itemSymbol{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;font-weight:700;color:#496d5d;max-width:80%}.itemPreview{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#243830;font-size:13px;margin:5px 0 7px}.state{font-size:10px;color:#a06b36}.state.done{color:#23825a}.state.bad{color:#c05b48}.pager{display:flex;justify-content:space-between;align-items:center;gap:8px;padding-top:14px;font-size:12px;color:#667a70}
main{min-width:0;padding:clamp(16px,2.7vw,38px);max-width:1500px;width:100%;margin:0 auto}.instruction{border:1px dashed #aecabb;border-radius:14px;padding:65px 20px;text-align:center;background:#fff;color:#788f84}.instruction b{display:block;color:#325846;font-size:18px;margin-bottom:5px}.editor{display:none}.editor.active{display:block}
.titleRow{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;margin-bottom:17px}.titleRow h2{margin:0;font-size:20px;letter-spacing:-.3px;overflow-wrap:anywhere}.origin{font-size:12px;color:#698074;overflow-wrap:anywhere;margin-top:6px;max-width:750px}.statusPill{border-radius:100px;background:#fff0db;color:#8e5e2a;padding:7px 11px;font-size:11px;font-weight:700}.statusPill.done{background:#e4f6ed;color:#207a50}.statusPill.bad{background:#ffece7;color:#a3422b}
.columns{display:grid;grid-template-columns:1fr 1fr;gap:14px}.pane{background:#fff;border:1px solid #dce7df;border-radius:15px;padding:20px;min-width:0;box-shadow:0 2px 6px #122e2006}.paneTitle{display:flex;justify-content:space-between;align-items:center;margin-bottom:17px;font-weight:730;font-size:14px}.readonlyBadge{font-size:11px;font-weight:500;color:#82968b}.sourceText{background:#f7faf8;border-radius:10px;border:1px solid #e2ede6;padding:16px;line-height:2.15;overflow-wrap:anywhere;white-space:pre-wrap;min-height:145px;font-size:14px}.token{display:inline-block;padding:0 7px;border:1px solid #c7d7d0;border-radius:6px;background:#e4ede9;color:#406254;font:11px/2 ui-monospace,Consolas,monospace;white-space:pre;user-select:none;vertical-align:baseline;cursor:not-allowed}.token:before{content:'⌁ ';color:#799a8c}.hint{color:#7d9085;font-size:12px;line-height:1.6;margin-top:13px}.segment{margin-bottom:12px}.segLabel{font-size:11px;font-weight:730;color:#6f8376;margin-bottom:6px}.textPart{display:block;resize:vertical;min-height:64px;max-width:100%;width:100%;line-height:1.5;padding:12px;border:1px solid #ccdcd2;background:#fff;border-radius:9px;font-size:14px;color:#263747;outline-color:#429b7b}.dividerToken{display:flex;align-items:center;gap:8px;margin:10px 0 13px}.dividerToken:after{content:'';height:1px;flex:1;background:#e7eee9}.actions{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:18px}.actions button{padding:12px 18px}.actions .clear{color:#a95042}.saveState{font-size:12px;color:#678675}.warning{background:#fff5ec;color:#985321;border:1px solid #eac69b;border-radius:10px;padding:15px;line-height:1.5;font-size:13px}.notice{margin-top:17px;padding:12px 14px;background:#eef7f0;border:1px solid #c7dfd0;border-radius:10px;color:#476e5a;font-size:12px;line-height:1.55}.bottom{color:#7c9084;font-size:12px;line-height:1.65;margin-top:23px}.kbd{font:11px ui-monospace,monospace;background:#eff3ef;border:1px solid #dfe7e1;border-radius:4px;padding:2px 4px;color:#607568}
.toast{position:fixed;bottom:22px;right:24px;padding:13px 17px;border-radius:10px;background:#225d46;color:#fff;font-size:13px;box-shadow:0 12px 35px #254b3555;z-index:10;max-width:min(500px,90vw)}.toast.error{background:#984433}.hidden{display:none!important}
.drop{position:fixed;inset:0;background:#123c2ac9;z-index:20;display:none;align-items:center;justify-content:center;color:white;font-size:27px;font-weight:730;border:12px dashed #d4ede1}.drop.active{display:flex}
@media(max-width:1060px){.shell{grid-template-columns:270px minmax(0,1fr)}.columns{grid-template-columns:1fr}.list{max-height:600px}}
@media(max-width:710px){.shell{display:flex;flex-direction:column}aside{border-right:0;border-bottom:1px solid #dce6e1}.list{max-height:205px}.columns{grid-template-columns:1fr}.metrics{gap:4px}.metric{padding:0 6px}.metric strong{font-size:17px}.top h1{font-size:18px}.topActions{width:100%}.topActions button{flex:1}.bottom{margin-bottom:18px}}
</style>
</head>
<body>
<header class="top">
  <div class="brand"><span class="logo" aria-hidden="true">L</span><div><h1>LeafGreen <span style="font-weight:450;color:#84988b">/ Студия перевода</span></h1><div class="sub">English + Русский · полностью автономный HTML-редактор</div></div></div>
  <div class="topActions"><button id="loadBtn" title="Загрузить сохранённый каталог en_ru.csv">↥ Загрузить CSV</button><button id="downloadBtn" class="primary" title="Сохранить изменения в файл en_ru.csv">↧ Скачать CSV</button><input id="fileInput" class="fileInput" type="file" accept=".csv,text/csv"></div>
</header>
<section class="metrics"><div class="metric"><strong id="totalCount">—</strong><small>всего строк</small></div><div class="metric"><strong id="doneCount">—</strong><small>переведено</small></div><div class="metric"><strong id="leftCount">—</strong><small>осталось</small></div><div class="progress"><div id="progressFill" class="progressFill"></div></div></section>
<div class="shell">
<aside>
  <div class="sidetitle">Каталог текстов</div>
  <input id="search" class="search" placeholder="Поиск: текст, персонаж, файл…" aria-label="Поиск строк" autocomplete="off">
  <div class="filterrow"><select id="filter" aria-label="Фильтр по готовности"><option value="all">Все строки</option><option value="todo">Без перевода</option><option value="done">Переведённые</option><option value="needs">Нужна проверка</option></select><select id="kind" aria-label="Тип строки"><option value="all">Все источники</option><option value="asm">Диалоги ASM</option><option value="c">Тексты C</option></select></div>
  <div class="listmeta"><span id="resultCount">Загрузка…</span><span id="pageNumber">—</span></div><div id="list" class="list" aria-label="Найденные строки"></div>
  <div class="pager"><button id="prevBtn">← Назад</button><span id="pageRange">—</span><button id="nextBtn">Дальше →</button></div>
</aside>
<main>
  <div id="instruction" class="instruction"><b>Выберите строку слева</b>Английский оригинал и русский перевод появятся рядом. Изменять можно только обычный текст.</div>
  <div id="editor" class="editor"><div class="titleRow"><div><h2 id="symbol">—</h2><div id="origin" class="origin"></div></div><span id="statusPill" class="statusPill">Без перевода</span></div>
  <div class="columns">
   <section class="pane"><div class="paneTitle"><span>🇬🇧 Английский оригинал</span><span class="readonlyBadge">Только чтение</span></div><div id="english" class="sourceText"></div><div class="hint">Оригинал берётся из репозитория. Этот редактор его не изменяет.</div></section>
   <section class="pane"><div class="paneTitle"><span>🇷🇺 Русский перевод</span><span class="readonlyBadge">Коды защищены</span></div><div id="russian"></div><div class="hint">🔒 Плашки с игровыми переменными, управляющими кодами и окончанием строки нельзя удалить, переместить или исправить. Переводите только текстовые блоки.</div></section>
  </div>
  <div class="actions"><button id="saveBtn" class="primary">Сохранить строку</button><button id="resetBtn" class="clear">Очистить перевод</button><span class="saveState" id="saveState">Изменений нет</span></div>
  <div class="notice">Переводы сохраняются в памяти этой страницы до скачивания CSV. Используйте <b>«Скачать CSV»</b> и замените полученным файлом <code>localization/en_ru.csv</code> в репозитории. HTML не редактирует исходники игры.</div>
  <p class="bottom"><span class="kbd">Ctrl + S</span> — сохранить строку · <span class="kbd">Ctrl + Shift + S</span> — скачать каталог · Нет необходимости запускать Python или сервер.<br>База двуязычной ROM уже добавлена в исходники. Переведённые строки попадут в игру после генерации ресурсов и сборки ROM.</p>
  </div>
</main></div>
<div id="toast" class="toast hidden" role="status" aria-live="polite"></div><div id="drop" class="drop">Отпустите CSV, чтобы импортировать перевод</div>
<script id="embedded-data" type="application/json">__EMBEDDED_CATALOG__</script>
<script>
'use strict';
// Game codes must remain in their exact original order: {PLAYER}, \\n, \\p, \\l, \\v..., $, etc.
const PROTECTED = /\{[^{}]*\}|\\.|(?<!\\)\$/g;
const FORBIDDEN_IN_TEXT = /[{}\\$"\r\n]/;
const COLUMNS = ['key','type','file','symbol','english','russian','status'];
const $ = id => document.getElementById(id);
const state={rows:[],filtered:[],page:0,selected:-1,dirty:false,unexported:false,displayedParts:[]};
let toastTimeout=0;
function notify(message,bad=false){const el=$('toast');el.textContent=message;el.className='toast'+(bad?' error':'');clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.classList.add('hidden'),4800);}
function tokens(s){return s.match(PROTECTED)||[]}
function parts(s){return s.split(PROTECTED)}
function tokensEqual(a,b){return a.length===b.length && a.every((x,i)=>x===b[i]);}
function isInvalid(r){return !!r.russian && (r.status==='source_changed' || !tokensEqual(tokens(r.english),tokens(r.russian)));}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;}
function pill(t){const n=el('span','token',t);n.setAttribute('aria-label','Заблокированный игровой код '+t);n.title='Неизменяемый служебный код';return n;}
function csvParse(input){
 const text=input.replace(/^\uFEFF/,'');let rows=[],row=[],value='',quoted=false;
 for(let i=0;i<text.length;i++){
   const c=text[i];
   if(quoted){if(c==='"' && text[i+1]==='"'){value+='"';i++;}else if(c==='"'){quoted=false;}else{value+=c;}continue;}
   if(c==='"' && value===''){quoted=true;continue;}
   if(c===','){row.push(value);value='';continue;}
   if(c==='\r' || c==='\n'){
     if(c==='\r' && text[i+1]==='\n')i++;
     row.push(value);if(row.some(x=>x!==''))rows.push(row);row=[];value='';continue;
   }
   value+=c;
 }
 if(quoted)throw Error('Незакрытые кавычки в CSV.');
 if(row.length || value){row.push(value);rows.push(row);}
 if(!rows.length)throw Error('Пустой CSV.');
 const head=rows.shift();for(const field of COLUMNS){if(!head.includes(field))throw Error('Отсутствует колонка '+field);}
 const seen=new Set();const result=[];
 for(let i=0;i<rows.length;i++){
   if(rows[i].length!==head.length)throw Error('Некорректное число колонок в строке CSV '+(i+2));
   const out={};head.forEach((x,j)=>out[x]=rows[i][j]);
   if(!out.key || seen.has(out.key))throw Error('Пустой или повторяющийся идентификатор в строке '+(i+2));
   seen.add(out.key);result.push(out);
 }
 return result;
}
function csvCell(s){s=String(s??'');return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;}
function csvWrite(rows){return '\ufeff'+[COLUMNS.join(','),...rows.map(r=>COLUMNS.map(k=>csvCell(r[k])).join(','))].join('\r\n')+'\r\n';}
function metrics(){const done=state.rows.filter(r=>!!r.russian).length;$('totalCount').textContent=state.rows.length.toLocaleString('ru-RU');$('doneCount').textContent=done.toLocaleString('ru-RU');$('leftCount').textContent=(state.rows.length-done).toLocaleString('ru-RU');$('progressFill').style.width=(state.rows.length?100*done/state.rows.length:0)+'%';}
const PAGE=36;
function updateResults(reset){
 if(reset)state.page=0;
 const q=$('search').value.trim().toLocaleLowerCase('ru'),status=$('filter').value,kind=$('kind').value;
 const results=[];
 for(let i=0;i<state.rows.length;i++){
  const r=state.rows[i];
  if(kind!=='all' && r.type!==kind)continue;
  if(status==='todo' && r.russian)continue;
  if(status==='done' && (!r.russian || isInvalid(r)))continue;
  if(status==='needs' && !isInvalid(r))continue;
  if(q && !(r.key+' '+r.english+' '+r.russian).toLocaleLowerCase('ru').includes(q))continue;
  results.push(i);
 }
 state.filtered=results;state.page=Math.max(0,Math.min(state.page,Math.ceil(results.length/PAGE)-1));renderList();
}
function renderList(){
 const root=$('list');root.replaceChildren();const start=state.page*PAGE, end=Math.min(start+PAGE,state.filtered.length);
 for(const i of state.filtered.slice(start,end)){
  const r=state.rows[i];const b=el('button','item'+(i===state.selected?' active':''));b.type='button';
  const head=el('div','itemHead');head.append(el('span','itemSymbol',r.symbol||r.key),el('span','state'+(isInvalid(r)?' bad':r.russian?' done':''),isInvalid(r)?'⚠':r.russian?'●':'○'));
  b.append(head,el('div','itemPreview',r.russian||r.english),el('div','state'+(isInvalid(r)?' bad':r.russian?' done':''),isInvalid(r)?'Проверьте служебные коды':r.russian?'Переведено':'Не переведено'));
  b.addEventListener('click',()=>choose(i));root.append(b);
 }
 $('resultCount').textContent=`Найдено: ${state.filtered.length.toLocaleString('ru-RU')}`;
 $('pageNumber').textContent=`Страница ${state.filtered.length?state.page+1:0}`;
 $('pageRange').textContent=state.filtered.length?`${start+1}–${end}`:'0';
 $('prevBtn').disabled=state.page===0;$('nextBtn').disabled=end>=state.filtered.length;
}
function choose(i){
 if(state.dirty && !confirm('У текущей строки есть несохранённые изменения. Отменить их?'))return;
 state.selected=i;state.dirty=false;
 $('instruction').classList.add('hidden');$('editor').classList.add('active');
 const r=state.rows[i],invalid=isInvalid(r);
 $('symbol').textContent=r.symbol||'Игровая строка';$('origin').textContent=r.file+' · '+r.type+' · '+r.key;
 const badge=$('statusPill');badge.textContent=invalid?'Нужна проверка':r.russian?'Переведено':'Без перевода';badge.className='statusPill'+(invalid?' bad':r.russian?' done':'');
 const en=$('english');en.replaceChildren();const enParts=parts(r.english), enTokens=tokens(r.english);
 for(let j=0;j<enParts.length;j++){en.append(document.createTextNode(enParts[j]));if(j<enTokens.length)en.append(pill(enTokens[j]));}
 const edit=$('russian');edit.replaceChildren();state.displayedParts=[];
 if(invalid){edit.append(el('div','warning','У текущего русского перевода нарушены служебные коды или исходный текст изменился. Чтобы избежать повреждения игры, редактор не позволяет редактировать такую запись. Можно очистить её и перевести заново.'));$('saveBtn').disabled=true;}
 else{
  const ruParts=parts(r.russian||r.english);
  for(let j=0;j<ruParts.length;j++){
    const segment=el('div','segment');segment.append(el('div','segLabel','Текстовый фрагмент '+(j+1)));
    const textarea=el('textarea','textPart');textarea.value=ruParts[j];textarea.spellcheck=true;textarea.rows=Math.min(8,Math.max(2,Math.ceil(ruParts[j].length/70)));textarea.setAttribute('aria-label','Перевод фрагмента '+(j+1));
    textarea.addEventListener('beforeinput',e=>{
      if(e.inputType==='insertLineBreak' || e.inputType==='insertParagraph' || (e.data && FORBIDDEN_IN_TEXT.test(e.data))){e.preventDefault();notify('Служебные символы { } \\ $ и кавычки запрещены в редактируемом тексте.',true);}
    });
    textarea.addEventListener('paste',e=>{
      const text=e.clipboardData?.getData('text/plain')||'';
      if(FORBIDDEN_IN_TEXT.test(text)){e.preventDefault();notify('Вставка отменена: в тексте есть служебные символы или переносы строк.',true);}
    });
    textarea.addEventListener('input',()=>{state.dirty=true;saveStatus();});
    segment.append(textarea);edit.append(segment);state.displayedParts.push(textarea);
    if(j<enTokens.length){const sep=el('div','dividerToken');sep.append(pill(enTokens[j]));edit.append(sep);}
  }
  $('saveBtn').disabled=false;
 }
 saveStatus();renderList();
}
function saveStatus(){ $('saveState').textContent=state.dirty?'● Строка не сохранена':state.unexported?'● CSV ещё не скачан':'Все изменения сохранены в файле';document.title=(state.unexported?'● ':'')+'LeafGreen · Студия перевода EN / RU';}
function saveSelected(){
 if(state.selected<0)return true;
 const r=state.rows[state.selected];if(isInvalid(r)){notify('Нельзя сохранять строку с повреждёнными кодами. Очистите перевод.',true);return false;}
 const segments=state.displayedParts.map(x=>x.value);
 if(segments.some(x=>FORBIDDEN_IN_TEXT.test(x))){notify('Найдены запрещённые управляющие символы. Проверьте текстовые фрагменты.',true);return false;}
 if(segments.some(x=>x.length>10000)){notify('Слишком длинный текстовый фрагмент.',true);return false;}
 const t=tokens(r.english);if(segments.length!==t.length+1){notify('Ошибка структуры текстовых блоков.',true);return false;}
 const reconstructed=segments.map((x,i)=>x+(t[i]||'')).join('');
 if(!tokensEqual(t,tokens(reconstructed))){notify('Служебные коды не совпадают с оригиналом.',true);return false;}
 if(!reconstructed.trim()){notify('Пустой перевод нельзя сохранить. Используйте «Очистить перевод».',true);return false;}
 const changed=r.russian!==reconstructed || r.status!=='translated';
 if(changed){r.russian=reconstructed;r.status='translated';state.unexported=true;metrics();}
 state.dirty=false;choose(state.selected);notify(changed?'Перевод сохранён в памяти. Скачайте CSV, чтобы записать его на диск.':'Перевод без изменений.');return true;
}
function resetSelected(){
 if(state.selected<0)return;
 if(!confirm('Удалить русский перевод выбранной строки? Оригинал останется на месте.'))return;
 const r=state.rows[state.selected];if(r.russian||r.status!=='untranslated'){r.russian='';r.status='untranslated';state.unexported=true;}
 state.dirty=false;metrics();choose(state.selected);notify('Русский перевод удалён. Скачайте CSV для сохранения на диск.');
}
function download(){
 if(state.dirty && !saveSelected())return;
 const blob=new Blob([csvWrite(state.rows)],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob);
 const a=document.createElement('a');a.href=url;a.download='en_ru.csv';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2500);
 state.unexported=false;saveStatus();notify('CSV сформирован. Сохраните файл в localization/en_ru.csv вашего репозитория.');
}
async function importFile(file){
 if(!file)return;
 if(!file.name.toLowerCase().endsWith('.csv')){notify('Можно импортировать только CSV-файлы.',true);return;}
 if(file.size>25*1024*1024){notify('Размер CSV не должен превышать 25 МБ.',true);return;}
 if((state.dirty||state.unexported) && !confirm('Текущие несохранённые изменения будут потеряны. Загрузить другой CSV?'))return;
 try{
  const parsed=csvParse(await file.text());if(!parsed.length)throw Error('Нет текстовых записей.');
  state.rows=parsed;state.selected=-1;state.dirty=false;state.unexported=false;
  $('editor').classList.remove('active');$('instruction').classList.remove('hidden');$('search').value='';$('filter').value='all';$('kind').value='all';
  metrics();updateResults(true);saveStatus();notify(`Загружено ${parsed.length.toLocaleString('ru-RU')} строк. Английский текст доступен только для чтения.`);
 }catch(err){notify('Не удалось загрузить CSV: '+err.message,true);}
}
$('saveBtn').addEventListener('click',saveSelected);$('resetBtn').addEventListener('click',resetSelected);$('downloadBtn').addEventListener('click',download);
$('loadBtn').addEventListener('click',()=>$('fileInput').click());$('fileInput').addEventListener('change',async e=>{await importFile(e.target.files[0]);e.target.value='';});
let debounce;
$('search').addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>updateResults(true),130)});
$('filter').addEventListener('change',()=>updateResults(true));$('kind').addEventListener('change',()=>updateResults(true));
$('prevBtn').addEventListener('click',()=>{state.page=Math.max(0,state.page-1);renderList();});$('nextBtn').addEventListener('click',()=>{state.page++;renderList();});
document.addEventListener('keydown',e=>{
 if((e.ctrlKey||e.metaKey)&&e.shiftKey&&e.key.toLowerCase()==='s'){e.preventDefault();download();}
 else if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();saveSelected();}
});
window.addEventListener('beforeunload',e=>{if(state.dirty||state.unexported){e.preventDefault();e.returnValue='';}});
let dragDepth=0;
window.addEventListener('dragenter',e=>{if(e.dataTransfer?.types?.includes('Files')){dragDepth++;$('drop').classList.add('active');}});
window.addEventListener('dragleave',()=>{dragDepth--;if(dragDepth<=0){dragDepth=0;$('drop').classList.remove('active');}});
window.addEventListener('dragover',e=>{if(e.dataTransfer?.types?.includes('Files'))e.preventDefault();});
window.addEventListener('drop',e=>{e.preventDefault();dragDepth=0;$('drop').classList.remove('active');if(e.dataTransfer?.files?.length)importFile(e.dataTransfer.files[0]);});
try{state.rows=JSON.parse($('embedded-data').textContent);if(state.rows.length<10000)throw Error('Неожиданное число строк.');metrics();updateResults(true);saveStatus();}
catch(err){notify('Ошибка встроенного каталога: '+err.message,true);}
</script>
</body>
</html>'''
# Protect HTML raw script JSON from injection (game source is untrusted strings).
json_str=json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
html=template.replace('__EMBEDDED_CATALOG__',json_str)
assert html.count('__EMBEDDED_CATALOG__')==0
out=root/'tools/localization/leafgreen-offline-editor.html'
out.write_text(html,encoding='utf-8')
# The standalone HTML stays in tools/localization/. Keep it alongside the repository.
print(out, out.stat().st_size, 'rows', len(rows))
