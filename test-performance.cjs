// Adaptive graphics should respond to a sustained slow frame rate, not one bad frame.
const fs=require('fs'),assert=require('assert'),html=fs.readFileSync('index.html','utf8');
const source=html.slice(html.indexOf('let gfxN=0,'),html.indexOf('// ===== แมพสี่ทิศ:'));
function scenario(frames){let calls=0;const run=new Function('navigator','document','setGfx','say','refreshDisplayUI','gfxHigh','gfxReady',source+';return {probe:gfxProbe,ready:()=>gfxReady};')({webdriver:false},{hidden:false},(on,persist)=>{assert.equal(on,false);assert.equal(persist,true);calls++},()=>{},()=>{},true,false);for(const dt of frames)run.probe(dt);return {calls,ready:run.ready()};}
assert.deepEqual(scenario(Array(89).fill(1/15)),{calls:0,ready:true});
assert.equal(scenario(Array(100).fill(1/15)).calls,1,'sustained slow frames enable lower graphics');
assert.equal(scenario([...Array(30).fill(1/15),...Array(59).fill(1/60),1/5]).calls,0,'isolated slow frame does not trigger');
assert.equal(scenario(Array(100).fill(1/60)).calls,0,'smooth frames keep graphics');
console.log('PASS: adaptive graphics reacts once to sustained slow frames and ignores isolated delays');
