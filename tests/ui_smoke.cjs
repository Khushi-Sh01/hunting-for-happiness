/* DOM smoke tests with real JS and a stub-model FastAPI/SQLite server. Not visual QA. */
const fs=require('fs');
const {JSDOM}=require('jsdom');
const root=require('path').resolve(__dirname,'..');
const BASE=process.env.UI_TEST_BASE_URL || 'http://127.0.0.1:8765';
let offline=false, errors=[];
let liveDom;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function wait(check){for(let i=0;i<100;i++){if(check())return;await sleep(20)}throw Error('UI condition timeout');}
function make(saved){
 const dom=new JSDOM(fs.readFileSync(root+'/frontend/index.html','utf8'),{url:BASE,runScripts:'outside-only'});
 const w=dom.window;
 if(saved)w.localStorage.setItem('hfh-v1',saved);
 w.fetch=(path,options)=>{if(offline)return Promise.reject(Error('offline'));return fetch(new URL(path,BASE),options)};
 w.addEventListener('error',event=>errors.push(event.message));
 w.eval(fs.readFileSync(root+'/frontend/app.js','utf8'));
 liveDom=dom; return dom;
}
(async()=>{
 let dom=make(); let w=dom.window,d=w.document;
 await wait(()=>d.querySelector('#privacy').textContent.length>0);
 d.querySelector('#questForm').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
 await wait(()=>!d.querySelector('#offer').hidden);
 d.querySelector('#accept').click();
 await wait(()=>!d.querySelector('#zen').hidden);
 let saved=w.localStorage.getItem('hfh-v1'); let start=JSON.parse(saved).quest.started_at;
 dom.window.close(); dom=make(saved);w=dom.window;d=w.document;
 await wait(()=>!d.querySelector('#zen').hidden);
 if(JSON.parse(w.localStorage.getItem('hfh-v1')).quest.started_at!==start)throw Error('Timer restarted');
 d.querySelector('#return').click();
 d.querySelector('#note').value='I saw rounded and pointed leaves. Their edges made me slow down.';
 d.querySelector('#note').dispatchEvent(new w.Event('input',{bubbles:true}));
 saved=w.localStorage.getItem('hfh-v1');
 dom.window.close();offline=true;dom=make(saved);w=dom.window;d=w.document;
 if(d.querySelector('#reflection').hidden)throw Error('Offline reflection not restored');
 if(!d.querySelector('#note').value.includes('rounded'))throw Error('Draft missing');
 d.querySelector('#reflectionForm').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
 await wait(()=>d.querySelector('#status').textContent.includes('Connection unavailable'));
 if(JSON.parse(w.localStorage.getItem('hfh-v1')).receipt)throw Error('Fake offline reward');
 await wait(()=>!d.querySelector('#submit').disabled);offline=false;
 d.querySelector('#reflectionForm').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
 await wait(()=>!d.querySelector('#result').hidden);
 if(!d.querySelector('#award').textContent.includes('+45 XP'))throw Error('Reward not rendered');
 saved=w.localStorage.getItem('hfh-v1');dom.window.close();dom=make(saved);w=dom.window;d=w.document;
 if(d.querySelector('#result').hidden)throw Error('Result did not persist');
 await wait(()=>d.querySelector('#progress').textContent.includes('45 XP'));
 if(errors.length)throw Error(errors.join('\n'));
 console.log(JSON.stringify({DOMFlow:'pass',timestampPersistence:'pass',draftPersistence:'pass',offlineSubmissionRetainsDraft:'pass',noOfflineReward:'pass',reconnectSubmission:'pass',resultPersistence:'pass',errors}));
 dom.window.close();
})().catch(error=>{console.error(error);if(liveDom)liveDom.window.close();process.exitCode=1});
